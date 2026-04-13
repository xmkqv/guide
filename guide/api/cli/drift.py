"""Watch workspace: track contract drift in .md specs, cross-ref in code files.

.md files are spec — fences ```{lang}:{contract}``` define baselines.
Code files (.sql, .py, .ts, etc.) are scanned for contract name matches.

On .md save → compare body to cached baseline → inject/strip :{diff} suffix.
On any save → rebuild {doc}.gen.md mapping contracts to code paths.
Duplicate contracts within a file: last occurrence wins.

Gen file format::

    ---
    name: {doc}.gen
    resolver: |                          # planned: Starlark (not yet implemented)
      def resolve(ctx):
          if ctx["difference"] > 30:
              return run(ctx["contract"])
          return None
    ---
    create-user:
        db/init.sql

Resolver design (planned):

    Starlark (github.com/bazelbuild/starlark) — Python dialect, sandboxed.
    Executes computation (if/for/def/dict/list) but cannot perform I/O.
    Host injects builtins (run, notify, ...) that the resolver can call.
    Guaranteed termination (no while, no recursion, frozen collections).

    Starlark decides *whether* and *what*. Host decides *how*.

    Python integration: pystarlark (PyO3 wrapper over starlark-rust).
"""

import asyncio
import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from watchfiles import Change, awatch  # type: ignore[import-untyped]

from guide.utils import make_watch_filter

DIFFS_REL = Path(".qx/diffs.json")
_LANG_EXT: dict[str, str] = {
    "sql": ".sql",
    "py": ".py",
    "python": ".py",
    "ts": ".ts",
    "tsx": ".tsx",
    "js": ".js",
    "jsx": ".jsx",
    "rs": ".rs",
    "rust": ".rs",
}
_CODE_EXT = frozenset(_LANG_EXT.values())
_WATCHED = _CODE_EXT | {".md"}
_RE_FENCE = re.compile(
    r"^(?P<indent>\s*)"
    r"(?P<ticks>`{3,})"
    r"(?P<lang>[a-z]+):(?P<contract>[a-z][a-z0-9]*(?:-[a-z0-9]+)*)"
    r"(?=[:\s]|$)"
    r"(?::(?P<diff>\d+))?"
    r"(?P<rest>.*)$",
)

type Cache = dict[str, str]


@dataclass
class Block:
    contract: str
    lang: str
    body: str
    fence_idx: int
    ticks: str


@dataclass(frozen=True)
class Drift:
    """Track contract codeblock drift against cached baselines."""


def run(_cmd: Drift) -> None:
    asyncio.run(_drift())


def find_workspace() -> Path:
    c = Path.cwd().resolve()
    return next((p for p in [c, *c.parents] if (p / ".git").exists()), c)


def load_cache(ws: Path) -> Cache:
    p = ws / DIFFS_REL
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(ws: Path, cache: Cache) -> None:
    p = ws / DIFFS_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")


def difference(a: str, b: str) -> int:
    def norm(s: str) -> str:
        return "\n".join(ln.rstrip() for ln in s.split("\n")).strip()

    a, b = norm(a), norm(b)
    return (
        0 if a == b else max(1, round((1 - SequenceMatcher(None, a, b).ratio()) * 100))
    )


def parse_contracts(content: str) -> list[Block]:
    lines, blocks, i = content.split("\n"), [], 0
    while i < len(lines):
        if m := _RE_FENCE.match(lines[i]):
            ticks, start, body = m.group("ticks"), i, []
            i += 1
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith(ticks) and not s.replace("`", ""):
                    break
                body.append(lines[i])
                i += 1
            blocks.append(
                Block(
                    m.group("contract"), m.group("lang"), "\n".join(body), start, ticks
                )
            )
        i += 1
    by_name = {b.contract: b for b in blocks}
    return sorted(by_name.values(), key=lambda b: b.fence_idx)


def update_fences(
    content: str, cache: Cache, rel: str
) -> tuple[str, list[str], list[Block]]:
    blocks = parse_contracts(content)
    if not blocks:
        return content, [], []
    lines, changes = content.split("\n"), []
    for block in reversed(blocks):
        key = f"{rel}::{block.contract}"
        cached = cache.get(key)
        if cached is None:
            cache[key] = block.body
            changes.append(f"  {block.contract}: cached (new)")
            continue
        diff = difference(cached, block.body)
        if not (m := _RE_FENCE.match(lines[block.fence_idx])):
            continue
        base = f"{m.group('indent')}{block.ticks}{block.lang}:{block.contract}"
        new_fence = (
            f"{base}:{diff}{m.group('rest')}" if diff else f"{base}{m.group('rest')}"
        )
        if not diff:
            cache[key] = block.body
        if lines[block.fence_idx] != new_fence:
            lines[block.fence_idx] = new_fence
            changes.append(
                f"  {block.contract}: {'Δ' + str(diff) if diff else 'converged'}"
            )
    return "\n".join(lines), changes, blocks


def _matches(content: str, contract: str) -> bool:
    return contract in content or contract.replace("-", "_") in content


def _scan_refs(ws: Path, contracts: dict[str, str], filt) -> dict[str, set[str]]:
    refs: dict[str, set[str]] = {}
    for p in ws.rglob("*"):
        if (
            not p.is_file()
            or p.suffix not in _CODE_EXT
            or not filt(Change.modified, str(p))
        ):
            continue
        try:
            text = p.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        rel = str(p.relative_to(ws))
        for name, lang in contracts.items():
            if _LANG_EXT.get(lang) == p.suffix and _matches(text, name):
                refs.setdefault(name, set()).add(rel)
    return refs


def _write_gen(
    ws: Path, doc_rel: str, blocks: list[Block], refs: dict[str, set[str]]
) -> None:
    entries: list[str] = []
    for b in blocks:
        paths = sorted(refs.get(b.contract, set()))
        entry = (
            b.contract + ":\n" + "".join(f"\t{p}\n" for p in paths)
            if paths
            else b.contract + ":"
        )
        entries.append(entry)
    name = Path(doc_rel).stem + ".gen"
    (ws / doc_rel).with_suffix(".gen.md").write_text(
        f"---\nname: {name}\n---\n" + "\n".join(entries) + "\n"
    )


async def _drift() -> None:
    ws = find_workspace()
    cache = load_cache(ws)
    filt = make_watch_filter(ws)
    doc_blocks: dict[str, list[Block]] = {}
    contracts: dict[str, str] = {}
    for md in sorted(ws.rglob("*.md")):
        if md.name.endswith(".gen.md") or not filt(Change.modified, str(md)):
            continue
        blocks = parse_contracts(md.read_text())
        if blocks:
            rel = str(md.relative_to(ws))
            doc_blocks[rel] = blocks
            contracts.update({b.contract: b.lang for b in blocks})
    refs = _scan_refs(ws, contracts, filt)
    for doc_rel, blks in doc_blocks.items():
        _write_gen(ws, doc_rel, blks, refs)
    print(f"drift: watching {ws}")  # noqa: T201
    print(
        f"drift: {len(contracts)} contracts, {sum(len(v) for v in refs.values())} refs"
    )  # noqa: T201
    async for deltas in awatch(ws, debounce=500, watch_filter=filt):
        regen = False
        for _, path_str in deltas:
            path = Path(path_str)
            if (
                not path.is_file()
                or path.suffix not in _WATCHED
                or path.name.endswith(".gen.md")
            ):
                continue
            try:
                content = path.read_text()
            except (OSError, UnicodeDecodeError):
                continue
            rel = str(path.relative_to(ws))
            if path.suffix == ".md":
                updated, changes, blocks = update_fences(content, cache, rel)
                if blocks:
                    doc_blocks[rel] = blocks
                    contracts.update({b.contract: b.lang for b in blocks})
                elif rel in doc_blocks:
                    del doc_blocks[rel]
                if changes:
                    if updated != content:
                        path.write_text(updated)
                    save_cache(ws, cache)
                    for c in changes:
                        print(f"{rel}: {c.strip()}")  # noqa: T201
                regen = True
            else:
                for name, lang in contracts.items():
                    if _LANG_EXT.get(lang) != path.suffix:
                        continue
                    was_ref = rel in refs.get(name, set())
                    is_ref = _matches(content, name)
                    if is_ref and not was_ref:
                        refs.setdefault(name, set()).add(rel)
                        regen = True
                    elif was_ref and not is_ref:
                        refs[name].discard(rel)
                        regen = True
        if regen:
            for doc_rel, blks in doc_blocks.items():
                _write_gen(ws, doc_rel, blks, refs)

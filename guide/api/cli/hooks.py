"""Git hook management."""

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import tyro

HOOK_TEMPLATE = """\
#!/bin/bash
set -euo pipefail

[ "${QX_COMMIT_HOOK_ACTIVE:-}" = "1" ] && exit 0
[ -f "$(git rev-parse --git-dir)/MERGE_HEAD" ] && exit 0

exec guide hooks run changelog
"""


def _repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def _load_env(repo: Path) -> None:
    env_file = repo / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            os.environ[key.strip()] = val.strip()


@dataclass(frozen=True)
class _Install:
    """Install a git hook into the current repo."""

    name: Annotated[str, tyro.conf.Positional]


@dataclass(frozen=True)
class _Run:
    """Run a hook handler (called by the hook itself)."""

    name: Annotated[str, tyro.conf.Positional]


@dataclass(frozen=True)
class Hooks:
    """Manage git hooks."""

    cmd: (
        Annotated[_Install, tyro.conf.subcommand("install", prefix_name=False)]
        | Annotated[_Run, tyro.conf.subcommand("run", prefix_name=False)]
    )


KNOWN_HOOKS = {"changelog"}


def run(cmd: Hooks) -> int:
    match cmd.cmd:
        case _Install(name=name):
            if name not in KNOWN_HOOKS:
                print(
                    f"Unknown hook: {name}. Known: {', '.join(sorted(KNOWN_HOOKS))}",
                    file=sys.stderr,
                )
                return 1

            repo = _repo_root()
            hook_path = repo / ".git" / "hooks" / "pre-commit"

            # Remove stale hooks if they're ours
            for stale_name in ("post-commit", "commit-msg"):
                stale = repo / ".git" / "hooks" / stale_name
                if stale.exists() and "guide hooks run changelog" in stale.read_text():
                    stale.unlink()
                    print(f"Removed stale {stale}", file=sys.stderr)

            if hook_path.exists():
                print(f"Overwriting existing {hook_path}", file=sys.stderr)

            hook_path.write_text(HOOK_TEMPLATE)
            hook_path.chmod(0o755)
            print(f"Installed pre-commit hook → {hook_path}", file=sys.stderr)
            return 0

        case _Run(name=name):
            if name not in KNOWN_HOOKS:
                print(f"Unknown hook: {name}", file=sys.stderr)
                return 1

            repo = _repo_root()
            _load_env(repo)

            qx_commit = shutil.which("qx-commit")
            if not qx_commit:
                print("qx-commit not found on PATH", file=sys.stderr)
                return 1

            result = subprocess.run([qx_commit, "post"])
            return result.returncode

    return 0

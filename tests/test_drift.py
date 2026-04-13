"""Tests for guide.api.cli.drift — contract fence parsing, drift tracking, cross-ref."""

import json
from pathlib import Path

import pytest

from guide.api.cli.drift import (
    Block,
    _matches,
    _scan_refs,
    _write_gen,
    difference,
    load_cache,
    parse_contracts,
    save_cache,
    update_fences,
)


# ── parse_contracts ──────────────────────────────────────────────────


def test_parse_single_contract():
    content = "```sql:create-user\nSELECT 1;\n```"
    blocks = parse_contracts(content)
    assert len(blocks) == 1
    assert blocks[0].contract == "create-user"
    assert blocks[0].lang == "sql"
    assert blocks[0].body == "SELECT 1;"
    assert blocks[0].fence_idx == 0
    assert blocks[0].ticks == "```"


def test_parse_multiple_contracts():
    content = "```sql:create-user\nSELECT 1;\n```\n\n```py:validate\npass\n```"
    blocks = parse_contracts(content)
    assert len(blocks) == 2
    assert blocks[0].contract == "create-user"
    assert blocks[1].contract == "validate"


def test_parse_rejects_snake_case():
    content = "```sql:create_user\nSELECT 1;\n```"
    assert parse_contracts(content) == []


def test_parse_rejects_pascal_case():
    content = "```sql:CreateUser\nSELECT 1;\n```"
    assert parse_contracts(content) == []


def test_parse_four_backtick_fence():
    content = "````sql:create-user\nSELECT 1;\n````"
    blocks = parse_contracts(content)
    assert len(blocks) == 1
    assert blocks[0].ticks == "````"


def test_parse_unclosed_fence_body_to_eof():
    content = "```sql:create-user\nSELECT 1;\nSELECT 2;"
    blocks = parse_contracts(content)
    assert len(blocks) == 1
    assert blocks[0].body == "SELECT 1;\nSELECT 2;"


def test_parse_duplicate_last_wins():
    content = "```sql:create-user\nFIRST\n```\n```sql:create-user\nSECOND\n```"
    blocks = parse_contracts(content)
    assert len(blocks) == 1
    assert blocks[0].body == "SECOND"


def test_parse_with_existing_diff_suffix():
    content = "```sql:create-user:42\nSELECT 1;\n```"
    blocks = parse_contracts(content)
    assert len(blocks) == 1
    assert blocks[0].contract == "create-user"


def test_parse_with_indent():
    content = "  ```sql:create-user\n  SELECT 1;\n  ```"
    blocks = parse_contracts(content)
    assert len(blocks) == 1


def test_parse_no_contracts():
    content = "# Just a heading\n\nSome text.\n```python\nprint('hi')\n```"
    assert parse_contracts(content) == []


def test_parse_close_fence_needs_enough_ticks():
    content = "````sql:create-user\nBODY\n```\nSTILL BODY\n````"
    blocks = parse_contracts(content)
    assert len(blocks) == 1
    assert "STILL BODY" in blocks[0].body
    assert "```" in blocks[0].body


# ── difference ───────────────────────────────────────────────────────


def test_difference_identical():
    assert difference("SELECT 1;", "SELECT 1;") == 0


def test_difference_trailing_whitespace_ignored():
    assert difference("SELECT 1;  ", "SELECT 1;") == 0


def test_difference_trailing_newlines_ignored():
    assert difference("SELECT 1;\n\n", "SELECT 1;") == 0


def test_difference_completely_different():
    d = difference("aaa", "zzz")
    assert d == 100


def test_difference_small_change():
    d = difference("SELECT * FROM users;", "SELECT * FROM users WHERE id = 1;")
    assert 1 <= d <= 50


def test_difference_at_least_one_when_different():
    d = difference("SELECT 1;", "SELECT 2;")
    assert d >= 1


# ── update_fences ────────────────────────────────────────────────────


def test_update_fences_first_encounter_caches():
    content = "```sql:create-user\nSELECT 1;\n```"
    cache: dict[str, str] = {}
    updated, changes, blocks = update_fences(content, cache, "spec.md")
    assert "spec.md::create-user" in cache
    assert cache["spec.md::create-user"] == "SELECT 1;"
    assert any("cached (new)" in c for c in changes)
    assert updated == content  # no fence modification on first encounter


def test_update_fences_injects_diff():
    content = "```sql:create-user\nSELECT 2;\n```"
    cache = {"spec.md::create-user": "SELECT 1;"}
    updated, changes, blocks = update_fences(content, cache, "spec.md")
    assert ":create-user:" in updated  # diff suffix injected
    # diff value is after the contract name
    lines = updated.split("\n")
    assert lines[0].startswith("```sql:create-user:")
    assert any("Δ" in c for c in changes)


def test_update_fences_strips_diff_on_convergence():
    body = "SELECT 1;"
    content = "```sql:create-user:42\nSELECT 1;\n```"
    cache = {"spec.md::create-user": body}
    updated, changes, blocks = update_fences(content, cache, "spec.md")
    assert updated.startswith("```sql:create-user\n")
    assert any("converged" in c for c in changes)


def test_update_fences_no_write_when_unchanged():
    body = "SELECT 1;"
    content = f"```sql:create-user\n{body}\n```"
    cache = {"spec.md::create-user": body}
    updated, changes, blocks = update_fences(content, cache, "spec.md")
    assert updated == content
    assert changes == []


def test_update_fences_preserves_rest():
    content = "```sql:create-user {.highlight}\nSELECT 2;\n```"
    cache = {"spec.md::create-user": "SELECT 1;"}
    updated, changes, blocks = update_fences(content, cache, "spec.md")
    assert "{.highlight}" in updated


def test_update_fences_returns_blocks():
    content = "```sql:create-user\nSELECT 1;\n```"
    cache: dict[str, str] = {}
    _, _, blocks = update_fences(content, cache, "spec.md")
    assert len(blocks) == 1
    assert blocks[0].contract == "create-user"


def test_update_fences_no_contracts():
    content = "Just plain text"
    cache: dict[str, str] = {}
    updated, changes, blocks = update_fences(content, cache, "spec.md")
    assert updated == content
    assert changes == []
    assert blocks == []


# ── _matches ─────────────────────────────────────────────────────────


def test_matches_kebab():
    assert _matches("-- create-user", "create-user")


def test_matches_snake():
    assert _matches("CREATE TABLE create_user", "create-user")


def test_matches_absent():
    assert not _matches("SELECT 1;", "create-user")


# ── cache I/O ────────────────────────────────────────────────────────


def test_cache_roundtrip(tmp_path: Path):
    cache = {"spec.md::create-user": "SELECT 1;"}
    save_cache(tmp_path, cache)
    loaded = load_cache(tmp_path)
    assert loaded == cache


def test_load_cache_missing(tmp_path: Path):
    assert load_cache(tmp_path) == {}


def test_load_cache_corrupt(tmp_path: Path):
    p = tmp_path / ".qx" / "diffs.json"
    p.parent.mkdir(parents=True)
    p.write_text("not json{{{")
    assert load_cache(tmp_path) == {}


# ── _scan_refs ───────────────────────────────────────────────────────


def _always_allow(_change, _path):
    return True


def test_scan_refs_finds_match(tmp_path: Path):
    sql = tmp_path / "db" / "migration.sql"
    sql.parent.mkdir()
    sql.write_text("CREATE TABLE create_user (id INT);")
    contracts = {"create-user": "sql"}
    refs = _scan_refs(tmp_path, contracts, _always_allow)
    assert "create-user" in refs
    assert "db/migration.sql" in refs["create-user"]


def test_scan_refs_ignores_wrong_extension(tmp_path: Path):
    py = tmp_path / "app.py"
    py.write_text("create_user = True")
    contracts = {"create-user": "sql"}  # looking for .sql, not .py
    refs = _scan_refs(tmp_path, contracts, _always_allow)
    assert refs == {}


def test_scan_refs_respects_filter(tmp_path: Path):
    sql = tmp_path / "migration.sql"
    sql.write_text("create_user")
    contracts = {"create-user": "sql"}
    refs = _scan_refs(tmp_path, contracts, lambda _c, _p: False)
    assert refs == {}


def test_scan_refs_nested_paths(tmp_path: Path):
    """Contract refs in deeply nested code files get correct relative paths."""
    deep = tmp_path / "db" / "migrations" / "v1" / "init.sql"
    deep.parent.mkdir(parents=True)
    deep.write_text("CREATE TABLE create_user (id INT);")
    sibling = tmp_path / "db" / "seeds" / "seed.sql"
    sibling.parent.mkdir(parents=True)
    sibling.write_text("INSERT INTO create_user VALUES (1);")
    unrelated = tmp_path / "src" / "app.sql"
    unrelated.parent.mkdir()
    unrelated.write_text("SELECT 1;")  # no contract match
    contracts = {"create-user": "sql"}
    refs = _scan_refs(tmp_path, contracts, _always_allow)
    paths = refs["create-user"]
    assert "db/migrations/v1/init.sql" in paths
    assert "db/seeds/seed.sql" in paths
    assert "src/app.sql" not in paths


def test_scan_refs_multiple_contracts_nested(tmp_path: Path):
    """Multiple contracts matched across nested files."""
    (tmp_path / "api").mkdir()
    (tmp_path / "api" / "handlers.ts").write_text("import { createUser, deleteUser }")
    (tmp_path / "db").mkdir()
    (tmp_path / "db" / "schema.sql").write_text("create_user\ndelete_user")
    contracts = {"create-user": "ts", "delete-user": "sql"}
    refs = _scan_refs(tmp_path, contracts, _always_allow)
    # ts file matches ts contract via kebab substring
    assert "api/handlers.ts" not in refs.get(
        "create-user", set()
    )  # createUser != create-user
    # sql file matches sql contract via snake
    assert "db/schema.sql" in refs.get("delete-user", set())


def test_write_gen_nested_doc(tmp_path: Path):
    """Gen file written as sibling to a nested spec doc."""
    docs = tmp_path / "docs" / "api"
    docs.mkdir(parents=True)
    spec = docs / "spec.md"
    spec.write_text("")
    blocks = [Block("create-user", "sql", "", 0, "```")]
    refs = {"create-user": {"db/init.sql"}}
    _write_gen(tmp_path, "docs/api/spec.md", blocks, refs)
    gen = docs / "spec.gen.md"
    assert gen.exists()
    content = gen.read_text()
    assert "name: spec.gen" in content
    assert "\tdb/init.sql" in content


# ── _write_gen ───────────────────────────────────────────────────────


def test_write_gen_with_refs(tmp_path: Path):
    spec = tmp_path / "spec.md"
    spec.write_text("")
    blocks = [Block("create-user", "sql", "", 0, "```")]
    refs = {"create-user": {"db/migration.sql", "db/seed.sql"}}
    _write_gen(tmp_path, "spec.md", blocks, refs)
    gen = tmp_path / "spec.gen.md"
    assert gen.exists()
    content = gen.read_text()
    assert content.startswith("---\nname: spec.gen\n---\n")
    assert "create-user:" in content
    assert "\tdb/migration.sql" in content
    assert "\tdb/seed.sql" in content


def test_write_gen_no_refs(tmp_path: Path):
    spec = tmp_path / "spec.md"
    spec.write_text("")
    blocks = [Block("create-user", "sql", "", 0, "```")]
    _write_gen(tmp_path, "spec.md", blocks, {})
    content = (tmp_path / "spec.gen.md").read_text()
    assert "create-user:" in content
    assert "\t" not in content


def test_write_gen_multiple_contracts(tmp_path: Path):
    spec = tmp_path / "spec.md"
    spec.write_text("")
    blocks = [
        Block("create-user", "sql", "", 0, "```"),
        Block("delete-user", "sql", "", 5, "```"),
    ]
    refs = {"create-user": {"a.sql"}}
    _write_gen(tmp_path, "spec.md", blocks, refs)
    content = (tmp_path / "spec.gen.md").read_text()
    assert "create-user:" in content
    assert "delete-user:" in content


# ── integration: full flow ───────────────────────────────────────────


def test_full_flow(tmp_path: Path):
    """Simulate the on-save lifecycle: cache → drift → converge → gen."""
    spec = tmp_path / "spec.md"
    sql = tmp_path / "db" / "init.sql"
    sql.parent.mkdir()

    # 1. Initial spec
    spec.write_text("```sql:create-user\nCREATE TABLE users (id INT);\n```\n")
    sql.write_text("-- create-user\nCREATE TABLE users (id INT);\n")

    # 2. First encounter → cache baseline
    cache: dict[str, str] = {}
    content = spec.read_text()
    updated, changes, blocks = update_fences(content, cache, "spec.md")
    assert "cached (new)" in changes[0]
    assert updated == content  # no change on first encounter

    # 3. Modify spec body → drift detected
    spec.write_text(
        "```sql:create-user\nCREATE TABLE users (id INT, name TEXT);\n```\n"
    )
    content = spec.read_text()
    updated, changes, blocks = update_fences(content, cache, "spec.md")
    assert any("Δ" in c for c in changes)
    lines = updated.split("\n")
    assert ":create-user:" in lines[0]  # diff suffix injected
    spec.write_text(updated)

    # 4. Revert to baseline → convergence
    spec.write_text("```sql:create-user:99\nCREATE TABLE users (id INT);\n```\n")
    content = spec.read_text()
    updated, changes, blocks = update_fences(content, cache, "spec.md")
    assert any("converged" in c for c in changes)
    assert ":create-user\n" in updated  # suffix stripped

    # 5. Cross-ref scan
    contracts = {b.contract: b.lang for b in blocks}
    refs = _scan_refs(tmp_path, contracts, _always_allow)
    assert "db/init.sql" in refs.get("create-user", set())

    # 6. Gen file
    _write_gen(tmp_path, "spec.md", blocks, refs)
    gen = (tmp_path / "spec.gen.md").read_text()
    assert "---\nname: spec.gen\n---\n" in gen
    assert "create-user:" in gen
    assert "\tdb/init.sql" in gen

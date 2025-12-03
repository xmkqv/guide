from __future__ import annotations

import ast
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from guide.paths import RESULTS_DIR, Preferences
from guide.utils import inject

type Language = Literal["py", "ts", "md"]


def discover_pytest_tests(base_dir: Path) -> Iterator[str]:
    """Discover all pytest test nodeids in a directory via AST parsing."""
    for pattern in ("test_*.py", "*_test.py"):
        for test_file in base_dir.rglob(pattern):
            rel_path = test_file.relative_to(base_dir)
            try:
                tree = ast.parse(test_file.read_text())
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    if not any(
                        isinstance(p, ast.ClassDef) for p in ast.walk(tree) if node in getattr(p, "body", [])
                    ):
                        yield f"{rel_path}::{node.name}"

                elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                            yield f"{rel_path}::{node.name}::{item.name}"

CLAUDE_MD_NAME = "claude.md"


class Lang(BaseModel):
    language: Language
    claude_context: list[Path | str] = Field(default_factory=list[Path | str])
    results_file_name: str = "placeholder.md"

    def install_claude(self, dir: Path) -> None:
        claude_md = dir / CLAUDE_MD_NAME
        inject(claude_md, *[str(p) for p in self.claude_context])

    def results_path(self, base_dir: Path) -> Path:
        return base_dir / RESULTS_DIR / self.results_file_name

    def discover_tests(self, base_dir: Path) -> Iterator[str]:
        match self.language:
            case "py":
                return discover_pytest_tests(base_dir)
            case "ts":
                return iter([])  # TODO: implement for TS
            case _:
                return iter([])

    def load_test_results(self, base_dir: Path) -> Iterator[TestResult]:
        def load_pytest_results():
            results_file = self.results_path(base_dir)
            if not results_file.exists():
                return
            for line in results_file.read_text().splitlines():
                if not line.strip():
                    continue
                item = json.loads(line)
                if item.get("when") != "call":
                    continue
                yield TestResult(
                    ref=item["nodeid"],
                    status="passed" if item["outcome"] == "passed" else "failed",
                    details={"duration": str(item.get("duration", 0))},
                )

        def load_ts_results():
            raise NotImplementedError("TS results loading not implemented yet")

        match self.language:
            case "py":
                return load_pytest_results()
            case "ts":
                return load_ts_results()
            case _:
                raise NotImplementedError(
                    f"Test results loading not implemented for language: {self.language}"
                )


class TestResult(BaseModel):
    ref: str
    status: str
    details: dict[str, str] | None = None


md = Lang(language="md")


py = Lang(
    language="py",
    claude_context=[
        Preferences.code.directive,
        Preferences.py.directive,
        "Use pytest-reportlog to log test results in JSONL format.",
    ],
    results_file_name="results.jsonl",
)

ts = Lang(
    language="ts",
    claude_context=[Preferences.code.directive, Preferences.ts.directive],
)

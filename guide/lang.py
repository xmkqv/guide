from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from guide.paths import Preferences
from guide.utils import inject

type Language = Literal["py", "ts", "md"]

CLAUDE_MD_NAME = "claude.md"


class Lang(BaseModel):
    language: Language
    claude_context: list[Path] = Field(default_factory=list)
    results_file_name: str = "placeholder.md"

    def install_claude(self, dir: Path) -> None:
        claude_md = dir / CLAUDE_MD_NAME
        inject(claude_md, *[to_directive(p) for p in self.claude_context])


def to_directive(path: Path | str) -> str:
    path = Path(path).resolve()
    assert path.exists(), f"Path does not exist: {path}"
    return f"@{path}"


md = Lang(language="md")

py = Lang(
    language="py",
    claude_context=[Preferences.code, Preferences.py],
    results_file_name="results.jsonl",
)

ts = Lang(
    language="ts",
    claude_context=[Preferences.code, Preferences.ts],
)

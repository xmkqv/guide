from pathlib import Path
from typing import Any, Literal

from guide.utils import AutoDir

GUIDE_YAML_NAME = "guide.yaml"
RESULTS_DIR_NAME = "results"
RESULTS_DIR = Path("results")


class Workspace(AutoDir, dir="."):
    guide = GUIDE_YAML_NAME
    results = RESULTS_DIR_NAME


PYPROJECT_TOML_NAME = "pyproject.toml"
PACKAGE_JSON_NAME = "package.json"

###

this_file = Path(__file__).resolve()
GUIDES = this_file.parent.parent / "guides"
STYLE = GUIDES / "style"

###


class Style(AutoDir, dir=STYLE):
    spec_schema = "spec.schema.yaml"
    comms = "comms"
    moods = "moods"


class Preferences(AutoDir, dir=GUIDES / "preferences"):
    py = "py.md"
    ts = "ts.md"
    code = "code.md"
    ml = "ml.md"
    meta = "meta.md"
    prose = "prose.md"

    @property
    def directive(self) -> str:
        return f"@{self.path}"


class Commands(AutoDir, dir=GUIDES / "commands"):
    gen_limn = "gen-limn.md"
    gen_comm = "gen-comm.md"
    gen_mood = "gen-mood.md"

    async def aask(
        self,
        *content: str,
        model: Literal["opus", "sonnet"] = "opus",
        timeout_seconds: float = 300.0,
        **details: Any,
    ) -> str:
        from guide.llm import aask

        formatted = "\n\n".join([f"## {k}\n\n{v}" for k, v in details.items()])
        parts = (self.path.read_text(), *content, formatted)

        return await aask(*parts, model=model, timeout_seconds=timeout_seconds)

"""Mission: declarative anti-fragile self-healing reifier.

Flow: Design -> Code -> Signal
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from guide.design import Spec
from guide.lang import Lang
from guide.loader import Loader
from guide.logger import Logger
from guide.signal import Test
from guide.tester import Tester


def gen_acronym(name: str) -> str:
    """Generate lowercase acronym from name words."""
    words = name.split()
    return "".join(w[0].lower() for w in words if w)


class Mission(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    dir: Path

    name: str
    lang: Lang

    logger: Logger | None = Field(default=None, exclude=True)
    tester: Tester | None = Field(default=None, exclude=True)

    design: Annotated[list[Spec], Field(default_factory=list)]
    signal: Annotated[list[Test], Field(default_factory=list)]
    datasets: Annotated[list[Loader[Any]], Field(default_factory=list)]

    @model_validator(mode="before")
    @classmethod
    def generate_id(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Generate id from name if not provided."""
        if "id" not in data and "name" in data:
            data["id"] = gen_acronym(data["name"])
        return data

    @model_validator(mode="after")
    def configure_tester(self) -> Self:
        """Auto-instantiate tester from lang if not provided."""
        if self.tester is None:
            match self.lang:
                case Lang.Py:
                    from guide.tester.py import Tester as PyTester

                    object.__setattr__(self, "tester", PyTester())
                case Lang.Ts:
                    from guide.tester.ts import Tester as TsTester

                    object.__setattr__(self, "tester", TsTester())
        return self

    @property
    def path(self) -> Path:
        return self.dir / "mission.yaml"

    def sync(self) -> Mission:
        """Sync test results and return updated Mission."""
        assert self.tester is not None, "Tester is not configured"
        signals = self.tester.get_signal(self)
        new_mission = self.model_copy(update={"signal": signals})
        dump = new_mission.model_dump(exclude={"dir"}, mode="json")
        with self.path.open("w") as f:
            yaml.safe_dump(
                dump,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
        return new_mission

    @staticmethod
    def find_nearest() -> Path:
        current = Path.cwd()
        while current != current.parent:
            candidate = current / "mission.yaml"
            if candidate.exists():
                return candidate
            current = current.parent
        raise FileNotFoundError("No mission.yaml found, create it first")

    @classmethod
    def load_nearest(cls) -> Mission:
        path = cls.find_nearest()
        with path.open("r") as f:
            data = yaml.safe_load(f)
        return Mission.model_validate({**data, "dir": path.parent})

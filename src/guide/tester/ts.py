"""TypeScript test result parser (stub).

Not yet implemented. Will parse vitest/jest JSON output into Tests.
"""

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict

from guide import signal
from guide.lang import Lang

if TYPE_CHECKING:
    from guide.mission import Mission


class Tester(BaseModel):
    model_config = ConfigDict(frozen=True)

    lang: Literal[Lang.Ts] = Lang.Ts
    results_path_stem: str = "results/results.json"

    def get_signal(self, mission: "Mission") -> list[signal.Test]:
        results_path = mission.dir / self.results_path_stem
        if not results_path.exists():
            raise FileNotFoundError(f"Results file not found: {results_path}")
        raise NotImplementedError("TypeScript tester not yet implemented")

"""TypeScript logger bridge.

Installs build-time instrumentation configuration for TypeScript missions.
The actual instrumentation is handled by the logbot unplugin.
"""

import json
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from guide.lang import Lang

if TYPE_CHECKING:
    from guide.mission import Mission


class Logger(BaseModel):
    model_config = ConfigDict(frozen=True)

    lang: Literal[Lang.Ts] = Lang.Ts
    patterns: list[str] = Field(default_factory=list)

    def install(self, mission: "Mission") -> None:
        config = {
            "enabled": True,
            "patterns": {"include": [f"/{p}/" for p in self.patterns]},
            "capture": {"args": True, "return": True, "timing": True, "errors": True},
        }
        config_path = mission.dir / "logbot.config.json"
        with config_path.open("w") as f:
            json.dump(config, f, indent=2)

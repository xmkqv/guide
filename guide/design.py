from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Spec(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(pattern=r"^S\d+$")
    name: str
    aspect_id: str | None = Field(default=None, pattern=r"^S\d+$")
    detail: dict[str, Any] = Field(default_factory=dict)

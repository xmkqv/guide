import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Test(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(pattern=r"^T\d+$")
    ref: str
    args: dict[str, Any] = Field(default_factory=dict)
    data: dict[str, Any] = Field(default_factory=dict)


def gen_timestamp() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")

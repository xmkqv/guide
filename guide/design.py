import secrets
from collections.abc import Generator
from pathlib import Path

from pydantic import BaseModel, Field

from guide.lang import TestResult


class Spec(BaseModel):
    key: str = Field(default_factory=lambda: secrets.token_hex(3))
    defn: str = "..."
    test: "Test | None" = None
    limn: "Limn | None" = None
    specs: list["Spec"] = Field(default_factory=list["Spec"])

    def flat(self) -> Generator["Spec"]:
        yield self
        for spec in self.specs:
            yield from spec.flat()


class Design(Spec):
    pass


class Test(BaseModel):
    ref: str
    result: TestResult | None = None


class Limn(BaseModel):
    type: str
    path: Path
    desc: str

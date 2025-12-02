import secrets
from collections.abc import Generator
from pathlib import Path
from typing import Any, Union

from pydantic import BaseModel, Field

from guide.utils import get_func


class Spec(BaseModel):
    key: str = Field(default_factory=lambda: secrets.token_hex(3))
    defn: str = "..."
    test: Union["Test", None] = None
    limn: Union["Limn", None] = None
    specs: list["Spec"] = Field(default_factory=list["Spec"])

    async def sync(
        self,
        *,
        tests: bool = False,
        limns: bool = False,
    ):
        if self.test and tests:
            yield self.test.sync()
        if self.limn and limns:
            yield self.limn.sync()

    def flat(self) -> Generator["Spec"]:
        def _recurse(specs: list["Spec"]) -> Generator["Spec"]:
            for spec in specs:
                yield spec
                yield from _recurse(spec.specs)

        yield from _recurse(self.specs)


class Design(Spec):
    report: dict[str, Any] = Field(default_factory=dict)

    async def sync(
        self, *, tests: bool = False, limns: bool = False, report: bool = False
    ):
        async for r in super().sync(tests=tests, limns=limns):
            yield r

        if report:
            raise NotImplementedError("Design.report sync not implemented yet")


class Test(BaseModel):
    ref: str
    result: dict[str, Any]

    async def sync(self) -> None:
        try:
            get_func(self.ref)
        except (ImportError, AttributeError) as e:
            raise RuntimeError(f"Failed to import test function '{self.ref}'") from e


class Limn(BaseModel):
    type: str
    path: Path
    desc: str

    async def sync(self):
        from guide.llm import aask
        from guide.paths import Commands

        await aask(Commands.gen_limn, self.model_dump_json())

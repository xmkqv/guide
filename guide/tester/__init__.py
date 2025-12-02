from typing import Annotated

from pydantic import Field

from . import py, ts

type Tester = Annotated[py.Tester | ts.Tester, Field(discriminator="lang")]

__all__ = ["Tester"]

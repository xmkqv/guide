from typing import Annotated

from pydantic import Field

from . import py, ts

Logger = Annotated[py.Logger | ts.Logger, Field(discriminator="lang")]

__all__ = ["Logger"]

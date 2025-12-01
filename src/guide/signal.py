"""Signal: test results linked to design specifications.

Tests declare spec linkage via docstring pattern: @design(S0, S1, ...)
"""

import datetime
import re
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

SPEC_ID_PATTERN = re.compile(r"^S\d+$")
DESIGN_DOCSTRING_PATTERN = re.compile(r"@design\(([^)]+)\)")


class Test(BaseModel):
    """Test result linked to specifications.

    Attributes:
        id: Unique test identifier (T0, T1, ...)
        ref: Qualified path to programmatic test (optional)
        spec_ids: Verified spec references this test covers
        result: Framework-structured test result data
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(pattern=r"^T\d+$")
    ref: str | None = Field(default=None)
    spec_ids: Annotated[list[str], Field(default_factory=list)]
    result: dict[str, Any] = Field(default_factory=dict)

    @field_validator("spec_ids")
    @classmethod
    def validate_spec_ids(cls, v: list[str]) -> list[str]:
        for sid in v:
            if not SPEC_ID_PATTERN.match(sid):
                raise ValueError(f"Invalid spec_id: {sid}, must match /S\\d+/")
        return v


def parse_design_ids(docstring: str | None) -> list[str]:
    """Extract spec IDs from docstring @design(...) pattern.

    Pattern: @design(S0, S1, S2)

    Returns list of valid spec IDs (matching /S\\d+/).
    Invalid IDs are silently ignored.
    """
    if not docstring:
        return []

    match = DESIGN_DOCSTRING_PATTERN.search(docstring)
    if not match:
        return []

    raw_ids = match.group(1).split(",")
    return [
        sid.strip()
        for sid in raw_ids
        if SPEC_ID_PATTERN.match(sid.strip())
    ]


def gen_timestamp() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")

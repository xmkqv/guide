from typing import Literal

import attrs


@attrs.frozen
class LoadError:
    """Error during mission loading."""

    stage: Literal["find", "parse", "validate"]
    reason: str
    path: str | None = None
    remediation: str | None = None


@attrs.frozen
class SyncError:
    """Error during mission sync."""

    stage: Literal["test", "persist"]
    reason: str
    remediation: str | None = None


type DashboardError = LoadError | SyncError

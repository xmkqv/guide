"""SpecFlow control for visualizing spec hierarchies as flow diagrams."""

from __future__ import annotations

from typing import Any

from flet.core.constrained_control import ConstrainedControl


class SpecFlow(ConstrainedControl):
    """Interactive flow diagram for spec hierarchies.

    Uses graphview to render specs as nodes with parent-child edges.
    """

    def __init__(
        self,
        nodes: str | None = None,
        connections: str | None = None,
        expand: bool | int | None = None,
        **kwargs: Any,
    ):
        ConstrainedControl.__init__(self, expand=expand, **kwargs)
        self._set_attr("nodes", nodes or "[]")
        self._set_attr("connections", connections or "[]")

    def _get_control_name(self) -> str:
        return "spec_flow"

    @property
    def nodes(self) -> str:
        return self._get_attr("nodes") or "[]"

    @nodes.setter
    def nodes(self, value: str | None) -> None:
        self._set_attr("nodes", value or "[]")

    @property
    def connections(self) -> str:
        return self._get_attr("connections") or "[]"

    @connections.setter
    def connections(self, value: str | None) -> None:
        self._set_attr("connections", value or "[]")

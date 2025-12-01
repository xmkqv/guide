"""SpecFlow control for visualizing spec hierarchies as flow diagrams."""

from __future__ import annotations

from typing import Optional

from flet import LayoutControl, control


@control("spec_flow")
class SpecFlow(LayoutControl):
    """Interactive flow diagram for spec hierarchies.

    Wraps vyuh_node_flow to render specs as nodes with parent-child edges.
    Nodes and connections are JSON strings for Dart interop.
    """

    nodes: Optional[str] = None
    """JSON string of nodes: [{id, label, node_type, x, y}, ...]"""

    connections: Optional[str] = None
    """JSON string of connections: [{id, source_id, target_id}, ...]"""

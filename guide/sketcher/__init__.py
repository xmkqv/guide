"""Sketcher: Generate system diagrams from project structure.

Usage:
    from guide.sketcher import sketch

    result = sketch.tree(path=project_path, max_depth=3)
    results = sketch.all(project_path)
"""

from pathlib import Path
from typing import Literal

from .base import SketchResult

__all__ = ["SketchResult", "sketch"]


class _Sketcher:
    """Namespace for sketch operations with typed methods."""

    @staticmethod
    def tree(
        *,
        path: Path,
        max_depth: int = 4,
        exclude: tuple[str, ...] = (
            "__pycache__",
            ".git",
            ".cache",
            ".hypothesis",
            ".pytest_cache",
            ".ruff_cache",
            ".venv",
            "node_modules",
            "build",
            "dist",
        ),
    ) -> SketchResult:
        """Generate directory tree sketch."""
        from . import tree as _tree

        return _tree.sketch(_tree.Config(path=path, max_depth=max_depth, exclude=exclude))

    @staticmethod
    def dependency(
        *,
        path: Path,
        format: Literal["mermaid", "ascii"] = "mermaid",
        max_depth: int = 2,
        internal_only: bool = True,
        exclude: tuple[str, ...] = (
            "__pycache__",
            ".git",
            ".venv",
            "node_modules",
            "tests",
            ".pytest_cache",
            "build",
            "dist",
        ),
    ) -> SketchResult:
        """Generate module dependency graph."""
        from . import dependency as _dep

        return _dep.sketch(
            _dep.Config(
                path=path,
                format=format,
                max_depth=max_depth,
                internal_only=internal_only,
                exclude=exclude,
            )
        )

    @staticmethod
    def entity(
        *,
        path: Path,
        format: Literal["mermaid", "ascii"] = "mermaid",
        include_kinds: tuple[str, ...] = ("dataclass", "attrs", "pydantic", "namedtuple"),
        exclude: tuple[str, ...] = (
            "__pycache__",
            ".git",
            ".venv",
            "node_modules",
            "tests",
            ".pytest_cache",
            "build",
            "dist",
        ),
    ) -> SketchResult:
        """Generate domain entity diagram."""
        from . import entity as _ent

        return _ent.sketch(
            _ent.Config(
                path=path,
                format=format,
                include_kinds=include_kinds,
                exclude=exclude,
            )
        )

    @staticmethod
    def all(path: Path) -> list[SketchResult]:
        """Generate all sketches with default parameters."""
        return [
            _Sketcher.tree(path=path),
            _Sketcher.dependency(path=path),
            _Sketcher.entity(path=path),
        ]


sketch = _Sketcher()

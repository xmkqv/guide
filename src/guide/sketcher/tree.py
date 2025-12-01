"""Directory tree sketch module."""

from dataclasses import dataclass

from .base import SketchConfig, SketchResult
from .utils import build_tree_ascii


@dataclass(frozen=True)
class Config(SketchConfig):
    """Configuration for directory tree sketch."""

    max_depth: int = 4
    exclude: tuple[str, ...] = (
        "__pycache__",
        ".git",
        ".cache",
        ".hypothesis",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "node_modules",
    )


def sketch(config: Config) -> SketchResult:
    """Generate directory tree visualization."""
    content = build_tree_ascii(
        root=config.path,
        max_depth=config.max_depth,
        exclude=config.exclude,
    )

    return SketchResult(
        name="tree",
        format="ascii",
        content=content,
    )

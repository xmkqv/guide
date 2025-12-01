"""Base types for the sketcher system."""

import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Literal

# Module-level registry: name -> module containing Config and sketch
_registry: dict[str, types.ModuleType] = {}


@dataclass(frozen=True)
class SketchConfig:
    """Base configuration for all sketch types.

    Subclasses auto-register their containing module when defined.
    The module must also define a `sketch(config) -> SketchResult` function.
    """

    path: Path

    # Track registered names for introspection
    _registered: ClassVar[set[str]] = set()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Skip registration for base module
        if cls.__module__ == __name__:
            return
        module = sys.modules.get(cls.__module__)
        if module is not None:
            name = cls.__module__.split(".")[-1]
            _registry[name] = module
            SketchConfig._registered.add(name)


@dataclass(frozen=True)
class SketchResult:
    """Output from a sketch operation."""

    name: str
    format: Literal["mermaid", "ascii", "d2"]
    content: str


def get_registry() -> dict[str, types.ModuleType]:
    """Return the current sketcher registry."""
    return _registry.copy()

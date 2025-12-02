"""Import hook for automatic module instrumentation."""

import re
import sys
from collections.abc import Sequence
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType

from .instrument import instrument

_patterns: list[re.Pattern[str]] = []


class InstrumentingFinder(MetaPathFinder):
    """Meta path finder that instruments modules matching configured patterns."""

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        """Check if module should be instrumented, return None to defer to other finders."""
        if not _should_instrument(fullname):
            return None

        for finder in sys.meta_path:
            if finder is self:
                continue
            spec = finder.find_spec(fullname, path, target)
            if spec is not None and spec.loader is not None:
                spec.loader = InstrumentingLoader(spec.loader, fullname)
                return spec

        return None


class InstrumentingLoader(Loader):
    """Loader wrapper that instruments modules after loading."""

    def __init__(self, wrapped: Loader, fullname: str) -> None:
        self._wrapped = wrapped
        self._fullname = fullname

    def create_module(self, spec: ModuleSpec) -> ModuleType | None:
        """Delegate module creation to wrapped loader."""
        if hasattr(self._wrapped, "create_module"):
            return self._wrapped.create_module(spec)
        return None

    def exec_module(self, module: ModuleType) -> None:
        """Execute module then instrument it."""
        if hasattr(self._wrapped, "exec_module"):
            self._wrapped.exec_module(module)
        instrument(module)


def _should_instrument(fullname: str) -> bool:
    """Check if module name matches any configured pattern."""
    return any(pattern.match(fullname) for pattern in _patterns)


def install(*patterns: str) -> None:
    """Install import hook for automatic instrumentation of matching modules.

    Args:
        patterns: Regex patterns to match module names. Common patterns:
            - "ugi_flight" matches exactly "ugi_flight"
            - "ugi_flight.*" matches "ugi_flight" and all submodules
            - "ugi_(flight|ground).*" matches both packages and submodules

    Usage:
        import logbot

        # Instrument specific packages and submodules
        logbot.install(r"ugi_flight.*", r"ugi_ground.*")

        # All subsequent imports matching patterns will be instrumented
        import ugi_flight  # automatically instrumented
    """
    for p in patterns:
        try:
            _patterns.append(re.compile(p))
        except re.error as e:
            raise ValueError(f"invalid regex pattern {p!r}: {e}") from e

    if not any(isinstance(f, InstrumentingFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, InstrumentingFinder())


def uninstall() -> None:
    """Remove instrumentation hook and clear patterns."""
    _patterns.clear()
    sys.meta_path[:] = [
        f for f in sys.meta_path if not isinstance(f, InstrumentingFinder)
    ]


def is_installed() -> bool:
    """Check if instrumentation hook is active."""
    return any(isinstance(f, InstrumentingFinder) for f in sys.meta_path)

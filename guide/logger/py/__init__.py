"""Structured logging and instrumentation for SAR processing.

Usage:
    import logbot

    # Configure once at startup
    logbot.configure(enabled=True, level="INFO")

    # Get a logger for your module
    log = logbot.get_logger(__name__)

    # Log events
    log.info("processing_started", burst_id=123, n_samples=1024)

    # Time operations
    with logbot.timed(log, "range_compression", burst_id=123):
        result = compress_range(burst)

Instrumentation:
    import logbot

    # Manual decoration
    @logbot.traced
    def my_function(): ...

    # Instrument entire module
    import my_module
    logbot.instrument(my_module)

    # Auto-instrument on import
    logbot.install("ugi_flight", "ugi_ground")
    import ugi_flight  # automatically instrumented
"""

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from guide.lang import Lang

if TYPE_CHECKING:
    from guide.mission import Mission


class Logger(BaseModel):
    model_config = ConfigDict(frozen=True)

    lang: Literal[Lang.Py] = Lang.Py
    patterns: list[str] = Field(default_factory=list)

    def install(self, mission: "Mission") -> None:
        del mission  # unused for Python runtime instrumentation
        from .hook import install as _install

        _install(*self.patterns)


__all__ = ["Logger"]

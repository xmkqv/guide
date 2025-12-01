"""Structured logging for SAR processing with timing support."""

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

import structlog

DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40

_LEVELS = {"DEBUG": DEBUG, "INFO": INFO, "WARNING": WARNING, "ERROR": ERROR}


def configure(
    *,
    enabled: bool = True,
    json_output: bool = False,
    level: str = "INFO",
) -> None:
    """Configure structlog for the application.

    Args:
        enabled: Whether logging is active
        json_output: Use JSON format (for machine parsing) vs console (for humans)
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
    """
    if not enabled:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(50),
        )
        return

    level_num = _LEVELS.get(level.upper(), INFO)

    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty()))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level_num),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a logger bound to a module name."""
    return structlog.get_logger(name)


@contextmanager
def timed(
    logger: Any,
    operation: str,
    **context: Any,
) -> Iterator[None]:
    """Context manager for timing operations.

    Usage:
        log = get_logger(__name__)
        with timed(log, "range_compression", burst_id=123):
            compress_range(burst)
    """
    start = perf_counter()
    logger.info(f"{operation}.start", **context)
    try:
        yield
    except Exception:
        duration_ms = (perf_counter() - start) * 1000
        logger.exception(f"{operation}.error", duration_ms=duration_ms, **context)
        raise
    else:
        duration_ms = (perf_counter() - start) * 1000
        logger.info(f"{operation}.done", duration_ms=duration_ms, **context)

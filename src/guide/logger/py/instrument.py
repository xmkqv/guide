"""Function and module instrumentation via runtime wrapping."""

import functools
import inspect
from collections.abc import Callable
from time import perf_counter
from types import FunctionType, ModuleType
from typing import Any

import structlog

_capture_args_default = False
_capture_return_default = False


def set_defaults(*, capture_args: bool = False, capture_return: bool = False) -> None:
    """Set default capture settings for traced decorator."""
    global _capture_args_default, _capture_return_default
    _capture_args_default = capture_args
    _capture_return_default = capture_return


def _truncate(s: str, max_len: int = 200) -> str:
    """Truncate string to max length."""
    return s if len(s) <= max_len else s[: max_len - 3] + "..."


def _make_sync_wrapper(
    func: Callable[..., Any],
    logger: Any,
    fn_name: str,
    capture_args: bool,
    capture_return: bool,
) -> Callable[..., Any]:
    """Create sync wrapper for a function."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        ctx: dict[str, Any] = {}
        if capture_args and args:
            ctx["args"] = _truncate(repr(args))
        if capture_args and kwargs:
            ctx["kwargs"] = _truncate(repr(kwargs))

        logger.debug(f"{fn_name}.entry", **ctx)
        try:
            result = func(*args, **kwargs)
            ctx["duration_ms"] = round((perf_counter() - start) * 1000, 3)
            if capture_return and result is not None:
                ctx["result"] = _truncate(repr(result))
            logger.debug(f"{fn_name}.exit", **ctx)
            return result
        except BaseException:
            ctx["duration_ms"] = round((perf_counter() - start) * 1000, 3)
            logger.exception(f"{fn_name}.error", **ctx)
            raise

    return wrapper


def _make_async_wrapper(
    func: Callable[..., Any],
    logger: Any,
    fn_name: str,
    capture_args: bool,
    capture_return: bool,
) -> Callable[..., Any]:
    """Create async wrapper for a coroutine function."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        ctx: dict[str, Any] = {}
        if capture_args and args:
            ctx["args"] = _truncate(repr(args))
        if capture_args and kwargs:
            ctx["kwargs"] = _truncate(repr(kwargs))

        logger.debug(f"{fn_name}.entry", **ctx)
        try:
            result = await func(*args, **kwargs)
            ctx["duration_ms"] = round((perf_counter() - start) * 1000, 3)
            if capture_return and result is not None:
                ctx["result"] = _truncate(repr(result))
            logger.debug(f"{fn_name}.exit", **ctx)
            return result
        except BaseException:
            ctx["duration_ms"] = round((perf_counter() - start) * 1000, 3)
            logger.exception(f"{fn_name}.error", **ctx)
            raise

    return wrapper


def traced(
    fn: Callable[..., Any] | None = None,
    *,
    capture_args: bool | None = None,
    capture_return: bool | None = None,
) -> Any:
    """Decorator to trace function entry/exit/errors.

    Usage:
        @traced
        def my_function(): ...

        @traced(capture_args=True)
        def my_function(x, y): ...
    """
    _args = capture_args if capture_args is not None else _capture_args_default
    _return = capture_return if capture_return is not None else _capture_return_default

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        logger: Any = structlog.get_logger(getattr(func, "__module__", __name__))
        fn_name: str = getattr(func, "__name__", "unknown")

        if inspect.iscoroutinefunction(func):
            return _make_async_wrapper(func, logger, fn_name, _args, _return)
        return _make_sync_wrapper(func, logger, fn_name, _args, _return)

    if fn is not None:
        return decorator(fn)
    return decorator


def instrument(
    module: ModuleType,
    *,
    include: tuple[str, ...] | None = None,
    exclude: tuple[str, ...] | None = None,
) -> None:
    """Instrument all public functions and classes in a module.

    Args:
        module: The module to instrument
        include: Only instrument names containing these substrings
        exclude: Skip names containing these substrings
    """
    for name in list(vars(module).keys()):
        if name.startswith("_"):
            continue
        if exclude and any(p in name for p in exclude):
            continue
        if include and not any(p in name for p in include):
            continue

        obj = getattr(module, name)

        if isinstance(obj, FunctionType) and obj.__module__ == module.__name__:
            setattr(module, name, traced(obj))
        elif isinstance(obj, type) and obj.__module__ == module.__name__:
            instrument_class(obj)


def instrument_class(cls: type) -> None:
    """Instrument all public methods in a class."""
    for name, value in list(vars(cls).items()):
        if name.startswith("_"):
            continue

        if isinstance(value, FunctionType):
            setattr(cls, name, traced(value))
        elif isinstance(value, staticmethod):
            inner: Any = getattr(value, "__func__", None)  # pyright: ignore[reportUnknownArgumentType]
            if isinstance(inner, FunctionType):
                setattr(cls, name, staticmethod(traced(inner)))
        elif isinstance(value, classmethod):
            inner = getattr(value, "__func__", None)  # pyright: ignore[reportUnknownArgumentType]
            if isinstance(inner, FunctionType):
                setattr(cls, name, classmethod(traced(inner)))

import inspect
import os
import re
import sys
from collections.abc import Callable, Sequence
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import FunctionType, ModuleType

import numpy as np


def wrap_module_funcs[F: Callable[..., object]](
    mod: ModuleType, wrapper: Callable[[F], F]
) -> None:
    """Wrap all public functions in a module with the given decorator."""
    for name, obj in vars(mod).items():
        if all(
            (
                not name.startswith("_"),
                isinstance(obj, FunctionType),
                obj.__module__ == mod.__name__,
            )
        ):
            setattr(mod, name, wrapper(obj))


def mega_wrap[F: Callable[..., object]](
    patterns: list[str], wrapper: Callable[[F], F]
) -> None:
    """Install import hook that wraps functions in matching modules."""
    if not patterns:
        return
    compiled = [re.compile(p) for p in patterns]

    class Finder(MetaPathFinder):
        def find_spec(
            self,
            name: str,
            path: Sequence[str] | None,
            target: ModuleType | None = None,
        ) -> ModuleSpec | None:
            if not any(p.match(name) for p in compiled):
                return None

            for f in sys.meta_path:
                if f is self:
                    continue

                spec = f.find_spec(name, path, target)
                if spec and spec.loader:
                    orig = spec.loader.exec_module

                    def exec_module(
                        mod: ModuleType, _o: Callable[[ModuleType], None] = orig
                    ) -> None:
                        _o(mod)
                        wrap_module_funcs(mod, wrapper)

                    spec.loader.exec_module = exec_module  # type: ignore[method-assign]
                    return spec
            return None

    sys.meta_path.insert(0, Finder())


def get_func(ref: str) -> FunctionType:
    module_name, func_name = ref.rsplit(".", 1)
    module = __import__(module_name, fromlist=[func_name])
    func = getattr(module, func_name)
    assert inspect.isfunction(func)
    return func


def get_seed() -> int:
    return int(os.environ.get("RND_SEED", "42"))


def get_rng() -> np.random.Generator:
    return np.random.default_rng(get_seed())


def touch_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def inject(target: Path, *chunks: str):
    if not target.exists():
        target.touch()
    content = target.read_text()
    for directive in chunks:
        escaped = re.escape(directive)
        if not re.search(escaped, content):
            content += f"\n{directive}\n"
    target.write_text(content)


class AutoDir:
    base: Path

    def __init_subclass__(cls, base: Path, **kwargs: dict[str, object]) -> None:
        super().__init_subclass__(**kwargs)

        cls.base = base.resolve()
        for k, v in vars(cls).items():
            if k.startswith("_"):
                continue
            if not isinstance(v, str):
                continue
            patched_path = (cls.base / v).resolve()
            assert patched_path.exists(), f"Path does not exist: {patched_path}"
            setattr(cls, k, patched_path)

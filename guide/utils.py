import inspect
import os

import numpy as np


def get_func(ref: str):
    module_name, func_name = ref.rsplit(".", 1)
    module = __import__(module_name, fromlist=[func_name])
    func = getattr(module, func_name)
    assert inspect.isfunction(func)
    return func


def get_seed() -> int:
    return int(os.environ.get("RND_SEED", "42"))


def get_rng() -> np.random.Generator:
    return np.random.default_rng(get_seed())

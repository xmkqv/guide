from collections.abc import Callable
from typing import Protocol, Self, cast, runtime_checkable

import numpy as np
from pydantic import BaseModel, ConfigDict, PrivateAttr

from guide.utils import get_func, get_rng


@runtime_checkable
class DataType(Protocol):
    def __len__(self) -> int: ...

    def __getitem__(self, index: int | slice) -> Self: ...


class Loader[T: DataType](BaseModel):
    model_config = ConfigDict(frozen=True)

    ref: str
    target: str

    _loader: Callable[[str], T] | None = PrivateAttr(default=None, init=False)
    _data: T | None = PrivateAttr(default=None, init=False)

    def data(self, force_reload: bool = False) -> T:
        if self._data and not force_reload:
            return self._data
        loader = get_func(self.ref)
        data = loader(self.target)
        return cast("T", data)

    def data_split(self, /, test_fraction: float) -> tuple[T, T]:
        rng = get_rng()
        data = self.data()
        indices = np.arange(len(data))
        indices_shuffled = rng.permutation(indices)
        split_idx = int(len(indices) * (1 - test_fraction))
        idxs0 = slice(indices_shuffled[:split_idx])
        idxs1 = slice(indices_shuffled[split_idx:])
        set0 = data[idxs0]
        set1 = data[idxs1]
        return (set0, set1)


__all__ = ["Loader"]

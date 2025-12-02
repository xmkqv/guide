from collections.abc import Callable
from typing import Any, Protocol, Self, cast, runtime_checkable

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from guide import utils


@runtime_checkable
class DataType(Protocol):
    def __len__(self) -> int: ...

    def __getitem__(self, index: Any) -> Self: ...


class Datasets[T: DataType](BaseModel):
    model_config = ConfigDict(frozen=True)

    loaders: list["Loader[T]"] = Field(default_factory=list["Loader[T]"])


class Loader[T: DataType](BaseModel):
    model_config = ConfigDict(frozen=True)

    ref: str
    target: str
    detail: dict[str, Any] = Field(default_factory=dict)

    _loader: Callable[[str], T] | None = PrivateAttr(default=None, init=False)
    _data: T | None = PrivateAttr(default=None, init=False)

    def data(self, force_reload: bool = False) -> T:
        if self._data and not force_reload:
            return self._data
        loader = utils.get_func(self.ref)
        data = loader(self.target)
        return cast("T", data)

    def data_split(self, /, test_fraction: float) -> tuple[T, T]:
        rng = utils.get_rng()
        data = self.data()
        indices = np.arange(len(data))
        shuffled = rng.permutation(indices)
        split_idx = int(len(indices) * (1 - test_fraction))
        train_set = data[shuffled[:split_idx]]
        test_set = data[shuffled[split_idx:]]
        return (train_set, test_set)


__all__ = ["Datasets", "Loader"]

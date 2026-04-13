---
description: Python Style Guide
paths:
  - "**/*.py"
---

Python 3.13+. Declarative, fully-typed, no comments.

```python
from __future__ import annotations
from project import validation

BUFFER_SIZE = 4096

Position = NewType("Position", Float[Array, "3"])

class Repository(Protocol):
    def find(self, id: EntityId) -> Result[Entity, NotFound]: ...
    def save(self, entity: Entity) -> Result[Entity, SaveError]: ...

class Config(BaseModel):
    host: str
    port: int = 8080

def process(data: Input) -> Result[Output, ProcessError]:
    return validate(data).bind(transform).bind(persist)
```

# Types

- native syntax: `list[T]`, `dict[K, V]`, `X | None`
- Pydantic models for data
- Protocols for boundaries

# Results

errors as values, not exceptions (railway-oriented)

| approach | when |
| --- | --- |
| `expression.Result` | default; `.bind()` / `.map()` |
| `returns` library | complex pipelines |
| explicit `match` | simple cases |

- validate external input → Result types
- assert internal invariants

# Protocols

ports as protocols; adapters as implementations; inject explicitly; test via substitution

# Shape Typing

semantic dimensions + shape annotations; validate at boundaries

```python
Position = NewType("Position", Float[Array, "3"])
Trajectory = NewType("Trajectory", Float[Array, "time 3"])

@beartype  # boundary validation
def load_trajectory(path: Path) -> Trajectory: ...

def integrate(pos: Position, vel: Position, dt: float) -> Position:
    return pos + vel * dt  # internal: trust types
```

shape syntax: `"3"` → (3,); `"N 3"` → (N, 3); `""` → scalar

# Vectorization

broadcasting > loops; semantic reshaping

```python
corrected = raw * gain[:, np.newaxis] - bias

from einops import rearrange, reduce
pooled = reduce(tensor, "b h w c -> b c", "mean")
```

# Imports

import modules; explicit provenance

```python
from project import validation
result = validation.check_bounds(value, limits)
```

# Style

- immutable state, pure functions, comprehensions, generators, itertools
- `None` as default → initialize in function body
- side effects inside functions
- catch specific exceptions

invs:
  ¬ tautological comments
  ¬ bare `except`
  ¬ mutable default arguments
  ¬ shadowing builtins
  ¬ `from module import *`

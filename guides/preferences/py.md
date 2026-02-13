# Python

Write fully-typed Python 3.13+ with native syntax (`list[T]`, `dict[K, V]`).
Use Pydantic models.
Use functional style: immutable state, pure functions, comprehensions, generators, itertools.
Use `None` as default, initialize in function body.
Execute side effects inside functions.
Catch specific exceptions.
Validate external input with Result types. Assert internal invariants.
Preserve builtin names.

## Result Types

Railway-oriented programming. Chain fallible operations; surface errors as values.

| Approach            | When                          |
|---------------------|-------------------------------|
| `expression.Result` | Default, `.bind()` / `.map()` |
| `returns` library   | Complex pipelines             |
| Explicit `match`    | Simple cases                  |

```python
def process(data: Input) -> Result[Output, ProcessError]:
    return validate(data).bind(transform).bind(persist)
```

## Protocols

Ports as protocols. Adapters as implementations. Inject explicitly. Test via substitution.

```python
class Repository(Protocol):
    def find(self, id: EntityId) -> Result[Entity, NotFound]: ...
    def save(self, entity: Entity) -> Result[Entity, SaveError]: ...
```

## Shape Typing

Semantic dimensions with shape annotations. Validate at boundaries.

```python
Position = NewType("Position", Float[Array, "3"])
Trajectory = NewType("Trajectory", Float[Array, "time 3"])

@beartype  # boundary validation
def load_trajectory(path: Path) -> Trajectory: ...

def integrate(pos: Position, vel: Position, dt: float) -> Position:
    return pos + vel * dt  # internal: trust types
```

Shape syntax: `"3"` is (3,), `"N 3"` is (N, 3), `""` is scalar.

## Vectorization

Broadcasting over loops. Semantic reshaping.

```python
corrected = raw * gain[:, np.newaxis] - bias

from einops import rearrange, reduce
pooled = reduce(tensor, "b h w c -> b c", "mean")
```

## Imports

Import modules. Explicit provenance.

```python
from project import validation
result = validation.check_bounds(value, limits)
```

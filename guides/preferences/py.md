Python guidelines inspired by
    - Fluent Python (Ramalho)
    - Effective Python (Slatkin)
    - Robust Python (Viafore)
    - Architecture Patterns with Python (Percival/Gregory)

| Aspect      | Tool     | Config?                                        |
|-------------|----------|------------------------------------------------|
| Linter      | Ruff     | extend $GUIDES_DIR/configs/ruff.toml           |
| Formatter   | Ruff     | extend $GUIDES_DIR/configs/ruff.toml           |
| Typechecker | pyright  | `ln -s $GUIDES_DIR/configs/pyrightconfig.json` |
| Entrypoint  | justfile |                                                |

# Domain Types

Immutable, typed, structural equality. Make illegal states unrepresentable.

Options:
- `@attrs.frozen`: feature-rich, slots optimization
- `@dataclass(frozen=True)`: stdlib, zero dependencies
- `typing.NamedTuple`: simple cases, tuple interop
- `pydantic.BaseModel`: validation-heavy, serialization

Algebraic data types via union:

```python
type ParseError = MissingField | InvalidFormat | OutOfRange
```

# Result Types

Railway-oriented programming. Chain fallible operations; surface errors as values.

Options:
- `expression.Result` with `.bind()` / `.map()`
- `returns` library with `@pipeline`
- Explicit `match` on Result variants
- Exception-based with boundary conversion

One approach:

```python
def process(data: Input) -> Result[Output, ProcessError]:
    return (
        validate(data)
        .bind(transform)
        .bind(persist)
    )

match process(data):
    case Ok(output): handle_success(output)
    case Error(e): handle_failure(e)
```

# Protocols

Ports as protocols. Adapters as implementations.

```python
class Repository(Protocol):
    def find(self, id: EntityId) -> Result[Entity, NotFound]: ...
    def save(self, entity: Entity) -> Result[Entity, SaveError]: ...
```

Inject explicitly. Test via substitution.

# Shape Typing

For numerical code: semantic dimensions with shape annotations. Validate at boundaries only.

```python
Position = NewType("Position", Float[Array, "3"])
Trajectory = NewType("Trajectory", Float[Array, "time 3"])

@beartype  # boundary validation
def load_trajectory(path: Path) -> Trajectory:
    return np.load(path)

def integrate(pos: Position, vel: Position, dt: float) -> Position:
    return pos + vel * dt  # internal: trust types
```

Shape syntax: `"3"` is (3,), `"N 3"` is (N, 3), `""` is scalar.

# Generators

Streaming for memory efficiency. One item at a time.

```python
def read_records(path: Path) -> Iterator[Record]:
    with open(path) as f:
        for line in f:
            yield parse_record(line)

def process(records: Iterator[Record]) -> Iterator[Result]:
    for record in records:
        yield transform(record)
```

# Context Managers

Resource lifecycle via context protocol.

```python
@contextmanager
def timed(name: str):
    start = perf_counter()
    try:
        yield
    finally:
        log.info(f"{name}: {perf_counter() - start:.3f}s")
```

# Vectorization

Broadcasting over loops. Semantic reshaping.

```python
corrected = raw * gain[:, np.newaxis] - bias

from einops import rearrange, reduce
pooled = reduce(tensor, "b h w c -> b c", "mean")
```

# Pattern Matching

Exhaustive matching with assert_never.

```python
def handle(status: Status) -> str:
    match status:
        case Loading(): return "..."
        case Success(value=v): return f"Got: {v}"
        case Failure(error=e): return f"Error: {e}"
        case _ as unreachable: assert_never(unreachable)
```

# Namespace Pattern

Import modules, not contents. Explicit provenance.

```python
from project import validation

result = validation.check_bounds(value, limits)
```

# Async

Structured concurrency. Bounded parallelism.

```python
async def fetch_all(urls: list[str]) -> list[Response]:
    async with TaskGroup() as tg:
        tasks = [tg.create_task(fetch(url)) for url in urls]
    return [t.result() for t in tasks]

async def bounded(items: list[Item], limit: int = 10) -> list[Result]:
    sem = Semaphore(limit)
    async def process_one(item: Item) -> Result:
        async with sem:
            return await process(item)
    return await gather(*[process_one(i) for i in items])
```

# Testing

Descriptive names. Properties for invariants.

```python
def test_roundtrip_preserves_data():
    original = make_sample_data()
    recovered = decode(encode(original))
    assert original == recovered

@given(st.lists(st.integers()))
def test_sort_preserves_length(xs):
    assert len(sorted(xs)) == len(xs)
```

# Never

- Mutable default arguments
- Import-time side effects
- Bare `except:`
- `assert` for validation (use explicit checks)
- Shadowing builtins

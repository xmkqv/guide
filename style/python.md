# Python Style Guide

@code.md

## Tooling

- Ruff: global config at `/Users/m/guide/configs/ruff.toml`
- Pyright: symlink `/Users/m/guide/configs/pyrightconfig.json` to workspace

## Domain Types

Frozen attrs for all domain models. Immutable by default.

```python
import attrs
from numpy.typing import NDArray
import numpy as np

@attrs.frozen(slots=True)
class Spectrum:
    wavelengths: NDArray[np.float64]
    flux: NDArray[np.float64]
    uncertainty: NDArray[np.float64]

    def resample(self, new_grid: NDArray[np.float64]) -> "Spectrum":
        return attrs.evolve(self, wavelengths=new_grid, flux=interp(new_grid))
```

Union types for ADTs:

```python
type FitError = ConvergenceError | SingularMatrixError | BoundsError
```

## Shape Typing

Semantic dimensions with jaxtyping. Validate at boundaries only.

```python
from jaxtyping import Float, Array
from typing import NewType
from beartype import beartype

Position = NewType("Position", Float[Array, "3"])
Trajectory = NewType("Trajectory", Float[Array, "time 3"])

@beartype
def parse_trajectory(path: Path) -> Trajectory:
    return np.load(path)

def integrate(pos: Position, vel: Position, dt: float) -> Position:
    return pos + vel * dt
```

Shape syntax: `"3"` is (3,), `"N 3"` is (N, 3), `""` is scalar.

## Result Types

Railway-oriented error handling with expression library.

```python
from expression import Result, Ok, Error

def calibrate(
    raw: RawFrame, flat: FlatField, dark: DarkFrame
) -> Result[CalibratedFrame, CalibrationError]:
    return (
        subtract_dark(raw, dark)
        .bind(lambda f: divide_flat(f, flat))
        .bind(detect_cosmics)
        .bind(extract_spectrum)
    )

match calibrate(raw, flat, dark):
    case Ok(frame):
        save(frame)
    case Error(e):
        log.error(e)
```

Validation at boundaries:

```python
def fit_continuum(
    spectrum: Spectrum, model: ContinuumModel
) -> Result[FittedContinuum, FitError]:
    if spectrum.flux.size < model.min_points:
        return Error(FitError(stage="continuum", reason="insufficient points"))
    if np.any(spectrum.uncertainty <= 0):
        return Error(FitError(stage="continuum", reason="non-positive uncertainty"))
    return Ok(do_fit(spectrum, model))
```

## Protocols

Ports as protocols. Adapters as implementations. Inject explicitly.

```python
from typing import Protocol

class SequenceAligner(Protocol):
    def align(self, query: Sequence, ref: Genome) -> Result[Alignment, AlignError]: ...
    def score(self, alignment: Alignment) -> float: ...

class Repository(Protocol):
    def find(self, id: EntityId) -> Result[Entity, NotFound]: ...
    def save(self, entity: Entity) -> Result[Entity, SaveError]: ...
```

## Generators

Streaming pipelines. One item in memory at a time.

```python
def read_records(path: Path) -> Iterator[Record]:
    with open(path) as f:
        for line in f:
            yield parse_record(line)

def process_stream(records: Iterator[Record]) -> Iterator[Result]:
    for record in records:
        if record.is_valid:
            yield transform(record)

pipeline = process_stream(read_records(path))
results = list(islice(pipeline, 1000))
```

## Context Managers

Resource lifecycle via context protocol.

```python
from contextlib import contextmanager

@contextmanager
def timed(name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        log.info(f"{name}: {time.perf_counter() - start:.3f}s")

with timed("calibration"):
    result = calibrate(raw, flat, dark)
```

## Vectorization

Broadcasting over loops. Einops for semantic dimensions.

```python
corrected = raw_counts * gain[:, np.newaxis] - bias
power = np.abs(fft.fft(signal, axis=1)) ** 2

from einops import rearrange, reduce, repeat

transposed = rearrange(image, "h w c -> c h w")
pooled = reduce(tensor, "b h w c -> b c", "mean")
expanded = repeat(weights, "f -> b f", b=batch_size)
```

## Pattern Matching

Exhaustive matching with assert_never.

```python
from typing import assert_never

type Status = Loading | Success | Failure

def handle(status: Status) -> str:
    match status:
        case Loading():
            return "..."
        case Success(value=v):
            return f"Got: {v}"
        case Failure(error=e):
            return f"Error: {e}"
        case _ as unreachable:
            assert_never(unreachable)
```

## Namespace Pattern

Module as namespace. Import the module, not its contents.

```python
from atlas import photometry

mag = photometry.calibrate_flux(counts, zeropoint, airmass)
color = photometry.compute_index(mag_b, mag_v)
```

## Testing

Descriptive names. Property-based for invariants.

```python
def test_fft_preserves_energy():
    signal = make_gaussian_pulse(n_samples=1024, sigma=10.0)
    spectrum = compute_fft(signal)
    assert np.isclose(parseval_energy(signal), parseval_energy(spectrum), rtol=1e-10)

def test_redshift_is_invertible():
    rest = make_emission_line(center=6563.0)
    shifted = apply_redshift(rest, z=0.5)
    recovered = remove_redshift(shifted, z=0.5)
    assert np.allclose(rest.wavelengths, recovered.wavelengths)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False)))
def test_sort_preserves_length(xs):
    assert len(sorted(xs)) == len(xs)
```

## Async

Structured concurrency. Bounded parallelism.

```python
async def fetch_all(urls: list[str]) -> list[Response]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(url)) for url in urls]
    return [t.result() for t in tasks]

async def bounded_process(items: list[Item], limit: int = 10) -> list[Result]:
    sem = asyncio.Semaphore(limit)
    async def bounded(item: Item) -> Result:
        async with sem:
            return await process(item)
    return await asyncio.gather(*[bounded(i) for i in items])
```

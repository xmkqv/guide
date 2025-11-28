# Python Style Guide

@code.md

## Types

- Use `@attrs.frozen(slots=True)` for all domain types
- Immutable by default, no mutable state in core
- Type union for ADTs: `type FitError = ConvergenceError | SingularMatrixError`

```python
@attrs.frozen(slots=True)
class Spectrum:
    wavelengths: NDArray[np.float64]
    flux: NDArray[np.float64]
    uncertainty: NDArray[np.float64]
```

## Result Type

- Use `Result[T, E]` from expression library
- Chain with `.bind()` for railway-oriented processing
- Pattern match on `Ok`/`Error` at boundaries

```python
def reduce_observation(
    raw: RawFrame, flat: FlatField, dark: DarkFrame
) -> Result[CalibratedFrame, ReductionError]:
    def _apply_flat(f: RawFrame) -> Result[RawFrame, ReductionError]:
        return divide_flat(f, flat)

    def _extract(f: RawFrame) -> Result[CalibratedFrame, ReductionError]:
        return detect_cosmics(f).bind(lambda clean: extract_spectrum(clean))

    return subtract_dark(raw, dark).bind(_apply_flat).bind(_extract)
```

## Validation

```python
def fit_continuum(
    spectrum: Spectrum, model: ContinuumModel
) -> Result[FittedContinuum, FitError]:
    if spectrum.flux.size < model.min_points:
        return Error(FitError(stage="continuum", message="Insufficient data points"))
    if np.any(spectrum.uncertainty <= 0):
        return Error(FitError(stage="continuum", message="Non-positive uncertainties"))
    # ... fitting
    return Ok(fitted)
```

## Protocols

- Define ports as `Protocol` classes
- Implement as concrete adapters
- Inject dependencies explicitly

```python
class SequenceAligner(Protocol):
    def align(self, query: Sequence, reference: Genome) -> Result[Alignment, AlignError]: ...
    def score(self, alignment: Alignment) -> float: ...
```

## Namespace Pattern

NumPy/SciPy convention for module APIs:

```python
from atlas import photometry
mag = photometry.calibrate_flux(counts, zeropoint, airmass)
color = photometry.compute_index(mag_b, mag_v)
```

## Testing

```python
def test_fourier_transform_preserves_energy():
    signal = make_gaussian_pulse(n_samples=1024, sigma=10.0)
    spectrum = compute_fft(signal)
    assert np.isclose(parseval_energy(signal), parseval_energy(spectrum), rtol=1e-10)

def test_redshift_invertible():
    rest = make_emission_line(center=6563.0)
    shifted = apply_redshift(rest, z=0.5)
    recovered = remove_redshift(shifted, z=0.5)
    assert np.allclose(rest.wavelengths, recovered.wavelengths)
```

## Vectorization

- Prefer numpy broadcasting over Python loops
- Use axis-aware operations (`fft(data, axis=1)`, `mean(axis=(1, 3))`)
- Avoid `.tolist()` or element-wise iteration on arrays
- Use einops for explicit dimension labeling

```python
# numpy broadcasting
corrected = raw_counts * gain[:, np.newaxis] - bias
power_spectrum = np.abs(fft.fft(signal, axis=1)) ** 2

# einops for tensor operations
from einops import repeat, reduce, rearrange

k_space = repeat(k_vectors, 'k -> k atoms', atoms=n_atoms)
binned = reduce(photon_events, '(t bin) channels -> t channels', 'sum', bin=64)
covariance = rearrange(outer_products, 'batch i j -> i j batch').mean(axis=-1)
```

Prefer einops when:
- Building coordinate grids (k-space, real-space transforms)
- Dimension names clarify intent
- Same logic targets multiple backends (numpy/cupy/jax)

## Ruff

Global config at `/Users/m/guide/configs/ruff.toml`. Root pyproject.toml extends it. No local ruff configs in libs - they inherit from root.

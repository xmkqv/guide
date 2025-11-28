# Code Style Guide

All examples use pseudocode. Adapt naming conventions and syntax to your language idiom.

## Fundamentals

Nine principles governing correctness, maintainability, and reliability.

| Pillar | Fundamental | Governs | Principle | Constraint |
| ------ | ----------- | ------- | --------- | ---------- |
| Style | Purity | Effects, state, randomness | Pure core, effectful shell, explicit RNG | No hidden mutation, no implicit randomness |
| Style | Semantics | Meaning, naming | Domain language, typed values, named constants | No primitives for domain concepts, no magic |
| Style | Composition | Granularity | Single concern, streaming pipelines | No memory-heavy materialization |
| Design | Boundaries | Validation | Parse at entry, trust typed internals | No redundant validation, no naive trust |
| Design | Budgets | Memory, time | Budget tracking, deadline propagation | No unbounded allocation or execution |
| Design | Observability | Telemetry | Structured events, operation IDs, causality | No silent failures, no unobservable states |
| Design | Degradation | Partial success | Fallback strategies, best-effort results | No all-or-nothing outcomes |
| Checks | Totality | Errors, numerics | Result types, exhaustive matching, stability checks | No partial functions, no silent NaN |

## Architecture

Hexagonal (Ports and Adapters) with functional core. IO at edges only.

```text
Package/
  Subdomain/       -- vertical slice by domain concept
    Concept        -- module = cohesive unit of behavior
  Model            -- domain types at root
  Error            -- error types at root
  Value            -- type aliases, newtypes at root
  Const            -- package constants at root
  Ports/           -- interface definitions (input and output)
  Adapters/        -- interface implementations
  Infra/           -- cross-cutting (config, metrics, telemetry)
```

Dependency direction: Adapters → Ports → Core. Never reverse. Inject at composition root.

Rules:
- No cycles: dependency graph forms DAG
- No service locators: no global registries, no implicit resolution
- Stable dependencies: core imports only stable, pinned dependencies

Package by Feature, not Package by Layer. Structure reveals domain, not framework.

## Style

### Purity

Pure functions: same inputs produce same outputs, no observable side effects.

```text
function Compress.Range(samples, chirp) -> CompressedSamples:
    windowed = Apply.Window(samples)
    spectrum = Fft(windowed)
    return Correlate(spectrum, chirp)

function Process.Burst(path) -> Result[Product, Error]:
    samples = Read.File(path)               -- IO at boundary
    compressed = Compress.Range(samples, chirp)  -- pure
    return Write.Output(compressed)         -- IO at boundary
```

Randomness: inject RNG explicitly, never use global random state.

```text
function Add.Noise(signal, snr, rng: RNG) -> Signal:
    noise = rng.Normal(0, 1, signal.shape)
    return signal + noise * (Signal.Power(signal) / snr)
```

Domain types: frozen/immutable by default. Mutation only in adapters.

Principles:
- Effect visibility: return type reveals effect (Result, Option, Generator)
- No hidden IO: logging, metrics, telemetry injected, not imported
- Copy-on-modify: return new instances, do not mutate arguments

### Semantics

Names carry meaning. Types encode domain concepts.

Naming patterns (`.` = word boundary, adapt to language idiom):

| Element | Pattern | Example |
| ------- | ------- | ------- |
| Subdomain | `DomainNoun/` | `Sar/`, `Geocode/`, `Orbit/` |
| Module | `Concept` | `Focus`, `Interpolate`, `Backward` |
| Function | `Verb[.Noun]` | `Fft`, `Compress.Range`, `Estimate.Doppler` |
| Type | `ContextNoun` | `FlightBurst`, `OrbitState` |
| Interface | `ResourceRole` | `StorageWriter`, `ConfigReader` |
| Error | `ContextError` | `FocusError`, `ParseError` |
| Constant | `UPPER.CASE.PATH` | `SPEED.OF.LIGHT`, `MAX.ITERATIONS` |
| Private | `_prefix` | `_internal`, `_helper` |
| Test | prose description | `test "FFT preserves energy"` |

Concept: a cohesive unit of domain behavior (noun or verb representing primary operation).

Typed values over primitives:

```text
-- Primitive obsession (avoid)
function Compute.Doppler(wavelength: Float, velocity: Float) -> Float

-- Typed domain values (prefer)
function Compute.Doppler(wavelength: Wavelength, velocity: Velocity) -> Frequency
```

Make illegal states unrepresentable: use types to prevent invalid combinations.

### Composition

Small, composable units. Data flows through transformations.

```text
result = (
    raw_samples
    |> Apply.Window
    |> Fft
    |> Correlate(chirp)
    |> Ifft
)

function Process.Swath(bursts: Stream[Burst]) -> Stream[Product]:
    for burst in bursts:
        yield Process.Burst(burst)  -- one burst in memory at a time
```

Function size heuristic: if it needs comments to section it, split it.

## Design

### Boundaries

Validate at entry points. Trust typed internals.

Validation boundaries:
- External: untrusted (user input, sensor data, external APIs)
- Module: semi-trusted (type contracts enforced)
- Function interior: trusted (invariants hold by construction)

```text
function Parse.Orbit.Data(raw: Bytes) -> Result[OrbitState, ParseError]:
    if not Valid.Epoch(raw.epoch):
        return Error(ParseError("invalid epoch"))
    return Ok(OrbitState(...))

function Propagate.Orbit(state: OrbitState, dt: Duration) -> OrbitState:
    -- state already validated; only check critical numerical invariants
    return Integrate(state, dt)
```

Parse, do not validate: transform untyped input into typed domain values at boundary.

Prefer allowlist over denylist: define what IS valid, reject everything else.

### Budgets

Explicit lifecycle. Bounded allocation. Deadline awareness.

```text
type FftWorkspace:
    buffer: Array  -- preallocated, reused

function Compress.Range(samples, workspace: FftWorkspace) -> Compressed:
    Fft.Inplace(samples, workspace.buffer)
    return Compressed(workspace.buffer.copy())

function Process.Swath(bursts, deadline: Timestamp) -> Result[Swath, Error]:
    results = []
    for burst in bursts:
        remaining = deadline - Now()
        if remaining <= 0:
            return Ok(PartialSwath(results, reason="deadline"))
        results.append(Process.Burst(burst, timeout=remaining))
    return Ok(Swath(results))
```

Progress signals: long operations emit periodic heartbeats for observability.

Principles:
- Explicit ownership: clear which component owns which resource
- Acquire contextually: use context managers / RAII patterns
- Reserve headroom: leave margin for transient allocation

### Observability

Structured telemetry. Causal tracing. No silent failures.

```text
type ProcessingStarted:
    operation_id: UUID
    burst_id: BurstID
    timestamp: Timestamp

function Process.Burst(burst, ctx: TraceContext) -> Result[Product, Error]:
    Emit(ProcessingStarted(ctx.operation_id, burst.id, Now()))
    result = Do.Processing(burst)
    Emit(ProcessingCompleted(ctx.operation_id, result.status, Elapsed()))
    return result
```

All errors logged with context sufficient to diagnose from telemetry alone.

- Context propagation: pass trace context through call stack
- No catch-and-ignore: every exception handled or re-raised with context

### Degradation

Graceful fallbacks. Partial success over total failure.

```text
type ProcessingResult:
    product: Product
    quality: QualityLevel  -- Full, Degraded, Minimal
    warnings: List[Warning]
    skipped: List[SkippedItem]

function Geolocate(point, dem) -> Result[Location, Error]:
    result = Geolocate.With.Dem(point, dem)
    if result.is_error() and Is.Dem.Unavailable(result.error):
        return Geolocate.Ellipsoid(point)  -- fallback to simpler model
    return result
```

## Checks

### Totality

Handle all inputs. No partial functions in core.

Result types for domain errors:

```text
function Parse.Config(text) -> Result[Config, ConfigError]:
    if Missing.Required.Field(text):
        return Error(ConfigError("missing field"))
    return Ok(Config(...))
```

Railway-oriented chaining:

```text
function Process(input) -> Result[Output, Error]:
    return (
        Validate(input)
        .bind(Transform)
        .bind(Enrich)
        .bind(Format)
    )

match Process(input):
    case Ok(output): Write.Output(output)
    case Error(e): Log.Error(e)
```

Exhaustive matching: handle all cases explicitly, avoid catch-all patterns.

Error context with remediation:

```text
type ProcessingError:
    stage: String          -- "Range.Compression"
    input_id: String       -- "burst_042"
    reason: String         -- "insufficient samples"
    remediation: String?   -- "increase burst duration"
```

Numerical stability:

```text
function Compute.Arcsin(x) -> Result[Float, MathError]:
    if Abs(x) > 1.0:
        return Error(MathError("arcsin domain violation"))
    return Ok(Arcsin(x))

function Compress.Signal(signal) -> Result[Compressed, Error]:
    input_energy = Sum(Abs(signal) ** 2)
    compressed = Do.Compression(signal)
    output_energy = Sum(Abs(compressed) ** 2)
    if not (0.9 <= output_energy / input_energy <= 1.1):
        return Error(StabilityError("energy not conserved"))
    return Ok(compressed)
```

Distinction:
- Domain error: expected, recoverable, part of business logic
- Programming error: unexpected, indicates bug, should crash

## Constants

Named values at appropriate scope. No magic numbers.

Hierarchy:
- Library: `Lib/Const` - physical, mathematical invariants
- Package: `Package/Const` - domain-specific to that package
- Module: internal constant at top - local to module only

```text
SPEED.OF.LIGHT = 299792458           -- m/s, library
EARTH.RADIUS.EQUATORIAL = 6378137    -- m, library

RANGE.WINDOW.OVERSAMPLE = 1.2        -- package
AZIMUTH.AMBIGUITY.MARGIN = 0.1       -- package

_MAX.ITERATIONS = 100                -- module internal
_CONVERGENCE.TOLERANCE = 1e-9        -- module internal
```

Semantic names over values. Document derivation in comments.

## Testing

Verification through types, tests, lints, and property checks.

Unit tests: pure functions, deterministic, fast.

```text
test "range compression preserves signal energy":
    signal = Make.Chirp(bandwidth=50e6, duration=10e-6)
    compressed = Compress.Range(signal, chirp_replica)
    assert Energy.Ratio(compressed, signal) within (0.95, 1.05)

test "orbit interpolation is smooth":
    states = [Propagate(initial, t) for t in Range(0, 100, 10)]
    velocities = Diff(Positions(states)) / 10
    assert Max(Diff(velocities)) < SMOOTHNESS.THRESHOLD
```

Property tests: invariants that hold for all inputs.

```text
property "compression then decompression recovers signal":
    for all signal in Arbitrary.Signals():
        compressed = Compress(signal)
        recovered = Decompress(compressed)
        assert Signals.Equal(signal, recovered, tolerance=1e-6)
```

Integration tests:
- Pipeline flows with fixtures
- Boundary crossing with real systems
- Failure modes: verify degradation and recovery paths

Property test categories:
- Round-trip: encode/decode, transform/inverse
- Metamorphic: relationships between related inputs

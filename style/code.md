# Code Style Guide

Principles for reasoning about software. Adapt to context. Apply with judgment.

## Preamble

This guide provides heuristics for architectural decision-making, not templates for mechanical application. Every principle admits exceptions when problem structure demands. Rigid adherence to patterns causes as much damage as their absence.

Skilled practitioners recognize the difference between a pattern that fits and a pattern imposed. Structure should emerge from a problem's natural joints—not from conformance to an external template.

Diagnostic: If satisfying architectural constraints requires more code than solving the actual problem, reconsider the architecture.

## Properties

Three properties characterize well-structured code. They exist in tension; maximizing one may compromise another. Navigate tradeoffs deliberately.

| Property | Manifestation | Diagnostic Question |
| -------- | ------------- | ------------------- |
| Referential Transparency | Expressions substitutable for their values | Can this be inlined or extracted without behavioral change? |
| Information Locality | Related concerns colocated; unrelated concerns separated | Does understanding require traversing distant modules? |
| Representation Fidelity | Types encode domain invariants | Can invalid states be constructed? |

## Complexity

Complexity is the primary adversary. It accumulates through accretion and metastasizes through coupling.

### Manifestations

- Change amplification: modifications require coordinated edits across locations
- Cognitive load: understanding demands excessive held context
- Hidden coupling: modifications trigger failures in apparently unrelated components

### Mitigation

Two complementary strategies:

Elimination: Reduce intrinsic complexity. Simplify. Remove unnecessary abstraction. Consolidate scattered logic. Delete code that no longer earns its keep.

Encapsulation: Hide irreducible complexity behind stable interfaces. The interface should be simpler than the implementation it conceals.

```text
-- Shallow (complexity exposed through interface)
function Process(data, mode, flags, opts, overrides, ctx) -> Result

-- Deep (complexity absorbed by implementation)
function Process(request: Request) -> Result
```

Module depth is the ratio of functionality provided to interface complexity. Prefer depth. Configuration parameters and excessive options push complexity onto callers—consider absorbing reasonable defaults.

## Architecture

No single architectural pattern suits all problems. Patterns are tools with applicability conditions, not universal templates.

### Pattern Applicability

Functional Core / Imperative Shell
- Effective when business logic separates cleanly from effects
- Core computes decisions; shell executes them
- Less effective when logic and effects are inherently interleaved

Ports and Adapters
- Appropriate when external dependencies vary across environments or require substitution for testing
- Overhead unjustified for stable, single-implementation dependencies

Vertical Slices
- Suitable when features deploy independently with minimal shared infrastructure
- Introduces duplication when features share significant logic

Layered
- Acceptable for straightforward request-response flows with minimal domain complexity
- Degrades when domain logic doesn't align with layer boundaries

### Anti-Patterns

Structural Cargo Culting
- Imposing hexagonal architecture on a utility script
- Decomposing a cohesive 50-line module into five files to satisfy a template
- Creating Ports and Adapters when a single implementation exists and will never change

Premature Abstraction
- Extracting a "reusable" component from a single use site
- Generalizing before the second concrete case exists
- Building extension points for requirements that may never materialize

Indirection Without Purpose
- Every layer, interface, and abstraction has a cost
- Indirection is justified only when it provides concrete value: substitutability, testability, or isolation of change
- Indirection for its own sake is complexity

## Style

### Purity

Pure functions—same inputs produce same outputs, no observable effects—compose without coordination and test without mocking.

```text
function Compress.Range(samples, chirp) -> CompressedSamples:
    windowed = Apply.Window(samples)
    spectrum = Fft(windowed)
    return Correlate(spectrum, chirp)
```

When to apply: Core domain logic, transformations, computations, anything that benefits from referential transparency.

When to relax:
- Adapter code at system edges
- Infrastructure concerns (logging, metrics, configuration)
- Performance-critical paths where profiling demonstrates mutation provides measurable benefit
- Interop with libraries that assume mutable interfaces

Randomness and time are implicit dependencies. Make them explicit when determinism matters for testing or reproducibility.

Local mutation invisible to callers preserves referential transparency. A function that internally uses mutable buffers but exposes a pure interface remains pure.

### Semantics

Names compress meaning. Types prevent misuse.

```text
-- Low semantic density
function Process(id: String, data: Dict, flag: Bool) -> Dict

-- High semantic density
function Settle.Trade(id: TradeId, terms: SettlementTerms) -> Settlement
```

Type distinctions: Use distinct types to prevent confusion where confusion causes harm. `AccountId` vs `UserId` prevents transposition errors that `String` vs `String` permits. Apply proportionally—not every string requires a newtype.

Naming patterns (adapt separator to language idiom):

| Element | Pattern | Rationale |
| ------- | ------- | --------- |
| Function | `Verb.Noun` | Action and target explicit |
| Type | `ContextNoun` | Domain concept with scope |
| Constant | `SEMANTIC_NAME` | Meaning over value |

When naming is difficult, the abstraction is likely wrong.

### Composition

Granularity is a judgment call. Neither "many tiny functions" nor "few large functions" is universally correct.

Heuristics for decomposition:
- Extract when a block has a name that clarifies intent
- Extract when the same logic appears in multiple locations (after the second occurrence)
- Extract when testing a subset in isolation provides value

Heuristics against decomposition:
- Logic is only used once and inline reading is clearer
- Extraction requires passing many parameters or introduces awkward signatures
- The "abstraction" merely moves code without adding understanding

Streaming and lazy evaluation reduce memory pressure when processing sequences. Apply when data volume warrants; unnecessary for small collections.

## Design

### Boundaries

Boundaries occur where trust transitions. Parse at boundaries; trust typed internals thereafter.

```text
Untrusted → [Parse] → Domain Values → [Logic] → [Effect] → External
```

Boundary locations:
- System edges: user input, network, filesystem, external APIs
- Subsystem interfaces: between teams, services, bounded contexts

Not boundaries: Internal function calls between trusted components operating on validated domain types within the same trust domain. Redundant validation here is noise. However, treat team or security boundaries as trust transitions even within a single process.

Parse, don't validate: transform unstructured input into typed domain values. The type system then enforces invariants—re-checking is unnecessary and obscures where trust is actually established.

Smart constructors: Hide type constructors. Expose only parsing functions.

```text
module Email:
    type Email (private)
    function parse(raw: String) -> Result[Email, ParseError]
```

All instances valid by construction. No runtime validation needed thereafter.

### Resources

Explicit lifecycle management when resources are scarce or expensive.

When to apply: Database connections, file handles, memory buffers in tight loops, operations with hard deadlines.

When unnecessary: Short-lived computations with abundant resources, garbage-collected environments where resource pressure is absent.

```text
function Process.Batch(items, deadline: Timestamp) -> Result[Batch, Error]:
    results = []
    for item in items:
        if Now() > deadline:
            return Ok(PartialBatch(results, reason="deadline"))
        results.append(Process(item))
    return Ok(Batch(results))
```

### Observability

Structured telemetry enables diagnosis. Emit events with operation identifiers; trace causality across calls.

When essential: Production services, distributed systems, long-running operations, anything where post-hoc diagnosis is required.

When optional: Local scripts, exploratory code, tests (which have their own assertions).

```text
function Execute(op: Operation, trace: TraceContext) -> Result:
    Emit(Started(trace.id, op.id, Now()))
    result = Perform(op)
    Emit(Completed(trace.id, result.status, Elapsed()))
    return result
```

Errors should carry sufficient context for diagnosis without access to the original environment.

### Resilience

Graceful degradation when full success is impossible.

```text
type Result:
    output: Output
    quality: Full | Degraded | Partial
    warnings: List[Warning]
```

When to apply: User-facing services, batch processing where partial results have value, systems where availability trumps consistency.

When inappropriate: Safety-critical systems where partial results are dangerous, transactions requiring atomicity.

### Concurrency

Prefer message-passing over shared mutable state. Immutable data crosses thread boundaries without synchronization.

When shared state is unavoidable:
- Encapsulate synchronization within a module
- Expose a pure interface to callers
- Prefer structured concurrency (task groups, scopes) over unstructured spawning

Concurrency correctness follows from the same principles: information hiding, explicit dependencies, total functions.

## Checks

### Totality

Handle all representable inputs. Partial functions—those undefined for some inputs—propagate failure modes silently.

Refined input types eliminate partiality at the source:

```text
-- Partial
function first(xs: List[A]) -> A

-- Total via refined input
function first(xs: NonEmpty[A]) -> A

-- Total via refined output
function first(xs: List[A]) -> Option[A]
```

Prefer refined inputs when callers can guarantee the constraint. Prefer refined outputs when the constraint is situational.

Result types model expected failure as values:

```text
function Parse.Config(text) -> Result[Config, ConfigError]:
    if Missing.Field(text, "required"):
        return Error(ConfigError.MissingField("required"))
    return Ok(Config(...))
```

When to use Result: Failure is a normal outcome. Callers must handle the failure case. The error carries domain-relevant information.

When to let exceptions propagate: Failure indicates a bug. Recovery is impossible or meaningless. The call site cannot usefully handle the error.

Exhaustive pattern matching ensures all cases are handled. Avoid catch-all branches that silently swallow unexpected variants.

Use assert_never (or equivalent) to make inexhaustive matches a type error:

```text
match status:
    case Pending(): handle_pending()
    case Active(): handle_active()
    case _: assert_never(status)  -- type error if cases missing
```

### Effects

Effect types distinguish computational contexts.

| Type | Meaning | Use When |
| ---- | ------- | -------- |
| Result[A, E] | May fail with E | Parsing, validation, fallible operations |
| Option[A] | May be absent | Lookup, search, nullable replacement |
| List[A] | Multiple results | Non-determinism, queries |
| IO[A] | External effects | Files, network, time, randomness |

Result and Option are values (pure). IO describes effects (impure when executed).

### Testing

Testing strategy follows from code structure, not vice versa.

| Component | Approach | Rationale |
| --------- | -------- | --------- |
| Pure functions | Unit tests, property tests | Deterministic, fast, high coverage achievable |
| Effectful code | Integration tests | Verify coordination and external interaction |
| Boundaries | Contract tests | Validate parsing, serialization, protocol compliance |

Property tests are valuable when algebraic properties exist: round-trip (encode/decode), associativity, commutativity, invariant preservation. Not every function has meaningful properties—example-based tests suffice when properties are absent or contrived.

```text
property "serialize then parse is identity":
    for all x in Valid.Inputs():
        assert Parse(Serialize(x)) == x
```

## Heuristics

When principles conflict, these defaults often apply. Context overrides.

| Tension | Default | Override When |
| ------- | ------- | ------------- |
| Abstraction vs Concreteness | Delay abstraction until second use | Pattern is well-established and stable |
| DRY vs Locality | Tolerate duplication over wrong abstraction | Duplication causes actual maintenance burden |
| Depth vs Breadth | Deeper modules with simpler interfaces | Interface complexity is inherent to domain |
| Purity vs Pragmatism | Pure where feasible | Performance or interop requires mutation |
| Explicit vs Implicit | Explicit dependencies and effects | Boilerplate overwhelms signal |

Universal defaults: Measure before optimizing. Delete before commenting. Simplify before generalizing.

## Application

This guide informs decision-making. It does not substitute for it.

Before applying any pattern:
1. Identify the problem's actual constraints and forces
2. Evaluate whether the pattern addresses those forces
3. Consider the pattern's cost against its benefit in this context
4. Select the simplest approach that adequately addresses the problem

The best code often uses no named pattern at all. It simply solves the problem with clarity.

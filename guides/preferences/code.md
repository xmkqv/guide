# Code

Principles for reasoning about software. Adapt to context. Apply with judgment.

## Foundations

Clean Code (Martin). Pragmatic Programmer (Hunt/Thomas). A Philosophy of Software Design (Ousterhout). Domain-Driven Design (Evans). Functional Core, Imperative Shell (Bernhardt).

- Referential transparency: pure expressions that can be substituted for their values
- Algebraic structure: operations that compose via well-defined laws (associativity, identity)
- Effect isolation: separating "what to compute" from "how to execute"
- Point-free style: data flows through pipelines without intermediate bindings

**Robust, Typed, Professional, Production-ready, Modular, Clean Code (by Robert C. Martin), Practical Functional Programming, SOLID, DRY, KISS, YAGNI**

- Naming
  - Functions: `{verb}{sep}{noun}` (e.g., `get_user`, `set_value`)

## Orientation

Complexity is the adversary. Structure emerges from problem shape, not template conformance.

Diagnostic: If satisfying architectural constraints requires more code than solving the problem, reconsider the architecture.

## Properties

Three properties characterize well-structured code. They exist in tension.

| Property                 | Meaning                                    | Diagnostic                                               |
|--------------------------|--------------------------------------------|----------------------------------------------------------|
| Referential transparency | Expressions substitutable for their values | Can this be inlined/extracted without behavioral change? |
| Information locality     | Related concerns colocated                 | Does understanding require traversing distant modules?   |
| Representation fidelity  | Types encode domain invariants             | Can invalid states be constructed?                       |

## Complexity

Manifestations:
- Change amplification: modifications require coordinated edits across locations
- Cognitive load: understanding demands excessive held context
- Hidden coupling: changes trigger failures in apparently unrelated components

Mitigation:
- Elimination: simplify, remove unnecessary abstraction, delete code that doesn't earn its keep
- Encapsulation: hide irreducible complexity behind stable interfaces simpler than what they conceal

Module depth (Ousterhout): ratio of functionality to interface complexity. Prefer depth.

## Purity

Same inputs produce same outputs, no observable effects. Compose without coordination, test without mocking.

Default to pure. Relax at system edges, in infrastructure concerns, and where profiling demonstrates necessity.

Local mutation invisible to callers preserves referential transparency.

## Architecture

No single pattern suits all problems. Patterns have applicability conditions.

| Pattern                            | When Effective                                 | When Not                                 |
|------------------------------------|------------------------------------------------|------------------------------------------|
| Functional core / Imperative shell | Logic separates cleanly from effects           | Logic and effects inherently interleaved |
| Ports and adapters                 | Dependencies vary or require test substitution | Single stable implementation             |
| Vertical slices                    | Features deploy independently                  | Features share significant logic         |
| Layered                            | Straightforward request-response               | Domain doesn't align with layers         |

Anti-patterns:
- Structural cargo culting: imposing architecture on problems that don't need it
- Premature abstraction: generalizing before the second concrete case
- Indirection without purpose: layers that provide no concrete value

## Boundaries

Parse, don't validate (King). Transform unstructured input into typed domain values at trust transitions.

Trust transitions occur at:
- System edges: user input, network, filesystem, external APIs
- Subsystem interfaces: between teams, services, bounded contexts

Not trust transitions: internal calls between components operating on validated types in the same trust domain.

Smart constructors: hide type constructors, expose only parsing functions. All instances valid by construction.

## Semantics

Names compress meaning. Types prevent misuse.

| Element  | Pattern       | Rationale                  |
|----------|---------------|----------------------------|
| Function | verb_noun     | Action and target explicit |
| Type     | ContextNoun   | Domain concept with scope  |
| Constant | SEMANTIC_NAME | Meaning over value         |

When naming is difficult, the abstraction is likely wrong.

Distinct types prevent confusion where confusion causes harm. Apply proportionally.

## Totality

Handle all representable inputs. Partial functions propagate failure modes silently.

Options:
- Refined input types: `first(xs: NonEmpty[A]) -> A`
- Refined output types: `first(xs: List[A]) -> Option[A]`
- Result types for expected failures: `parse(s) -> Result[T, ParseError]`

Exhaustive pattern matching. Use assert_never for inexhaustive matches.

## Composition

Decomposition heuristics:
- Extract when a name clarifies intent
- Extract when logic appears in multiple locations (after second occurrence)
- Extract when testing a subset provides value

Against decomposition:
- Logic used once, inline reading clearer
- Extraction requires passing many parameters
- The "abstraction" merely moves code without adding understanding

## Observability

Structured telemetry for production systems. Emit events with operation identifiers; trace causality.

Errors carry sufficient context for diagnosis without access to the original environment.

## Testing

| Component      | Approach                   |
|----------------|----------------------------|
| Pure functions | Unit tests, property tests |
| Effectful code | Integration tests          |
| Boundaries     | Contract tests             |

Property tests when algebraic properties exist: round-trip, associativity, invariant preservation.

## Tensions

| Tension                     | Default                            | Override When                         |
|-----------------------------|------------------------------------|---------------------------------------|
| Abstraction vs Concreteness | Delay abstraction until second use | Pattern is well-established           |
| DRY vs Locality             | Tolerate duplication               | Duplication causes maintenance burden |
| Depth vs Breadth            | Deeper modules                     | Interface complexity is inherent      |
| Purity vs Pragmatism        | Pure where feasible                | Profiling shows necessity             |
| Explicit vs Implicit        | Explicit dependencies              | Boilerplate overwhelms signal         |

## Defaults

Measure before optimizing. Delete before commenting. Simplify before generalizing.

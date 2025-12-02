# Style Guide Authorship for Agent Systems

Principles for writing documentation that activates rather than prescribes.

## Premise

AI agents are pattern completion systems, not rule execution engines. Style guides should activate learned patterns through strategic reference, not enumerate exhaustive rules. The model's training corpus is an asset; effective documentation leverages it.

Diagnostic: If your guide re-derives what canonical works already specify, you are wasting tokens and risking divergence.

## The Seven Principles

### 1. Reference Invocation

Cite canonical works to activate rich conceptual frameworks.

The phrase "Clean Code (Martin)" activates:
- Single Responsibility Principle
- Function length heuristics
- Naming conventions
- Comment philosophy
- Dozens of associated practices

Re-specifying these is redundant. The model knows the source material. Citation compresses.

```text
-- Inefficient (re-derives known material)
Functions should do one thing. They should do it well.
They should do it only. Names should reveal intent.
Comments are failures to express in code...
[500 more words]

-- Efficient (activates via reference)
Foundations: Clean Code (Martin), Pragmatic Programmer (Hunt/Thomas)
```

Caveat: Reference invocation assumes training coverage. For obscure or recent works, explicit specification remains necessary.

### 2. Principle Over Tool

State the operative principle; offer tools as contextual options.

Principles are stable. Tools change. A guide that mandates `attrs.frozen` becomes obsolete when the ecosystem shifts. A guide that specifies "immutable domain types" remains valid across tool generations.

```text
-- Tool prescription (brittle)
Use attrs.frozen(slots=True) for all domain models.

-- Principle with options (adaptive)
Domain types: immutable, typed, structural equality.

Options by context:
- attrs.frozen: feature-rich, slots optimization
- dataclasses(frozen=True): stdlib, zero dependencies
- pydantic.BaseModel(frozen=True): validation-heavy, serialization
- typing.NamedTuple: simple cases, tuple protocol interop

Selection: match existing codebase; minimize dependencies; prefer explicit.
```

The agent recognizes which option fits the encountered context. Prescription removes that judgment.

### 3. Exemplar Optionality

Mark examples as illustrative, not prescriptive.

Code examples carry false authority. Their syntactic specificity implies mandate. Counter this with explicit optionality markers.

```text
-- Unmarked example (reads as mandate)
def process(data: Input) -> Result[Output, Error]:
    return validate(data).bind(transform).bind(persist)

-- Marked example (reads as option)
Railway pattern (one approach):

def process(data: Input) -> Result[Output, Error]:
    return validate(data).bind(transform).bind(persist)

Alternatives: match statements on Result; exception boundaries;
async pipelines with error channels.
```

When the agent encounters a codebase using a different pattern, unmarked examples create conflict. Marked examples create informed choice.

### 4. Canonical Terminology

Use established terms as semantic anchors.

Terms like "referential transparency," "parse don't validate," "ports and adapters" are compressed knowledge. They:
- Have precise definitions in literature
- Activate associated implications
- Enable external lookup
- Signal discourse community

```text
-- Vague (requires re-derivation each use)
Make sure functions always return the same output for the same input
and don't change anything outside themselves.

-- Precise (activates known concept)
Referential transparency: expressions substitutable for their values.
```

Cite sources for non-obvious terms: "Parse, don't validate (King)" anchors to the original treatment, allowing the model to draw on that full context.

### 5. Semantic Generalization Trust

State principles; trust the agent to recognize applicability.

Agents match patterns through semantic similarity, not syntactic lookup. Exhaustive enumeration is unnecessary and counterproductive—it implies the unlisted cases don't apply.

```text
-- Exhaustive enumeration (implies closed set)
Use pure functions for:
- Data transformation
- Business logic
- Validation
- Serialization
- Configuration parsing
- Report generation
- ...

-- Principle statement (implies open applicability)
Default to pure functions. Relax at system edges and
where profiling demonstrates necessity.
```

The agent recognizes "report generation" as semantically similar to "pure function territory" without explicit listing.

### 6. Specificity Calibration

Match specificity level to concern type.

| Concern Type | Appropriate Specificity | Rationale |
| ------------ | ----------------------- | --------- |
| Hardware constraints | High | Physics admits no interpretation |
| Security requirements | High | Errors are exploits |
| Architecture patterns | Medium | Principles with exemplars |
| Tool choices | Low | Principle + options |
| Aesthetic preferences | Medium | Examples establish tone |

A guide uniformly high in specificity over-constrains flexible concerns. A guide uniformly low in specificity under-constrains critical concerns.

```text
-- Appropriate calibration

## Memory Format (HIGH - hardware constraint)
Tensor cores require NHWC. Convert model and input:
  model.to(memory_format=channels_last)
  input.to(memory_format=channels_last)
No exceptions on Ampere+.

## Error Handling (MEDIUM - pattern with options)
Surface errors as values at boundaries.
Options: Result types, Option types, validated newtypes.
Match existing codebase conventions.

## HTTP Client (LOW - tool choice)
Needs: async, connection pooling, timeout configuration.
Options: httpx, aiohttp, requests (sync contexts).
```

### 7. Mode Activation

Establish cognitive mode; don't prescribe every decision.

The guide's primary function is putting the agent into the right "mode" of thinking. Decisions then emerge from that mode naturally.

```text
-- Decision prescription (micromanages)
Functions must be under 20 lines.
Each function must have exactly one responsibility.
Variable names must be camelCase.
All public functions must have docstrings.
...

-- Mode activation (establishes orientation)
Orientation: Clean Code (Martin). Practical functional programming.
Clarity over cleverness. Explicit over implicit. Simple over easy.
```

Mode activation leverages the model's training. The phrase "Clean Code (Martin)" activates function length intuitions, naming conventions, and dozens of associated practices without enumeration.

## Document Structure

Effective agent guides follow this hierarchy:

```text
1. MODE ACTIVATION
   - Reference invocations (canonical works)
   - Core principles (semantic anchors)
   - Philosophical stance (what matters)

2. PRINCIPLES
   - Canonical terminology with citations
   - Applicability heuristics
   - Tension acknowledgment (when principles conflict)

3. PATTERNS (by context)
   - Context description
   - Principle instantiation options
   - Selection heuristics
   - Marked exemplars

4. CONSTRAINTS (non-negotiable)
   - Hard requirements
   - Security boundaries
   - Hardware/platform limits
   - High specificity appropriate
```

Mode activation primes; principles guide; patterns illustrate; constraints bound.

## Anti-Patterns

### The Enumeration Trap

Listing every case implies unlisted cases don't apply. Prefer principle statements that generalize.

### The False Precision Trap

Specific syntax in examples becomes interpreted as the only valid syntax. Mark optionality explicitly.

### The Re-Derivation Trap

Re-specifying what canonical works already cover wastes tokens, risks divergence, and loses the richness of the original treatment. Cite instead.

### The Uniform Specificity Trap

Applying the same specificity level across all concerns. Calibrate to concern type.

### The Rule Book Trap

Treating the guide as exhaustive rules rather than activation patterns. Agents don't execute rules; they complete patterns.

## Compression Techniques

### Canonical References

Single phrases that activate entire frameworks:
- "Clean Code (Martin)"
- "Parse, don't validate (King)"
- "Functional core, imperative shell"
- "Make illegal states unrepresentable"
- "Railway-oriented programming"

### Tension Tables

Acknowledge that principles conflict; provide navigation heuristics:

| Tension | Default | Override When |
| ------- | ------- | ------------- |
| DRY vs Locality | Tolerate duplication | Duplication causes maintenance burden |
| Purity vs Pragmatism | Pure where feasible | Profiling shows necessity |
| Abstraction vs Concreteness | Delay abstraction | Pattern is well-established |

### Negative Space

Sometimes what NOT to do is more activating than what to do:

```text
Never:
- Catch-all exception handlers that swallow context
- Mutable default arguments
- Import-time side effects

These activate avoidance patterns more reliably than positive enumeration.
```

## Validation

A well-constructed agent guide should:

1. Fit in working context without truncation
2. Activate appropriate patterns on first read
3. Not require re-reading for each decision
4. Remain valid as tools evolve
5. Complement rather than contradict canonical sources

Test: Give the guide to the agent, then present novel scenarios. Does the agent make decisions consistent with the guide's intent without explicit coverage of those scenarios? If yes, the guide activates effectively.

## Summary

Write guides that activate, not prescribe. Leverage training through reference. State principles, not tools. Mark examples as options. Trust semantic generalization. Calibrate specificity. Prime mode, then let pattern completion do its work.

The goal is not comprehensive coverage. The goal is effective activation.

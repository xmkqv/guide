
Dynamic declarative reifier.

Self-healing: The system frames the build, test, and incremental evolution of qualia.
Anti-fragile: Divergence → signals → improvements.

```text
∆Design → ∆Qualia → ∆Signal
   ↑                   ↓
   └────── ∇Loss ──────┘
```

- Design: Declarative specification.
- Qualia: Expressed constructs.
- Signal: Behavior insight.

```bash
guide sync # sync spec.test, log undeclared tests
guide check # lint, format, typecheck
```

```yaml
# guide.yaml

design: {spec}
```

# Design

Specs decompose into irreducible, orthogonal, necessary, and consequential elements.

```sql
type test (
    ref text, -- qualified path to single programmatic test
    result? jsonb
)

type limn (
    type text, -- { ...plot-types, architecture, ... }
    path text,
    desc text
)

spec (
    key text pk generated always as random_hex(len=3),
    defn text, -- declarative, specific, and unambiguous
    test? test,
    limn? limn,
    specs? list[spec],
)
```

Undeclared tests should be pruned.
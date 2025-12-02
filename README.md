
Declarative anti-fragile self-healing reifier.

- Self-healing: Deltas behave as stochastic gradient updates.
- Anti-fragile: Flaws → signals → insights

```bash
guide sync # create if not exists, tests → specs, specs → limns
guide check # lint, format, typecheck
```

```yaml
# guide.yaml

rgxlog?: {list[text]} # instrumented logger target function patterns
design: {list[spec]}
datasets?: {list[loader]}
```

# Design

Specs decompose mission into irreducible, orthogonal, necessary, and consequential elements.

```sql
type test (
    path text, -- qualified path to single programmatic test
    result? jsonb
)

type limn (
    type text, -- { ...plot-types, architecture }
    path text,
    desc text
)

spec(
    key text pk generated always as random_hex(len=3),
    defn text,
    test? test,
    limn? limn,
    specs list[spec],
)
```

# Datasets

Optional dataset manifest.

```sql
loader(
    ref text,
    target text,
    detail jsonb
)
```

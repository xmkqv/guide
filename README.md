
Declarative anti-fragile self-healing reifier.

# Usage

```bash
guide
guide style sync # runs bash style/align.sh
guide check # replace qxgo
```

- [Walkthrough](./walkthroughs/mission.md)

# Mission

```sql
enum Lang = {Py, Ts}

mission (
    name text,
    lang Lang,
    design list[spec],
    datasets? jsonb
)
```

- mission.yaml

```yaml
name: {string}
lang: {lang}
design: {list[spec]}
datasets?: {list[loader]}
```

- Self-healing: Deltas behave as stochastic gradient updates.
- Anti-fragile: Flaws → signals → insights

## Design

Specs decompose mission into irreducible, orthogonal, necessary, and consequential elements.

```sql
type test (
    path text, -- qualified path to single programmatic test
    result jsonb
)

type limn (
    type text, -- plot or diagram type
    path text,
    desc text
)

spec(
    key text pk generated always as random_hex(len=3),
    def text,
    test? test,
    limn? limn,
    detail jsonb,
    design list[spec]
)
```

## Datasets

Optional dataset manifest.

```sql
loader(
    ref text,
    target text,
    detail jsonb
)
```

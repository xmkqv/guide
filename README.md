
Declarative anti-fragile self-healing reifier.

# Mission

```sql
enum Lang = {Py, Ts}

mission (
    id text pk generated always as lowercase-acronym(name),
    name text,
    lang Lang
)
```

- mission.yaml

```yaml
id: {string}
name: {string}
lang: {lang}
design: {list[spec]}
signal: {list[test]}
datasets?: {list[loader]}
```

- Self-healing: Deltas behave as stochastic gradient updates.
- Anti-fragile: Flaws → signals → insights

## Design

```sql
spec(
    id text /S\d+/ pk, 
    name text,
    aspect_id text /S\d+/ fk spec.id,
    detail jsonb
)
```

- Idea: aspect_id = null
  - Unstructured multimodel information eg {tenets, sketches, scenarios, behaviors, exemplars, ...}.
- Directive: aspect_id != null
  - Irreducible, orthogonal, necessary, and consequential element of spec decomposition

## Code

Implementation intended to satisfy Specs.

## Signal

Lang determines the Tester, which parses programmatic tests and their results.

```text
1. tests = get_tests()
2. for test in tests:
    a. signal_test = to_signal_test(test)
    b. add to signal if has spec_ids
```

```sql
test(
    id text /T\d+/ pk,
    ref? text, -- qualified path to programmatic test
    spec_ids (text /S\d+/)[], -- verified spec references
    result jsonb -- framework structured test result
)
```

- Inline Design Spec Ids Pattern: `@design(/S\d+/,...)`

## Datasets

Optional dataset manifest.

```sql
loader(
    ref text,
    target text
)
```

# Usage

```bash
# Launch
guide
```

- [Exemplar](./exemplar.md)


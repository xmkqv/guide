
Declarative anti-fragile self-healing reifier.

[Complete Exemplar](./exemplar.md)

- Usage: `guide` launch guide app, aliased in ~/.zshrc.

# Mission

```sql
enum Lang = {Py, Ts}

mission (
    id text pk generated always as lowercase-acronym(name),
    name text,
    lang Lang
)
```

- mission.yaml; Intended to be consumed by an agent to quickly understand the mission & state.

```yaml
id: {string}
name: {string}
lang: {lang}
design: {list[spec]}
signal: {list[test]}
datasets: {list[dataset]}
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

App syncs test suites to Signal. Semantically, heuristically, and non-invasively link test results to Specs. Formal connections are out of scope.

```sql
test(
    id text /T\d+/ pk,
    ref? text,
    args jsonb,
    data jsonb,
)
```

## Datasets

Optional dataset manifest & protocol.

```sql
dataset(
    name text,
    loader_ref? text
)
```

```python
from guide import Mission

mission = Mission.load_nearest()
registry = mission.get_registry()

loader = registry.get_loader("dataset_name")
train, test = loader.load_split(test_fraction=0.2, seed=42)
```

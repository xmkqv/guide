# Self-Healing

```text
load_results()
```

```text
calc_coherence(guide) 
    specs = guide.design.flat()
    tests_results = load_results()
    coverage = how many **testable** specs have tests?
    n_flaw = how many specs have failing tests?
    return coherence = coverage / (coverage + n_flaw)
```text
guide sync
    │
    │   reads guide.yaml
    │   S = design.flat()
    │
    ▼
  load
    │
    │   reads .guide/results.jsonl
    │   R = [TestResult(ref, status) for line in file]
    │   for r in R: if s.test.ref == r.ref: s.test.result = r
    │
    ▼
 measure
    │
    │   for s in S:
    │     if s.test and s.test.result:
    │       L(s) = 0 if result.status == "passed" else 1
    │     else:
    │       L(s) = u
    │   L = sum(L(s)) / len(S)
    │   O = [r for r in R if no spec claims r.ref]
    │
    ▼
 report
    │
    │   stdout:
    │     L = {L}
    │     confirmed: [s.key for s in S if confirmed(s)]
    │     contradicted: [(s.key, s.defn, s.test.ref) for s in S if contradicted(s)]
    │     unbound: [(s.key, s.defn) for s in S if ¬bound(s)]
    │     orphans: [r.ref for r in O]
    │
    ▼
 human
    │
    │   reads report
    │   edits guide.yaml:
    │     - adds spec.test.ref to bind
    │     - changes spec.defn to revise
    │     - adds new spec to spawn
    │
    ▼
 tests (external)
    │
    │   pytest runs
    │   writes .guide/results.jsonl
    │
    └──────────────────────────────► guide sync
```

## Definitions

```text
u = 0.5

bound(s)        = s.test ≠ None
resolved(s)     = bound(s) ∧ ∃r ∈ R: r.ref = s.test.ref
confirmed(s)    = resolved(s) ∧ r.status = "passed"
contradicted(s) = resolved(s) ∧ r.status ≠ "passed"

L(s) = 0 if confirmed(s)
L(s) = 1 if contradicted(s)
L(s) = u otherwise

L = Σ L(s) / |S|

O = {r ∈ R : ¬∃s ∈ S: s.test.ref = r.ref}
```

## Output Format

```yaml
coherence:
  loss: 0.73
  confirmed: 3
  contradicted: 2
  unbound: 6

contradicted:
  - key: a1b
    defn: "user can login"
    ref: test::auth::login

unbound:
  - key: c2d
    defn: "session expires after 1h"

orphans:
  - ref: test::auth::logout
```

## Future: Auto-bind

```text
sim(s, o) = 1 - levenshtein(s.defn, o.ref) / max(len(s.defn), len(o.ref))

candidates(o) = [(s, sim(s, o)) for s in S if ¬bound(s)]
gap(o) = candidates[0].sim - candidates[1].sim

auto-bind when: sim > 0.7 ∧ gap > 0.3
```

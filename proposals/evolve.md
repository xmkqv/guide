# Evolve

Auto-evolution loop for guide. Minimal viable implementation.

## Premise

The guide.yaml contains Design. After sync, each spec has test results populated. The agent reads the complete state and proposes mutations. Human approves. Loop continues.

```text
∆Design → ∆Qualia → ∆Signal
   ↑                   ↓
   └────── agent ──────┘
```

The agent replaces ∇Loss with semantic reasoning.

## State

After sync, the guide contains:

```text
guide.design: Spec tree
  spec.key: identifier
  spec.defn: intended qualia (Design)
  spec.test.ref: binding to signal source
  spec.test.result: observed qualia (Signal)
  spec.specs: children
```

Flatten to work with:

```python
S = guide.design.flat()  # all specs as list
```

## Classification

Each spec occupies exactly one state:

```python
state(s):
  if s.test is None:
    return UNBOUND
  if s.test.result is None:
    return STALE
  if s.test.result.status == "passed":
    return VERIFIED
  return CONTRADICTED
```

Partition S by state:

```python
verified     = [s for s in S if state(s) == VERIFIED]
contradicted = [s for s in S if state(s) == CONTRADICTED]
unbound      = [s for s in S if state(s) == UNBOUND]
stale        = [s for s in S if state(s) == STALE]
orphans      = [r for r in results if r.ref not in {s.test.ref for s in S if s.test}]
```

## Actions

Four primitive mutations:

| Action | Precondition               | Effect                                     |
|--------|----------------------------|--------------------------------------------|
| bind   | s in unbound, o in orphans | s.test = Test(ref=o.ref)                   |
| unbind | s in stale                 | s.test = None                              |
| revise | s in contradicted          | s.defn = new_defn                          |
| spawn  | o in orphans               | S.append(Spec(defn, test=Test(ref=o.ref))) |

## Proposal

The agent generates actions with confidence, then partitions:

```python
propose(guide, classified) -> tuple[list[Action], list[Action]]:
  actions = []

  for s in stale:
    actions.append(Action("unbind", s.key, confidence=1.0))

  for o in orphans:
    match, conf = best_match(o, unbound)  # LLM call
    if match:
      actions.append(Action("bind", match.key, conf, value=o.ref))
    else:
      defn, conf = infer_defn(o)  # LLM call
      actions.append(Action("spawn", o.ref, conf, value=defn))

  for s in contradicted:
    new_defn, conf = infer_revision(s)  # LLM call
    actions.append(Action("revise", s.key, conf, value=new_defn))

  auto   = [a for a in actions if a.confidence > 0.8]
  review = [a for a in actions if a.confidence <= 0.8]
  return auto, review
```

## Execution

```python
execute(guide, actions):
  spec_map = {s.key: s for s in guide.design.flat()}
  for a in actions:
    match a.type:
      case "unbind": spec_map[a.target].test = None
      case "bind":   spec_map[a.target].test = Test(ref=a.value)
      case "revise": spec_map[a.target].defn = a.value
      case "spawn":  guide.design.specs.append(Spec(defn=a.value, test=Test(ref=a.target)))
  guide.dump()
```

## Loop

```python
evolve(guide):
  classified = classify(guide)
  auto, review = propose(guide, classified)
  execute(guide, auto)
  approved = human_review(review)
  execute(guide, approved)
```

Triggered by:

```bash
guide sync --evolve
```

## Prompt

```text
You are analyzing a guide for evolution.

State: {guide.yaml contents}

Classification:
  verified: {count}
  contradicted: {list with defn and result}
  unbound: {list with defn}
  stale: {list with defn and missing ref}
  orphans: {list with ref}

Task: Propose actions to improve coherence.

Output:
  actions:
    - type: bind | unbind | revise | spawn
      target: {spec.key or orphan.ref}
      confidence: {0.0-1.0}
      rationale: {brief}
      value: {new_defn or orphan.ref}
```

## Invariants

1. Schema validity: guide.yaml remains parseable
2. Monotonicity: verified count non-decreasing (circuit breaker on violation)
3. Traceability: every mutation has recorded rationale

## Summary

```text
sync → classify → propose → execute(auto) → review → execute(approved) → dump
```

Design evolves toward Signal. The agent mediates. Human approves when uncertain.

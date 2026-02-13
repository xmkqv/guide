# Coherence Analysis

Detect violations. Enumerate solutions.

## Violations

### Edge Contradictions

Same node pair with incompatible relationship types.

| Contradiction | Example |
|--------------|---------|
| requires + excludes | A requires B, A excludes B |
| precedes + follows | A precedes B, A follows B |
| contains + disjoint | A contains B, A disjoint B |
| enables + blocks | A enables B, A blocks B |

### Structural Violations

Graph properties that violate domain invariants.

| Violation | Detection | Domains |
|-----------|-----------|---------|
| Cycle in DAG | SCC with >1 node | Dependencies, inheritance |
| Layer violation | Edge from higher to lower layer | Architecture |
| Orphan required | Node marked required but unreachable | Configs, schemas |
| Missing root | No source nodes in tree structure | Hierarchies |
| Multi-parent in tree | Node with in-degree > 1 | Taxonomies |

### Semantic Violations

Domain-specific contradictions.

| Domain | Violation |
|--------|-----------|
| Code | Circular import, unused dependency |
| Systems | Bidirectional sync without conflict resolution |
| Concepts | Mutual exclusion in same category |
| Process | Parallel steps with shared mutable state |

## Detection

### Edge Contradiction Detection

```
For each node pair (A, B):
  edges = all edges between A and B
  For each edge type pair (e1, e2) in edges:
    If contradicts(e1.type, e2.type):
      Report contradiction
```

Contradiction matrix (symmetric):

|           | requires | excludes | enables | blocks |
|-----------|----------|----------|---------|--------|
| requires  |          | ✗        |         | ✗      |
| excludes  | ✗        |          | ✗       |        |
| enables   |          | ✗        |         | ✗      |
| blocks    | ✗        |          | ✗       |        |

### Structural Violation Detection

**DAG cycles:**
```
Run topological sort
If sort fails → cycles exist
Extract SCCs for cycle membership
```

**Layer violations:**
```
Assign layers via longest path from sources
For each edge (A → B):
  If layer(A) > layer(B): violation (higher depends on lower)
```

**Orphan detection:**
```
Mark all nodes reachable from roots
Unreached required nodes → orphans
```

## Solutions

### Edge Contradiction Resolution

| Strategy | When | Action |
|----------|------|--------|
| Prioritize | Clear precedence | Keep higher-priority edge, drop other |
| Qualify | Context-dependent | Add conditions (e.g., "requires if X") |
| Abstract | Over-specified | Replace both with weaker relationship |
| Escalate | Domain decision | Flag for human review |

### Cycle Breaking

| Strategy | When | Action |
|----------|------|--------|
| Invert | Wrong direction | Reverse one edge |
| Extract | Shared dependency | Create new node both depend on |
| Interface | Abstraction needed | Insert protocol/interface node |
| Accept | Intentional coupling | Document and mark as known |

### Layer Violation Resolution

| Strategy | When | Action |
|----------|------|--------|
| Move node | Misplaced | Reassign to correct layer |
| Add intermediate | Missing abstraction | Insert mediating node |
| Demote edge | Optional dependency | Mark as weak/optional |
| Restructure | Fundamental issue | Redesign layer boundaries |

## Output Format

When `--cohere` is specified, add after Motifs:

```markdown
## Coherence

| # | Type | Location | Description |
|---|------|----------|-------------|
| 1 | Contradiction | A↔B | requires + excludes |
| 2 | Cycle | {C,D,E} | 3-node SCC |
| 3 | Layer | F→G | L3 → L1 |

### Resolutions
(numbered options per violation)
```

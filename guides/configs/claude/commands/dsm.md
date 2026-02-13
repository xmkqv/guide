---
name: dsm
---

DSM: Design Structure Matrix; adjacency matrix encoding task dependencies
DMM: Domain Mapping Matrix; cross-domain DSM for heterogeneous artifacts

# Task Relations

| Relation | Syntax | Meaning |
|----------|--------|---------|
| Sequential | A → B | B requires A complete |
| Parallel   | A ∥ B | Independent; concurrent execution valid |
| Coupled    | A ⇄ B | Cyclic; requires iteration or tearing |

# Dependency Graph

Node := { task, doc, decision, code, test, artefact }
Edge := { blocks, informs, validates, implements }

DAG: Directed Acyclic Graph; admits topological sort
DCG: Directed Cyclic Graph; contains coupled blocks
SCC: Strongly Connected Component; maximal subgraph where every node reaches every other

coupling degree: count of edges incident to a node (in + out)
sink: node with out-degree 0; depends on others, nothing depends on it
topological sort: linear ordering where for every edge A→B, A precedes B

feedback distance: path length of shortest feedback loop through a node
feedback arc set: minimal edge set whose removal makes graph acyclic

critical path: longest path through DAG; determines minimum completion time
makespan: total duration from first task start to last task finish

Coupled Block: SCC with |nodes| > 1

# Ordering Principles

[^O:LeastCoupledFirst]: Least Coupled First
  Execute tasks in ascending order of coupling degree
  Clears noise, builds momentum, defers coupled blocks

  ```diagram:dependency-matrix
  Before (arbitrary):          After (O-LCF):
      │1 │2 │3 │4 │5 │6 │          │6 │5 │1 │2 │3 │4 │
  ────┼──┼──┼──┼──┼──┼──┤      ────┼──┼──┼──┼──┼──┼──┤
  1   │  │  │  │→ │  │  │      6   │  │  │  │  │  │  │ ← 0
  2   │  │  │⇄ │→ │→ │  │      5   │  │  │  │← │  │  │ ← 1
  3   │  │⇄ │  │→ │  │  │      1   │  │  │  │  │  │→ │ ← 1
  4   │← │← │← │  │  │  │      2   │  │→ │  │  │⇄ │→ │ ← 3
  5   │  │← │  │  │  │  │      3   │  │  │  │⇄ │  │→ │ ← 2
  6   │  │  │  │  │  │  │      4   │  │  │← │← │← │  │ ← 3

  Order: 6(0) → 5(1) → 1(1) → {2,3}(coupled) → 4(sink)
  ```

[^O:SequentialFirst]: Sequential First
  Topologically sort acyclic subgraph before addressing cycles

[^O:MaximizeParallelism]: Maximize Parallelism
  Independent tasks execute concurrently; critical path determines makespan

[^O:TearCoupledBlocks]: Tear Coupled Blocks
  Break cycles via provisional assumptions; mark assumptions for validation
  Tearing Point: edge removed to break cycle; requires explicit revisit

[^O:FailFastLoops]: Fail Fast Loops
  When cycles unavoidable, minimize feedback distance
  Prefer A → B → C → A over A → ... → Z → A

[^O:LocalizeCoupling]: Localize Coupling
  Coupled tasks should be adjacent in execution order
  Minimizes context switching and assumption drift

# Sequencing Algorithm

1. Partition graph into SCCs (strongly connected components)
2. Topologically sort the DAG of SCCs
3. Within each coupled SCC:
   a. Identify tearing points (minimum feedback arc set)
   b. Order to minimize feedback distance
   c. Mark torn edges as assumptions requiring validation
4. Execute in order; iterate coupled blocks until convergence

# Cross-Domain Mapping (DMM)

For heterogeneous artifacts, use typed adjacency:

```diagram:domain-mapping-matrix
        │ doc │ decision │ code │ test │
────────┼─────┼──────────┼──────┼──────┤
task    │  r  │    r     │  w   │  w   │
doc     │  -  │    i     │  i   │  -   │
decision│  -  │    -     │  b   │  -   │
code    │  -  │    -     │  -   │  v   │

r: requires    i: informs    b: blocks    v: validates
```

# Checks

[^C:NoUntrackedCoupling]: No Untracked Coupling
  Every coupled pair has explicit tearing strategy or iteration bound

[^C:AssumptionsTrackValidation]: Assumptions Track Validation
  Torn edges record: { assumption, validator_task, validated_at? }

[^C:CoupledBlocksBounded]: Coupled Blocks Bounded
  SCC size ≤ 5 tasks; larger blocks indicate design decomposition failure

# Guidance

[^M:TearBeforeDive]: Tear Before Dive
  Identify and document tearing points before executing coupled block

[^M:IteratePostValidation]: Iterate Post-Validation
  After torn assumption validated, reassess dependent tasks for rework

[^M:DecisionMakesFreedom]: Decision Makes Freedom
  Resolve decision nodes early; they gate parallel execution paths

# Trigger

When: Plan contains >3 tasks OR tasks touch overlapping files OR review identifies multiple fixes

1. ENUMERATE
   List tasks: { id, description, files[] }

2. BUILD MATRIX
   For each (i, j): mark → (i informs j), ⇄ (mutual), ∅ (none)

3. COMPUTE DEGREE
   degree(t) = |edges_in(t)| + |edges_out(t)|

4. IDENTIFY BLOCKS
   SCCs with |nodes| > 1 are coupled blocks
   Treat each SCC as atomic execution unit

5. ORDER (O-LCF)
   Sort: degree ASC → dependency direction
   → isolated → low-coupling → coupled blocks → sinks

6. EXECUTE
   independent   → execute directly
   coupled block → tear, execute with assumption, mark validation
   sink          → execute after dependencies stable

7. VALIDATE
   Revisit torn assumptions; iterate block if invalidated

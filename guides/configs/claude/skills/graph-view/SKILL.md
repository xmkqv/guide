---
name: graph-view
description: This skill should be used when the user asks to "2graph", "analyze relationships",
  "find patterns", "decompose into graph", "identify motifs", "map dependencies",
  "visualize connections", "understand structure", "--cohere", or mentions graph analysis,
  dependency mapping, coherence checking, or structural pattern recognition.
---

# Graph View

Analyze any domain as a graph. Identify nodes, relationships, and structural patterns.

## Workflow

```
1. BUILD       Nodes → Edges → Matrix
2. ANALYZE     Layers, Motifs, [Cohere]
3. INTERPRET   Domain insights
```

---

## Phase 1: Build

Construct the graph representation.

### Decompose

Identify discrete entities in the domain. Each node should be:
- Nameable with a short identifier
- Distinguishable from other nodes
- At consistent granularity

### Node Types by Domain

| Domain | Node Types |
|--------|------------|
| Code | Modules, classes, functions, files |
| Systems | Services, components, databases |
| Concepts | Ideas, terms, principles |
| Data | Tables, entities, schemas |
| Process | Steps, stages, milestones |
| Organization | Teams, roles, departments |

### Relate

Identify connections between nodes. For each edge, determine:
- Direction (A → B, B → A, or A ↔ B)
- Type (what kind of relationship)
- Strength (strong, normal, weak)

### Edge Types by Domain

| Domain | Edge Types |
|--------|------------|
| Code | imports, calls, inherits, implements |
| Systems | calls, reads, writes, depends |
| Concepts | requires, implies, contradicts, refines |
| Data | references, contains, derives |
| Process | precedes, enables, blocks |
| Organization | reports-to, collaborates, owns |

### Matrix

Build adjacency matrix (Design Structure Matrix). Rows depend on columns.

```
        │ A │ B │ C │ D │
    ────┼───┼───┼───┼───┤
    A   │   │ → │   │   │   A depends on B
    B   │   │   │ → │   │   B depends on C
    C   │   │   │   │ → │   C depends on D
    D   │ ⇄ │   │   │   │   D mutual with A
```

### Notation

| Symbol | Meaning |
|--------|---------|
| → | Dependency (row depends on column) |
| ⇄ | Mutual dependency (cycle) |
| ○ | Weak dependency |
| (empty) | No relationship |

### Matrix Properties

Compute for each node:
- **In-degree**: Count of → pointing to node (column sum)
- **Out-degree**: Count of → pointing from node (row sum)
- **Degree**: In-degree + Out-degree

---

## Phase 2: Analyze

Find structural patterns. Use Operations/Queries as needed.

### Layering

Compute dependency layers for DAG structure.

```
layer(n) = 0                           if in_degree(n) = 0
layer(n) = 1 + max(layer(d) for d in deps(n))  otherwise
```

**Layer violation**: Edge from higher layer to lower layer (e.g., layer 3 → layer 1) indicates architectural inversion.

### Operations (tool)

Transform graphs as needed.

| Op | Syntax | Effect |
|----|--------|--------|
| filter | `G[predicate]` | Subgraph matching condition |
| project | `G.nodes(type)` | Extract node subset by type |
| aggregate | `G.cluster(attr)` | Merge nodes sharing attribute |
| invert | `G.T` | Reverse all edge directions |
| compose | `G1 ∘ G2` | Overlay graphs, union edges |
| diff | `G1 - G2` | Edges in G1 not in G2 |

### Queries (tool)

Answer structural questions.

| Query | Expression | Returns |
|-------|------------|---------|
| Reachability | `path(A, B) ≠ ∅` | Can A reach B? |
| Impact | `descendants(A)` | What does A affect? |
| Dependencies | `ancestors(A)` | What does A require? |
| Criticality | `components(G - A)` | What breaks if A removed? |
| Shortest path | `dist(A, B)` | Minimum hops A→B |
| Common ancestor | `LCA(A, B)` | Nearest shared dependency |

### Motifs

Detect structural patterns. See [references/motifs.md](references/motifs.md) for full catalog.

**Node-level:**
- **Hub**: Degree > 2× average
- **Source**: In-degree = 0, out-degree > 0
- **Sink**: Out-degree = 0, in-degree > 0
- **Bridge**: Removal disconnects graph
- **Isolate**: Degree = 0

**Cluster-level:**
- **Clique**: Every node connects to every other
- **Star**: One hub, many leaves
- **Chain**: Linear sequence A → B → C
- **Cycle**: Circular path A → B → C → A
- **Community**: Dense internal, sparse external connections

**Global:**
- **Tree**: DAG with single root
- **Layered**: Nodes fall into dependency layers
- **Tangled**: High cycle count, poor layering

### Cohere (optional)

See [references/cohere.md](references/cohere.md). Only when `--cohere` specified.

---

## Phase 3: Interpret

Translate patterns to domain meaning.

| Pattern | Indicates | Action |
|---------|-----------|--------|
| Hub | Critical component, cascade risk | Extract interface, add redundancy |
| Bridge | Single point of failure | Add alternate path |
| Cycle | Tight coupling, init complexity | Break via interface or accept |
| Community | Natural boundary | Align with team/module |
| Source | Entry point, no deps | API surface candidate |
| Sink | Terminal, no dependents | Output/logging layer |
| Isolate | Dead code or missing edge | Remove or connect |

## Output Format

```markdown
# Graph Analysis: {domain}

## Nodes
| ID | Name | Type |
## Relationships
| From | To | Type | Strength |
## Matrix
(adjacency matrix with → ⇄ ○ symbols)
## Layers
| Layer | Nodes |
## Motifs
- Hubs: {nodes}
- Bridges: {nodes}
- Cycles: {node sets}
- Communities: {clusters}
## Metrics
| Metric | Value |
## Insights
(numbered interpretations)
## Coherence (--cohere only)
(violations and resolutions)
```

## Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Density | `E / (N × (N-1))` | <0.1 sparse, >0.3 dense |
| Avg Degree | `2E / N` | Typical connectivity |
| Clustering | `triangles / possible` | Local density |
| Modularity | `Q = Σ(e_ii - a_i²)` | Community strength |
| Diameter | `max(shortest paths)` | Graph spread |

## Verification

Check analysis quality:

```
V-NODE: Every entity is a node (no implicit actors)
V-EDGE: Every relationship is an edge (no hidden deps)
V-TYPE: Edge types are consistent within domain
V-MOTIF: All cycles and clusters documented
V-INSIGHT: Patterns have domain-specific interpretation
```

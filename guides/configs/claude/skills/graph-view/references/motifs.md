# Structural Motifs Reference

Complete catalog of graph patterns with detection heuristics and interpretation guidance.

## Node-Level Patterns

### Hub

High-degree node connecting many others.

**Detection:**
```
degree(node) > 2 × avg_degree(graph)
```

**Subtypes:**
- **In-hub**: High in-degree (many depend on it)
- **Out-hub**: High out-degree (depends on many)
- **Bidirectional hub**: High both directions

**Interpretation:**
- Critical component - failure causes cascade
- Natural integration point
- Candidate for interface extraction
- High maintenance burden

**Example:**
```
        │ A │ B │ C │ D │ E │
    ────┼───┼───┼───┼───┼───┤
    A   │   │   │   │ → │   │
    B   │   │   │   │ → │   │
    C   │   │   │   │ → │   │
    D   │   │   │   │   │   │  ← D is in-hub (degree=3)
    E   │   │   │   │ → │   │
```

### Source

Node with only outgoing edges.

**Detection:**
```
in_degree(node) = 0
out_degree(node) > 0
```

**Interpretation:**
- Entry point to system
- Origin of data or control flow
- No external dependencies
- Often: main(), config, constants

### Sink

Node with only incoming edges.

**Detection:**
```
out_degree(node) = 0
in_degree(node) > 0
```

**Interpretation:**
- Terminal point
- Final consumer
- Often: output, logging, persistence

### Bridge

Node whose removal disconnects the graph.

**Detection:**
```
Remove node → graph splits into components
```

Also called: Articulation point, cut vertex

**Interpretation:**
- Single point of failure
- Integration bottleneck
- Candidate for redundancy
- Natural API boundary

**Example:**
```
A ─── B ─── C ─── D ─── E
          ↑
      Bridge (removal splits into {A,B} and {D,E})
```

### Isolate

Node with no connections.

**Detection:**
```
degree(node) = 0
```

**Interpretation:**
- Dead code
- Orphaned entity
- Missing relationships
- Possibly incomplete analysis

## Dyad Patterns

Two-node relationships.

### Mutual (Reciprocal)

Bidirectional connection between two nodes.

**Notation:** A ⇄ B

**Detection:**
```
edge(A, B) exists AND edge(B, A) exists
```

**Interpretation:**
- Tight coupling
- Potential cycle
- Co-evolution required
- Consider merging or interface

## Triad Patterns (Census)

Three-node configurations. 16 possible types when considering direction.

### Common Triads

**Chain (A → B → C):**
```
A → B → C
Transitive dependency
```
Interpretation: Information flows through B

**Cycle (A → B → C → A):**
```
A → B
↑   ↓
└── C
```
Interpretation: Mutual dependency, complex initialization

**Star (hub + leaves):**
```
    A
   ↗ ↑ ↖
  B  C  D
```
Interpretation: Central coordination point

**Triangle (clique of 3):**
```
A ⇄ B
 ↖ ↗
  C
```
Interpretation: Tight cluster, all interconnected

### Transitive vs Intransitive

**Transitive:** A → B → C implies A → C
- Clean layering
- Good abstraction

**Intransitive:** A → B → C but A ↛ C
- Proper encapsulation
- B mediates access

## Cluster Patterns

### Clique

Fully connected subgraph where every node connects to every other.

**Detection:**
```
For all pairs (i, j) in cluster:
  edge(i, j) OR edge(j, i) exists
```

**Interpretation:**
- Tightly coupled module
- All-to-all communication
- Difficult to split
- Consider if cohesion is justified

**Example (clique of 4):**
```
A ⇄ B
⇅ ⤫ ⇅
C ⇄ D
```

### Near-Clique

Almost fully connected, missing few edges.

**Detection:**
```
density(cluster) > 0.8
```

Where density = edges / possible_edges

**Interpretation:**
- Cohesive unit
- Missing edges may be implicit
- Natural module boundary

### Star

One central hub connected to many leaves with no leaf-to-leaf connections.

**Detection:**
```
One node has degree = n-1
All other nodes have degree = 1
```

**Interpretation:**
- Coordinator pattern
- God object risk
- Façade opportunity
- Message broker

### Chain

Linear sequence of dependencies.

**Detection:**
```
Longest path through nodes where each has degree ≤ 2
```

**Interpretation:**
- Pipeline pattern
- Sequential processing
- Long dependency chain = fragility

### Cycle (Strongly Connected Component)

Set of nodes where every node can reach every other.

**Detection:**
Tarjan's algorithm or Kosaraju's algorithm

```
For all pairs (i, j) in SCC:
  path from i to j exists
  path from j to i exists
```

**Interpretation:**
- Circular dependency
- Initialization complexity
- Candidate for breaking via interface
- May indicate poor layering

**Resolution strategies:**
1. Identify tearing point (edge to break)
2. Extract common dependency
3. Introduce interface/abstraction
4. Accept and document coupling

### Community

Dense internal connections, sparse external connections.

**Detection:**
```
internal_density >> external_density
Modularity score > 0.3
```

**Interpretation:**
- Natural module boundary
- Team ownership candidate
- Microservice boundary
- Cohesive unit

## Structural Roles

Node positions in overall topology.

### Peripheral

Low degree, edge of network.

**Detection:**
```
degree(node) = 1 or 2
Located at graph boundary
```

**Interpretation:**
- Leaf functionality
- Specialized concern
- Easy to modify in isolation

### Connector

Links between communities.

**Detection:**
```
Node has edges to multiple communities
Low within-community degree
High between-community degree
```

**Interpretation:**
- Integration layer
- API boundary
- Translation/adaptation logic
- High importance despite low degree

### Provincial Hub

Hub within a single community.

**Detection:**
```
High degree within community
Low degree outside community
```

**Interpretation:**
- Module coordinator
- Internal façade
- Community leader

### Kinless Hub

Hub spanning multiple communities.

**Detection:**
```
High degree to multiple communities
No strong community affiliation
```

**Interpretation:**
- Global utility
- Cross-cutting concern
- Potential god object
- Consider splitting by concern

## Global Patterns

### Tree / DAG

Directed acyclic graph with hierarchical structure.

**Detection:**
```
No cycles (topological sort succeeds)
```

**Properties:**
- Clear layering
- Clean dependencies
- Simple reasoning

### Layered

Nodes organize into dependency layers.

**Detection:**
```
Assign layer = max(layer of dependencies) + 1
Few or no edges within same layer
```

**Interpretation:**
- Good architecture
- Clear abstraction levels
- Easy to understand

### Tangled

High cycle count, poor layer structure.

**Detection:**
```
Many SCCs
Low modularity score
Edges violate layer ordering
```

**Interpretation:**
- Architectural debt
- Difficult reasoning
- Refactoring needed

## Domain-Specific Patterns

### Code Graphs

| Pattern | Meaning |
|---------|---------|
| Import cycle | Modules mutually depend |
| God class (hub) | Does too much |
| Orphan (isolate) | Dead code |
| Deep chain | Long dependency path |
| Layer violation | Lower depends on higher |

### System Graphs

| Pattern | Meaning |
|---------|---------|
| Service cycle | Distributed deadlock risk |
| Single database (hub) | Scaling bottleneck |
| Redundant paths | Fault tolerance |
| Star topology | Central coordination |

### Concept Graphs

| Pattern | Meaning |
|---------|---------|
| Prerequisite chain | Learning path |
| Concept cluster | Related ideas |
| Bridge concept | Connects domains |
| Foundational (source) | Core concept |
| Derived (sink) | Advanced topic |


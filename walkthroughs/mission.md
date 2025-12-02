# Exemplar

## Philosophy

Specs declare invariants. Tests derive from specs. Signals ground design in reality.

```text
∆Design → ∆Code → ∆Signal
    ↑                  ↓
    └──── ∇Loss ───────┘
```

Each signal is a loss measurement. Each delta is a gradient step. Iteration converges toward correctness.

- Anti-fragile: Flaws reveal hidden assumptions. Each failure strengthens.
- Self-healing: Failures contain remediation signals. No external oracle required.

## Mission Structure

```yaml
id: kv
name: Key-Value Store
lang: Py

design:
  # Ideas (aspect_id: null) - unstructured intent
  - id: S0
    name: Durability
    aspect_id: null
    detail:
      type: tenet
      content: Data survives process crash

  # Directives (aspect_id: S*) - testable invariants
  - id: S1
    name: Write-Ahead Log
    aspect_id: S0
    detail:
      invariant: write(k,v) → log.append(k,v) → ack
      constraint: ack implies persisted

  - id: S2
    name: Recovery
    aspect_id: S0
    detail:
      invariant: crash → restart → state = replay(log)
      constraint: no acknowledged write lost

signal: []  # populated by tester
```

## Test Derivation

Tests declare spec linkage via docstring: `@design(S0, S1, ...)`

The invariant `write(k,v) → log.append(k,v) → ack` derives:

```python
def test_wal_ordering():
    """Verify write-ahead log preserves order.

    @design(S1)
    """
    store = KVStore()
    ops = []
    for i in range(1000):
        k, v = f"k{i}", f"v{i}"
        store.write(k, v)
        ops.append((k, v))

    log_entries = store.read_log()
    assert ops == log_entries
```

The invariant `crash → restart → state = replay(log)` derives:

```python
def test_crash_recovery():
    """Verify no acknowledged write lost after crash.

    @design(S2)
    """
    store = KVStore()
    for i in range(500):
        store.write(f"k{i}", f"v{i}")

    store.simulate_crash()
    store.recover()

    for i in range(500):
        assert store.read(f"k{i}") == f"v{i}"
```

Tests without `@design(...)` are excluded from signal by default.

## Iteration 0: Initial

```python
import attrs

@attrs.define
class KVStore:
    _data: dict = attrs.Factory(dict)
    _log: list = attrs.Factory(list)

    def write(self, k, v):
        self._log.append((k, v))
        self._data[k] = v

    def read(self, k):
        return self._data.get(k)

    def read_log(self):
        return list(self._log)

    def simulate_crash(self):
        self._data.clear()

    def recover(self):
        for k, v in self._log:
            self._data[k] = v
```

After `pytest --report-log=results/results.jsonl` and sync:

```yaml
signal:
  - id: T0
    ref: tests/test_kv.py::test_wal_ordering
    spec_ids: [S1]
    result:
      outcome: passed
      duration: 0.042
      timestamp: 2025-12-01T10:00:00Z

  - id: T1
    ref: tests/test_kv.py::test_crash_recovery
    spec_ids: [S2]
    result:
      outcome: failed
      duration: 0.018
      timestamp: 2025-12-01T10:00:00Z
```

## Iteration 1: Gradient Step

T1 failure reveals: log in memory, lost on crash.

∆Design - refine S1:

```yaml
- id: S1
  name: Write-Ahead Log
  aspect_id: S0
  detail:
    invariant: write(k,v) → disk.append(k,v) → ack
    constraint: ack implies durable
```

∆Code:

```python
def write(self, k, v):
    with open(self._log_path, "a") as f:
        f.write(f"{k}\t{v}\n")
        f.flush()
        os.fsync(f.fileno())
    self._data[k] = v
```

∆Signal:

```yaml
- id: T1
  ref: tests/test_kv.py::test_crash_recovery
  spec_ids: [S2]
  result:
    outcome: passed
    duration: 0.156
    timestamp: 2025-12-01T11:00:00Z
```

Loss decreased.

## Iteration 2: Stress Reveals

Add stress test:

```python
def test_throughput():
    """Verify write throughput under load.

    @design(S1)
    """
    store = KVStore()
    start = time.perf_counter()
    for i in range(100_000):
        store.write(f"k{i}", f"v{i}")
    elapsed = time.perf_counter() - start
    ops_per_sec = 100_000 / elapsed
    assert ops_per_sec > 10_000, f"Too slow: {ops_per_sec:.0f} ops/sec"
```

Signal:

```yaml
- id: T2
  ref: tests/test_kv.py::test_throughput
  spec_ids: [S1]
  result:
    outcome: failed
    duration: 8.333
    timestamp: 2025-12-01T12:00:00Z
```

Flaw: fsync per write yields 12 ops/sec.

## Iteration 3: Insight

The flaw reveals hidden assumption: durability requires immediate fsync. The spec says `ack implies persisted` - not `persisted immediately`.

∆Design - add batching directive:

```yaml
- id: S3
  name: Batch Commit
  aspect_id: S1
  detail:
    invariant: batch(writes) → single fsync → ack_all
    constraint: latency(ack) < 10ms p99
    tradeoff: durability window = batch interval
```

∆Code:

```python
def write(self, k, v):
    self._batch.append((k, v))
    if len(self._batch) >= BATCH_SIZE or self._batch_age() > MAX_WAIT:
        self._flush_batch()
    self._data[k] = v
```

Update test to verify both specs:

```python
def test_throughput():
    """Verify write throughput under load.

    @design(S1, S3)
    """
    # ...
```

∆Signal:

```yaml
- id: T2
  ref: tests/test_kv.py::test_throughput
  spec_ids: [S1, S3]
  result:
    outcome: passed
    duration: 2.222
    timestamp: 2025-12-01T13:00:00Z
```

System is stronger than before stress.

## Final State

```yaml
id: kv
name: Key-Value Store
lang: Py

design:
  - id: S0
    name: Durability
    aspect_id: null
    detail:
      type: tenet
      content: Data survives process crash

  - id: S1
    name: Write-Ahead Log
    aspect_id: S0
    detail:
      invariant: write(k,v) → disk.append(k,v) → ack
      constraint: ack implies durable

  - id: S2
    name: Recovery
    aspect_id: S0
    detail:
      invariant: crash → restart → state = replay(log)
      constraint: no acknowledged write lost

  - id: S3
    name: Batch Commit
    aspect_id: S1
    detail:
      invariant: batch(writes) → single fsync → ack_all
      constraint: latency(ack) < 10ms p99
      tradeoff: durability window = batch interval

signal:
  - id: T0
    ref: tests/test_kv.py::test_wal_ordering
    spec_ids: [S1]
    result:
      outcome: passed
      duration: 0.042
      timestamp: 2025-12-01T13:00:00Z

  - id: T1
    ref: tests/test_kv.py::test_crash_recovery
    spec_ids: [S2]
    result:
      outcome: passed
      duration: 0.089
      timestamp: 2025-12-01T13:00:00Z

  - id: T2
    ref: tests/test_kv.py::test_throughput
    spec_ids: [S1, S3]
    result:
      outcome: passed
      duration: 2.222
      timestamp: 2025-12-01T13:00:00Z
```

## Spec Hierarchy

```text
S0 Durability (idea)
├── S1 Write-Ahead Log (directive)
│   └── S3 Batch Commit (directive)
└── S2 Recovery (directive)
```

Ideas ground in tenets. Directives decompose into testable invariants. The tree grows as understanding deepens.

## Properties

Gradient descent:
- Loss = test failures
- Gradient = insight from failure
- Step = design delta
- Convergence = all tests pass

Anti-fragile:
- Iteration 0: Naive, brittle
- Iteration 1: Correct, slow
- Iteration 2: Stress reveals weakness
- Iteration 3: Stronger than before stress

Self-healing:
- Failures contain remediation signals
- System evolves toward robustness
- No external oracle decides fixes

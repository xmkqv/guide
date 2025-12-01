# Exemplar

## Philosophy

Specs declare invariants. Tests derive from specs. Signals ground design in reality.

```text
∆Design → ∆Code → ∆Signal
    ↑                  ↓
    └──── ∇Loss ───────┘
```

Each signal is a loss measurement. Each delta is a gradient step. Iteration converges toward correctness.

Anti-fragile: Flaws do not weaken. They reveal hidden assumptions. Each failure strengthens.

## mission.yaml

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

signal:
  - id: T1
    ref: S1
    args: {ops: 1000}
    data: null

  - id: T2
    ref: S2
    args: {crash_after: 500}
    data: null
```

## Derivation

Specs generate tests. The invariant `write(k,v) → log.append(k,v) → ack` derives:

```python
def test_t1_wal_ordering():
    """S1: ack implies persisted"""
    store = KVStore()
    ops = []
    for i in range(1000):
        k, v = f"k{i}", f"v{i}"
        store.write(k, v)
        ops.append((k, v))

    log_entries = store.read_log()
    assert ops == log_entries  # order preserved, all present
```

The invariant `crash → restart → state = replay(log)` derives:

```python
def test_t2_crash_recovery():
    """S2: no acknowledged write lost"""
    store = KVStore()
    for i in range(500):
        store.write(f"k{i}", f"v{i}")

    store.simulate_crash()
    store.recover()

    for i in range(500):
        assert store.read(f"k{i}") == f"v{i}"
```

## Iteration 0: Initial Implementation

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
        self._data.clear()  # memory lost

    def recover(self):
        for k, v in self._log:
            self._data[k] = v
```

Signal:

```yaml
signal:
  - id: T1
    ref: S1
    data: {status: pass}

  - id: T2
    ref: S2
    data: {status: fail, reason: "log in memory, lost on crash"}
```

## Iteration 1: Gradient Step

T2 failure reveals: log must persist to disk, not memory.

∆Design:

```yaml
- id: S1
  name: Write-Ahead Log
  aspect_id: S0
  detail:
    invariant: write(k,v) → disk.append(k,v) → ack  # memory → disk
    constraint: ack implies durable
```

∆Code:

```python
def write(self, k, v):
    with open(self._log_path, "a") as f:
        f.write(f"{k}\t{v}\n")
        f.flush()
        os.fsync(f.fileno())  # force to disk
    self._data[k] = v
```

∆Signal:

```yaml
- id: T2
  ref: S2
  data: {status: pass}
```

Loss decreased. But new signal emerges.

## Iteration 2: Stress Reveals

Add stress test (anti-fragility probe):

```yaml
- id: T3
  ref: S1
  args: {ops: 100000, concurrent: 8}
  data: null
```

Signal:

```yaml
- id: T3
  ref: S1
  data: {status: fail, reason: "fsync per write: 12 ops/sec"}
```

Flaw revealed: fsync per write is correct but slow.

## Iteration 3: Insight

The flaw reveals a hidden assumption: durability requires immediate fsync. But the spec says `ack implies persisted` - it does not say `persisted immediately`.

∆Design: Add batching directive under S1.

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

∆Signal:

```yaml
- id: T3
  ref: S1
  data: {status: pass, throughput: "45000 ops/sec"}
```

The system is now stronger than before the flaw was discovered.

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
  - id: T1
    ref: S1
    data: {status: pass}

  - id: T2
    ref: S2
    data: {status: pass}

  - id: T3
    ref: S1
    data: {status: pass, throughput: "45000 ops/sec"}
```

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
- No external oracle decides fixes
- Failures contain their own remediation signal
- System evolves toward robustness

## Spec Hierarchy

```text
S0 Durability (idea)
├── S1 Write-Ahead Log (directive)
│   └── S3 Batch Commit (directive)
└── S2 Recovery (directive)
```

Ideas ground in tenets. Directives decompose into testable invariants. The tree grows as understanding deepens.

---
description: Machine Learning Style Guide
paths:
  - "**/*.py"
---

invs:
  profile before optimize
  measure before benchmark (warmup required)

# Profiling

```python
with torch.profiler.profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], with_stack=True) as prof:
    model(input)
```

bottleneck categories: compute-bound (high kernel time) | memory-bound (high bandwidth) | launch-overhead (many small kernels)

# Techniques

| technique | speedup | memory | when |
| --- | --- | --- | --- |
| `torch.compile` | 1.2–2x | neutral | always |
| mixed precision | 1.5–2x | 0.5x | Ampere+ |
| FlashAttention | 2–4x | O(N) vs O(N²) | transformers |
| activation checkpointing | 0.7–0.8x | 0.3–0.5x | memory-constrained |
| CUDA graphs | 1.5–2x | neutral | static shapes, small kernels |
| channels last | 1.1–1.3x | neutral | CNNs |

# Compilation

```python
model = torch.compile(model, mode="reduce-overhead")  # training
model = torch.compile(model, mode="max-autotune")     # inference
```

graph breaks kill performance; detect: `fullgraph=True`
causes: data-dependent control flow | `print` | `.item()`

# Precision

| format | bits | use |
| --- | --- | --- |
| FP32 | 32 | baseline |
| BF16 | 16 | training (Ampere+) |
| FP16 | 16 | inference, pre-Ampere |
| FP8 | 8 | Hopper |

∴ BF16 > FP16 on Ampere+: same dynamic range as FP32, no gradient scaling

# Memory

- activation checkpointing: `checkpoint(fn, x, use_reentrant=False)` at layer boundaries
- gradient accumulation: `loss / accumulation_steps`, step every N batches

# Sync Points

hidden synchronizations ⇒ throughput loss:
- `tensor.item()`: GPU → Python
- `print(tensor)`: requires sync
- `if tensor.any()`: Python control flow on GPU data
- `tensor.to(device)` without `non_blocking=True`

# Distributed

| scale | approach |
| --- | --- |
| model fits in GPU | DistributedDataParallel |
| model exceeds GPU | FullyShardedDataParallel |

invs:
  ¬ DataParallel (synchronizes every forward)
  ¬ CPU-GPU ping-pong in training loop
  ¬ Python loops over tensor elements
  ¬ synchronous logging in hot path
  ¬ default weight initialization
  ¬ benchmarking without warmup

# PyTorch

Performance axioms. Hardware constraints admit no interpretation.

## Foundations

PyTorch Performance Tuning Guide. FlashAttention (Dao). Mixed Precision Training (Micikevicius). CUDA C++ Best Practices Guide.

## Axioms

Profile first. Optimization without measurement is superstition.

```python
with torch.profiler.profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], with_stack=True) as prof:
    model(input)
```

Bottleneck categories: compute-bound (high kernel time), memory-bound (high bandwidth), launch-overhead (many small kernels).

| Technique | Speedup | Memory | When |
| --------- | ------- | ------ | ---- |
| `torch.compile` | 1.2-2x | neutral | Always |
| Mixed precision | 1.5-2x | 0.5x | Ampere+ |
| FlashAttention | 2-4x | O(N) vs O(N²) | Transformers |
| Activation checkpointing | 0.7-0.8x | 0.3-0.5x | Memory-constrained |
| CUDA graphs | 1.5-2x | neutral | Static shapes, small kernels |
| Channels last | 1.1-1.3x | neutral | CNNs |

## Compilation

```python
model = torch.compile(model, mode="reduce-overhead")  # training
model = torch.compile(model, mode="max-autotune")     # inference
```

Graph breaks kill performance. Detect with `fullgraph=True`. Causes: data-dependent control flow, print statements, `.item()`.

## Precision

| Format | Bits | Use |
| ------ | ---- | --- |
| FP32 | 32 | baseline |
| BF16 | 16 | training (Ampere+) |
| FP16 | 16 | inference, pre-Ampere |
| FP8 | 8 | Hopper |

BF16 over FP16 on Ampere+: same dynamic range as FP32, no gradient scaling. Practical speedup ~1.5-2x end-to-end; FP8 adds ~2x over FP16.

## Memory

Activation checkpointing: `checkpoint(fn, x, use_reentrant=False)`. Checkpoint at layer boundaries.

Gradient accumulation: `loss / accumulation_steps`, step every N batches.

## Sync Points

Hidden synchronizations kill throughput:
- `tensor.item()`: GPU to Python
- `print(tensor)`: requires sync
- `if tensor.any()`: Python control flow on GPU data
- `tensor.to(device)` without `non_blocking=True`

## Distributed

| Scale | Approach |
| ----- | -------- |
| Model fits in GPU | DistributedDataParallel |
| Model exceeds GPU | FullyShardedDataParallel |

## Never

- DataParallel (synchronizes every forward)
- CPU-GPU ping-pong in training loop
- Python loops over tensor elements
- Synchronous logging in hot path
- Default weight initialization
- Benchmarking without warmup

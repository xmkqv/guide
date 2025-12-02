# Neural Networks

Performance axioms for PyTorch. Hardware constraints admit no interpretation.

## Foundations

PyTorch Performance Tuning Guide. FlashAttention (Dao). Mixed Precision Training (Micikevicius). CUDA C++ Best Practices Guide.

## Axiom Zero: Profile First

Optimization without measurement is superstition.

```python
with torch.profiler.profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    with_stack=True
) as prof:
    model(input)
prof.export_chrome_trace("trace.json")
```

Identify the bottleneck category before applying axioms:
- Compute-bound: low GPU idle, high kernel time
- Memory-bound: high memory bandwidth utilization
- Launch-overhead-bound: many small kernels, high CPU time

## Axioms

| Axiom | Speedup | Memory | When |
| ----- | ------- | ------ | ---- |
| JIT compilation | 2-4x | neutral | Always for training/inference |
| Lower precision | 2-16x | 0.25-0.5x | Ampere+ GPUs |
| Fused attention | 2-8x | O(N) vs O(N²) | Transformer models |
| Activation checkpointing | 0.75x | 0.4x | Memory-constrained |
| CUDA graphs | 1.5-2.3x | neutral | Static shapes, inference |
| Channels last | 1.2-1.5x | neutral | CNNs on tensor cores |
| Async data loading | varies | varies | CPU-GPU overlap needed |

## Compilation

```python
model = torch.compile(model, mode="reduce-overhead")  # training
model = torch.compile(model, mode="max-autotune")     # inference
```

Warmup before serving: JIT compiles on first call.

Graph breaks interrupt compilation. Detect with `fullgraph=True`. Common causes: data-dependent control flow, print statements.

## Precision

| Format | Bits | Throughput | Use |
| ------ | ---- | ---------- | --- |
| FP32 | 32 | 1x | baseline |
| BF16 | 16 | 16x | training (Ampere+) |
| FP16 | 16 | 16x | inference, pre-Ampere |
| FP8 | 8 | 32x | Hopper (H100) |

BF16 over FP16 on Ampere+: same dynamic range as FP32, no gradient scaling needed.

```python
with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
    output = model(input)
    loss = criterion(output, target)
loss.backward()  # BF16: direct backward, no scaler
```

## Attention

Scaled dot-product attention auto-selects optimal backend:

```python
output = F.scaled_dot_product_attention(q, k, v)
# Dispatches to FlashAttention-2, Memory-Efficient, or Math
```

FlashAttention: 37x faster than naive, O(N) memory.

Requirements: CUDA >= 8.0, head dims 64/128/256.

## Memory

Activation checkpointing trades compute for memory:

```python
from torch.utils.checkpoint import checkpoint

def forward(self, x):
    return checkpoint(self._forward, x, use_reentrant=False)
```

Always `use_reentrant=False`. Checkpoint at layer boundaries.

Gradient accumulation for effective large batches:

```python
for i, batch in enumerate(loader):
    loss = model(batch) / accumulation_steps
    loss.backward()
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

## Async Operations

Hidden sync points kill throughput:
- `tensor.item()`: GPU to Python
- `print(tensor)`: requires sync
- `if tensor.any()`: Python control flow on GPU data

Fix: keep data on GPU, use tensor comparisons.

```python
# Bad: synchronizes
if loss.item() < threshold: break

# Good: stays on GPU
if loss < threshold_tensor: break
```

Non-blocking transfers require pinned memory:

```python
tensor.to(device, non_blocking=True)
```

## Data Loading

```python
DataLoader(
    dataset,
    batch_size=32,
    num_workers=4 * num_gpus,
    pin_memory=True,
    prefetch_factor=2,
    persistent_workers=True
)
```

## Initialization

Match initialization to activation function:

| Activation | Initialization |
| ---------- | -------------- |
| ReLU | Kaiming (fan_in) |
| Tanh/Sigmoid | Xavier |
| Linear (none) | Xavier |

PyTorch defaults are often suboptimal. Always initialize explicitly.

## Distributed

| Scale | Approach |
| ----- | -------- |
| Model fits in GPU | DistributedDataParallel |
| Model exceeds GPU | FullyShardedDataParallel |

Never use DataParallel. It synchronizes every forward pass.

## Inference Checklist

```python
model = torch.compile(model, mode="max-autotune")
model = model.to(torch.bfloat16)
model = model.to(memory_format=torch.channels_last)  # CNNs

with torch.inference_mode():
    output = model(input)
```

## Training Checklist

```python
model = torch.compile(model, mode="reduce-overhead")
torch.backends.cudnn.benchmark = True  # static shapes only

loader = DataLoader(..., pin_memory=True, num_workers=4*ngpu)

with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
    loss = model(batch)
loss.backward()
```

## Never

- CPU-GPU ping-pong in training loop
- Python loops over tensor elements
- Synchronous logging (`print(loss.item())`)
- DataParallel
- Default weight initialization
- Benchmarking without warmup

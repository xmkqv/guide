# Neural Networks Hyper Guide

First principles, irrevocable axioms for PyTorch performance.

Version 1.0 | November 2025

## Axiom Overview

Nine axioms govern neural network performance. Each is provable, measurable, and non-negotiable.

| Domain | Axiom | Speedup | Memory | Citation |
| ------ | ----- | ------- | ------ | -------- |
| Compilation | JIT everything | 2-4x | neutral | [PyTorch Tutorials](https://docs.pytorch.org/tutorials/intermediate/torch_compile_tutorial.html) |
| Precision | Lower is faster | 2-16x | 0.25-0.5x | [PyTorch AMP Blog](https://pytorch.org/blog/what-every-user-should-know-about-mixed-precision-training-in-pytorch/) |
| Attention | Fuse the quadratic | 2-8x | O(N) vs O(N^2) | [PyTorch SDPA](https://docs.pytorch.org/tutorials/intermediate/scaled_dot_product_attention_tutorial.html) |
| Memory | Trade compute for space | 0.75x | 0.4x | [PyTorch Checkpointing](https://pytorch.org/blog/activation-checkpointing-techniques/) |
| Kernels | Capture and replay | 1.5-2.3x | neutral | [PyTorch CUDA Graphs](https://pytorch.org/blog/accelerating-pytorch-with-cuda-graphs/) |
| Layout | Tensor cores want NHWC | 1.22-1.5x | neutral | [Channels Last Tutorial](https://docs.pytorch.org/tutorials/intermediate/memory_format_tutorial.html) |
| Loading | Overlap CPU and GPU | varies | varies | [Performance Tuning Guide](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html) |
| Sync | Async or die | varies | neutral | [PyTorch Performance](https://towardsdatascience.com/pytorch-model-performance-analysis-and-optimization-part-3-1c5876d78fe2/) |
| Stability | Initialize for your activation | n/a | n/a | [Lightning Tutorial](https://lightning.ai/docs/pytorch/stable/notebooks/course_UvA-DL/03-initialization-and-optimization.html) |

## Axiom 1: JIT Everything

Compilation transforms Python into fused GPU kernels.

### The Rule

```text
model = Compile(model, mode="reduce-overhead")
optimizer = Compile(optimizer)
```

### Mode Selection

- `default`: fastest compile, moderate inference
- `reduce-overhead`: balanced, best for training
- `max-autotune`: slowest compile, fastest inference

### When to Use Each Mode

- Training: `reduce-overhead` (limited window for ROI)
- Inference: `max-autotune` (amortize over model lifetime)
- Experimentation: `default` (fast iteration)

### Critical Practice: Warmup

```text
-- Before serving traffic
for _ in Range(warmup_iterations):
    model(representative_input)  -- triggers all compilation paths
```

JIT compilation happens on first call. Cold starts destroy latency SLAs.

### Graph Breaks

Graph breaks interrupt compilation when encountering unsupported Python. Each break loses optimization opportunity.

Common causes:
- Data-dependent control flow
- Python print statements
- Unsupported operations

Detection:

```text
Compile(model, fullgraph=True)  -- errors on graph breaks
```

### Compile the Full Loop

Maximum benefit comes from compiling the entire training step:

```text
function TrainStep(batch):
    loss = ComputeLoss(model, batch)
    Backward(loss)
    optimizer.Step()
    return loss

compiled_step = Compile(TrainStep)
```

Source: [torch.compile Tutorial](https://docs.pytorch.org/tutorials/intermediate/torch_compile_tutorial.html)

## Axiom 2: Lower is Faster

Reduced precision doubles throughput and halves memory.

### The Hierarchy

| Precision | Bits | Throughput vs FP32 | Use Case |
| --------- | ---- | ------------------ | -------- |
| FP32 | 32 | 1x | baseline |
| TF32 | 19 | 8x on Ampere+ | default on A100+ |
| BF16 | 16 | 16x on A100+ | training (preferred) |
| FP16 | 16 | 16x | inference, legacy training |
| FP8 | 8 | 32x on H100+ | training/inference on Hopper |
| INT8 | 8 | 2-4x | inference quantization |

### BF16 vs FP16: The Decision

BF16 on Ampere+ (A100, RTX 30xx, H100):
- 8-bit exponent matches FP32 dynamic range
- Tolerates large/small magnitudes
- No gradient scaling needed
- Fewer NaNs, fewer overflows

FP16 only when:
- BF16 not available (pre-Ampere)
- BF16 slower on specific hardware
- Legacy model compatibility

### Mixed Precision Pattern

```text
scaler = GradScaler("cuda")  -- only for FP16, not BF16

for batch in dataloader:
    with AutoCast(device="cuda", dtype=bfloat16):
        output = model(batch)
        loss = ComputeLoss(output, targets)

    -- BF16: direct backward
    Backward(loss)
    optimizer.Step()

    -- FP16: scaled backward
    scaler.Scale(loss).Backward()
    scaler.Step(optimizer)
    scaler.Update()
```

### FP8 on Hopper

Two FP8 formats exist:
- E4M3: 4 exponent, 3 mantissa, range +/-448 (forward pass)
- E5M2: 5 exponent, 2 mantissa, range +/-57344 (backward pass)

Requires NVIDIA Transformer Engine:

```text
import transformer_engine as te

with te.fp8_autocast(enabled=True):
    output = model(input)
```

Performance: ~20% additional speedup over BF16 on H100.

Source: [PyTorch AMP](https://pytorch.org/blog/what-every-user-should-know-about-mixed-precision-training-in-pytorch/), [Transformer Engine](https://github.com/NVIDIA/TransformerEngine)

## Axiom 3: Fuse the Quadratic

Standard attention is O(N^2) in memory. Fused attention is O(N).

### Scaled Dot Product Attention

PyTorch SDPA automatically selects optimal backend:

```text
output = ScaledDotProductAttention(query, key, value)
-- Automatically dispatches to:
-- 1. FlashAttention-2 (fastest, memory efficient)
-- 2. Memory-Efficient Attention (fallback)
-- 3. Math implementation (reference)
```

### Performance Numbers

| Implementation | Latency (us) | Memory |
| -------------- | ------------ | ------ |
| Math (naive) | 87046 | O(N^2) |
| Flash Attention | 2334 | O(N) |
| Memory Efficient | 4344 | O(N) |

FlashAttention is 37x faster than naive.

### Backend Control

```text
-- Force specific backend
with SdpaKernel(FLASH_ATTENTION):
    output = ScaledDotProductAttention(q, k, v)

-- Disable globally
backends.cuda.EnableFlashSdp(False)
backends.cuda.EnableMemEfficientSdp(False)
```

### When Flash Attention Fails

Hardware requirements:
- CUDA compute capability >= 8.0 (Ampere+)
- Head dimensions: 64, 128, or 256
- Sequence length > 0

If unsupported, SDPA silently falls back to slower implementations.

### KV Caching for Inference

Static KV cache + torch.compile = 4x speedup:

```text
-- Pre-allocate cache to max sequence length
kv_cache = StaticCache(max_length=4096)

-- Compile with static shapes
model = Compile(model, fullgraph=True)
```

Source: [SDPA Tutorial](https://docs.pytorch.org/tutorials/intermediate/scaled_dot_product_attention_tutorial.html), [PyTorch 2.2 Release](https://pytorch.org/blog/pytorch2-2/)

## Axiom 4: Trade Compute for Space

Activation checkpointing discards intermediate activations and recomputes them.

### The Tradeoff

- Memory: ~60% reduction
- Compute: ~25% increase
- Net effect: Train 4-10x larger models

### Implementation

```text
from torch.utils.checkpoint import checkpoint

class TransformerBlock:
    function forward(x):
        -- Checkpoint each block
        return checkpoint(self._forward_impl, x, use_reentrant=False)

    function _forward_impl(x):
        x = x + self.attention(self.norm1(x))
        x = x + self.mlp(self.norm2(x))
        return x
```

### Critical: use_reentrant=False

Always use `use_reentrant=False`:
- Non-reentrant is the future default
- Fixes edge cases with reentrant checkpointing
- Better gradient computation

### Selective Activation Checkpointing

Fine-grained control over what to recompute:

```text
-- Recompute cheap ops (pointwise), keep expensive ops (matmul)
policy = SelectiveCheckpointPolicy(
    recompute=[pointwise_ops],
    keep=[matmul_ops]
)
```

### Optimal Checkpoint Count

Too many checkpoints increases memory (recomputation overhead). Profile to find optimal granularity.

Heuristic: checkpoint at layer boundaries, not within layers.

Source: [Activation Checkpointing Techniques](https://pytorch.org/blog/activation-checkpointing-techniques/)

## Axiom 5: Capture and Replay

CUDA Graphs eliminate kernel launch overhead.

### The Problem

Each kernel launch has CPU overhead. For small operations, launch overhead dominates compute.

### The Solution

Capture a sequence of operations into a graph, replay it with minimal overhead:

```text
-- Warmup (required)
for _ in Range(3):
    output = model(static_input)

-- Capture
graph = CudaGraph()
with graph.Capture():
    output = model(static_input)

-- Replay (fast)
for batch in dataloader:
    static_input.CopyFrom(batch)  -- update input in-place
    graph.Replay()
    -- output is updated in-place
```

### Performance Impact

- 2.3x speedup on LLaMA-7B inference
- 60% time savings on full training iteration
- 12% improvement on HuggingFace models via torch.compile

### Integration with torch.compile

CUDA graphs are used by default in torch.compile:

```text
model = Compile(model, mode="reduce-overhead")
-- Implicitly uses CUDA graphs
```

### Limitations

CUDA graphs require static:
- Input shapes
- Control flow
- Memory addresses

Dynamic shapes force re-recording, negating benefits.

Source: [Accelerating PyTorch with CUDA Graphs](https://pytorch.org/blog/accelerating-pytorch-with-cuda-graphs/)

## Axiom 6: Tensor Cores Want NHWC

Tensor cores operate in NHWC (channels last) format internally.

### The Conversion

```text
-- Convert model
model = model.To(memory_format=channels_last)

-- Convert input
input = input.To(memory_format=channels_last)
```

### Performance Impact

- 22%+ gains with AMP on GPU
- 1.25-1.5x CNN speedup

### Hardware Requirements

- GPU: Volta, Turing, Ampere, or newer
- CPU: Ice Lake or newer
- cuDNN >= 7.6

### Channel Thrashing

Unsupported ops convert back to NCHW, then back to NHWC:

```text
-- BAD: causes thrashing
input (NHWC) -> unsupported_op (converts to NCHW) -> conv (converts back to NHWC)
```

Known gaps:
- GroupNorm lacks NHWC CUDA kernel (as of Jan 2024)
- Some custom ops

Check operation support before enabling globally.

Source: [Channels Last Tutorial](https://docs.pytorch.org/tutorials/intermediate/memory_format_tutorial.html)

## Axiom 7: Overlap CPU and GPU

Data loading should never block training.

### DataLoader Configuration

```text
DataLoader(
    dataset,
    batch_size=32,
    num_workers=4 * num_gpus,  -- CPU cores for loading
    pin_memory=True,            -- enable async host->device
    prefetch_factor=2,          -- batches per worker to prefetch
    persistent_workers=True     -- keep workers across epochs
)
```

### num_workers Tuning

- `num_workers=0`: main process loads (bottleneck)
- `num_workers=4 * num_gpus`: good starting point
- Too high: RAM contention, diminishing returns

Each worker copies parent process memory.

### pin_memory

Pinned memory enables async GPU transfers:
- Enable: GPU training
- Disable: CPU-only training (wastes RAM)

### prefetch_factor

Controls queue depth per worker:
- Default: 2
- Higher: more memory, smoother throughput
- Profile to tune

### persistent_workers

Eliminates worker spawn overhead between epochs. Essential for fast epochs.

Source: [Performance Tuning Guide](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html)

## Axiom 8: Async or Die

CPU-GPU synchronization kills throughput.

### Hidden Sync Points

Operations that trigger synchronization:
- `tensor.item()`: converts GPU scalar to Python
- `tensor.tolist()`: converts GPU tensor to Python list
- `print(tensor)`: requires sync to format
- `if tensor.any()`: Python control flow on GPU data
- `torch.nonzero()`: output size depends on input values

### The Fix

```text
-- BAD: synchronizes
if loss.item() < threshold:
    break

-- GOOD: keep on GPU
if loss < threshold_tensor:
    break

-- BAD: creates on CPU then copies
x = Rand(size).Cuda()

-- GOOD: creates directly on GPU
x = Rand(size, device="cuda")
```

### Non-Blocking Transfers

```text
-- Synchronous (default)
tensor.To(device)

-- Asynchronous (requires pinned memory)
tensor.To(device, non_blocking=True)
```

Async transfers overlap with computation only when source is pinned.

### Detection

Profile with:
- `torch.profiler`
- NVIDIA Nsight Systems
- `torch.cuda.synchronize()` timing

High CPU time with low GPU time indicates sync bottlenecks.

Source: [Performance Anti-Patterns](https://towardsdatascience.com/pytorch-model-performance-analysis-and-optimization-part-3-1c5876d78fe2/)

## Axiom 9: Initialize for Your Activation

Wrong initialization causes vanishing or exploding gradients.

### The Rules

| Activation | Initialization | Variance |
| ---------- | -------------- | -------- |
| Tanh, Sigmoid | Xavier | 1/n_in |
| ReLU | Kaiming (fan_in) | 2/n_in |
| Leaky ReLU | Kaiming (adjusted) | 2/(1+a^2)/n_in |
| Linear (no activation) | Xavier | 1/n_in |

### Implementation

```text
-- ReLU networks
for layer in model.Modules():
    if IsLinear(layer) or IsConv(layer):
        KaimingNormal(layer.weight, mode="fan_in", nonlinearity="relu")
        if layer.bias is not None:
            ZeroInit(layer.bias)

-- Tanh/Sigmoid networks
for layer in model.Modules():
    if IsLinear(layer) or IsConv(layer):
        XavierUniform(layer.weight)
```

### Residual Networks

Standard initialization does not account for skip connections. Variance doubles at each residual block.

Solutions:
- Use BatchNorm (normalizes variance)
- Scale residual branch by 1/sqrt(num_layers)
- Use pre-norm architecture

### PyTorch Defaults

Linear layers use Kaiming uniform with a=sqrt(5). This is often suboptimal:
- 82% -> 86% accuracy improvement reported from switching to Xavier

Always explicitly initialize.

Source: [Weight Initialization Guide](https://lightning.ai/docs/pytorch/stable/notebooks/course_UvA-DL/03-initialization-and-optimization.html)

## Stability Practices

### Gradient Clipping

Prevents exploding gradients in RNNs and Transformers:

```text
optimizer.ZeroGrad()
Backward(loss)
ClipGradNorm(model.Parameters(), max_norm=1.0)
optimizer.Step()
```

Heuristic for max_norm: monitor gradient norm distribution, set threshold at 2-10x average.

### Learning Rate Warmup

Prevents early training instability:

```text
warmup_scheduler = LinearLR(optimizer, start_factor=0.1, total_iters=warmup_steps)
main_scheduler = CosineAnnealingLR(optimizer, T_max=total_steps)
scheduler = SequentialLR(optimizer, [warmup_scheduler, main_scheduler], milestones=[warmup_steps])
```

### Cosine Annealing

Smooth LR decay prevents oscillation around minima:

```text
scheduler = CosineAnnealingWarmRestarts(
    optimizer,
    T_0=restart_period,
    T_mult=2  -- double period after each restart
)
```

Source: [CosineAnnealingWarmRestarts](https://docs.pytorch.org/docs/stable/generated/torch.optim.lr_scheduler.CosineAnnealingWarmRestarts.html)

## Distributed Training

### DDP vs FSDP Decision

| Criterion | DDP | FSDP |
| --------- | --- | ---- |
| Model fits in GPU | yes | yes |
| Model exceeds GPU | no | yes |
| Memory efficiency | 1x | 2-4x |
| Communication | all-reduce | reduce-scatter + all-gather |
| Complexity | low | medium |

### FSDP Configuration

```text
-- Wrap each transformer layer
for layer in model.Layers():
    FullyShard(layer)

-- Wrap root model
FullyShard(model)

-- Mixed precision policy
policy = MixedPrecision(
    param_dtype=bfloat16,
    reduce_dtype=float32  -- preserve gradient accuracy
)
```

### Sharding Levels

Higher sharding = more memory savings, more communication:
- FULL_SHARD: shard params, grads, optimizer (maximum savings)
- SHARD_GRAD_OP: shard grads and optimizer only
- NO_SHARD: equivalent to DDP

Source: [FSDP Tutorial](https://docs.pytorch.org/tutorials/intermediate/FSDP_tutorial.html)

## Memory Management

### Inference Mode

```text
with NoGrad():  -- or InferenceMode() for stricter
    output = model(input)
```

`InferenceMode` is stricter and faster than `NoGrad`.

### Gradient Accumulation

Train with effective large batches on limited memory:

```text
accumulation_steps = 4
for i, batch in Enumerate(dataloader):
    loss = model(batch) / accumulation_steps
    Backward(loss)

    if (i + 1) % accumulation_steps == 0:
        optimizer.Step()
        optimizer.ZeroGrad()
```

### Memory Cleanup

```text
del tensor          -- remove reference
cuda.EmptyCache()   -- release cached memory (not allocated)
```

`EmptyCache` does not reduce allocated memory. Use for debugging, not optimization.

### Detach Tensors

Prevent computation graph retention:

```text
-- BAD: retains graph
history.Append(hidden_state)

-- GOOD: breaks graph
history.Append(hidden_state.Detach())
```

Source: [PyTorch Memory Optimization](https://mljourney.com/pytorch-memory-optimization-techniques-tools-and-best-practices/)

## Quantization

### Post-Training Quantization

```text
-- Dynamic quantization (easiest)
quantized_model = DynamicQuantize(
    model,
    {Linear},
    dtype=qint8
)

-- Static quantization (more accurate)
model.Eval()
model.QConfig = GetDefaultQConfig("x86")
Prepare(model, inplace=True)
-- Calibrate with representative data
for batch in calibration_data:
    model(batch)
FuseModules(model, inplace=True)
Convert(model, inplace=True)
```

### INT8 Performance

- Model size: 4x reduction
- Inference: 2-4x speedup
- X86 backend: 2.97x geomean speedup over FP32

### TorchAO (Latest)

```text
import torchao

-- INT4 weight-only quantization
model = torchao.QuantizeInt4(model)
-- 1.73x speedup, 65% less memory
```

Source: [INT8 Quantization](https://pytorch.org/blog/int8-quantization/), [TorchAO](https://github.com/pytorch/ao)

## Anti-Patterns

### Never Do

1. CPU-GPU ping-pong
   - Moving tensors repeatedly between devices
   - Keep tensors on GPU throughout forward/backward

2. Python loops over tensor elements
   - Use vectorized operations
   - Use einops for complex reshaping

3. Synchronous logging
   - `print(loss.item())` in training loop
   - Log asynchronously or sample logging

4. DataParallel
   - Always use DistributedDataParallel
   - DP synchronizes on every forward pass

5. Recreating tensors in loops
   - Pre-allocate buffers
   - Reuse tensor storage

6. Default initialization
   - Always explicitly initialize weights
   - Match initialization to activation function

7. Ignoring graph breaks
   - Profile with `fullgraph=True`
   - Refactor code causing breaks

### Always Do

1. Profile before optimizing
   - `torch.profiler` for GPU
   - Nsight Systems for full picture

2. Warmup before benchmarking
   - JIT compilation happens lazily
   - First iterations are not representative

3. Use deterministic algorithms when debugging
   - `torch.use_deterministic_algorithms(True)`
   - Disable for production (slower)

4. Enable cuDNN autotuner for static shapes
   - `torch.backends.cudnn.benchmark = True`
   - Disable for dynamic shapes

## Quick Reference

### Inference Speedup Checklist

```text
-- 1. Compile
model = Compile(model, mode="max-autotune")

-- 2. Mixed precision
model = model.To(bfloat16)

-- 3. Channels last (CNNs)
model = model.To(memory_format=channels_last)

-- 4. Inference mode
with InferenceMode():
    output = model(input)

-- 5. Quantize (if accuracy permits)
model = DynamicQuantize(model, {Linear}, dtype=qint8)
```

### Training Speedup Checklist

```text
-- 1. Compile
model = Compile(model, mode="reduce-overhead")
optimizer = Compile(optimizer)

-- 2. Mixed precision
scaler = GradScaler() if fp16 else None
with AutoCast(dtype=bfloat16):
    loss = model(batch)

-- 3. DataLoader
loader = DataLoader(
    dataset,
    num_workers=4*num_gpus,
    pin_memory=True,
    persistent_workers=True
)

-- 4. Gradient checkpointing (large models)
model.GradientCheckpointingEnable()

-- 5. cuDNN autotuner (static shapes)
backends.cudnn.benchmark = True

-- 6. Channels last (CNNs)
model = model.To(memory_format=channels_last)
```

## Sources

Core References:
- [torch.compile Tutorial](https://docs.pytorch.org/tutorials/intermediate/torch_compile_tutorial.html)
- [Performance Tuning Guide](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html)
- [SDPA Tutorial](https://docs.pytorch.org/tutorials/intermediate/scaled_dot_product_attention_tutorial.html)
- [AMP Recipe](https://docs.pytorch.org/tutorials/recipes/recipes/amp_recipe.html)
- [FSDP Tutorial](https://docs.pytorch.org/tutorials/intermediate/FSDP_tutorial.html)

Blog Posts:
- [PyTorch 2.0 Release](https://pytorch.org/blog/pytorch-2-0-release/)
- [Activation Checkpointing Techniques](https://pytorch.org/blog/activation-checkpointing-techniques/)
- [CUDA Graphs Acceleration](https://pytorch.org/blog/accelerating-pytorch-with-cuda-graphs/)
- [Mixed Precision Training](https://pytorch.org/blog/what-every-user-should-know-about-mixed-precision-training-in-pytorch/)
- [INT8 Quantization](https://pytorch.org/blog/int8-quantization/)

External:
- [NVIDIA Transformer Engine](https://github.com/NVIDIA/TransformerEngine)
- [TorchAO](https://github.com/pytorch/ao)
- [PyTorch Lightning Effective Training](https://lightning.ai/docs/pytorch/stable/advanced/training_tricks.html)

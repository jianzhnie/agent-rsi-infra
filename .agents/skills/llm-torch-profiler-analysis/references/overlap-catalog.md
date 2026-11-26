# Overlap 专题索引

案例事实、源码路径、开关、上游版本与历史 PR 状态统一维护在 [融合与重叠目录](fuse-overlap-catalog.md)。本文只帮助从 overlap 分析结果定位案例，不复制事实表。历史状态不是本次重新核验的结论，使用前核对目标 revision。

## 案例导航

| 专题 | 案例入口 |
| --- | --- |
| 1. LLM / SRT kernel-overlap families | [Single-batch overlap (SBO)](fuse-overlap-catalog.md#2-llm--srt-kernel-overlap-families) |
| 1. LLM / SRT kernel-overlap families | [Q and K normalization on different streams](fuse-overlap-catalog.md#2-llm--srt-kernel-overlap-families) |
| 1. LLM / SRT kernel-overlap families | [DeepSeek shared-expert / routed-expert overlap](fuse-overlap-catalog.md#2-llm--srt-kernel-overlap-families) |
| 1. LLM / SRT kernel-overlap families | [Llama4 shared branch vs routed branch overlap](fuse-overlap-catalog.md#2-llm--srt-kernel-overlap-families) |
| 1. LLM / SRT kernel-overlap families | [ExaoneMoE shared experts vs router experts overlap](fuse-overlap-catalog.md#2-llm--srt-kernel-overlap-families) |
| 1. LLM / SRT kernel-overlap families | [Grok residual-MoE branch overlap](fuse-overlap-catalog.md#2-llm--srt-kernel-overlap-families) |
| 1. LLM / SRT kernel-overlap families | [NSA dual-stream overlap](fuse-overlap-catalog.md#2-llm--srt-kernel-overlap-families) |
| 1. LLM / SRT kernel-overlap families | [MoriEP async dispatch / combine comm stream](fuse-overlap-catalog.md#2-llm--srt-kernel-overlap-families) |
| 1. LLM / SRT kernel-overlap families | [Generic `alt_stream` overlap families](fuse-overlap-catalog.md#2-llm--srt-kernel-overlap-families) |
| 2. Staging / communication kernel-overlap families | [Heterogeneous-TP staging scatter overlap](fuse-overlap-catalog.md#2-llm--srt-kernel-overlap-families) |
| 2. Staging / communication kernel-overlap families | [Staging-buffer fused gather / scatter](fuse-overlap-catalog.md#1-llm--srt-fused-kernel-families) |
| 3. VLM / diffusion kernel-overlap families | [Vision QK norm with aux stream](fuse-overlap-catalog.md#3-vlm-specific-kernel-families) |
| 3. VLM / diffusion kernel-overlap families | [ViT CUDA graph disables vision aux stream](fuse-overlap-catalog.md#3-vlm-specific-kernel-families) |
| 3. VLM / diffusion kernel-overlap families | [Ulysses sequence-parallel attention](fuse-overlap-catalog.md#5-diffusion-kernel-overlap-and-async-communication-families) |
| 3. VLM / diffusion kernel-overlap families | [USP attention with all-to-all and ring attention](fuse-overlap-catalog.md#5-diffusion-kernel-overlap-and-async-communication-families) |
| 3. VLM / diffusion kernel-overlap families | [Turbo-layer async all-to-all pipelining](fuse-overlap-catalog.md#5-diffusion-kernel-overlap-and-async-communication-families) |
| 3. VLM / diffusion kernel-overlap families | [TorchInductor compute / communication reorder](fuse-overlap-catalog.md#5-diffusion-kernel-overlap-and-async-communication-families) |
| 3. VLM / diffusion kernel-overlap families | [Dual-stream diffusion models](fuse-overlap-catalog.md#5-diffusion-kernel-overlap-and-async-communication-families) |
| 4. PR-backed / in-flight kernel-overlap families | [PR `#21877` fused down-GEMM + combine superseding SBO](fuse-overlap-catalog.md#7-pr-backed--in-flight-kernel-overlap-families) |
| 5. FlashInfer kernel-overlap families | [FlashInfer PDL launch-overlap family](fuse-overlap-catalog.md#9-flashinfer-mainline-kernel-overlap-families) |
| 5. FlashInfer kernel-overlap families | [FlashInfer CuTeDSL MoE aux-stream async-memset overlap](fuse-overlap-catalog.md#9-flashinfer-mainline-kernel-overlap-families) |
| 5. FlashInfer kernel-overlap families | [FlashInfer green-context SM partition overlap](fuse-overlap-catalog.md#9-flashinfer-mainline-kernel-overlap-families) |
| 6. FlashInfer PR-backed / in-flight kernel-overlap families | [PR `#2720` PDL runtime-API migration](fuse-overlap-catalog.md#10-flashinfer-pr-backed--in-flight-fused-kernel-and-kernel-overlap-families) |
| 7. TensorRT-LLM-origin kernel-overlap families | [TensorRT-LLM multi-stream MLA attention](fuse-overlap-catalog.md#12-tensorrt-llm-origin-kernel-overlap-families) |
| 7. TensorRT-LLM-origin kernel-overlap families | [TensorRT-LLM multi-stream MoE shared-vs-routed overlap](fuse-overlap-catalog.md#12-tensorrt-llm-origin-kernel-overlap-families) |
| 7. TensorRT-LLM-origin kernel-overlap families | [TensorRT-LLM multi-stream FP8 GEMM fork parallelism](fuse-overlap-catalog.md#12-tensorrt-llm-origin-kernel-overlap-families) |
| 8. TokenSpeed-origin kernel-overlap families | [TokenSpeed allreduce / communication fusion](fuse-overlap-catalog.md#tokenspeed-communication-overlap) |
| 9. vLLM-origin kernel-overlap families | [vLLM-origin AsyncTP GEMM + collective overlap](fuse-overlap-catalog.md#16-vllm-origin-kernel-overlap-families) |
| 9. vLLM-origin kernel-overlap families | [vLLM-origin Sequence Parallelism staging](fuse-overlap-catalog.md#16-vllm-origin-kernel-overlap-families) |
| 9. vLLM-origin kernel-overlap families | [vLLM-origin shared-expert aux-stream overlap](fuse-overlap-catalog.md#16-vllm-origin-kernel-overlap-families) |
| 9. vLLM-origin kernel-overlap families | [vLLM-origin DCP async all-to-all overlap](fuse-overlap-catalog.md#16-vllm-origin-kernel-overlap-families) |
| 10. vLLM-origin PR-backed / in-flight kernel-overlap families | [PR `#35968` DSV3.2 multi-stream indexer overlap](fuse-overlap-catalog.md#17-vllm-origin-pr-backed--in-flight-fused-kernel-and-kernel-overlap-families) |
| 10. vLLM-origin PR-backed / in-flight kernel-overlap families | [PR `#39301` GLM5 router GEMM with PDL overlap](fuse-overlap-catalog.md#17-vllm-origin-pr-backed--in-flight-fused-kernel-and-kernel-overlap-families) |

## 使用边界

先核对依赖、stream、事件同步和硬件支持，再判断能否重叠。已有案例不代表目标框架启用了对应路径；开放或关闭的 PR 也不等于 mainline 能力。缺少测量时只记录待验证假设。

开关与维护检索统一见 [条件与限制](fuse-overlap-catalog.md#18-important-toggles-and-caveats) 和 [刷新方法](fuse-overlap-catalog.md#19-suggested-refresh-commands)。

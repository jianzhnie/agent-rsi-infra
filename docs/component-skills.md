# 按任务读取 Skill

进入目标组件前，先读目标仓库指令，再按本次改动或诊断目的选择下表入口。只加载适用的技能和按需参考，不因组件名称相近而加载整组规则。读取 Skill 不授权启动任务、修改分支或执行对外操作。

| 任务 | 先读的 Skill | 适用边界 |
| --- | --- | --- |
| 训练、RL rollout、Serving 或多阶段模型行为变更 | [training-inference-change](../.agents/skills/training-inference-change/SKILL.md) | 只读取相关参考；框架契约在目标 checkout 核实 |
| SGLang Kernel API 新增、迁移、注册或去重 | [sglang-kernel-organization](../.agents/skills/sglang-kernel-organization/SKILL.md) | 命名空间与注册要求按目标 SGLang 版本核实 |
| FlashInfer CUDA Kernel 新增或集成 | [flashinfer-add-cuda-kernel](../.agents/skills/flashinfer-add-cuda-kernel/SKILL.md) | FFI、JIT、trace 与打包按目标版本核实 |
| Triton Kernel 实现、特化或预热 | [triton-kernel-writing](../.agents/skills/triton-kernel-writing/SKILL.md) | JIT 预热细节按需读取附属参考 |
| Kernel 性能比较或异常计时 | [kernel-microbenchmark](../.agents/skills/kernel-microbenchmark/SKILL.md) | 明确计时边界与缓存策略 |
| vLLM 模型前向微基准 | [vllm-model-microbenchmark](../.agents/skills/vllm-model-microbenchmark/SKILL.md) | 需对应版本与 CUDA 环境；不等同服务吞吐 |
| 已有 LLM profiler trace 诊断 | [llm-torch-profiler-analysis](../.agents/skills/llm-torch-profiler-analysis/SKILL.md) | 默认离线分析 |
| SGLang 多 rank 挂起或 collective 超时 | [sglang-distributed-hang-debugging](../.agents/skills/sglang-distributed-hang-debugging/SKILL.md) | 先区分状态分歧、进程退出与通信故障 |
| SGLang prefill/decode 或缓存 logprob 一致性 | [sglang-kl-consistency-test](../.agents/skills/sglang-kl-consistency-test/SKILL.md) | 不把 bit-exact 或历史阈值推广为通用门槛 |
| 清理死代码、重复实现或兼容层 | [sglang-code-cleanup](../.agents/skills/sglang-code-cleanup/SKILL.md) | 案例来自 SGLang，先核对目标契约 |

## 训练优化专项路由

以下 InfraRSI 迁入资源均为 experimental，先读各 Skill 的 UPSTREAM.md。它们提供方法，不提供上游 harness 或 GPU 执行授权；只选与当前问题相关的一项。

| 任务 | Skill | 关键边界 |
| --- | --- | --- |
| 硬件、拓扑、NUMA 或开关不生效 | [discover-training-system](../.agents/skills/discover-training-system/SKILL.md) | 从实际进程和执行证据确认 |
| 并行布局、微批次与累积 | [choose-parallel-layout](../.agents/skills/choose-parallel-layout/SKILL.md) | 公式和合法组合按目标框架 |
| 完整 update 计时与慢 rank | [profile-whole-update](../.agents/skills/profile-whole-update/SKILL.md) | 同 rank/step 归因，阶段最大值不相加 |
| OOM、延迟初始化与状态驻留 | [manage-memory-lifetimes](../.agents/skills/manage-memory-lifetimes/SKILL.md) | 第二步、恢复与 allocator 外内存 |
| 重计算范围与开销 | [recompute-policy](../.agents/skills/recompute-policy/SKILL.md) | 目标版本互斥关系与生命周期 |
| MoE 布局、dispatch/combine | [moe-ep-communication](../.agents/skills/moe-ep-communication/SKILL.md) | 路由语义、数值与通信成本 |
| 数据预取、传输和 offload | [optimize-data-path](../.agents/skills/optimize-data-path/SKILL.md) | 保持约定的数据契约并验证依赖 |
| 训练融合和 Kernel 替换 | [optimize-training-kernels](../.agents/skills/optimize-training-kernels/SKILL.md) | 复用现有 Kernel 实现与测量技能 |
| 性能优化的语义审查 | [verify-training-semantics](../.agents/skills/verify-training-semantics/SKILL.md) | 任务定义不变量与容差 |
| 保存、新进程恢复及导出 | [validate-training-lifecycle](../.agents/skills/validate-training-lifecycle/SKILL.md) | 支持导出时才验证导出路径 |
| 从优化任务提炼资源改进 | [improve-optimization-skills](../.agents/skills/improve-optimization-skills/SKILL.md) | 回归与人工审查，不自动写全局规则 |
| 结构化模型动作与预算协议 | [model-action-protocol](../.agents/skills/model-action-protocol/SKILL.md) | 协议参考，不引入执行引擎 |

PT2 编译器排障技能 `pytorch-compiler-debugging` 保持显式调用策略，不作为自动必读项。上游针对 speculative naming、冻结类、环境变量和 Rust processor 的专项规则尚未迁入；修改那些组件时读取目标仓库当前指令，不假设本仓库已提供对应技能。

## 来源

适配自 [modify-component-must-read.md](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/modify-component-must-read.md)，固定 commit `049bf85d931c9633d26094ae5ff9a7dbac6723b4`，许可见[已保留的 Apache-2.0 全文](../.agents/skills/sglang-kernel-organization/LICENSE)。本表按本仓库已提供的能力重新路由，不复制上游组件路径或宣称所有客户端自动加载。

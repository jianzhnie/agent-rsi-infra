# 按任务读取 Skill

进入目标组件前，先读目标仓库指令，再按本次改动或诊断目的选择下表入口。只加载适用的技能和按需参考，不因组件名称相近而加载整组规则。读取 Skill 不授权启动任务、修改分支或执行对外操作。

| 任务 | 先读的 Skill | 适用边界 |
| --- | --- | --- |
| 训练、RL rollout、Serving 或多阶段模型行为变更 | [training-inference-change](../.agents/skills/training-inference-change/SKILL.md) | 只读取相关参考；框架契约在目标 checkout 核实 |
| SGLang Kernel API 新增、迁移、注册或去重 | [kernel-organization](../.agents/skills/kernel-organization/SKILL.md) | 命名空间与注册要求按目标 SGLang 版本核实 |
| FlashInfer CUDA Kernel 新增或集成 | [flashinfer-add-cuda-kernel](../.agents/skills/flashinfer-add-cuda-kernel/SKILL.md) | FFI、JIT、trace 与打包按目标版本核实 |
| Triton Kernel 实现、特化或预热 | [triton-kernel-writing](../.agents/skills/triton-kernel-writing/SKILL.md) | JIT 预热细节按需读取附属参考 |
| Kernel 性能比较或异常计时 | [kernel-microbenchmark](../.agents/skills/kernel-microbenchmark/SKILL.md) | 明确计时边界与缓存策略 |
| vLLM 模型前向微基准 | [model-microbenchmark](../.agents/skills/model-microbenchmark/SKILL.md) | 需对应版本与 CUDA 环境；不等同服务吞吐 |
| 已有 LLM profiler trace 诊断 | [llm-torch-profiler-analysis](../.agents/skills/llm-torch-profiler-analysis/SKILL.md) | 默认离线分析 |
| SGLang 多 rank 挂起或 collective 超时 | [debug-distributed-hang](../.agents/skills/debug-distributed-hang/SKILL.md) | 先区分状态分歧、进程退出与通信故障 |
| SGLang prefill/decode 或缓存 logprob 一致性 | [kl-consistency-test](../.agents/skills/kl-consistency-test/SKILL.md) | 不把 bit-exact 或历史阈值推广为通用门槛 |
| 清理死代码、重复实现或兼容层 | [code-cleanup](../.agents/skills/code-cleanup/SKILL.md) | 案例来自 SGLang，先核对目标契约 |
| 证明文件拆分、移动或重命名是机械变换 | [mechanical-refactor-verify](../.agents/skills/mechanical-refactor-verify/SKILL.md) | 先审查脚本与 hooks；仍需行为验证 |

PT2 编译器排障技能 `pt2-bug-basher` 保持显式调用策略，不作为自动必读项。上游针对 speculative naming、冻结类、环境变量和 Rust processor 的专项规则尚未迁入；修改那些组件时读取目标仓库当前指令，不假设本仓库已提供对应技能。

## 来源

适配自 [modify-component-must-read.md](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/modify-component-must-read.md)，固定 commit `049bf85d931c9633d26094ae5ff9a7dbac6723b4`，许可见[已保留的 Apache-2.0 全文](../.agents/skills/kernel-organization/LICENSE)。本表按本仓库已提供的能力重新路由，不复制上游组件路径或宣称所有客户端自动加载。

# Agent 资源索引

这里集中索引角色、共享 Skills 与 Claude 适配资源。共享指令见根目录 `AGENTS.md`。角色源文件位于 `roles/`，采用通用 Markdown 与元数据；Skills 位于 `skills/`。

`roles/` 定义角色职责；`skills/` 定义可复用任务流程，并保留客户端约定的技能发现路径。客户端专用角色目录仍使用 `.claude/agents/` 和 `.codex/agents/`。

## 资源索引

路径相对本文件。角色与 Skill 的作者、版本、许可保留在各自 Frontmatter 中；未独立署名的脚本不推断具体作者，按仓库 Apache-2.0 许可维护。

| 名称 | 文件 | 用途 |
| --- | --- | --- |
| code-reviewer | [共享 Skill](skills/code-reviewer/SKILL.md) | 默认 light、按需 strict，只读报告有证据的问题 |
| debugger | [角色](roles/debugger.md) | 复现、定位和修复问题 |
| performance-analyzer | [角色](roles/performance-analyzer.md) | 根据性能测量分析瓶颈 |
| install-skill-from-github | [共享 Skill](skills/install-skill-from-github/SKILL.md) | GitHub Skill 迁入、许可与来源记录 |
| shell-check | [共享 Skill](skills/shell-check/SKILL.md) | 可执行 Shell 检查与结果汇总 |
| pt2-bug-basher | [上游适配 Skill](skills/pt2-bug-basher/SKILL.md) | 显式调用的 PyTorch 2 编译器排障流程 |
| add-or-fix-type-checking | [上游 Skill](skills/add-or-fix-type-checking/SKILL.md) | Transformers 类型检查流程，保留上游原文 |
| kernel-microbenchmark | [上游适配 Skill](skills/kernel-microbenchmark/SKILL.md) | GPU Kernel 正确性、计时与多卡基准 |
| triton-kernel-writing | [上游适配 Skill](skills/triton-kernel-writing/SKILL.md) | Triton 索引、特化、同步与调优 |
| model-recipes | [上游适配 Skill](skills/model-recipes/SKILL.md) | 按模型与硬件查询 vLLM 部署配置 |
| model-microbenchmark | [上游适配 Skill](skills/model-microbenchmark/SKILL.md) | 使用 vllm bench forward 测量模型前向 |
| debug-distributed-hang | [上游适配 Skill](skills/debug-distributed-hang/SKILL.md) | SGLang 多卡挂起、rank 分歧与通信诊断 |
| llm-torch-profiler-analysis | [上游适配 Skill](skills/llm-torch-profiler-analysis/SKILL.md) | 离线 LLM trace 分析与融合、重叠线索 |
| code-cleanup | [上游适配 Skill](skills/code-cleanup/SKILL.md) | 有证据的代码清理与兼容边界检查 |
| kernel-organization | [上游适配 Skill](skills/kernel-organization/SKILL.md) | SGLang Kernel 契约、归属与去重 |
| kl-consistency-test | [上游适配 Skill](skills/kl-consistency-test/SKILL.md) | SGLang prefill/decode 与缓存状态一致性 |
| flashinfer-add-cuda-kernel | [上游适配 Skill](skills/flashinfer-add-cuda-kernel/SKILL.md) | FlashInfer CUDA、FFI、JIT 与 trace 集成 |
| training-inference-change | [共享 Skill](skills/training-inference-change/SKILL.md) | 训练、RL 与推理变更的契约和分层验证 |
| choose-parallel-layout | [上游适配 Skill](skills/choose-parallel-layout/SKILL.md) | 选择并行布局、微批次与梯度累积 |
| discover-training-system | [上游适配 Skill](skills/discover-training-system/SKILL.md) | 核对训练硬件、拓扑、有效环境及执行路径 |
| learn-optimization-skills | [上游适配 Skill](skills/learn-optimization-skills/SKILL.md) | 从可复现任务中提炼候选，经回归与人工评审采用 |
| manage-memory-lifetimes | [上游适配 Skill](skills/manage-memory-lifetimes/SKILL.md) | 诊断训练 OOM、延迟初始化与恢复内存 |
| moe-ep-communication | [上游适配 Skill](skills/moe-ep-communication/SKILL.md) | 诊断与优化 MoE 专家布局和通信 |
| optimize-data-path | [上游适配 Skill](skills/optimize-data-path/SKILL.md) | 优化保持既定数据契约的预取与传输 |
| optimize-training-kernels | [上游适配 Skill](skills/optimize-training-kernels/SKILL.md) | 评估训练融合与 Kernel 替换 |
| profile-whole-update | [上游适配 Skill](skills/profile-whole-update/SKILL.md) | 分析训练完整 update 耗时和收益 |
| recompute-policy | [上游适配 Skill](skills/recompute-policy/SKILL.md) | 评估激活重计算的内存时间权衡 |
| validate-training-lifecycle | [上游适配 Skill](skills/validate-training-lifecycle/SKILL.md) | 验证训练保存、恢复与适用的导出路径 |
| verify-training-semantics | [上游适配 Skill](skills/verify-training-semantics/SKILL.md) | 审查训练优化是否保持约定语义 |
| weak-model-protocol | [上游适配 Skill](skills/weak-model-protocol/SKILL.md) | 实验性动作协议参考；本仓不提供执行器 |
| context | [脚本](../.claude/hooks/session/context.sh) | 初始化会话，compact/resume 时保留已有记录 |
| record-event | [脚本](../.claude/hooks/logging/record-event.sh) | 命令、Agent、配置及异常日志 |
| guard-tool | [脚本](../.claude/hooks/tools/guard-tool.sh) | 工具调用前的补充拦截 |
| format-file | [脚本](../.claude/hooks/tools/format-file.sh) | 编辑后的 pre-commit 与 Shell 检查 |
| notify | [脚本](../.claude/hooks/notifications/notify.sh) | 可选桌面、语音与 Server酱通知 |
| summarize | [脚本](../.claude/hooks/session/summarize.sh) | 可选会话摘要通知 |
| status-line | [脚本](../.claude/scripts/status-line.sh) | 上下文用量、模型与 Git 状态 |
| settings | [设置示例](../.claude/settings.example.json) | 可选 Hook 事件绑定与状态栏 |

Claude 角色适配生成到 `.claude/agents/`，Codex 角色配置生成到 `.codex/agents/`；Skills 仍通过 `.claude/skills -> ../.agents/skills` 共享。角色修改后运行 `python3 scripts/sync_agents.py`，禁止手工修改生成文件。工程与提交约定由根 `CLAUDE.md` 导入 `AGENTS.md`。

`code-reviewer` 与两档清单统一维护在 `.agents/skills/code-reviewer/`，通过 `skills` 链接供 Claude 使用；不再维护重复 Agent。

## 维护状态与验证边界

`active` 表示当前维护并接受缺陷反馈；`experimental` 表示适用边界仍在试用；`deprecated` 必须注明替代入口与退出计划。状态不代表任务成功率或真实客户端兼容性。目前未标记弃用资源，领域 Skills 按 experimental 管理，待真实任务报告支持后逐项调整。

目标客户端为 Claude Code、Codex，以及待核实发现机制的 Gemini；精确版本与逐能力状态统一维护在[兼容矩阵](../docs/agent-compatibility.md)，此处不重复版本事实。下表资源的真实客户端版本和最近真实任务验证日期均未记录；静态检查日期见兼容矩阵，不能代替任务执行日期。

上游 URL、revision 和本地适配以各资源的来源说明为准，不在表内复制 commit。存在来源说明不表示已验证上游当前版本；更新时同时复核许可和适配边界。

| Skill | 维护状态 | 来源 / revision / 本地适配记录 | 任务资源需求（依目标任务确认） |
| --- | --- | --- | --- |
| add-or-fix-type-checking | experimental | [来源与适配](skills/add-or-fix-type-checking/UPSTREAM.md) | 目标 Transformers 及类型检查依赖 |
| code-cleanup | experimental | [来源与适配](skills/code-cleanup/UPSTREAM.md) | 目标源码与测试环境；设备依受影响路径 |
| code-reviewer | active | [来源与适配](skills/code-reviewer/references/UPSTREAM.md) | 代码与 diff；通常不需 GPU |
| debug-distributed-hang | experimental | [来源与适配](skills/debug-distributed-hang/UPSTREAM.md) | 多 rank 日志；复现需目标多卡/通信环境 |
| flashinfer-add-cuda-kernel | experimental | [来源与适配](skills/flashinfer-add-cuda-kernel/UPSTREAM.md) | CUDA 工具链、目标 FlashInfer 和 GPU |
| install-skill-from-github | active | [来源与适配](skills/install-skill-from-github/UPSTREAM.md) | Git、GitHub 网络/按需凭证；无需执行下载代码 |
| kernel-microbenchmark | experimental | [来源与适配](skills/kernel-microbenchmark/UPSTREAM.md) | 目标 GPU、编译器与框架；不一定需要权重 |
| kernel-organization | experimental | [来源与适配](skills/kernel-organization/UPSTREAM.md) | 目标 SGLang；数值/性能验证需相应 GPU |
| kl-consistency-test | experimental | [来源与适配](skills/kl-consistency-test/UPSTREAM.md) | 目标 SGLang、模型权重和设备 |
| llm-torch-profiler-analysis | experimental | [来源与适配](skills/llm-torch-profiler-analysis/UPSTREAM.md) | 已有 trace 和分析依赖；离线分析不需 GPU |
| model-microbenchmark | experimental | [来源与适配](skills/model-microbenchmark/UPSTREAM.md) | CUDA、目标 vLLM、模型权重及足够显存 |
| model-recipes | experimental | [来源与适配](skills/model-recipes/UPSTREAM.md) | 查询需网络及脚本依赖；部署另需 GPU/权重 |
| pt2-bug-basher | experimental | [来源与适配](skills/pt2-bug-basher/UPSTREAM.md) | 目标 PyTorch 环境；复现可能需要 GPU |
| shell-check | active | 本仓维护，revision 与改动见 Git 历史 | Bash、ShellCheck；无需 GPU |
| training-inference-change | experimental | [来源与适配](skills/training-inference-change/UPSTREAM.md) | 目标训练/推理环境；按契约需要设备与权重 |
| triton-kernel-writing | experimental | [来源与适配](skills/triton-kernel-writing/UPSTREAM.md) | 目标 GPU、Triton 与 reference |
| choose-parallel-layout | experimental | [来源与适配](skills/choose-parallel-layout/UPSTREAM.md) | 目标训练环境、设备及按需模型/数据；本仓未验证 |
| discover-training-system | experimental | [来源与适配](skills/discover-training-system/UPSTREAM.md) | 目标训练环境、设备及按需模型/数据；本仓未验证 |
| learn-optimization-skills | experimental | [来源与适配](skills/learn-optimization-skills/UPSTREAM.md) | 日志/历史产物；真实结论需目标训练环境 |
| manage-memory-lifetimes | experimental | [来源与适配](skills/manage-memory-lifetimes/UPSTREAM.md) | 目标训练环境、设备及按需模型/数据；本仓未验证 |
| moe-ep-communication | experimental | [来源与适配](skills/moe-ep-communication/UPSTREAM.md) | 目标训练环境、设备及按需模型/数据；本仓未验证 |
| optimize-data-path | experimental | [来源与适配](skills/optimize-data-path/UPSTREAM.md) | 目标训练环境、设备及按需模型/数据；本仓未验证 |
| optimize-training-kernels | experimental | [来源与适配](skills/optimize-training-kernels/UPSTREAM.md) | 目标训练环境、设备及按需模型/数据；本仓未验证 |
| profile-whole-update | experimental | [来源与适配](skills/profile-whole-update/UPSTREAM.md) | 目标训练环境、设备及按需模型/数据；本仓未验证 |
| recompute-policy | experimental | [来源与适配](skills/recompute-policy/UPSTREAM.md) | 目标训练环境、设备及按需模型/数据；本仓未验证 |
| validate-training-lifecycle | experimental | [来源与适配](skills/validate-training-lifecycle/UPSTREAM.md) | 目标训练环境、设备及按需模型/数据；本仓未验证 |
| verify-training-semantics | experimental | [来源与适配](skills/verify-training-semantics/UPSTREAM.md) | 目标训练环境、设备及按需模型/数据；本仓未验证 |
| weak-model-protocol | experimental | [来源与适配](skills/weak-model-protocol/UPSTREAM.md) | 日志/历史产物；真实结论需目标训练环境 |

共享角色、Claude Hooks 与设置模板为 active；生成适配随源文件维护。角色执行、Hook 事件和通知的真实验证仍按兼容矩阵分别记录。通知可选依赖桌面命令或外部服务，不能由隔离测试推定已接通。

[使用样例](../docs/skill-examples.md)提供任务输入、反例与交付要求。维护进展以可复现失败、回归结果、真实任务证据和兼容性记录衡量，不以 Skill/角色数量、Prompt 长度或配置文件数衡量。

## 部署

参见 [部署说明](../docs/deployment.md)。`settings.example.json` 仅保留 Hooks 和状态栏，不预设模型、权限豁免、插件或外部工具授权；选择需要的事件再合并到目标设置。

- `hooks/notifications/common.sh` 随脚本部署，不单独注册为 Hook。
- 基础依赖为 Bash、Git、jq；格式检查使用 pre-commit 和 shellcheck。
- 通知密钥从目标项目 `.claude/.env` 的 `SCT_SENDKEY` 读取，不执行该文件内容。无密钥时不发送网络通知。
- 测试替换 curl、osascript 和 say，不发送真实通知。真实客户端加载与事件触发需另行确认。
- `guard-tool` 仅补充已定义的拦截，不是完整的 Shell 安全边界。

## 维护来源

本地脚本、状态栏和原始设置可追溯到仓库 Git 历史，如 `80faff2`、`a241329`、`1cf2354`、`65be515`、`f52ed88`。共享资源保留各自署名与许可；不因目录迁移改写来源。

## TorchTitan 补充资源

本次在已有 Skill 内补充，不新增发现入口：

| 所属 Skill | 新资源 | 来源与验证状态 |
| --- | --- | --- |
| triton-kernel-writing | [三方数值验证](skills/triton-kernel-writing/references/kernel-numerics.md) | [固定来源与许可](skills/triton-kernel-writing/references/torchtitan/UPSTREAM.md)；GPU 未测 |
| llm-torch-profiler-analysis | [CUDA Graph trace 整理](skills/llm-torch-profiler-analysis/references/cuda-graph-trace.md) | [固定来源与许可](skills/llm-torch-profiler-analysis/references/torchtitan/UPSTREAM.md)；合成 trace 回归，真实 trace/客户端未测 |
| training-inference-change | [离线数值比较](skills/training-inference-change/references/offline-numerics.md) | [固定来源与许可](skills/training-inference-change/references/torchtitan/UPSTREAM.md)；合成日志回归，真实模型/GPU 未测 |

编译优化方法见[性能诊断](../docs/performance-profiling.md#编译优化先测量再选择区域)，分布式与配置边界补充到训练参考，测试及 PR 方法补充到贡献指南。相关 Skill 保持 experimental，真实客户端版本与任务验证日期仍未记录。

## InfraRSI 训练优化资源

12 个训练优化 Skill 按固定版本迁入，来源与本地适配边界由各 Skill 的 UPSTREAM.md 维护。共享负结果目录已移除，不提供上游 harness 或训练执行服务；历史案例不作为本仓实测结果。

ATTUNE 测量参考已合入 profile-whole-update，来源及实验边界统一见 [UPSTREAM.md](skills/profile-whole-update/UPSTREAM.md)。

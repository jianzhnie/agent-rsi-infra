# 来源与适配

本 Skill 是依据本仓库两份调研归纳的原创工作流，不是任何上游 Skill 的原文快照：

- [训练框架调研](../../../docs/research/training-frameworks-agent-engineering.md)：9 个项目的 Agent 工作顺序、贡献治理、训练/RL/Kernel 验证。
- [推理框架调研](../../../docs/research/inference-frameworks-agent-engineering.md)：8 个项目的配置契约、硬件分层、模型接入和多阶段运行时。

项目名称、采用内容、实际文件与未迁入约束见下文。上游链接由报告保留；可变分支不伪装成固定 commit，报告未确认的配置不补写成上游事实。初始流程未复制上游代码，原创部分许可沿用本仓库 [Apache-2.0](../../../LICENSE)。已有迁入 Skill 保留各自来源与许可。

适配采用本仓库的共享源、按需参考和客户端分层；不复制其他项目的权限、提交、签名、fork、CI bot 或设备运行命令。本地验证不证明目标框架或硬件行为，真实任务应记录目标代码 revision 与实际结果。

后续适配：迁入 TorchTitan 离线数值比较脚本并补充训练/配置参考，固定来源、BSD 许可、本地修正与验证边界见 [TorchTitan 来源记录](references/torchtitan/UPSTREAM.md)。此工具不是原始原创流程的一部分。

后续提炼 slime 的配置/运行状态边界与自定义 Hook 兼容方法，固定来源、许可及范围见 [slime 来源记录](references/slime/UPSTREAM.md)。测试与 CI 方法补入根贡献指南，不新增同名 Skill。

## 调研方法的项目映射

以下仅记录已有调研中的采用方向，不是上游规范快照。未记录精确 revision 的项目继续以原调研的链接和核查范围为准，不补写版本或运行结论。

### 训练项目

| 项目 | 采用内容与落点 | 保留的边界 |
| --- | --- | --- |
| Megatron-LM | 根指令的材料→Skill→分析顺序；贡献文档的来源记录；[训练参考](references/training.md)的进程组、并行与恢复验证；严格审查已有 Core 专项规则 | draft、fork、签名、Testmon 及库/训练循环例外按目标规则，不变成本仓库全局政策 |
| verl | 工程标准与贡献流程的重复工作排查、人工责任、AI 参与和有效测试；[RL 参考](references/rl.md)的样本和权重版本检查 | 不复制禁止一切小修复的政策，不自动回复或发布 PR |
| DeepSpeed | 既有严格审查的设备接口、异步 buffer、collective 契约；训练参考补充 offload、状态与跨并行配置验证 | 不在其他框架禁止 torch.cuda/torch.distributed；不强制全硬件组合 |
| TorchTitan | 训练参考的实验/稳定核心边界、配置 recipe、数值与模型级验证 | 不照搬 experiments 目录或把实验成功当核心 API 已验收 |
| ms-swift | 训练参考的新模型注册、模板、文档与 smoke/unit 层级；[代码规范](../../../CONTRIBUTING.md#代码规范与依赖)补充命名、缩进、依赖选择及 lint/行为测试分离，记录固定来源 | 不新增重复 formatter 或复刻模型注册表；不迁入首次贡献 Issue、Fork 或算力政策 |
| slime | RL 参考的 training、rollout、data buffer 边界；[配置与状态归属](references/training.md#配置与运行状态)、Hook 兼容及严格审查；[CI 接入](../../../CONTRIBUTING.md#测试接入-ci)；[固定来源](references/slime/UPSTREAM.md) | 不维护 Megatron fork 或大型 RL 抽象，不复制专用 GPU 常量、workflow 路径与 README 编辑限制 |
| vime | RL 参考的 backend 隔离、generation/reward/environment、GPU/NPU 影响与日志约定 | 不复制硬件分支、签名或 PR 标签政策 |
| Unsloth | 训练参考中 LoRA/量化、patch、logits/loss/梯度与显存风险，作为待核实验证方向 | 原报告缺少足够 Agent 配置证据，不声称已迁入上游指令或发布支持承诺 |
| Liger Kernel | 训练参考的 correctness、模型 convergence、独立 benchmark 三层；复用已有微基准 Skill | 模型验证按训练数值影响执行，不要求所有文档变化运行训练 |

### 推理项目

| 项目 | 采用内容与落点 | 保留的边界 |
| --- | --- | --- |
| vLLM | 既有模型 recipe、前向微基准、Kernel 与 Triton Skills；[推理参考](references/inference.md)补充请求到执行路径与负载证据 | 不混淆前向与端到端服务性能，不复制 Buildkite 或 bot 策略 |
| SGLang | 既有 Kernel 组织、KL、分布式挂起与离线 trace Skills；推理参考补充缓存与调度契约 | 专用架构、KL 阈值和硬件开关按目标版本；不从离线诊断切换在线 |
| LMDeploy | 推理参考的多语言门禁与正确性/重型自动化/benchmark 分离 | 按目标配置运行版权、文档和 C++ 检查，不额外引入同类工具 |
| TensorRT-LLM | 推理参考的配置生成契约、API snapshot、Attention/MoE/KV 生命周期 | 不复制 NVIDIA 版权头、DCO、owner 审批、参数 manifest 命令到本仓库 |
| MAX / Modular | 推理参考的模型 pipeline、serving、语言专用工具边界；共享 Skills 与客户端薄适配沿用本仓库架构 | 不默认安装官方 Skills、插件或 Mojo 工具链；不冒称已具备其模型导入能力 |
| DeepInfer | 推理参考的 CPU/GPU/NPU 分层、平台 marker 与重型验证独立；统一检查保留 check/fix 分离 | 不把目标项目 ci/ci_npu marker 加入本仓库，CPU import 不替代设备结果 |
| vLLM-Omni | 工作流的需求依据、最窄参考与未验证项；推理参考的 stage/model/processor/recipe 接入与性能证据 | 已明确需求不重复要求许可；缺少产品语义才澄清，不自动对外发 PR |
| SGLang-Omni | 推理参考的多阶段职责、relay、取消、失败传播、流式与资源清理 | 模型 forward 通过不代表整条流水线正确；真实模型/设备支持需单独验证 |

## 跨资源适配记录

- TorchTitan 固定版本和数值工具分别记录在 [训练诊断](references/torchtitan/UPSTREAM.md)、[Kernel 数值参考](../triton-kernel-writing/references/torchtitan/UPSTREAM.md)和 [CUDA Graph trace](../llm-torch-profiler-analysis/references/torchtitan/UPSTREAM.md) 的来源文件。编译区域选择、重编译预算和 launch/graph replay 对照整理到 [性能诊断](../../../docs/performance-profiling.md#编译优化先测量再选择区域)；未迁入 fake 后端、torch_bisect、模型迁移清单或内部工具设置。
- SGLang-Omni 的审查和评测结果管理只作方法提炼；固定 revision、许可和未采用政策见 [来源记录](../code-reviewer/references/sglang-omni/UPSTREAM.md)，不迁入评测 runner、私有配置或自动提交动作。
- 协作方法归纳为 [Agent 协作契约](../../../docs/agent-collaboration.md)，角色正文维护于共享源，客户端适配由生成器产生；不复制其他项目的工具权限或默认委派策略。

以上映射不证明目标框架、真实客户端、GPU/NPU、多节点或模型行为已验证。

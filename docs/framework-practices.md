# 训练与推理工程实践迁移

依据 [RSI 设计](RSI_DESIGN.md)，从[训练框架调研](research/training-frameworks-agent-engineering.md)和[推理框架调研](research/inference-frameworks-agent-engineering.md)选择可复用方法。本次迁移知识与执行流程，不安装目标框架，不创建提交，不触发 CI、远程运行或 PR。

两份调研是本次知识输入，不等于上游当前版本规范。以下条目为本仓库的适配选择；源码路径、CLI、版本、支持矩阵与组织政策在真实任务中按目标 checkout 核对。已存在的专项技能继续维护，不复制第二套正文。

## 训练项目

| 项目 | 采用内容与落点 | 保留的边界 |
| --- | --- | --- |
| Megatron-LM | 根指令的材料→Skill→分析顺序；贡献文档的来源记录；[训练参考](../.agents/skills/training-inference-change/references/training.md)的进程组、并行与恢复验证；严格审查已有 Core 专项规则 | draft、fork、签名、Testmon 及库/训练循环例外按目标规则，不变成本仓库全局政策 |
| verl | 工程标准与贡献流程的重复工作排查、人工责任、AI 参与和有效测试；[RL 参考](../.agents/skills/training-inference-change/references/rl.md)的样本和权重版本检查 | 不复制禁止一切小修复的政策，不自动回复或发布 PR |
| DeepSpeed | 既有严格审查的设备接口、异步 buffer、collective 契约；训练参考补充 offload、状态与跨并行配置验证 | 不在其他框架禁止 torch.cuda/torch.distributed；不强制全硬件组合 |
| TorchTitan | 训练参考的实验/稳定核心边界、配置 recipe、数值与模型级验证 | 不照搬 experiments 目录或把实验成功当核心 API 已验收 |
| ms-swift | 训练参考的新模型注册、模板、文档与 smoke/unit 层级；格式复用已有工具 | 不新增重复 formatter 或复刻目标项目模型注册表 |
| slime | RL 参考的 training、rollout、data buffer 和扩展接口边界；可复现优化与维护成本 | 不为本仓库维护 Megatron fork 或大型通用 RL 抽象 |
| vime | RL 参考的 backend 隔离、generation/reward/environment、GPU/NPU 影响与日志约定 | 不复制硬件分支、签名或 PR 标签政策 |
| Unsloth | 训练参考中 LoRA/量化、patch、logits/loss/梯度与显存风险，作为待核实验证方向 | 原报告缺少足够 Agent 配置证据，不声称已迁入上游指令或发布支持承诺 |
| Liger Kernel | 训练参考的 correctness、模型 convergence、独立 benchmark 三层；复用已有微基准 Skill | 模型验证按训练数值影响执行，不要求所有文档变化运行训练 |

## 推理项目

| 项目 | 采用内容与落点 | 保留的边界 |
| --- | --- | --- |
| vLLM | 既有模型 recipe、前向微基准、Kernel 与 Triton Skills；[推理参考](../.agents/skills/training-inference-change/references/inference.md)补充请求到执行路径与负载证据 | 不混淆前向与端到端服务性能，不复制 Buildkite 或 bot 策略 |
| SGLang | 既有 Kernel 组织、KL、分布式挂起与离线 trace Skills；推理参考补充缓存与调度契约 | 专用架构、KL 阈值和硬件开关按目标版本；不从离线诊断切换在线 |
| LMDeploy | 推理参考的多语言门禁与正确性/重型自动化/benchmark 分离 | 按目标配置运行版权、文档和 C++ 检查，不额外引入同类工具 |
| TensorRT-LLM | 推理参考的配置生成契约、API snapshot、Attention/MoE/KV 生命周期 | 不复制 NVIDIA 版权头、DCO、owner 审批、参数 manifest 命令到本仓库 |
| MAX / Modular | 推理参考的模型 pipeline、serving、语言专用工具边界；共享 Skills 与客户端薄适配沿用本仓库架构 | 不默认安装官方 Skills、插件或 Mojo 工具链；不冒称已具备其模型导入能力 |
| DeepInfer | 推理参考的 CPU/GPU/NPU 分层、平台 marker 与重型验证独立；统一检查保留 check/fix 分离 | 不把目标项目 ci/ci_npu marker 加入本仓库，CPU import 不替代设备结果 |
| vLLM-Omni | 工作流的需求依据、最窄参考与未验证项；推理参考的 stage/model/processor/recipe 接入与性能证据 | 已明确需求不重复要求许可；缺少产品语义才澄清，不自动对外发 PR |
| SGLang-Omni | 推理参考的多阶段职责、relay、取消、失败传播、流式与资源清理 | 模型 forward 通过不代表整条流水线正确；真实模型/设备支持需单独验证 |

## Agent 设计落点

[协作契约](agent-collaboration.md)定义主流程职责、交接输入、角色返回结果和升级条件，已接入共享 debugger 与 performance-analyzer，并通过生成器同步 Claude/Codex 适配。训练与推理专项知识按 Skill 参考加载，未复制上游 Agent 工具权限或默认多 Agent 调度。

## 使用入口与维护

在目标项目进行行为变更时使用 [training-inference-change](../.agents/skills/training-inference-change/SKILL.md)，按任务只读取相关参考。普通文档维护不加载整个领域流程；只读 review 保持现有 `code-reviewer` 的操作边界。具体数值、性能与硬件方法仍由[领域指南](ai_infra_agent.md#validation)及专项 Skill 承接。

此次不新增空 Agent 角色：训练与推理任务先由现有共享角色和上述工作流承接，出现明确、重复的分工需求后再扩展。`.codex/` 与 `.claude/` 仍是专用适配，角色正文只在 `.agents/agents/` 维护。

本次验证范围是文件结构、引用、技能发现、生成一致性与仓库测试；未运行目标框架、训练、模型评测、GPU/NPU 或多节点实验。迁移条目不等于设备能力已验证。

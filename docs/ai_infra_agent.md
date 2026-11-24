# AI Infra 项目中的 Coding Agent 工程实践

本文整理训练、推理和 Kernel 项目的公开工程规范，供团队设计仓库指令、开发流程和验证要求时参考。

资料复核日期：2026-11-24。本文抽查了关键项目的上游文件，未运行框架测试或复现性能结果。引用主要指向可变分支；正式采用某条规则前，应在目标 commit 上确认。项目实践与本文建议分别说明，不按“成熟度”给项目排名。

## 目录

- [1. 主要结论](#overview)
- [2. 训练与 RL 框架](#training)
- [3. 推理与多模态框架](#inference)
- [4. Kernel 与编译器](#kernels)
- [5. Kernel Agent](#kernel-agents)
- [6. 仓库指令与工具配置](#configuration)
- [7. 验证要求](#validation)
- [8. 实施顺序](#adoption)
- [9. 参考资料与复核范围](#references)

<a id="overview"></a>

## 1. 主要结论

AI Infra 开发需要同时处理代码质量、数值结果、分布式状态和硬件性能。Agent 的工作要求应覆盖这四类问题。

- **规则有共同来源。** 将通用约束放在 `AGENTS.md`，各工具入口复用；模块差异放在局部规则中，操作流程放在 Skills 中。
- **验证随改动选择。** 训练关注 loss、梯度、checkpoint 和恢复；推理关注模型质量、缓存、调度和服务行为；Kernel 关注数值契约、硬件支持和性能。
- **性能结论可以复现。** 记录代码版本、设备、软件、输入、测量方法和原始结果，同时报告回退与波动。
- **自动检查承接明确规则。** 格式、静态检查、兼容性和回归测试交给 pre-commit 或 CI。Hooks 可补充本地检查，但不能代替 CI。
- **提交者对结果负责。** 遵守目标仓库的 AI 披露、人工审查和贡献政策。签名、PR 格式等要求按项目执行。

阅读项目规范时，优先看四类入口：仓库指令、贡献指南、相关模块文档、实际 CI 与测试配置。仅发现一个 Skills 目录，不足以确认其中流程已被执行或验证。

<a id="training"></a>

## 2. 训练与 RL 框架

### 2.1 项目概览

| 项目 | 主要规范入口 | 关注点 |
| --- | --- | --- |
| [PyTorch](https://github.com/pytorch/pytorch) | 仓库指令、贡献与 AI 政策 | Python/C++/CUDA 分层、设备与构建矩阵、贡献责任 |
| [Transformers](https://github.com/huggingface/transformers) / [TRL](https://github.com/huggingface/trl) | 共享指令、贡献指南 | 模型开发、测试分层、不同 Agent 的规则复用 |
| [Megatron-LM](https://github.com/NVIDIA/Megatron-LM) | `AGENTS.md`、`skills/`、开发者贡献指南 | Skill 前置、进程组传递、PR 与代码来源 |
| [verl](https://github.com/verl-project/verl) | `AGENTS.md`、`CONTRIBUTING.md` | 重复工作检查、AI 披露、人工责任 |
| [DeepSpeed](https://github.com/deepspeedai/DeepSpeed) | 贡献指南、构建与测试文档 | ZeRO、Offload、通信、扩展编译与兼容性 |
| [TorchTitan](https://github.com/pytorch/torchtitan) | 贡献指南、实验与开发文档 | 实验与核心代码分层、并行和数值验证 |
| [ms-swift](https://github.com/modelscope/ms-swift) | 仓库指令、贡献指南 | 模型与数据接入、格式检查、smoke/unit tests |
| [slime](https://github.com/THUDM/slime) / [vime](https://github.com/vllm-project/vime) | 贡献指南、Skills 或扩展文档 | 训练与 rollout 边界、权重同步、性能复现 |
| [Unsloth](https://github.com/unslothai/unsloth) | 模型与训练说明；专项规范待补查 | LoRA、量化、模型适配与显存优化 |

表中“关注点”包含本文建议检查的方向，不代表各项目都将其写成强制规则。未充分复核 Agent 配置的项目，不据此推断其缺少相关规范。

### 2.2 Megatron-LM：任务流程与分布式边界

复核的 [`AGENTS.md`](https://github.com/NVIDIA/Megatron-LM/blob/main/AGENTS.md) 明确要求：先读取任务材料，再加载相关 Skill，之后分析或实现。`skills/` 承接测试、容器、依赖和 SLURM 等操作流程。

贡献规则还要求从个人 fork 创建 draft PR，按要求使用 DCO sign-off 与提交签名；复制外部代码时记录来源 URL、revision 和 license。`git commit -s` 添加 sign-off，`-S` 才是密码学签名，两者作用不同。

在 `megatron/core` 生产代码中，指南建议显式传入 `ProcessGroupCollection` 或进程组，避免新增对 `parallel_state` 全局进程组的直接读取。初始化、兼容层等有例外；这条指导不自动扩展到训练循环，也不是 CI 强制检查。

可借鉴之处：将分布式架构约束写清适用目录、替代方式和例外，便于实现与评审时判断。

### 2.3 verl：贡献范围与人工责任

复核的 [`AGENTS.md`](https://github.com/verl-project/verl/blob/main/AGENTS.md) 要求先检查重复 Issue/PR，避免低价值机械修改，不接受缺少人工理解和负责的纯 Agent PR；AI 辅助贡献需要披露并报告测试结果。

这些要求针对贡献流程。RL 行为是否正确，还需要检查 rollout、reward、训练数据和权重更新之间的关系，不能仅凭 PR 检查通过作出结论。

### 2.4 TorchTitan、slime 与 vime：控制模块边界

已有资料中有三种值得保留的做法：

- **TorchTitan** 区分研究实验与核心能力。实验进入核心前，应补齐接口、测试、数值和性能说明。
- **slime** 强调贡献的可验证性与维护成本。训练、rollout、数据流和扩展接口应分别定位，避免无明确收益的大规模重构。
- **vime** 基于 slime，默认使用 vLLM 与 router 承担 rollout。评审时应检查训练后端、生成后端及两者之间的数据与权重同步。

这里的 Agentic RL 指模型与工具或环境交互的训练任务，和“用 Coding Agent 修改训练框架”是两个概念。

### 2.5 训练改动应回答的问题

1. 改动影响模型、数据、优化器、并行策略，还是 rollout/reward？
2. 输入、mask、position、label、logprob 和 token 是否仍然对齐？
3. 哪些 rank 和通信组受影响？是否改变通信顺序或状态生命周期？
4. checkpoint 能否保存、加载和恢复？是否涉及版本转换或重新分片？
5. 需要比较哪些输出、loss、梯度或权重？容差依据是什么？

具体测试范围见[验证要求](#validation)。

<a id="inference"></a>

## 3. 推理与多模态框架

### 3.1 项目概览

| 项目 | 主要规范入口 | 可参考的做法 |
| --- | --- | --- |
| [vLLM](https://github.com/vllm-project/vllm) | `AGENTS.md`、Skills、领域指南 | 测试设计、模型评估、贡献治理 |
| [SGLang](https://github.com/sgl-project/sglang) | Kernel Skills、文档指令 | 计算契约、实现去重、测试归档 |
| [LMDeploy](https://github.com/InternLM/lmdeploy) | pre-commit、Skills、测试与 benchmark | Python/C++/CUDA 检查复用 |
| [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) | `AGENTS.md`、编码与子系统指南 | 配置快照、API 稳定性、生成文件管理 |
| [MAX](https://github.com/modular/modular) | 贡献指南、独立的 [Modular Skills](https://github.com/modular/skills) | MAX/Mojo 工作流集中维护与分发 |
| [DeepInfer](https://github.com/deepseek-ai/DeepInfer) | `CONTRIBUTING.md`、测试与评估目录 | GPU/NPU 标记、轻重测试分层 |
| [vLLM-Omni](https://github.com/vllm-project/vllm-omni) | 贡献指南、模型与测试 Skills | 需求依据、分阶段模型接入、性能证据 |
| [SGLang-Omni](https://github.com/sgl-project/sglang-omni) | 仓库指令、开发者参考 | Stage 协议、取消、流式与异常传播 |

LightLLM、llama.cpp 的专项 Agent 规范未纳入本次详细复核。

### 3.2 vLLM：先设计验证，再写测试

复核的 [`AGENTS.md`](https://github.com/vllm-project/vllm/blob/main/AGENTS.md) 要求先明确模块职责、输入输出、目标故障和最低成本的测试层级，再选择测试。它还规定使用仓库要求的 uv 环境，按贡献政策检查重复工作、披露 AI 使用，并在提交 PR 前运行相关检查流程。

对内部仓库可采用相同原则：复用现有 fixture，优先验证受影响行为；模型输出或服务行为发生变化时，增加相应评估。功能测试和性能 benchmark 分别报告，避免将一次单测通过写成性能或模型质量结论。

### 3.3 SGLang：先查已有 Kernel

复核的 [`kernel-organization` Skill](https://github.com/sgl-project/sglang/blob/main/.agents/skills/kernel-organization/SKILL.md) 按计算职责组织 Kernel，例如 attention、MoE、normalization、quantization 和 communication。

新增或优化实现前，先检查注册表、已有 Triton/PyTorch 实现、外部库封装及真实调用形状，再选择扩展、迁移、优化或替换。

这套做法减少了按模型复制 Kernel 的问题。保留多实现时，应说明架构、dtype、shape 或平台上的必要差异，并验证公共 API、后端选择、数值与性能。

### 3.4 TensorRT-LLM：配置变更也是接口变更

复核的 [`AGENTS.md`](https://github.com/NVIDIA/TensorRT-LLM/blob/main/AGENTS.md) 将编码指南、子系统文档与机器生成的配置契约关联起来：

- LLM args 或嵌套配置变化，需要更新 Golden Manifest。
- Serving YAML 的字段、别名、默认值、类型或约束变化，需要重新生成并检查 JSON Schema 快照，补充相关回归覆盖。
- 受保护 API 的签名变化由稳定性测试发现，并按项目要求接受审核。

可参考的原则是：修改配置时，同时检查代码、生成产物、兼容性测试和文档；生成文件通过指定脚本更新。

### 3.5 DeepInfer：区分硬件与验证成本

复核的 [`CONTRIBUTING.md`](https://github.com/deepseek-ai/DeepInfer/blob/main/CONTRIBUTING.md) 区分 pytest 核心测试与资源密集型独立推理示例，并使用 `ci`、`ci_npu` 标记对应硬件测试。

报告测试结果时，应写清实际设备及选中的测试范围。CPU 导入检查只能证明对应路径能导入，无法替代 GPU/NPU 执行验证。

### 3.6 Omni 框架：验证跨阶段行为

[vLLM-Omni 贡献指南](https://github.com/vllm-project/vllm-omni/blob/main/docs/contributing/README.md) 要求以 Issue、RFC 或设计文档确定预期行为，说明影响的模块契约，结合领域 Skill 与测试 Skill 完成验证，并报告未执行项。

SGLang-Omni 的开发者参考则按 Coordinator、Stage、Scheduler、ModelRunner 与通信模块划分职责。

多模态改动除模型 forward 外，还应检查：

- 各阶段输入输出的 shape、dtype、设备与协议。
- 流式顺序、时间戳、终止信号、背压和同步。
- 取消或异常发生后，任务能否停止、资源能否释放。
- 离线与在线路径、真实客户端和端到端输出。

音频和视频任务还需要首包延迟、实时率、流式间隔或同步误差等指标，不能直接套用文本生成的全部指标。

<a id="kernels"></a>

## 4. Kernel 与编译器

### 4.1 项目参考

| 项目 | 规范与实现入口 | 重点 |
| --- | --- | --- |
| [Liger Kernel](https://github.com/linkedin/Liger-Kernel) | [贡献文档](https://linkedin.github.io/Liger-Kernel/contributing/)、测试、收敛与 benchmark | 算子正确性、模型训练行为、速度与显存分开验证 |
| [FlashInfer](https://github.com/flashinfer-ai/flashinfer) | 仓库指令、测试与 benchmark | 真实输入形状、目标设备、优化前后性能 |
| [TileLang](https://github.com/tile-ai/tilelang) | 贡献指南、lint 配置、pytest | Python/C++ 分别检查，编译与运行结果验证 |
| [Triton](https://github.com/triton-lang/triton) | 贡献指南、编译器与后端模块 | IR、代码生成、解释器与硬件后端边界 |
| [Apache TVM](https://github.com/apache/tvm) | 仓库指令、代码与测试指南 | IR 变化、多 Target 测试、公共接口 |
| [CUTLASS](https://github.com/NVIDIA/cutlass) | 核心库、tools、examples 与 test | 模板库组织、硬件支持、构建与单元测试 |

这些项目涵盖不同抽象层：算子库、DSL、编译器和模板库不宜用同一套验收条件比较。表中入口承接已有调研，本次未逐项重新核验其全部配置。

### 4.2 先定义计算契约

Kernel 实现与评审至少需要明确：

| 内容 | 需要说明的问题 |
| --- | --- |
| 数学语义 | 参考实现、归约顺序、近似算法及允许误差 |
| 张量约束 | shape、dtype、stride、layout、对齐与动态范围 |
| 边界行为 | 空输入、非整齐尺寸、mask、NaN/Inf；按算子语义选择 |
| 执行条件 | 设备架构、工具链、并发、stream 与图捕获要求 |
| 集成方式 | 调度与选择逻辑、调用者、回退路径、训练时的梯度支持 |

### 4.3 分层验证

1. **编译与执行。** 目标工具链能够生成并运行实现；按风险检查越界、竞态与同步问题。
2. **数值正确性。** 在代表性输入和边界条件上与 reference 对比，说明容差。需要反向传播的算子同时验证梯度。
3. **模型集成。** 替换后检查端到端输出或训练行为。训练相关数值路径按影响补充多步 loss、梯度或权重对照。
4. **性能。** 在真实调用形状与相同环境下测量，记录收益、退化、显存以及编译开销。

多组随机输入通过，只能证明这些样本上的表现；涉及模型行为时，仍需模型级验证。

<a id="kernel-agents"></a>

## 5. Kernel Agent

### 5.1 项目类型与差异

| 项目 | 定位 | 公开资料中的主要机制 |
| --- | --- | --- |
| [CANNBot Skills](https://github.com/hicann/cannbot-skills) | CANN/昇腾开发的 Skills 与工作流 | 覆盖多种算子开发路径，以 Plugin、Agent、Skill 组织任务；默认分支为 `master` |
| [KernelAgent](https://github.com/meta-pytorch/KernelAgent) | PyTorch 到 Triton 的生成与优化系统 | 路径选择、子图提取、候选生成、执行验证、端到端组合与性能反馈 |
| [KDA](https://github.com/NVlabs/kda) | Coding Agent 驱动的 CUDA 研发工作流 | 项目指令、任务计划、实现、验证与性能迭代；README 定位为早期研究原型 |
| [Atrex Kernel Agent](https://github.com/alibaba/atrex-kernel-agent) | 可配置的 Kernel 优化与评测工作流 | 持续会话、精确 commit 的评测记录、源码策略检查与审计 |
| [ForgeKernel](https://github.com/OpenBMB/ForgeKernel) | 迭代式 Kernel 优化 Agent | 基于现有实现分解优化任务，以硬件实验积累可复用知识 |
| [KernelBench](https://github.com/ScalingIntelligence/KernelBench) | Kernel 生成评测框架与工具集 | 对候选进行正确性与性能评测，覆盖单算子、融合和模型任务 |

以上说明来自项目 README，不表示本文复现了其能力。KernelBench 可作为 Agent 的评测环境；其存在本身不提供完整的任务规划与优化流程。

### 5.2 Atrex 的版本差异

本次复核的 README 描述了轻量工作流：一个持续运行的 Coding Session 管理自身 Git 历史；提交候选需要该 commit 已有完整、正确性通过且性能结果可解析的评测记录，并接受选定的源码策略检查。

`submit-kernel` **不设置性能提升门槛，也不会自行重新评测、运行 ABBA、晋级或回退**。Supervisor 提供测量、检查和审计等能力，不强制将某条轨迹替换为另一条轨迹的代码。不能将旧版流程或本文建议的晋级策略写成当前项目行为。

### 5.3 建议的开发流程

以下是本文建议，需按任务成本和工具能力实现：

```text
固定 reference、输入与验收条件
  → 生成或修改候选
  → 编译与数值验证
  → 集成验证（如适用）
  → 性能测量与瓶颈分析
  → 决定保留、继续修改或回退
  → 保存代码版本、命令和原始结果
```

实施时需要控制三件事：

- **评测依据独立。** 候选实现不能自行修改 reference、隐藏测试失败或替换结果。
- **约束按任务定义。** 某些评测禁止 PyTorch fallback；生产实现则可能需要合法回退。是否允许调用现有计算库，应由目标任务约定。
- **结果绑定源码。** 任何性能或正确性记录都要对应确切的 commit 或内容哈希；后续修改后，旧结果不能直接沿用。

优化系统还应设置时间、迭代次数或资源预算，以及失败后的处理方式，避免无期限搜索。跨算子知识库只记录有实验条件和证据的结论，并注明适用硬件与范围。

<a id="configuration"></a>

## 6. 仓库指令与工具配置

### 6.1 各类文件的职责

| 类型 | 放置内容 | 使用原则 |
| --- | --- | --- |
| 仓库指令 | 项目结构、通用约束、常用命令、文档入口 | 短小，适用于多数任务 |
| 模块规则 | 局部接口、设备、生成文件或兼容要求 | 写清作用范围与例外 |
| Skill | 多步骤任务的输入、操作、验证和产物 | 按需加载，详细资料单独存放 |
| MCP | 外部工具与数据连接 | 按需配置访问权限 |
| Hook | 生命周期中的自动动作 | 处理明确、可检查的本地操作 |
| CI | 可重复执行的检查与合并条件 | 承接团队共同的质量要求 |

自然语言指令有助于指导行为。需要稳定执行的格式、构建与回归要求，应同时有可运行的检查。

### 6.2 工具入口

| 工具 | 常见仓库入口 | 共享规则方式 |
| --- | --- | --- |
| Claude Code | `CLAUDE.md`、`.claude/rules/`、`.claude/skills/` | 在入口导入共享指令，工具专用设置单独维护 |
| Codex | `AGENTS.md`、`.agents/skills/`、`.codex/config.toml` | 使用共享指令，运行与工具配置单独维护 |
| Cursor | `AGENTS.md`、`.cursor/rules/*.mdc` | 通用要求共享，需要路径条件时增加 Rules |
| GitHub Copilot | `.github/copilot-instructions.md`、路径指令等 | 按实际客户端支持适配共享内容 |

各工具的发现路径、继承、导入与权限机制不同。上表用于导航，采用前应对照[官方文档](#references)确认实际版本；共享文件不代表所有客户端都会自动读取或递归加载它。

### 6.3 推荐的最小目录

以下为建议布局，无需一次建立所有目录：

```text
repo/
├── AGENTS.md
├── CONTRIBUTING.md
├── CLAUDE.md                   # 导入共享指令，保留必要的工具差异
├── .agents/skills/
│   └── <task>/
│       ├── SKILL.md
│       ├── references/
│       └── scripts/
├── .claude/                    # 按需配置规则、Skills 适配与 Hooks
├── .cursor/rules/              # 按需添加路径规则
├── .codex/config.toml          # 按需添加项目配置
├── docs/developer/
│   ├── architecture.md
│   ├── testing.md
│   └── performance.md
├── tests/
└── benchmarks/
```

共享规范只维护一份。若工具不能直接加载，通过其支持的导入、链接或生成方式适配，并检查入口是否有效；不要依赖一句“请读取另一文件”就假定规则已加载。

根目录指令建议包含：项目与目录导航、环境与最短检查命令、变更范围、API/文档同步、测试报告要求，以及领域指南索引。权限与资源操作沿用团队现有政策。

### 6.4 Skill 的最小内容

| 项目 | 内容 |
| --- | --- |
| 适用条件 | 何时使用，何时不适用 |
| 输入 | 需求、相关代码、reference、设备与版本 |
| 步骤 | 查已有实现、说明契约、修改、验证、报告 |
| 验收 | 必需检查、可选检查及失败处理 |
| 产物 | 精确命令、代码版本、日志、结果与未执行项 |

优先编写经常重复、容易遗漏的流程，例如分布式调试、checkpoint 变更、模型接入、Kernel 开发、推理 benchmark 和 RL rollout 集成。

<a id="validation"></a>

## 7. 验证要求

本节是本文建议的检查清单。按变更影响选择适用项，并遵守目标项目的最低要求；不必为每次改动运行全部测试。

### 7.1 训练与 RL

| 变更 | 主要验证 | 按影响补充 |
| --- | --- | --- |
| 模型结构与注册 | 加载、forward、loss、参数与配置 | 多步训练、模型指标 |
| 数据与 packing | 样本、mask、position、label 对齐 | 分布统计与吞吐 |
| 并行策略与通信 | rank 映射、进程组、多卡行为 | 多节点、拓扑、超时与故障 |
| 优化器与训练状态 | 更新公式、状态保存恢复 | 多步数值与长跑稳定性 |
| Checkpoint | 保存、加载、断点恢复 | 版本兼容、重新分片、异常恢复 |
| RL rollout | token、logprob、终止与采样语义 | 多轮交互、权重同步、异步流程 |
| Reward/verifier | 输入输出、边界与异常 | 分布偏差、训练影响 |

### 7.2 推理与服务

| 变更 | 主要验证 | 按影响补充 |
| --- | --- | --- |
| 模型接入 | 权重映射、processor、forward、注册 | 精度、长上下文、在线服务 |
| KV Cache | 分配、回收、页表与状态生命周期 | Prefix Cache、并发、跨进程传输 |
| 调度器 | 队列、状态转换、抢占与批处理 | 混合请求、突发负载、公平性与尾延迟 |
| 量化 | 层级误差、输出与异常输入 | 模型质量、长上下文、性能 |
| 分布式推理 | 多 rank、通信顺序、错误传播 | 多节点、并行规模与故障恢复 |
| API 与配置 | 请求响应、Schema、默认值 | 旧配置与真实客户端兼容 |
| 多模态流水线 | 阶段协议、流式、取消与资源释放 | 音画同步、背压、端到端任务质量 |

### 7.3 Kernel 与编译器

| 变更 | 主要验证 | 按影响补充 |
| --- | --- | --- |
| CUDA/Triton 等 Kernel | 编译、reference 对照、shape/dtype/stride 边界 | 梯度、内存检查、多架构、性能 |
| Kernel 选择或迁移 | 调用覆盖、选择逻辑、支持范围 | 打包、旧路径清理、模型级结果 |
| Compiler IR/Pass | IR 与语义回归 | 多 Target、代码生成、执行结果 |
| 公共 C++/Python 接口 | 编译或导入、单元与接口测试 | ABI/API、依赖版本、生成文档 |

### 7.4 性能测量

性能报告至少记录以下信息：

| 类别 | 内容 |
| --- | --- |
| 版本 | baseline/candidate commit，模型及 revision |
| 环境 | 设备型号与数量、互连、驱动、运行时、框架与编译器 |
| 负载 | shape、dtype、batch、序列长度、并发、数据集与配置 |
| 方法 | warmup、重复次数、计时与同步方式、缓存条件、统计方法 |
| 结果 | 绝对耗时、吞吐、显存、波动，以及退化的测试项 |
| 产物 | 完整命令、原始日志、结果文件及对应源码 |

baseline 与候选使用相同设备、输入和配置；按任务说明是否计入编译、传输或预处理。GPU 异步执行需要正确计时；共享设备上的干扰也应记录。

指标按任务选择：

- **训练：** tokens/s、step time、峰值显存，并注明精度和并行配置。
- **文本推理：** TTFT（首 token 延迟）、TPOT（输出 token 间隔）、吞吐及延迟分位数，并说明各指标口径。
- **多模态：** 首包延迟、端到端延迟、流式间隔、实时率或同步误差。
- **Kernel：** 绝对延迟、显存或带宽等相关指标，以及覆盖的 shape。

单次最好成绩不足以说明稳定提升。没有完成测量的优化应写为假设或待验证结果。

### 7.5 PR 报告模板

```markdown
## 问题与改动
现象、预期行为、影响模块、主要设计选择。

## 兼容性
接口、配置、模型行为、硬件或版本的变化。

## 验证
- 代码版本与环境：
- 实际执行的命令及结果：
- 数值或性能结果（如适用）：
- 未执行项及原因：
- 日志与原始结果位置：

## AI 使用
按目标仓库政策说明工具、参与范围和人工审查情况。
```

<a id="adoption"></a>

## 8. 实施顺序

1. **整理现有入口。** 确认贡献指南、环境、测试与 CI 的实际状态，合并重复或冲突的指令。
2. **补齐验证清单。** 先覆盖最常见的模型、分布式、checkpoint 和 Kernel 变更，明确最低验证及报告方式。
3. **编写少量高频 Skills。** 从反复出现且容易遗漏的任务开始；流程有变化时同步更新脚本和文档。
4. **自动检查稳定规则。** 将格式、配置快照、数值和兼容回归接入 CI；性能测试单独安排资源与基线。
5. **按需要拆分 Agent 任务。** 需求分析、实现、性能测量和独立审查可分工，但应明确写入范围、共享产物和最终负责人。

先把单个任务的输入、验证和输出做清楚，再扩展工具或角色数量。

<a id="references"></a>

## 9. 参考资料与复核范围

### 9.1 本次直接复核的上游文件

| 领域 | 来源 |
| --- | --- |
| 训练规则 | [Megatron-LM AGENTS](https://github.com/NVIDIA/Megatron-LM/blob/main/AGENTS.md)、[verl AGENTS](https://github.com/verl-project/verl/blob/main/AGENTS.md) |
| 推理规则 | [vLLM AGENTS](https://github.com/vllm-project/vllm/blob/main/AGENTS.md)、[SGLang Kernel Skill](https://github.com/sgl-project/sglang/blob/main/.agents/skills/kernel-organization/SKILL.md)、[TensorRT-LLM AGENTS](https://github.com/NVIDIA/TensorRT-LLM/blob/main/AGENTS.md) |
| 测试与多模态 | [DeepInfer 贡献指南](https://github.com/deepseek-ai/DeepInfer/blob/main/CONTRIBUTING.md)、[vLLM-Omni 贡献指南](https://github.com/vllm-project/vllm-omni/blob/main/docs/contributing/README.md) |
| RL 框架 | [vime README](https://github.com/vllm-project/vime/blob/main/README.md) |
| Kernel 工作流 | [CANNBot README](https://github.com/hicann/cannbot-skills/blob/master/README.md)、[KernelAgent README](https://github.com/meta-pytorch/KernelAgent/blob/main/README.md)、[KDA README](https://github.com/NVlabs/kda/blob/main/README.md) |
| 优化与评测 | [Atrex README](https://github.com/alibaba/atrex-kernel-agent/blob/main/README.md)、[ForgeKernel README](https://github.com/OpenBMB/ForgeKernel/blob/main/README.md)、[KernelBench README](https://github.com/ScalingIntelligence/KernelBench/blob/main/README.md) |

其余项目保留已有资料中的工程方向与导航链接，未在本次逐条复核全部文件。公开文件的描述不等于功能已实测，主分支链接也不构成固定版本快照。

### 9.2 工具官方文档

以下用于核对配置与加载行为，本次未逐页复核：

- Claude Code：[项目指令](https://code.claude.com/docs/en/memory)、[Skills](https://code.claude.com/docs/en/skills)、[Hooks](https://code.claude.com/docs/en/hooks)、[设置](https://code.claude.com/docs/en/settings)。
- Codex：[AGENTS.md](https://developers.openai.com/codex/guides/agents-md)、[Skills](https://developers.openai.com/codex/skills)、[配置](https://developers.openai.com/codex/config-basic)。
- Cursor：[Rules](https://cursor.com/docs/rules)、[Skills](https://cursor.com/docs/skills)。
- GitHub Copilot：[自定义指令](https://docs.github.com/en/copilot/concepts/prompting-and-context/custom-instructions)、[配置参考](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)。

# 大模型训练框架与 AI Coding Agent 工程规范调研报告

> 调研范围：Megatron-LM、verl、DeepSpeed、TorchTitan、ms-swift、slime、vime、Unsloth、Liger Kernel；通用 Agent 规范及 Claude Code、OpenAI Codex、Cursor。
> 调研方式：检查公开 GitHub 仓库中的规范文件、贡献指南、项目结构/测试文档和官方 Agent 文档。
> 版本说明：链接指向仓库 `main` / `master` 当前文件，分支内容会变化；本报告是公开文件的静态检查，不等同于在目标 commit 上运行 CI 或验证所有脚本。

## 1. 执行摘要

### 1.1 关键结论

1. **训练框架的规范不能止于 Python style。** 大模型训练代码需要把正确性、可复现性、分布式行为、checkpoint 兼容、数值精度、性能回归和硬件矩阵纳入 PR 验证。
2. **Megatron-LM 的 Agent 工程化值得重点借鉴。** `AGENTS.md` 将 Skill 作为任务前置上下文，规定“先读取任务材料—选择并加载 Skill—再分析和实现”的顺序；同时明确 PR 草稿、fork 工作流、签名、代码来源和 Megatron Core 进程组传递约束。
3. **verl / vLLM 风格的 AI 贡献治理很严格。** 先排查重复 Issue/PR、拒绝低价值 busywork、要求人工逐行理解 AI 生成改动、报告测试与评测结果；Agent 规范还明确了环境、测试设计、lint 和领域指南。
4. **slime 与 vime 的规范体现 RL Infra 的工程特点。** 它们强调训练与 rollout 的模块边界、可验证的性能优化、可复现训练、GPU/NPU 影响以及不维护不必要的大型抽象。
5. **Liger Kernel 的质量门禁应按 Kernel 项目设计。** 除常规 lint 外，需要 correctness tests、模型级 convergence 对照和独立 benchmark；性能结果不能用未复现的单次数字代替。
6. **Agent 指令应该分层，而不是把所有内容堆进一个大文件。** `AGENTS.md` 放通用约束和命令；领域知识放专项指南；重复流程放 Skill；强制动作放 Hook/CI；工具访问放 MCP。
7. **建议采用一个规范源，多客户端适配。** 以 `AGENTS.md` 为通用规范源，Claude Code 通过 `CLAUDE.md` 引用它，Cursor 直接读取 `AGENTS.md` 或使用 `.cursor/rules/*.mdc`，Codex 读取 `AGENTS.md` 并可叠加 `.codex/config.toml`。

### 1.2 项目对比总表

| 项目 | 定位/关注重点 | 已检查的规范入口 | 规范成熟度（本次检查） | 可借鉴重点 |
|---|---|---|---|---|
| Megatron-LM | 大规模预训练、Megatron Core、并行策略 | `AGENTS.md`、`CLAUDE.md`、`CONTRIBUTING.md`、`skills/`、`docs/developer/contribute.md` | 高 | Skill 前置工作流、PR/签名/溯源、分布式架构约束 |
| verl | RLHF/RL 后训练、训练与 rollout 编排 | `AGENTS.md`、`CONTRIBUTING.md` | 高 | AI 贡献治理、重复 PR 检查、测试设计 |
| DeepSpeed | ZeRO、分布式训练、通信与内存优化 | `CONTRIBUTING.md`、README | 中 | 贡献流程、环境/构建/测试说明；本次未确认根目录 Agent 专属文件 |
| TorchTitan | PyTorch 原生训练平台、实验与核心能力 | `CONTRIBUTING.md`、README、`docs/`、`tests/` | 中 | 实验与核心代码分层、模型/并行/数值验证文档 |
| ms-swift | 多模型训练、微调、对齐与部署 | `AGENTS.md`、`CONTRIBUTING.md` | 中高 | 命名与格式约定、pre-commit、smoke/unit tests |
| slime | Megatron + SGLang 的 RL Scaling | `CONTRIBUTING.md`、`.agents/`、`.claude/skills/`、`.pre-commit-config.yaml` | 中高 | 协作范围清晰、性能优化证据、训练/rollout/data buffer 边界 |
| vime | vLLM + Megatron 后端的 RL post-training | `CONTRIBUTING.md`、`docs/en/get_started/agent.md` | 中高 | GPU/NPU 路径隔离、PR 分类、可验证性 |
| Unsloth | 高效微调与训练工具 | README；规范文件需进一步逐项核实 | 待补充 | 建议重点核查量化、LoRA、显存与数值一致性测试 |
| Liger Kernel | Triton LLM 训练 Kernel | 官方 Contributing 文档、README、测试/benchmark 目录 | 高（Kernel 维度） | Kernel correctness、convergence、benchmark 三层验证 |

> “成熟度”是对本次能定位到的公开工程规范覆盖度的定性判断，不是对项目整体质量或代码质量排名。对 Unsloth、DeepSpeed、TorchTitan 的 Agent 专属配置，本次未找到足够证据时不推断其不存在或存在。

---

## 2. 训练框架逐仓库调研

## 2.1 Megatron-LM

仓库：[NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM)

### 实际文件与内容

| 路径 | 规范/内容 | 适用意义 |
|---|---|---|
| [`AGENTS.md`](https://github.com/NVIDIA/Megatron-LM/blob/main/AGENTS.md) | 有专门的 Skills 章节；任务前必须读取相关 artifact，再选择并加载对应 `SKILL.md`，最后才开始推理/实现；不能跳过或调整顺序 | 把 Skill 变成研发流程的一部分，而不是可选提示词 |
| [`CLAUDE.md`](https://github.com/NVIDIA/Megatron-LM/blob/main/CLAUDE.md) | 仓库提供 Claude Code 指令入口；应与 `AGENTS.md` 配合检查 | 让 Claude Code 使用仓库规范 |
| [`skills/`](https://github.com/NVIDIA/Megatron-LM/tree/main/skills) | 覆盖测试、容器、依赖管理、SLURM 作业等任务型指南 | 把操作手册按场景拆分，按需加载 |
| [`docs/developer/contribute.md`](https://github.com/NVIDIA/Megatron-LM/blob/main/docs/developer/contribute.md) | 贡献政策、Issue 类型、PR 流程、提交约定和代码质量说明 | 规范贡献流程和评审预期 |
| [`CONTRIBUTING.md`](https://github.com/NVIDIA/Megatron-LM/blob/main/CONTRIBUTING.md) | 仓库贡献入口 | 贡献者入口与详细指南索引 |
| [`.pre-commit-config.yaml`](https://github.com/NVIDIA/Megatron-LM/blob/main/.pre-commit-config.yaml) | 机器可执行的静态检查配置 | 规范应由工具自动执行，而非只依赖 Agent 记忆 |

### 关键规范摘录（归纳）

**A. 强制 Skill 工作流**

`AGENTS.md` 定义的任务顺序：

1. 先读取任务相关材料：commit、PR、错误日志、代码文件等。
2. 根据任务类型选取并加载相关 Skill。
3. 完成上述步骤后，才开始分析、回答或修改代码。

示例（仓库要求的思想，命令按实际 Skill 路径调整）：

```text
任务：定位 Megatron Core checkpoint 恢复失败
1. 读取 issue / 日志 / checkpoint 代码和相关测试
2. 识别 checkpoint/debug 相关 skill
3. 阅读该 skill 的 SKILL.md
4. 再形成诊断结论和修改计划
5. 执行针对性测试并报告结果
```

**B. PR 与代码来源治理**

`AGENTS.md` 明确要求：

- PR 必须以 draft 形式创建。
- 不直接向 NVIDIA 主仓库推送分支，应推送个人 fork 再提 PR。
- rebase、cherry-pick 或 commit 时，按仓库要求同时使用 `-s` 与 `-S`（Signed-off-by 与签名）。
- 合并前检查依赖该 PR 的 stacked/dependent PR，避免合并后丢失依赖关系。
- 尽量避免复制其他仓库代码；如必须复制，在文件头标明来源 URL、revision、license，并在 PR 描述中填写 Code provenance。

**C. Megatron Core 领域架构约束**

在 `megatron/core` 生产代码中，避免新增直接从 `parallel_state` 读取全局 process group。优先由调用者传入 `ProcessGroupCollection` 或显式 `torch.distributed.ProcessGroup`。允许的兼容点包括 `parallel_state.py`、process group 配置、bootstrap 初始化、测试、文档和明确标注的迁移回退。

这类约束很重要：Agent 可能会为了快速实现而直接读取全局状态，但分布式库更需要依赖显式化、可组合和可测试。

### 评审建议

- 修改并行策略：必须说明 TP/PP/DP/EP/CP 维度、rank 映射、通信组及适用拓扑。
- 修改 checkpoint：必须验证保存、加载、恢复、跨并行度 reshard 和异常中断场景。
- 修改训练数值路径：至少比较 loss/grad/权重或关键中间量，说明精度和误差容限。
- 修改性能路径：给出基准环境、GPU 型号、规模、配置、warmup、测量次数和基线。
- 新增 Skill：写清触发条件、输入材料、执行步骤、验证命令和产物。

---

## 2.2 verl

仓库：[verl-project/verl](https://github.com/verl-project/verl)

### 实际文件

- [`AGENTS.md`](https://github.com/verl-project/verl/blob/main/AGENTS.md)
- [`CONTRIBUTING.md`](https://github.com/verl-project/verl/blob/main/CONTRIBUTING.md)

### `AGENTS.md` 的核心约束

1. **先排查重复工作**：使用 `gh issue view`、`gh pr list` 检查 Issue 和开放 PR，避免重复实现。
2. **禁止低价值 busywork PR**：孤立 typo、单一 style 清理、单个 mutable default 等，不应单独提交；机械性清理应合并到有实质内容的变更中。
3. **人工负责**：不接受纯代码 Agent 自动提交的 PR；提交人必须理解并能够解释整个改动。
4. **AI 参与透明化**：AI 辅助改动应在 PR 中说明 AI 使用情况，并报告测试结果。
5. **先读规则再动手**：Agent 指令文件及领域指南约束具体研发行为。

### 代表性命令

```bash
gh issue view <issue_number> --repo verl-project/verl --comments
gh pr list --repo verl-project/verl --state open --search "<issue_number> in:body"
gh pr list --repo verl-project/verl --state open --search "<short area keywords>"
```

### 贡献规范解读

verl 的价值不只是格式规范，而是把开源维护成本纳入 Agent 工作流：先确定是否值得做，再确认是否有人正在做，最后由人类承担质量责任。对 RL 框架尤其重要，因为一个看似局部的改动可能影响 rollout、reward、训练数据分布和最终模型行为。

**建议借鉴：** 在内部仓库中将“重复 PR 检查、AI 参与声明、人工逐行 review、训练/评测证据”设为 PR 模板必填项。

---

## 2.3 DeepSpeed

仓库：[deepspeedai/DeepSpeed](https://github.com/deepspeedai/DeepSpeed)（原 microsoft/DeepSpeed 地址已重定向）

### 实际文件

- [`CONTRIBUTING.md`](https://github.com/deepspeedai/DeepSpeed/blob/master/CONTRIBUTING.md)
- [`README.md`](https://github.com/deepspeedai/DeepSpeed/blob/master/README.md)

本次可确认的主要规范入口是贡献指南。没有足够证据将某个 Agent 专属文件（如 `AGENTS.md` 或 `CLAUDE.md`）列为已核实规范，因此不把通用贡献文档误写成 Agent 配置。

### 对 DeepSpeed 类项目应重点检查的规范维度

- ZeRO Stage 1/2/3 的参数、状态分片和通信行为。
- Optimizer/Offload/Activation checkpointing 的显存、吞吐和数值影响。
- CUDA、C++/CUDA extension 的编译矩阵与 ABI 兼容。
- 单机、多机、多 GPU 的测试覆盖。
- 与 PyTorch、CUDA、NCCL、不同 accelerator 的版本兼容。
- 性能优化必须附可复现 benchmark，不能只报告理论收益。

### 推荐 PR 验证示例

```bash
# 示例：按仓库当前贡献指南和测试目录选择实际命令
pytest tests/unit/ -q
# CUDA / distributed / integration 测试应在匹配的硬件和环境中执行
```

> 上述命令是验证层级示例，不应视为 DeepSpeed 所有分支均可直接执行的固定命令；提交前以当前 `CONTRIBUTING.md`、测试 README 和 CI workflow 为准。

---

## 2.4 TorchTitan

仓库：[pytorch/torchtitan](https://github.com/pytorch/torchtitan)

### 实际文件

- [`CONTRIBUTING.md`](https://github.com/pytorch/torchtitan/blob/main/CONTRIBUTING.md)
- [`README.md`](https://github.com/pytorch/torchtitan/blob/main/README.md)
- [`docs/`](https://github.com/pytorch/torchtitan/tree/main/docs)
- [`tests/`](https://github.com/pytorch/torchtitan/tree/main/tests)
- [`torchtitan/config/`](https://github.com/pytorch/torchtitan/tree/main/torchtitan/config)
- [`torchtitan/models/`](https://github.com/pytorch/torchtitan/tree/main/torchtitan/models)
- [`torchtitan/distributed/`](https://github.com/pytorch/torchtitan/tree/main/torchtitan/distributed)

### 贡献流程中明确的分层

TorchTitan README 明确区分：

- 新想法优先放到 `experiments/`，遵循实验目录指南。
- 对核心能力的修复和贡献，遵循正式 contributing guidelines。

这是一种值得借鉴的治理方式：先让研究实验以较低成本迭代，经过验证后再进入稳定核心层，避免实验代码直接扩大核心 API 面积。

### 文档覆盖的工程领域

README 指向的文档/代码入口包括：

| 领域 | 路径 |
|---|---|
| 运行配置与 recipe | `torchtitan/config` |
| 新增模型 | `torchtitan/models` |
| 并行与分布式 | `torchtitan/distributed` |
| 数据集和数据加载 | `torchtitan/components/data` |
| Checkpoint 与 HF 转换 | `torchtitan/components/checkpointer` |
| RL | `torchtitan/rl` |
| Debug / reproducibility / numerics | `docs/debugging.md` |
| Validation / evaluation | `docs/evaluation.md` |
| Benchmarks | `docs/benchmarks` |
| Tests / CI | `tests` |

### 推荐实践

TorchTitan 的实验/核心分层适合研究型训练框架：

```text
experiments/
  <experiment>/
    README.md
    config/
    train.py
    tests/

torchtitan/
  models/
  distributed/
  components/
```

实验代码进入核心前，建议补充：稳定 API、单元测试、端到端 recipe、性能对比、数值验证、文档与维护者评审。

---

## 2.5 ms-swift

仓库：[modelscope/ms-swift](https://github.com/modelscope/ms-swift)

### 实际文件

- [`AGENTS.md`](https://github.com/modelscope/ms-swift/blob/main/AGENTS.md)
- [`CONTRIBUTING.md`](https://github.com/modelscope/ms-swift/blob/main/CONTRIBUTING.md)

### `CONTRIBUTING.md` 明确的代码规范

- 变量命名使用下划线分隔（snake_case）。
- 类名采用首字母大写的驼峰形式（PascalCase）。
- Python 使用 4 空格缩进，不使用 Tab。
- 优先采用成熟、稳定的开源依赖。
- 避免重复实现已有能力。
- 机械性清理应打包为系统性改动，或先开 Issue 讨论。

### Lint 与测试

贡献指南要求本地运行 pre-commit：

```bash
pip install pre-commit
pre-commit run --all-files
```

同时要求为新功能增加 smoke tests，为边界行为增加 unit tests；CI 包含静态代码检查、smoke tests 和 unit tests，测试通过后才能合并。

### 可借鉴点

ms-swift 覆盖模型、数据、微调方法、硬件与训练流程，适合采用“统一基础规范 + 模型/算法专项 Skill”的结构。Agent 不应只被告知“遵循项目风格”，还应知道新增模型需要更新哪些注册表、模板、文档和测试。

---

## 2.6 slime

仓库：[THUDM/slime](https://github.com/THUDM/slime)

### 实际文件与目录

- [`CONTRIBUTING.md`](https://github.com/THUDM/slime/blob/main/CONTRIBUTING.md)
- [`.agents/`](https://github.com/THUDM/slime/tree/main/.agents)
- [`.claude/skills/`](https://github.com/THUDM/slime/tree/main/.claude/skills)
- [`.pre-commit-config.yaml`](https://github.com/THUDM/slime/blob/main/.pre-commit-config.yaml)
- [`tests/`](https://github.com/THUDM/slime/tree/main/tests)
- [`docs/`](https://github.com/THUDM/slime/tree/main/docs)
- [`examples/`](https://github.com/THUDM/slime/tree/main/examples)

### `CONTRIBUTING.md` 的协作范围

slime 对开源贡献范围有清晰边界。

**欢迎：**
- Bug 报告和修复，需有测试或清晰复现。
- 通用 RL 优化，需有可验证 benchmark。
- 能通过 CI 或常规训练流程验证的性能改进。

**当前不鼓励/不纳入主要协作范围：**
- 大规模重构（增加内部与开源版本同步成本）。
- 通用标准、抽象或框架化提案。
- 无法通过 CI 或常规训练明确验证的功能。
- 与 RL 框架相对独立的完整算法复现项目。
- 为 slime 维护一套长期 Megatron fork。

这表明项目把“可持续维护”和“能否验证”放在功能数量之前。

### README 所展示的架构边界

- Training：Megatron 负责训练主过程。
- Rollout：SGLang + router 负责生成数据、奖励/验证信息。
- Data Buffer：承接 prompt、数据与 rollout 生成流程。
- 自定义 generation、reward、verifier、environment 通过接口扩展。
- README 提到 CPU tests 覆盖核心行为和定制接口，GPU tests 覆盖 dense/MoE training、rollout、checkpoint、precision、异步 rollout、distillation、debug replay 等。

### Agent 目录信号

仓库根目录公开展示 `.agents/` 与 `.claude/skills/`。这说明项目采用了通用 Agent 资源与 Claude Skill 资源并存的布局。具体 Skill 文件应以仓库目录当前内容为准，不宜仅凭目录名称推断每个 Skill 的执行要求。

### 评审建议

RL 训练框架的变更至少要回答：

1. 改动属于 training、rollout、data buffer 还是环境/奖励接口？
2. 是否影响样本分布、token 对齐、reward 计算或权重同步？
3. 如何验证训练正确性、恢复能力和可复现性？
4. 性能提升是否来自同等配置下的可复现对照？

---

## 2.7 vime

仓库：[vllm-project/vime](https://github.com/vllm-project/vime)

### 实际文件

- [`CONTRIBUTING.md`](https://github.com/vllm-project/vime/blob/main/CONTRIBUTING.md)
- [`docs/en/get_started/agent.md`](https://github.com/vllm-project/vime/blob/main/docs/en/get_started/agent.md)

### 项目原则

`CONTRIBUTING.md` 将项目目标概括为：

- Lightweight：聚焦 RL training loop 与 rollout 集成，避免变成单体应用框架。
- Stable：优先合入可测试、可评审、对生产规模训练安全的改动。
- Concise code：遵循现有模式，避免没有明确收益的过度抽象和大规模重构。
- Hardware support：目标包含 CUDA GPU 与 Ascend 等 NPU；GPU/NPU 相关改动通过独立分支维护，避免在同一分支堆叠过重的硬件抽象。

### 贡献流程与命令

```bash
pip install -r requirements.txt
pip install pre-commit
pre-commit install

pre-commit run --all-files --show-diff-on-failure --color=always
pytest tests/
```

贡献指南还明确：
- 大功能先开 Issue，说明问题、方案、影响模块和验证计划。
- 行为变更应补测试。
- 用户可见变化应更新文档，适用时中英文同步。
- 禁止通配符导入。
- 库代码避免随意 `print()`，使用项目日志工具。
- Megatron training 与 vLLM rollout 应保持在各自 backend 模块。
- PR 标题使用模块标签，例如 `[Training]`、`[Rollout]`、`[Core]`、`[Example]`、`[Hardware][Ascend]`。
- commit 使用 `git commit -s`。
- 使用 AI 时，在 PR 描述中说明，并按需在 commit 中标注。

### Agentic RL 文档

`docs/en/get_started/agent.md` 将 Agentic RL 扩展入口分成：
- 自定义 generation function：支持工具调用、RAG、浏览器/终端/sandbox 等 Agent loop。
- 自定义 reward function：支持 verifier、测试奖励、环境成功检查、外部 reward service。
- 多样本返回：用于 subagent、多 Agent 或 context compaction 片段。

对 Agent 训练平台来说，这种“扩展接口与 Agent 行为解耦”的文档结构值得借鉴。

---

## 2.8 Unsloth

仓库：[unslothai/unsloth](https://github.com/unslothai/unsloth)

### 本次核查情况

已检查仓库 README；本次没有获得足够可靠的公开证据，能够逐条确认其当前 `AGENTS.md`、`CLAUDE.md` 或完整贡献规范。因此不将未经核实的文件路径和规则写成项目事实。

### 后续专项核查建议

Unsloth 的工程重点与通用训练框架略有差异，建议重点检查：

- LoRA/QLoRA、量化权重与 optimizer state 的正确性。
- 不同模型架构的 patch/monkey-patch 边界。
- 显存优化前后 logits、loss、梯度和最终训练结果的一致性。
- 不同 GPU、CUDA、PyTorch、Transformers 版本的兼容矩阵。
- notebook、训练脚本和库 API 是否使用一致的参数定义。
- 性能数字是否包含 batch size、sequence length、precision、GPU 型号、吞吐定义和峰值显存测量方式。

---

## 2.9 Liger Kernel

仓库：[linkedin/Liger-Kernel](https://github.com/linkedin/Liger-Kernel)

### 实际文件与文档

- [Contributing 文档](https://linkedin.github.io/Liger-Kernel/contributing/)
- [`README.md`](https://github.com/linkedin/Liger-Kernel/blob/main/README.md)
- [`ops/`](https://github.com/linkedin/Liger-Kernel/tree/main/src/liger_kernel/ops)
- [`transformers/`](https://github.com/linkedin/Liger-Kernel/tree/main/src/liger_kernel/transformers)
- [`tests/`](https://github.com/linkedin/Liger-Kernel/tree/main/tests)
- [`benchmark/`](https://github.com/linkedin/Liger-Kernel/tree/main/benchmark)
- [`convergence/`](https://github.com/linkedin/Liger-Kernel/tree/main/convergence)

> 上述代码目录以文档对项目结构的描述为依据；实际仓库目录布局若随版本调整，应以 GitHub 当前目录为准。

### 贡献指南明确要求

开发环境：

```bash
git clone https://github.com/linkedin/Liger-Kernel.git
cd Liger-Kernel
pip install -e ".[dev]"
prek install
prek run -a
```

文档将项目结构分成：
- `ops/`：核心 Triton operations。
- `transformers/`：基于 Triton operations 的 PyTorch `nn.Module`，并兼容 Transformers API。
- `tests/`：Triton layer correctness tests。
- `convergence/`：将 Kernel patch 到 Hugging Face 模型，运行多轮迭代，并逐层比较 weights、logits、loss。
- `benchmark/`：与 Hugging Face layer 比较运行时间和显存。

### Kernel PR 的三层验证模型

| 层次 | 目标 | 应报告的结果 |
|---|---|---|
| 单算子 correctness | 数学定义、边界 shape、dtype、mask、stride 等正确 | pytest、误差容限、支持的 shape/dtype |
| 模型 convergence | Kernel 替换后训练行为没有意外漂移 | layer-wise weights/logits/loss 对照，训练多步结果 |
| 性能 benchmark | 确认真实收益且可复现 | latency、throughput、memory、GPU/软件版本、基线 |

### Kernel 变更示例 checklist

```text
[ ] 数学定义与参考实现一致
[ ] 覆盖非连续 tensor、边界 shape、不同 dtype
[ ] 覆盖 forward / backward（若适用）
[ ] 说明数值误差阈值和测试依据
[ ] 在目标 GPU 上运行 correctness
[ ] 跑 convergence 或等价模型级验证
[ ] benchmark 有 warmup、重复测量和基线
[ ] 报告显存、吞吐/延迟和软硬件环境
[ ] 验证与目标训练栈（如 FSDP / DeepSpeed / Transformers）的兼容
```

---

## 3. 训练框架横向对比

| 维度 | Megatron-LM | verl | DeepSpeed | TorchTitan | ms-swift | slime | vime | Unsloth | Liger Kernel |
|---|---|---|---|---|---|---|---|---|---|
| 主要关注 | 大规模并行预训练 | RLHF/RL 训练 | 分布式训练优化 | PyTorch 原生训练 | 统一微调工具链 | RL scaling | RL post-training | 高效微调 | Triton 算子 |
| Agent 专属规范 | 已确认 | 已确认 | 本次未确认 | 本次未确认 | 已确认 AGENTS 入口 | Agent 目录/Skills | 专项 Agent 文档 | 本次未确认 | 本次未确认 |
| Skill/任务手册 | `skills/` | 指令/领域指南 | 需进一步核查 | 文档/实验指南 | 需进一步核查 | `.agents/`、`.claude/skills/` | Agentic RL 文档 | 需进一步核查 | 贡献指南 |
| 贡献门禁 | draft PR、签名、溯源 | 去重、人工负责 | CONTRIBUTING | experiments/core 分层 | pre-commit、CI | 范围与可验证性 | Issue、测试、签名、标签 | 待专项核查 | `prek`、测试、convergence、benchmark |
| 测试重点 | 分布式、checkpoint、精度 | RL 行为与训练流程 | ZeRO/通信/Offload | 数值、并行、模型 | smoke/unit | CPU/GPU、rollout、恢复 | GPU/NPU、training/rollout | 量化/LoRA/精度 | 算子正确性、收敛、性能 |
| 对内部规范的价值 | 最高 | 最高 | 分布式系统参考 | 实验治理参考 | 多模型工程参考 | RL Infra 参考 | 后训练工程参考 | 量化微调专项 | Kernel 专项 |

---

## 4. 通用 Agent 工程规范

## 4.1 规范文件分层

| 文件/机制 | 主要用途 | 应放内容 | 不应放内容 |
|---|---|---|---|
| `AGENTS.md` | 跨 Agent 通用项目说明 | 项目结构、构建/测试命令、全局约束、PR 要求 | 大篇幅领域教程、每次任务临时要求 |
| `CLAUDE.md` | Claude Code 项目入口 | Claude 特有配置或 `@AGENTS.md` 引用 | 与 AGENTS 重复的长篇规范 |
| `.cursor/rules/*.mdc` | Cursor 路径/任务范围规则 | 文件匹配范围、alwaysApply、按需规则 | 与通用规则冲突的副本 |
| `.codex/config.toml` | Codex 项目级运行配置 | sandbox、审批、MCP、模型/推理等设置 | 代码风格和架构长文 |
| `skills/<name>/SKILL.md` | 可复用工作流 | 触发条件、步骤、脚本、参考资料、验证 | 全局永久约束 |
| Hooks | 确定性门禁 | 格式化、敏感命令拦截、提交前检查 | 需要模型自由判断的复杂知识 |
| MCP | 外部工具与数据访问 | GitHub、工单、文档、监控、数据库工具 | 仓库规范正文 |

## 4.2 通用 AGENTS.md 推荐模板

```markdown
# Repository Instructions

## Project map
- `src/`: production code
- `tests/`: unit and integration tests
- `benchmarks/`: performance benchmarks
- `docs/`: user and developer documentation

## Workflow
1. Read the relevant source, tests, issue, and recent changes first.
2. Check existing issues/PRs before starting non-trivial work.
3. Read the relevant domain guide or Skill.
4. Make the smallest coherent change.
5. Run targeted tests, then broader checks when feasible.
6. Report exact commands and results; never claim unrun tests passed.

## Code quality
- Follow local style and existing abstractions.
- Add tests for behavior changes and edge cases.
- Do not add dependencies without justification.
- Do not use broad exception handling to hide failures.

## Distributed training
- State the affected ranks, process groups, and parallel dimensions.
- Avoid implicit global distributed state when explicit dependencies are possible.
- Validate checkpoint save/load and restart behavior.

## Numerical correctness
- Define reference behavior and tolerances.
- Compare outputs and gradients against a trusted baseline.
- Record dtype, device, and shape coverage.

## Performance
- Put benchmarks outside unit-test suites.
- Include hardware/software configuration, warmup, repetitions, baseline, and variance.
- Do not claim speedups without reproducible measurements.

## Pull requests
- Explain motivation, design, scope, and compatibility.
- List tests and results, including skipped tests and reasons.
- Disclose AI assistance where project policy requires it.
- A human author must review and understand every changed line.
```

## 4.3 训练框架建议采用的专项 Skills

```text
.agents/skills/
  add-model/
    SKILL.md
  distributed-parallelism/
    SKILL.md
  checkpoint-format/
    SKILL.md
  numerical-validation/
    SKILL.md
  kernel-development/
    SKILL.md
  performance-benchmark/
    SKILL.md
  rl-rollout-integration/
    SKILL.md
  reward-and-verifier/
    SKILL.md
  multi-node-debugging/
    SKILL.md
  release-and-compatibility/
    SKILL.md
```

Skill 至少包含：

```markdown
---
name: kernel-development
description: Use when adding or modifying Triton/CUDA kernels.
---

# Goal
Define the expected result.

# Read first
- Relevant operator implementation
- Reference implementation
- Existing tests
- Supported dtype/shape documentation

# Procedure
1. State the mathematical contract.
2. Implement the smallest change.
3. Add correctness and boundary tests.
4. Run model-level convergence checks.
5. Run benchmark against a named baseline.

# Verification
List exact commands and expected artifacts.

# Report
Summarize correctness, numerical error, performance, hardware, and limitations.
```

## 4.4 Agent 规范的强制性分级

建议将规则分为三级：

- **MUST**：违反即阻断，例如禁止未经授权执行破坏性命令、不得伪报测试、必须人工审查。
- **SHOULD**：默认遵循，若偏离需解释，例如优先复用现有抽象、优先补最小测试。
- **MAY**：可选实践，例如采用某种目录布局或 benchmark 工具。

不能把所有建议都写成 MUST，否则规范会迅速膨胀并降低遵循率。

---

## 5. Claude Code、Codex、Cursor 对比

## 5.1 Claude Code

官方文档：
- [Memory / CLAUDE.md](https://code.claude.com/docs/en/memory)
- [Skills](https://code.claude.com/docs/en/skills)
- [Hooks](https://code.claude.com/docs/en/hooks)
- [Sub-agents](https://code.claude.com/docs/en/sub-agents)
- [Settings](https://code.claude.com/docs/en/settings)

主要配置面：

| 配置 | 典型路径 | 作用 |
|---|---|---|
| 项目指令 | `CLAUDE.md` | 项目上下文和常驻规则 |
| 路径规则 | `.claude/rules/*.md` | 按路径加载的专项规则 |
| Skills | `.claude/skills/<name>/SKILL.md` | 可复用流程，按需触发 |
| Subagents | `.claude/agents/*.md` | 独立角色、工具范围和委派任务 |
| Hooks | `.claude/settings.json` | 生命周期事件上的确定性动作 |
| MCP | `.mcp.json` / 用户配置 | 外部工具接入 |

示例 `CLAUDE.md`：

```markdown
@AGENTS.md

## Claude-specific notes
- Read the relevant Skill before editing distributed or kernel code.
- Do not run multi-node jobs without explicit approval.
- Report exact test commands and results.
```

建议：Claude 的常驻指令保持短小；复杂的“新增模型”“调试 NCCL”“编写 Triton Kernel”流程放进 Skills；真正必须执行的安全/质量动作使用 Hooks 或 CI，而不是仅靠自然语言要求。

## 5.2 OpenAI Codex

官方文档：
- [Codex](https://developers.openai.com/codex)
- [AGENTS.md instructions](https://developers.openai.com/codex/guides/agents-md)
- [Configuration](https://developers.openai.com/codex/config-basic)
- [Skills](https://developers.openai.com/codex/skills)

主要配置面：

| 配置 | 典型路径 | 作用 |
|---|---|---|
| 全局指令 | `~/.codex/AGENTS.md` | 用户级通用规则 |
| 仓库指令 | `AGENTS.md` | 项目规则 |
| 子目录指令 | 子目录 `AGENTS.md` | 局部规则 |
| 覆盖文件 | `AGENTS.override.md` | 对相应目录/层级覆盖 |
| 项目配置 | `.codex/config.toml` | 项目级运行和工具配置 |
| Skills | `skills/<name>/SKILL.md` | 可复用工作流 |

Codex 的指令发现支持全局与项目逐层组合，离当前工作目录更近的目录指令可提供更具体的约束。应避免在多层文件中写出相互矛盾的命令。

示例：

```toml
# .codex/config.toml
# 仅示意；实际字段以当前 Codex 配置文档为准
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

> 配置字段和允许值可能随 Codex 版本变化，部署时必须对照官方配置参考，不应直接复制示例作为生产策略。

## 5.3 Cursor

官方文档：
- [Rules](https://cursor.com/docs/rules)
- [Skills](https://cursor.com/docs/skills)
- [MCP](https://cursor.com/docs/context/mcp)

支持：
- Project Rules：`.cursor/rules/*.mdc`
- User Rules：用户级规则
- Team Rules：团队级规则
- `AGENTS.md`：简单 Markdown 指令文件，支持根目录及子目录

`.mdc` 示例：

```markdown
---
description: Rules for distributed training code
globs: "src/distributed/**/*.py"
alwaysApply: false
---

- Pass process groups explicitly where possible.
- Add tests for rank-local and multi-rank behavior.
- Include checkpoint restart validation for stateful changes.
```

Cursor 文档特别指出 `.cursor/rules` 中的规则文件使用 `.mdc` 扩展名和 frontmatter；普通 `.md` 不作为 Project Rule 处理。若不需要路径/应用策略，使用 `AGENTS.md` 更简单。

## 5.4 三种工具对比

| 维度 | Claude Code | Codex | Cursor |
|---|---|---|---|
| 通用项目说明 | `CLAUDE.md`，也可引用 AGENTS | `AGENTS.md` | `AGENTS.md` |
| 路径级规则 | `.claude/rules/` | 子目录 `AGENTS.md` / override | `.cursor/rules/*.mdc` |
| Skill | `.claude/skills/` | Agent Skills | 支持 Skills |
| 子 Agent | `.claude/agents/` | 通过任务/Agent 工作流 | Agent 模式与规则 |
| Hooks | 原生支持 | 配置/扩展能力依版本演进 | 以 Rules、工具与工作流为主 |
| MCP | 支持 | 支持 | 支持 |
| 最佳适用场景 | 深度工作流、专门 Agent、生命周期自动化 | 终端/代码任务、仓库级规范、可控执行 | IDE 内开发、路径作用域规则 |

---

## 6. 建议的统一仓库目录

适用于训练框架、RL Infra 与 Kernel 混合仓库：

```text
repo/
├── AGENTS.md
├── CLAUDE.md
├── .cursor/
│   └── rules/
│       ├── 00-repository.mdc
│       ├── distributed-training.mdc
│       ├── kernel-development.mdc
│       └── tests-and-benchmarks.mdc
├── .codex/
│   └── config.toml
├── .claude/
│   ├── settings.json
│   ├── agents/
│   │   ├── code-reviewer.md
│   │   ├── distributed-debugger.md
│   │   └── kernel-reviewer.md
│   └── skills/
│       ├── add-model/SKILL.md
│       ├── debug-distributed/SKILL.md
│       ├── add-kernel/SKILL.md
│       └── benchmark-performance/SKILL.md
├── .agents/
│   └── skills/
│       ├── add-model/SKILL.md
│       ├── debug-distributed/SKILL.md
│       ├── add-kernel/SKILL.md
│       └── benchmark-performance/SKILL.md
├── docs/
│   └── developer/
│       ├── architecture.md
│       ├── testing.md
│       ├── numerical-validation.md
│       └── performance.md
├── src/
├── tests/
├── benchmarks/
└── .pre-commit-config.yaml
```

推荐让 `AGENTS.md` 成为规范源，`CLAUDE.md` 引用它；Cursor 直接读取 `AGENTS.md`，只有需要路径级规则时才增加 `.mdc`；Codex 使用同一份 `AGENTS.md`，项目配置独立放在 `.codex/config.toml`。

---

## 7. 面向训练框架的 PR 质量门禁

| 变更类型 | 必须验证 | 推荐补充 |
|---|---|---|
| 模型结构/模型注册 | 前向、loss、参数量、checkpoint load | 小规模训练收敛 |
| 数据处理/packing | 样本数、mask、position id、label 对齐 | 数据分布统计 |
| 并行策略 | 单卡/多卡、rank 映射、通信组 | 多节点与不同拓扑 |
| Optimizer/训练状态 | 更新公式、state 保存恢复 | 长跑稳定性 |
| Checkpoint | save/load、断点恢复、版本兼容 | reshard、损坏恢复 |
| RL rollout | token 对齐、终止条件、logprob、采样参数 | 多轮 Agent / 工具调用 |
| Reward/verifier | 输入输出契约、边界值、异常处理 | reward 分布与偏差分析 |
| Triton/CUDA Kernel | correctness、dtype/shape、梯度 | convergence、benchmark |
| 性能优化 | 基线、硬件、软件栈、测量方法 | 多 batch/seq length/并行规模 |

### 推荐 PR 模板

```markdown
## Motivation
问题背景、用户影响、关联 Issue。

## Design
改动模块、接口变化、并行/数据/数值影响。

## Compatibility
PyTorch/CUDA/NCCL/Transformers/后端版本与硬件影响。

## Validation
- [ ] lint / format
- [ ] unit tests
- [ ] integration / distributed tests
- [ ] numerical validation
- [ ] checkpoint save/load / resume（如适用）
- [ ] benchmark（性能改动必须）
- [ ] docs / examples

## Results
写出真实执行的命令、环境、结果；未执行项说明原因。

## AI assistance
是否使用 AI；提交人已审阅并理解所有改动。
```

---

## 8. 落地优先级建议

### P0：先统一底线

- 建立根目录 `AGENTS.md`，控制在短小、可执行的范围。
- 建立 `CONTRIBUTING.md` 与 PR 模板，明确人工责任和验证证据。
- 用 CI/pre-commit 实施格式、类型、基础单测门禁。
- 明确分布式、checkpoint、数值、Kernel 变更的专项测试要求。

### P1：按研发领域建设 Skills

优先建设：
1. `debug-distributed`
2. `checkpoint-change`
3. `add-model`
4. `kernel-development`
5. `benchmark-performance`
6. `rl-rollout-integration`

每个 Skill 必须有触发条件、输入材料、步骤、命令和输出格式。

### P2：将自然语言约束转成确定性自动化

- 禁止高风险命令：Hook/权限策略。
- 格式与静态检查：pre-commit/CI。
- PR 模板必填项：GitHub PR template / CI。
- checkpoint 兼容性：自动化测试。
- Kernel 性能回归：独立 benchmark workflow。
- AI 使用披露与人工 review：PR 流程。

### P3：建设领域 Agent

建议角色：
- **Training Architect**：模型结构、并行策略、训练 recipe。
- **Distributed Debugger**：NCCL、process group、rank hang、通信异常。
- **Checkpoint Reviewer**：格式兼容、恢复、reshard。
- **Kernel Engineer**：Triton/CUDA correctness、性能、融合策略。
- **RL Workflow Engineer**：rollout、reward、verifier、异步采样。
- **Performance Reviewer**：基线、统计方法、回归分析。

领域 Agent 应只获得完成任务所需的最小工具权限；执行训练作业、删除 checkpoint、修改生产环境等操作必须有明确审批。

---

## 9. 来源索引

### 训练框架

- Megatron-LM `AGENTS.md`：https://github.com/NVIDIA/Megatron-LM/blob/main/AGENTS.md
- Megatron-LM `CLAUDE.md`：https://github.com/NVIDIA/Megatron-LM/blob/main/CLAUDE.md
- Megatron-LM `skills/`：https://github.com/NVIDIA/Megatron-LM/tree/main/skills
- Megatron-LM contributing：https://github.com/NVIDIA/Megatron-LM/blob/main/docs/developer/contribute.md
- verl `AGENTS.md`：https://github.com/verl-project/verl/blob/main/AGENTS.md
- verl contributing：https://github.com/verl-project/verl/blob/main/CONTRIBUTING.md
- DeepSpeed contributing：https://github.com/deepspeedai/DeepSpeed/blob/master/CONTRIBUTING.md
- DeepSpeed README：https://github.com/deepspeedai/DeepSpeed/blob/master/README.md
- TorchTitan contributing：https://github.com/pytorch/torchtitan/blob/main/CONTRIBUTING.md
- TorchTitan README：https://github.com/pytorch/torchtitan/blob/main/README.md
- ms-swift `AGENTS.md`：https://github.com/modelscope/ms-swift/blob/main/AGENTS.md
- ms-swift contributing：https://github.com/modelscope/ms-swift/blob/main/CONTRIBUTING.md
- slime contributing：https://github.com/THUDM/slime/blob/main/CONTRIBUTING.md
- slime Agent 目录：https://github.com/THUDM/slime/tree/main/.agents
- slime Claude Skills：https://github.com/THUDM/slime/tree/main/.claude/skills
- vime contributing：https://github.com/vllm-project/vime/blob/main/CONTRIBUTING.md
- vime Agentic RL 文档：https://github.com/vllm-project/vime/blob/main/docs/en/get_started/agent.md
- Unsloth README：https://github.com/unslothai/unsloth/blob/main/README.md
- Liger Kernel contributing：https://linkedin.github.io/Liger-Kernel/contributing/
- Liger Kernel README：https://github.com/linkedin/Liger-Kernel/blob/main/README.md

### Agent 官方文档

- Claude Code Memory / CLAUDE.md：https://code.claude.com/docs/en/memory
- Claude Code Skills：https://code.claude.com/docs/en/skills
- Claude Code Hooks：https://code.claude.com/docs/en/hooks
- Claude Code Subagents：https://code.claude.com/docs/en/sub-agents
- Claude Code Settings：https://code.claude.com/docs/en/settings
- Codex：https://developers.openai.com/codex
- Codex AGENTS.md：https://developers.openai.com/codex/guides/agents-md
- Codex Config：https://developers.openai.com/codex/config-basic
- Codex Skills：https://developers.openai.com/codex/skills
- Cursor Rules：https://cursor.com/docs/rules
- Cursor Skills：https://cursor.com/docs/skills
- Cursor MCP：https://cursor.com/docs/context/mcp

---

## 10. 结论

对训练框架研发团队，最值得组合采用的实践是：

- 从 **Megatron-LM** 借鉴“任务前先读材料、再加载领域 Skill”的强制流程，以及分布式架构和代码溯源规范。
- 从 **verl / vLLM** 借鉴 AI 贡献治理：去重、拒绝低价值 PR、人工逐行负责、测试/评测结果透明。
- 从 **TorchTitan** 借鉴实验代码与稳定核心分层。
- 从 **ms-swift** 借鉴清晰的命名、格式、pre-commit 和 smoke/unit test 要求。
- 从 **slime / vime** 借鉴 RL 训练与 rollout 的模块边界、硬件路径影响说明和可验证性优先。
- 从 **Liger Kernel** 借鉴 correctness—convergence—benchmark 三层 Kernel 验证。

最终原则：**Agent 负责提升研发效率，规范和自动化负责守住工程底线，人类提交者对训练正确性、性能结论和生产风险承担责任。**

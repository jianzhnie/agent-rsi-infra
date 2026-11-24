# 大模型推理框架与 AI Agent 工程规范调研报告

> 调研范围：vLLM、SGLang、LMDeploy、TensorRT-LLM、MAX、DeepInfer、vLLM-Omni、SGLang-Omni；通用 Agent 规范及 Claude Code、Codex、Cursor。
>
> 资料基线：GitHub 上游仓库 `main` 分支及官方产品文档。仓库文件会持续变化，正式落地时应以目标 commit SHA 重新核对。
>
> 调研方法：优先检查仓库实际存在的 `AGENTS.md`、`CLAUDE.md`、`.agents/skills/`、`.claude/skills/`、`CONTRIBUTING.md`、`CODING_GUIDELINES.md`、`.pre-commit-config.yaml`、测试目录及开发者文档。没有查到的文件不推定存在；“未发现”不等于项目没有内部规范。

---

## 1. 执行摘要

本次推理框架的 Agent 工程规范呈现出三个成熟度层次：

1. **仓库级 Agent 规则已经成为主流基础设施。** vLLM 的 `AGENTS.md` 将重复 PR 检查、禁止纯 Agent PR、测试策略、uv 环境、性能评估和 AI 辅助披露写成强制要求；TensorRT-LLM 的 `AGENTS.md` 则把 Agent 规则与 C++/Python 编码规范、API 配置契约、Attention/MoE/KV Cache 专项开发指南关联起来。
2. **领域 Skills 正在从“提示词模板”升级为工程工作流。** SGLang 的 `.agents/skills/` 包含 Kernel 组织、测试、迁移和性能等任务技能；vLLM-Omni 的 `.claude/skills/` 把模型接入、PR 预检、代码评审和性能证据变成可执行清单；Modular 为 MAX/Mojo 单独维护跨 Agent 的官方 Skills 仓库。
3. **推理系统的质量门禁不能止于单测和 lint。** 模型服务、Kernel、调度、KV Cache、量化、并行通信和多模态流水线都要求额外的正确性、精度、吞吐、延迟、显存和硬件证据。优秀项目逐渐要求 PR 提供可复现命令、具体 GPU/软件版本、并发度、warmup、重复测量及 A/B 对照。

### 1.1 框架对比总表

| 项目 | 核心定位/重点领域 | Agent 文件与 Skills 现状（本次核实） | 规范成熟度判断 | 最值得借鉴的做法 |
|---|---|---|---|---|
| [vLLM](https://github.com/vllm-project/vllm) | 通用 LLM serving；模型执行、调度、KV Cache、Kernel、分布式推理 | 根目录 `AGENTS.md`；`.agents/skills/`；`docs/contributing/editing-agent-instructions.md`；文档目录有 `docs/AGENTS.md` | 很高 | Agent 规则与领域指南、测试层级、性能评测和防重复 PR 联动 |
| [SGLang](https://github.com/sgl-project/sglang) | 高性能 LLM/VLM serving；Runtime、Kernel、调度、缓存 | 根目录 `.agents/skills/`、`.claude/`；`docs/AGENTS.md`；Kernel 专项 Skill | 很高（Kernel/文档技能突出） | Kernel 单一契约、注册表、实现去重、测试位置与迁移验证 |
| [LMDeploy](https://github.com/InternLM/lmdeploy) | TurboMind 与 PyTorch Engine；压缩、部署、服务 | 仓库有 `.claude/skills/`；`.pre-commit-config.yaml`；本次未确认根目录 `AGENTS.md` | 中高（存在 Skills 与自动化质量门禁） | Ruff、mdformat、docformatter、版权检查、clang-format 统一约束 Python/CUDA/C++ |
| [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) | NVIDIA GPU 优化推理；TensorRT/CUDA、PyTorch backend、Executor | 根目录 `AGENTS.md`、`CLAUDE.md` 引用关系、`CODING_GUIDELINES.md`、多份 Attention/MoE/KV Cache Developer Guide | 很高 | 修改前必须读子系统指南；配置 Schema 变更更新 Golden Manifest；DCO 与版权头 |
| [MAX](https://github.com/modular/modular) | Modular MAX 推理平台、模型 Pipeline、Mojo Kernel | 主仓库 `CONTRIBUTING.md`；官方独立仓库 [`modular/skills`](https://github.com/modular/skills) 提供 MAX/Mojo Agent Skills | 高（Agent 能力集中在独立 Skills 仓库） | 同一套 Agent Skills 可跨 Claude Code、Codex 等工具安装 |
| [DeepInfer](https://github.com/deepseek-ai/DeepInfer) | DeepSeek 模型大规模推理；NVIDIA CUDA 与 Ascend CANN 路径 | 根目录 `CONTRIBUTING.md`；`tests/`、`examples/`、`eval/`；本次未确认仓库级 Agent 文件 | 中高（贡献与测试规范清晰，Agent 专项较少） | GPU/NPU 测试标记、轻量 CI 核心测试与重型端到端验证分层 |
| [vLLM-Omni](https://github.com/vllm-project/vllm-omni) | 多模态/全模态多阶段推理与服务 | `AGENTS.md`、`CLAUDE.md`、`.claude/skills/`；贡献文档有 human intent gate、Skill 使用和证据要求 | 很高 | PR 前置人工意图门禁；性能/精度证据模板；测试硬件标记和差分约束 |
| [SGLang-Omni](https://github.com/sgl-project/sglang-omni) | 语音、TTS、Omni 多阶段运行时；阶段调度、跨阶段传输 | 根目录 `AGENTS.md`；`CLAUDE.md` 为指向 `AGENTS.md` 的符号链接；`.claude/skills/`；Developer Reference | 高 | 多阶段模型接入边界、Stage/Coordinator/Relay 分层、硬件适配和专项 Skills |

> 成熟度是对“可观察到的仓库工程规范”的定性评估，不是框架性能排名，也不表示 Agent 一定能自主正确完成任务。

### 1.2 关键结论

- **优先把 `AGENTS.md` 作为跨 Agent 的事实源**，Claude Code 通过 `CLAUDE.md` 引用或链接，避免多份规则漂移。
- **Skills 负责流程，AGENTS 负责约束。** 不要把几十步的 Kernel 优化、模型接入、性能评测 SOP 全塞进根目录指令。
- **推理框架必须采用证据驱动的 PR 标准。** “代码已生成”“单测通过”不等于模型行为正确，也不等于性能提升。
- **Kernel 优化必须先检索同一计算契约的既有实现。** SGLang 对这一点写得尤其具体：先查 registry、Triton/PyTorch 实现、外部 Kernel 库及真实调用形状，再决定扩展、迁移、优化或替换。
- **多模态框架需要独立的阶段级契约。** vLLM-Omni 和 SGLang-Omni 的验证对象不仅是单个模型 forward，还包括 stage 输入输出、跨阶段传输、流式时序、取消/异常传播和端到端 API。

---

## 2. 项目逐一深入检查

## 2.1 vLLM

仓库：[https://github.com/vllm-project/vllm](https://github.com/vllm-project/vllm)

### 关键文件

| 文件路径 | 作用 | 规范要点 |
|---|---|---|
| [`AGENTS.md`](https://github.com/vllm-project/vllm/blob/main/AGENTS.md) | 全仓库 AI Agent 指令 | 强制检查重复 Issue/PR；禁止低价值零散 PR；禁止纯 Agent PR；人工审查每一行；PR 披露 AI 使用情况、测试命令和模型评测 |
| [`docs/contributing/editing-agent-instructions.md`](https://github.com/vllm-project/vllm/blob/main/docs/contributing/editing-agent-instructions.md) | 如何维护 Agent 指令和 Skills | Skills 放在 `.agents/skills/<name>/`；Claude Code 不直接读取 `.agents/`，通过 `.claude/skills/` 符号链接复用；`SKILL.md` 控制在 500 行以内 |
| [`docs/contributing/README.md`](https://github.com/vllm-project/vllm/blob/main/docs/contributing/README.md) | 贡献、测试、lint 和 AI 辅助贡献 | pre-commit、pytest、Google Python/C++ 风格；AI 辅助代码必须人工审查并披露 |
| `docs/contributing/model/tests.md` | 模型变更测试规范 | 模型相关改动的测试要求由专门文档承接 |
| `benchmarks/kernels/` | Kernel 性能工作 | Kernel benchmark 不应混入普通 `tests/` 单测目录 |

### Agent 规范重点

`AGENTS.md` 的主要强制规则：

1. **先做重复工作检查**：检查 Issue 评论、已开启 PR 及关键词相似 PR；已有 PR 覆盖同一问题时不重复提交。
2. **不接受纯 Agent PR**：提交者必须理解和解释改动；人工审查全部改动行并运行相关测试。
3. **AI 辅助工作必须透明**：PR 描述说明 AI 参与情况，提供测试命令和结果；影响输出、精度或 serving 的改动还要提供模型评测。
4. **Fail-closed**：若属于重复工作或低价值机械修改，Agent 应停止，而不是擅自继续。
5. **统一 Python 环境**：通过 `uv` 管理环境，不使用系统 `python3` 或裸 `pip`；按仓库要求安装 pre-commit。
6. **测试先设计后编写**：先明确模块职责、I/O 契约、要防止的失败、最低成本测试层级；优先扩展现有测试和 fixture。
7. **性能测试分层**：普通单测验证行为；Kernel 性能测试放 `benchmarks/kernels/`；模型行为变化要执行模型评测。
8. **文档同步**：改变用户可见的 CLI、配置、环境变量或行为时，同 PR 更新文档。

### 示例：vLLM Agent 的测试决策

```text
修改一个 scheduler 行为
  -> 先定位模块 I/O 契约
  -> 复用现有 conftest.py / fixture
  -> 优先增加最小 unit/regression test
  -> 若影响模型输出或 serving 行为，执行 model eval
  -> 若是 Kernel 性能工作，放到 benchmarks/kernels/
  -> PR 写明命令、结果、未运行的测试及原因
```

### Skills 的组织方式

vLLM 的 Agent 指令文档明确建议：

```text
.agents/
  skills/
    <skill-name>/
      SKILL.md
      references/
      scripts/

.claude/
  skills/
    <skill-name> -> ../../.agents/skills/<skill-name>
```

这样 Codex/支持 Agent Skills 标准的工具可读取 `.agents/skills/`，Claude Code 通过链接读取同一份 Skill。仓库还通过 `tools/pre_commit/check_agent_files.py` 对 Agent 文件进行检查。

**评价：** vLLM 的优势是将“Agent 应该怎么做”写成可审计的贡献规则，并将测试成本、性能验证和模型评测纳入明确的工程流程。

---

## 2.2 SGLang

仓库：[https://github.com/sgl-project/sglang](https://github.com/sgl-project/sglang)

### 关键文件

| 文件路径 | 作用 | 规范要点 |
|---|---|---|
| [`.agents/skills/kernel-organization/SKILL.md`](https://github.com/sgl-project/sglang/blob/main/.agents/skills/kernel-organization/SKILL.md) | Kernel 组织与迁移规范 | 按计算职责分组；统一公共 API；实现去重；规定测试目录；迁移时验证数值和性能 |
| [`.agents/skills/`](https://github.com/sgl-project/sglang/tree/main/.agents/skills) | 仓库 Agent Skills | 覆盖 Kernel、测试、运行时等专项任务 |
| [`docs/AGENTS.md`](https://github.com/sgl-project/sglang/blob/main/docs/AGENTS.md) | SGLang 文档站 Agent 规范 | 不猜 CLI/环境变量/默认值；以代码和权威文档为准；示例需可复制 |
| [`docs/CONTRIBUTING.md`](https://github.com/sgl-project/sglang/blob/main/docs/CONTRIBUTING.md) | 文档贡献规范 | 主动语态、直接面向读者、短句、先目标后步骤、术语一致、提供示例 |
| [`python/sglang/kernels/README.md`](https://github.com/sgl-project/sglang/blob/main/python/sglang/kernels/README.md) | Kernel 目录与注册约定 | 与 Kernel Skill 配套阅读 |
| [`test/README.md`](https://github.com/sgl-project/sglang/blob/main/test/README.md) | 测试目录和运行约定 | 与 Kernel Skill 配套阅读 |

### Kernel 组织 Skill 的关键规则

这是本次调研中最值得推理框架团队借鉴的规范之一。

**1. 按计算职责分组，而不是按模型或 GPU 分组。**

例如：

- GEMM/GEMV 放 `gemm`
- Expert routing 放 `moe`
- Attention index selection 放 `attention`
- Sampling 放 `sampling`
- Normalization 放 `layernorm`
- KV Cache 内容读写放 `kvcache`
- 纯量化格式转换放 `quantization`
- 跨 rank collective、peer-memory 访问归 `communication`

**2. 一个计算契约尽量只有一个主实现。**

Skill 要求新增或优化 Kernel 前先搜索：

- Kernel registry；
- 所属逻辑分组；
- `srt/layers` 和模型文件中的 Triton/PyTorch 实现；
- AOT wheel；
- FlashInfer、DeepGEMM、TensorRT-LLM、CUTLASS 等外部库封装。

然后依据实测结果决定：

- 扩展现有实现；
- 将调用迁移到已有更优实现；
- 优化最有希望收敛的实现；
- 用新实现替换旧实现；
- 只有平台、架构、dtype 或真实 shape 有明确差异时才保留多实现。

**3. 公共 API、后端实现和 Runtime 解耦。**

- 公共 Kernel API 位于 `sglang.kernels.ops.<group>`。
- 后端通过 `KernelSpec` 等元数据注册。
- 逻辑分组的导入不能触发 GPU Kernel 实现导入或编译。
- Kernel 不应依赖 SRT Runtime 内部对象；需要的状态应通过参数传递。

**4. 测试必须按职责归位。**

| 测试类型 | 推荐目录 |
|---|---|
| Kernel 数值测试 | `test/registered/kernels/ops/<group>/` |
| CI 微基准 | `test/registered/kernels/benchmark/<group>/` |
| Registry/selector 测试 | `test/registered/unit/kernels/` |
| Runtime 单测 | `test/registered/unit/<subsystem>/` |
| 非 CI 手工 Smoke/Benchmark | `test/manual/kernels/` |

**5. Kernel 迁移必须提供证据。**

迁移前检索所有调用、注册、文档、测试、打包引用；迁移后检查测试清单、CI 注册覆盖和包内文件。数值一致性要考虑 ties、NaN、全 mask 等边界情况；性能要按真实 shape 对比，并说明每个实现最终是否保留。

### 示例：新增 Kernel 的 Agent 工作流

```text
收到新增 fused attention kernel 需求
  1. 阅读 kernel-organization Skill、kernels README、test README
  2. 搜索 registry、Triton、PyTorch、FlashInfer、CUTLASS 等实现
  3. 明确计算契约：输入/输出、dtype、layout、边界行为
  4. 测量现有候选在真实 dispatch shapes 上的延迟
  5. 选择扩展/迁移/优化/替换，而非直接复制一份实现
  6. 在逻辑 group 注册公共 API
  7. 添加数值测试、CI benchmark 和 selector 测试
  8. 运行 namespace/dispatch CPU tests、相关 GPU tests、pre-commit
  9. PR 列出其他实现、各自耗时、测试与性能证据
```

### 文档 Agent 规范

`docs/AGENTS.md` 特别强调：

- 不要猜测 flags、默认值、API 或性能行为；
- 先查当前实现、官方文档或权威厂商文档；
- 命令示例注明 GPU 平台、OS、模型标识、并行参数和所需 Token；
- 所有代码块声明语言；
- 使用 `docs.json`，不要使用已弃用的 `mint.json`。

**评价：** SGLang 的 Kernel 规范是“计算契约驱动”的工程治理，不只是格式规范。适合拥有多套 CUDA/Triton/外部 Kernel Backend 的推理框架。

---

## 2.3 LMDeploy

仓库：[https://github.com/InternLM/lmdeploy](https://github.com/InternLM/lmdeploy)

### 已核实的文件

| 文件路径 | 作用 | 规范要点 |
|---|---|---|
| [`.pre-commit-config.yaml`](https://github.com/InternLM/lmdeploy/blob/main/.pre-commit-config.yaml) | 自动化代码质量门禁 | Ruff、pre-commit-hooks、mdformat、docformatter、版权检查、clang-format |
| [`.claude/skills/`](https://github.com/InternLM/lmdeploy/tree/main/.claude/skills) | Claude Code 专项 Skills | 仓库存在该目录；具体技能清单应以当前目录内容为准 |
| [`tests/`](https://github.com/InternLM/lmdeploy/tree/main/tests) | 测试代码 | Python/C++/推理行为测试 |
| [`autotest/`](https://github.com/InternLM/lmdeploy/tree/main/autotest) | 自动化测试 | 与普通单测、端到端验证区分 |
| [`benchmark/`](https://github.com/InternLM/lmdeploy/tree/main/benchmark) | 性能评估 | 推理性能工作与功能测试分离 |
| [`src/`](https://github.com/InternLM/lmdeploy/tree/main/src) | C++/CUDA 等底层实现 | 受 clang-format 等工具约束 |

本次没有将根目录 `AGENTS.md` 或 `CONTRIBUTING.md` 作为已确认事实；GitHub 仓库实际目录可确认 `.claude/skills/` 和 `.pre-commit-config.yaml` 存在。

### Pre-commit 规则

` .pre-commit-config.yaml` 包含：

- `ruff-check`：Python lint；
- `trailing-whitespace`、`check-yaml`、`end-of-file-fixer`、`check-merge-conflict`；
- `mdformat`：Markdown 格式，使用 OpenMMLab 扩展；
- `docformatter`：Python Docstring 格式；
- `check-copyright`：项目版权检查；
- `clang-format`：针对 `src/` 下 C/C++/CUDA 文件。

### 示例

```bash
# Python lint
pre-commit run --all-files

# 对 C++ / CUDA 源文件执行格式检查
pre-commit run clang-format --all-files

# 项目配置中包含 Ruff、Markdown、Docstring 和版权检查
```

**评价：** LMDeploy 的优势是底层多语言代码质量门禁覆盖面较完整。Agent 在修改 TurboMind、CUDA/C++、Python Engine 或文档时，应先复用已有 pre-commit，而不是自创格式要求。建议进一步把 `.claude/skills/` 中的模型接入、性能分析等工作流与跨工具 `AGENTS.md` 对齐。

---

## 2.4 TensorRT-LLM

仓库：[https://github.com/NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)

### 关键文件

| 文件路径 | 作用 | 规范要点 |
|---|---|---|
| [`AGENTS.md`](https://github.com/NVIDIA/TensorRT-LLM/blob/main/AGENTS.md) | Agent 全局规则 | 必须阅读 `CODING_GUIDELINES.md`；版权头；DCO；pre-commit；LLM args golden manifest |
| [`CLAUDE.md`](https://github.com/NVIDIA/TensorRT-LLM/blob/main/CLAUDE.md) | Claude Code 入口 | 指向/导入共享 Agent 规则 |
| [`CODING_GUIDELINES.md`](https://github.com/NVIDIA/TensorRT-LLM/blob/main/CODING_GUIDELINES.md) | C++/Python 规范 | Google C++ 风格、PEP 8、命名、格式化、Pydantic 约束 |
| [`CONTRIBUTING.md`](https://github.com/NVIDIA/TensorRT-LLM/blob/main/CONTRIBUTING.md) | PR、DCO、API 稳定性 | 单一关注点 PR、Conventional Commits、API 稳定性测试 |
| `tensorrt_llm/_torch/attention/ATTENTION_DEVELOPER_GUIDE.md` | Attention 开发指南 | Attention、MLA、Backend、metadata、KV Cache 行为 |
| `tensorrt_llm/_torch/moe/fused_moe/MOE_DEVELOPER_GUIDE.md` | MoE 开发指南 | MoE 架构、Backend、通信和开发模式 |
| `tensorrt_llm/_torch/pyexecutor/kv_cache/PAGE_TABLE_SPEC_GUIDE.md` | KV Cache Page Table | 跨进程/跨阶段传输与 KV Cache Sharing 契约 |
| `tensorrt_llm/_torch/pyexecutor/kv_cache/REGIONS_DEVELOPER_GUIDE.md` | KV Cache Regions | 持久状态生命周期与布局 |
| `scripts/generate_llm_args_golden_manifest.py` | 配置契约生成 | LLM args/nested config 变更时更新 Golden Manifest |

### Agent 强制规则

1. 所有 Python/C++ 改动先读 `CODING_GUIDELINES.md`。
2. 新文件添加 NVIDIA Copyright Header；修改文件更新年份。
3. 使用 `git commit -s`，提交 DCO sign-off；不要把 AI 工具写进 sign-off 行。
4. 不要自行增加 co-author，除非用户明确要求。
5. pre-commit 自动执行；如果 Hook 修改文件，需要重新 stage 并提交。
6. 修改 LLM args 或嵌套配置时，执行：

```bash
python3 scripts/generate_llm_args_golden_manifest.py
```

并提交生成的：

```text
tensorrt_llm/usage/llm_args_golden_manifest.json
```

新增配置字段还需要相关 Telemetry/Privacy Code Owner 审核。

### 编码规范示例

Python：

- Python 3.10+；
- 4 空格缩进；
- 不使用 Tab；
- 文件名 `snake_case.py`；
- 类名 `PascalCase`；
- 不使用 wildcard imports；
- 更新 `__all__`；
- 新文件通常 100 列，legacy 文件可能仍为 80 列，遵循 `pyproject.toml` 和相应 Hook。

C++：

- 主要遵循 Google C++ Style Guide；
- Namespace 结束括号添加注释；
- 优先 `const`/`constexpr`，避免不必要的 `#define`；
- 遵循 clang-format、clang-tidy、pre-commit 工具。

### API 稳定性

`CONTRIBUTING.md` 要求对受保护 API 进行稳定性测试。涉及 API 破坏时，需要 Code Owner 参与；API 稳定性测试通过 Snapshot 对比发现签名变化。PR 标题和描述应说明 API 兼容性及潜在性能/功能影响。

**评价：** TensorRT-LLM 的优势是“领域指南 + Agent 总则 + 机器生成契约”三层结构。对配置 Schema、KV Cache、Attention、MoE 等高耦合子系统尤其适用。

---

## 2.5 MAX / Modular

主仓库：[https://github.com/modular/modular](https://github.com/modular/modular)

官方 Agent Skills：[https://github.com/modular/skills](https://github.com/modular/skills)

### 关键文件与资源

| 路径 | 作用 | 规范要点 |
|---|---|---|
| [`CONTRIBUTING.md`](https://github.com/modular/modular/blob/main/CONTRIBUTING.md) | Modular 主仓库贡献指南 | Issue 先查重；Bug 报告提供可复现测试；贡献 PR 流程 |
| [`max/python/max/serve/`](https://github.com/modular/modular/tree/main/max/python/max/serve) | MAX Inference Server | OpenAI-compatible 服务实现 |
| [`max/python/max/pipelines/`](https://github.com/modular/modular/tree/main/max/python/max/pipelines) | MAX 模型 Pipeline | Python 模型执行图 |
| [`max/kernels/`](https://github.com/modular/modular/tree/main/max/kernels) | MAX Kernel | 加速算子 |
| [`modular/skills`](https://github.com/modular/skills) | 官方 Agent Skills | 面向 MAX/Mojo 的 Agent 技能，可供多个编码 Agent 使用 |

### 官方 Skills 的价值

`modular/skills` 明确面向 MAX 和 Mojo 开发，覆盖：

- Mojo 语言开发；
- MAX 模型导入；
- MAX 模型 Serving；
- MAX 模型性能测量。

它遵循 Agent Skills Standard，而不是绑定某个单一 Agent 产品。官方 README 给出安装方式：

```bash
# Codex 和其他兼容 Agent
npx skills add modular/skills

# 更新 Skills
npx skills update
```

Claude Code 可通过插件市场安装：

```text
/plugin marketplace add modular/skills
/plugin install skills@modular
```

也可以只安装 MAX 或 Mojo 子集。

**评价：** MAX 的亮点是把领域知识维护在独立、可分发的 Skills 仓库中。对于同时使用 Claude Code、Codex、Cursor 等工具的团队，这比在每个项目中复制 Prompt 更易维护。

---

## 2.6 DeepInfer

仓库：[https://github.com/deepseek-ai/DeepInfer](https://github.com/deepseek-ai/DeepInfer)

### 关键文件

| 文件路径 | 作用 | 规范要点 |
|---|---|---|
| [`CONTRIBUTING.md`](https://github.com/deepseek-ai/DeepInfer/blob/main/CONTRIBUTING.md) | 贡献与测试规范 | Python/C++ 格式、pytest 测试标记、GPU/NPU 测试 |
| [`README.md`](https://github.com/deepseek-ai/DeepInfer/blob/main/README.md) | 构建与运行说明 | Linux、GCC、Python、CUDA/CANN 环境要求 |
| `pyproject.toml` | Python 工具配置 | Ruff 规则 |
| `scripts/format_csrc.sh` | C++/CUDA 格式化 | `clang-format` 格式化和检查 |
| `tests/` | pytest 测试 | 核心测试 |
| `examples/` | 独立推理和重型验证 | 不默认纳入 pytest 自动发现 |
| `eval/README.md` | 评估 Benchmark | 模型评估入口 |
| `csrc/` | C++/CUDA 实现 | 由专用格式化脚本检查 |

### 测试规范

DeepInfer 将核心测试和资源密集型验证分开：

- `tests/`：pytest 测试，默认可被 pytest 发现；
- `examples/`：独立离线推理及耗时较长的验证，不作为普通 pytest 测试收集；
- `eval/`：模型/评估 Benchmark。

核心测试通过 pytest marker 标注硬件平台：

```python
@pytest.mark.ci
def test_gpu_path():
    ...

@pytest.mark.ci_npu
def test_npu_path():
    ...

@pytest.mark.ci
@pytest.mark.ci_npu
def test_shared_gpu_npu_path():
    ...
```

运行命令：

```bash
# GPU 核心测试
python -m pytest -v -s -m ci tests

# NPU 核心测试
python -m pytest -v -s -m ci_npu tests

# 全量 pytest
python -m pytest -v -s tests
```

### 格式化规范

```bash
# Python
ruff check --fix
ruff format

# Python 检查
ruff check --no-cache
ruff format --check --no-cache

# C++ / CUDA
bash scripts/format_csrc.sh
bash scripts/format_csrc.sh --check
```

**评价：** DeepInfer 值得借鉴的是硬件平台测试分层。对于同时支持 CUDA 与 CANN 的推理框架，Agent 必须显式报告在哪类设备上运行了测试，不能用 CPU import 成功替代 GPU/NPU 正确性证据。

---

## 2.7 vLLM-Omni

仓库：[https://github.com/vllm-project/vllm-omni](https://github.com/vllm-project/vllm-omni)

### 关键文件

| 文件路径 | 作用 | 规范要点 |
|---|---|---|
| [`AGENTS.md`](https://github.com/vllm-project/vllm-omni/blob/main/AGENTS.md) | 全仓库 Agent 指令 | 贡献责任、开发流程、测试与项目特定规范 |
| [`CLAUDE.md`](https://github.com/vllm-project/vllm-omni/blob/main/CLAUDE.md) | Claude Code 入口 | 复用仓库 Agent 规则 |
| [`docs/contributing/README.md`](https://github.com/vllm-project/vllm-omni/blob/main/docs/contributing/README.md) | 贡献指南 | Human intent gate、Skills、可执行证据 |
| [`.claude/skills/precheck-pr/SKILL.md`](https://github.com/vllm-project/vllm-omni/tree/main/.claude/skills/precheck-pr) | PR 提交前预检 | PR 标题、Bug、性能、模型、代码质量和 CI 检查 |
| [`.claude/skills/review-pr/SKILL.md`](https://github.com/vllm-project/vllm-omni/blob/main/.claude/skills/review-pr/SKILL.md) | 代码评审 | 证据驱动、优先级、可操作性、简洁 |
| [`.claude/skills/add-omni-model/`](https://github.com/vllm-project/vllm-omni/tree/main/.claude/skills/add-omni-model) | Omni 模型接入 | 多阶段模型集成流程 |
| [`docs/contributing/model/adding_omni_model.md`](https://github.com/vllm-project/vllm-omni/blob/main/docs/contributing/model/adding_omni_model.md) | Omni 模型开发指南 | Stage 实现、统一模型类、Registry、Pipeline、Input Processor、测试和 Recipe |
| [`docs/contributing/ci/`](https://github.com/vllm-project/vllm-omni/tree/main/docs/contributing/ci) | CI/PR 工作流 | precheck、证据与合并流程 |

### Human Intent Gate

在开始实现前，先确认贡献者的真实意图。对于缺失的需求信息，Agent 应先询问并等待，而不是替用户擅自决定产品行为。Bug 修复还需要真实失败证据。这个 Gate 不阻止独立 PR Review。

### Skills 工作流

贡献指南要求：

1. 先提供 Issue、RFC 或设计文档作为行为依据；
2. Agent 先说明假设、影响模块和接口契约；
3. 选择最窄的领域 Skill；
4. 修改生产行为或测试时，增加 `vllm-omni-test`；
5. Bug 修复提供最小复现和回归测试；
6. 运行相关检查，报告精确命令和结果；
7. 说明因缺少 GPU、模型权重、凭证或依赖而未运行的检查；
8. 人工审查 diff，确认没有覆盖无关工作。

### 性能 PR 证据要求

`precheck-pr` 的检查清单非常具体：

- 至少提供一项 Before/After 指标：RTF、RPS、Latency 或 VRAM；
- 指定 GPU 型号、数量和显存；
- 吞吐优化至少提供两个并发度的测量；
- 解释任何性能回退；
- 完整证据应包括 PyTorch、CUDA、vLLM、vLLM-Omni 版本；
- 说明 warmup 和测量轮数；
- 报告标准差或范围，不只报告最好的一次；
- 报告峰值显存；
- 提供可运行的 Benchmark 脚本和准确命令；
- 提供 pytest 汇总；
- 配置变化需说明旧值、新值及原因。

### 多模态模型接入路径

`adding_omni_model.md` 将模型接入拆成：

1. 创建各阶段模型目录和 Stage 实现；
2. 实现统一模型类，编排各阶段；
3. 在 `registry.py` 注册模型；
4. 在 `pipeline.py` 和 `vllm_omni/deploy/` 定义拓扑与部署默认值；
5. 实现 Stage Input Processor；
6. 编写测试；
7. 增加模型 Recipe 并更新索引。

### PR 标题与代码质量

项目约定 PR 标题前缀，例如：

```text
[Bugfix] Fix Ovis image text encoder dtype
[Model] Add MiniCPM-o 4.5 support
[Kernel] Optimize fused attention path
[Hardware][Ascend] Fix model execution on Ascend
[Core] Improve multi-stage scheduling
```

代码评审还特别关注：

- 避免新增通过 `kwargs["..."]` 隐式传参的字符串查找逻辑；
- 避免吞掉异常；
- 避免新增模型特定 Python 示例，优先复用共享任务入口；
- 使用结构化日志；
- 使用 Context Manager 管理资源；
- 不要无理由增加同步锁或依赖；
- 数值准确性和性能必须提供对应证据。

**评价：** vLLM-Omni 是本次研究中最系统的多模态 Agent 工作流样本之一。它把模型接入、PR 预检、评审、性能证据、硬件标记和示例治理串成一套闭环。

---

## 2.8 SGLang-Omni

仓库：[https://github.com/sgl-project/sglang-omni](https://github.com/sgl-project/sglang-omni)

### 关键文件

| 文件路径 | 作用 | 规范要点 |
|---|---|---|
| [`AGENTS.md`](https://github.com/sgl-project/sglang-omni/blob/main/AGENTS.md) | Agent 共享规则 | 仓库级 Agent 规范入口 |
| [`CLAUDE.md`](https://github.com/sgl-project/sglang-omni/blob/main/CLAUDE.md) | Claude Code 入口 | 当前是指向 `AGENTS.md` 的符号链接 |
| [`.claude/skills/`](https://github.com/sgl-project/sglang-omni/tree/main/.claude/skills) | Claude Skills | 仓库级专项技能 |
| [`docs/developer_reference/main.md`](https://github.com/sgl-project/sglang-omni/blob/main/docs/developer_reference/main.md) | 架构与开发者参考 | HTTP API、Coordinator、Stage、Scheduler、ModelRunner、Communication 分层 |
| [`sglang_omni/`](https://github.com/sgl-project/sglang-omni/tree/main/sglang_omni) | 运行时实现 | Pipeline、Scheduling、Model Runner、Models、Config、Relay、Serve、Client、Proto |
| [`tests/`](https://github.com/sgl-project/sglang-omni/tree/main/tests) | 测试 | 多阶段 Runtime 和模型测试 |
| [`.pre-commit-config.yaml`](https://github.com/sgl-project/sglang-omni/blob/main/.pre-commit-config.yaml) | 质量门禁 | 格式与静态检查 |

### 架构约束

SGLang-Omni 把 Omni 生成建模为多阶段 Runtime：

```text
HTTP API
  -> Client
  -> Coordinator
  -> Stage
  -> Scheduler
  -> ModelRunner
  -> model forward
```

各层职责：

- HTTP API：OpenAI-compatible 请求/响应、SSE、HTTP 错误；
- Client：请求转换、结果聚合和音频编码；
- Coordinator：请求生命周期、入口 Stage 提交、结果收集、Abort 广播；
- Stage：控制面 I/O、Relay I/O、Fan-in、流路由；
- Scheduler：每个 Stage 的执行循环和失败传播；
- ModelRunner：AR forward 准备、模型分发、输出抽取；
- Communication：控制消息和 Relay 数据传输。

模型专属代码应位于：

```text
sglang_omni/models/<model>/
```

模型开发不应随意把 Stage 生命周期、通信协议或调度逻辑散落到模型目录之外。

### 适合 Agent 的验证重点

- Stage 输入/输出协议与 dtype、shape、设备一致；
- Stage 之间的 Relay 后端行为一致；
- Coordinator 取消请求后，各 Stage 能停止并释放资源；
- 异常能沿 Stage/Scheduler/Coordinator 正确传播；
- 流式输出顺序、时间戳和终止信号正确；
- 离线路径与在线路径行为一致；
- 多模态端到端结果需要使用真实模型和真实硬件验证。

**评价：** SGLang-Omni 的关键是阶段边界和生命周期。Agent 不应只关注某个模型的 forward 是否跑通，还要验证跨阶段调度、传输、取消、流式和错误传播。

---

## 3. 跨框架规范对比

### 3.1 Agent 配置与技能治理

| 维度 | vLLM | SGLang | LMDeploy | TensorRT-LLM | MAX | DeepInfer | vLLM-Omni | SGLang-Omni |
|---|---|---|---|---|---|---|---|---|
| 根目录 AGENTS | 是 | 本次未确认根目录文件 | 本次未确认 | 是 | 本次未确认 | 本次未确认 | 是 | 是 |
| Claude 入口 | 通过链接/兼容目录 | `.claude/` 目录 | `.claude/skills/` | `CLAUDE.md` | 官方 Skills 插件 | 本次未确认 | 是 | 是，链接 AGENTS |
| Agent Skills | `.agents/skills/` | `.agents/skills/` | `.claude/skills/` | 以 AGENTS/开发指南为主 | 独立 `modular/skills` | 本次未确认 | `.claude/skills/` | `.claude/skills/` |
| 人工责任/AI 披露 | 明确 | 需按贡献指南执行 | 本次未发现 Agent 专项规则 | DCO/贡献规则明确 | 贡献流程 | 贡献流程 | 明确 | 以仓库 AGENTS/贡献规则为准 |
| 领域开发指南 | 多份 | Kernel Skills | Skills/工程配置 | Attention/MoE/KV Cache | MAX/Mojo Skills | README/CONTRIBUTING | 模型/性能/PR Skills | Developer Reference/Skills |

### 3.2 测试和性能证据

| 维度 | 推荐实践 | 代表项目 |
|---|---|---|
| 单元测试 | 最小行为、明确 I/O 契约、复用 fixture | vLLM |
| GPU/NPU 分层 | CI marker 区分硬件平台 | DeepInfer、vLLM-Omni |
| Kernel 数值测试 | 按算子组归档，覆盖边界值 | SGLang |
| Kernel Benchmark | 独立 benchmark 目录，不混入普通单测 | SGLang、vLLM |
| 模型评测 | 模型输出、精度、服务行为变化时必须评测 | vLLM |
| API 兼容性 | Golden Manifest / Snapshot 测试 | TensorRT-LLM |
| 多阶段 E2E | Stage、Coordinator、Relay、Streaming 一起验证 | vLLM-Omni、SGLang-Omni |
| 性能对比 | 同硬件/模型/请求集的 A/B，重复测量，报告波动 | vLLM-Omni |

---

## 4. 推理框架 Agent 通用规范建议

以下为综合上述项目后建议落地的规范模板，不代表某个仓库的原文。

### 4.1 Agent 文件分层

```text
repository/
├── AGENTS.md                    # 跨 Agent 的全局事实源
├── CLAUDE.md                    # Claude Code 入口：引用 AGENTS.md
├── .agents/
│   └── skills/
│       ├── add-model/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── add-kernel/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── debug-serving/
│       ├── optimize-kv-cache/
│       ├── benchmark-inference/
│       ├── validate-accuracy/
│       └── review-pr/
├── .claude/
│   ├── skills/                   # 链接到 .agents/skills
│   ├── agents/                   # 专项 Subagents
│   └── settings.json             # Hooks/权限等
├── .cursor/
│   └── rules/                    # Cursor 专属规则
├── .codex/
│   └── config.toml               # 仓库级 Codex 配置（按需）
└── docs/
    └── developer/
        ├── architecture/
        ├── model-integration/
        ├── kernel-development/
        ├── kv-cache/
        ├── scheduler/
        ├── distributed/
        └── performance/
```

### 4.2 根目录 AGENTS.md 应包含什么

建议只放所有任务都需要知道的内容：

1. 项目定位、核心架构和目录导航；
2. Python/C++/CUDA/Mojo 等语言规范入口；
3. 构建、测试、lint、pre-commit 的最短命令；
4. 代码变更的通用原则：最小 diff、禁止无关重构、先查已有实现；
5. 测试和性能证据要求；
6. API/配置/文档同步要求；
7. 安全、版权、DCO、依赖和数据隐私规则；
8. 需要读取的领域指南索引；
9. 人工审查、AI 披露和 PR 责任。

不要把所有 Kernel 参数、所有模型适配步骤和每种硬件命令写在根文件中。

### 4.3 推理系统专项 Skills 清单

| Skill | 触发场景 | 必须完成的工作 |
|---|---|---|
| `add-model` | 新模型接入 | 配置、权重映射、Tokenizer/Processor、模型注册、测试、文档、模型评测 |
| `add-kernel` | 新算子/Kernel | 检索重复实现、定义数值契约、选择 Backend、正确性测试、性能对比 |
| `optimize-kernel` | Kernel 优化 | 真实 shape、硬件计数器、Roofline、A/B、正确性、回归分析 |
| `optimize-kv-cache` | KV Cache 变化 | block/page 生命周期、分配/回收、prefix cache、跨进程传输、并发压力 |
| `debug-scheduler` | 调度器变化 | Admission、Preemption、Batching、Fairness、队列延迟和吞吐 |
| `debug-distributed` | TP/PP/DP/EP/PD 变化 | Rank 拓扑、通信顺序、死锁、超时、错误传播和多节点验证 |
| `validate-quantization` | FP8/INT8/INT4 等量化 | 数值误差、长上下文、异常分布、模型级指标和性能 |
| `benchmark-inference` | 性能测试 | 硬件、模型、请求集、并发、warmup、测量轮数、延迟分位数、吞吐和显存 |
| `add-omni-model` | 多模态模型 | Stage 图、跨阶段协议、流式、取消、端到端 API |
| `review-pr` | PR 审核 | 只报告有证据的问题，按严重度排序，指出最小修复方向 |

---

## 5. 推理框架必须建立的验证矩阵

推理框架不能把 `pytest` 通过作为唯一合格标准。建议按改动影响选择验证层级。

| 变更类型 | 最低验证 | 强烈建议的额外验证 |
|---|---|---|
| Python 工具/配置 | lint、unit test | 配置兼容性、文档示例 |
| 新模型接入 | 权重加载、forward、模型注册测试 | 离线/在线 E2E、精度、长短上下文 |
| Attention/MLA Kernel | 数值对比、dtype/shape 边界 | 多 GPU 架构、CUDA Graph、真实模型性能 |
| MoE Kernel | dispatch/combine 数值测试 | 多专家规模、EP 通信、负载不均衡 |
| KV Cache | 分配/回收/页表单测 | Prefix Cache、长上下文、并发、PD disaggregation |
| Scheduler | 队列和状态机测试 | 混合请求、突发流量、P50/P95/P99 |
| Quantization | 层级误差、输出稳定性 | 真实任务集、长上下文、模型质量指标 |
| TP/PP/DP/EP | 单节点分布式测试 | 多节点、多机型、故障恢复、通信性能 |
| Runtime API | API 单测、Schema/Snapshot | 向后兼容和真实客户端 |
| Omni/多模态 Pipeline | Stage 单测、协议测试 | 流式 E2E、音画同步、取消和背压 |
| 性能优化 | Before/After 基准 | 多并发度、多轮测量、显存和回归矩阵 |

### 5.1 性能 PR 必须报告的字段

```yaml
benchmark:
  framework: "<framework>"
  commit: "<base-sha>"
  candidate_commit: "<candidate-sha>"
  model: "<model-id-and-revision>"
  hardware:
    gpu: "<GPU model>"
    gpu_count: 8
    interconnect: "<NVLink/PCIe/IB>"
  software:
    driver: "<driver>"
    cuda_or_rocm: "<version>"
    framework: "<torch/version>"
  workload:
    input_tokens: [128, 2048]
    output_tokens: [128, 512]
    concurrency: [1, 8, 32, 64]
    request_dataset: "<dataset-or-generator>"
  measurement:
    warmup_rounds: 2
    measured_rounds: 5
    metrics:
      - ttft_p50
      - ttft_p99
      - tpot_p50
      - tpot_p99
      - request_throughput
      - output_tokens_per_second
      - peak_memory
  correctness:
    reference: "<reference implementation>"
    max_abs_error: "<value>"
    max_rel_error: "<value>"
    model_metric: "<task metric>"
  artifacts:
    command: "<exact command>"
    logs: "<artifact path>"
    raw_results: "<artifact path>"
```

注意：以上是建议的证据 Schema，不是某个框架实际采用的配置格式。

### 5.2 Kernel PR 必须回答的问题

- 是否存在同一数值契约的其他实现？
- 输入/输出 dtype、layout、shape、stride、mask 和边界行为是什么？
- 支持哪些 GPU 架构、编译路径和 Backend？
- 是否正确处理 NaN、Inf、空输入、全 Mask、极端长度和对齐边界？
- 对比基准是否使用真实请求形状和真实调用路径？
- 性能收益是否覆盖多个 shape 和并发度？
- 是否增加了重复实现、额外编译时间或维护成本？
- CUDA Graph、torch.compile、分布式通信等路径是否仍然成立？

---

## 6. Claude Code、Codex、Cursor 对比

### 6.1 能力与配置方式

| 维度 | Claude Code | OpenAI Codex | Cursor |
|---|---|---|---|
| 全局/项目指令 | `CLAUDE.md`、Rules | `AGENTS.md`、`AGENTS.override.md` | Project Rules、`AGENTS.md` |
| 子目录规则 | `.claude/rules/` 路径作用域 | 逐层发现嵌套 AGENTS | 支持嵌套 AGENTS.md 和规则 |
| 可复用工作流 | `.claude/skills/<name>/SKILL.md` | Skills | Rules/Skills（依产品版本和配置） |
| 专项 Agent | `.claude/agents/` Subagents | Agent/Skills 工作流 | Agent 模式与项目规则 |
| 确定性自动化 | Hooks、Permissions | Hooks/工具权限及配置 | Rules、工具权限与自动化能力 |
| 外部工具 | MCP、Plugins | MCP、Apps/Plugins | MCP |
| 共享规范建议 | `AGENTS.md` 为主，CLAUDE.md 引用 | 原生读取 AGENTS.md | 原生支持 AGENTS.md，复杂规则可用 `.cursor/rules` |

### 6.2 Claude Code

官方资料：

- [Claude Code Docs](https://code.claude.com/docs)
- [Claude Code customization guidance](https://claude.com/resources/articles/steering-claude-code-skills-hooks-rules-subagents-and-more)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Claude Code Hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents)

推荐分工：

- `CLAUDE.md`：项目结构、常用命令、长期有效的规则；
- `.claude/rules/`：按路径生效的规则；
- `.claude/skills/`：模型接入、Kernel 优化、性能测试等流程；
- `.claude/agents/`：独立审查、架构分析、测试执行等子任务；
- Hooks：格式化、lint、危险命令拦截等确定性操作；
- MCP：连接外部文档、Issue、CI 或内部工具。

重要原则：如果某条规则必须 100% 执行，不要只依赖自然语言提示。应使用 Hook、权限或 CI 强制门禁。

### 6.3 Codex

官方资料：

- [Codex AGENTS.md instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [OpenAI Skills Repository](https://github.com/openai/skills)

Codex 的规则发现链：

1. 全局 `~/.codex/AGENTS.override.md`，否则 `~/.codex/AGENTS.md`；
2. 从项目根目录到当前工作目录逐层发现；
3. 每层优先 `AGENTS.override.md`，否则 `AGENTS.md`；
4. 按目录层级合并，越靠近当前目录的规则越具体；
5. 默认有项目指令总字节数限制，可通过 `config.toml` 调整；
6. Skills 用于可复用任务工作流，`AGENTS.md` 用于持久项目约束。

示例：

```text
~/.codex/
  AGENTS.md

repo/
  AGENTS.md
  .codex/
    config.toml
  src/
    runtime/
      AGENTS.md
```

### 6.4 Cursor

官方资料：

- [Cursor Rules](https://cursor.com/docs/rules)

支持：

- Project Rules：`.cursor/rules/*.mdc`，可版本控制并按路径、手动触发或相关性加载；
- User Rules：用户级规则；
- Team Rules：团队级规则；
- `AGENTS.md`：简单 Markdown 规则文件，可放根目录和子目录；
- 嵌套 `AGENTS.md`：针对子目录提供更具体上下文。

建议：简单项目直接使用 `AGENTS.md`；复杂项目使用 `.cursor/rules` 进行路径作用域和规则拆分，避免把所有规则都常驻上下文。

---

## 7. 推荐的统一 Agent 配置示例

### 7.1 根目录 AGENTS.md 模板

```markdown
# Repository Agent Instructions

## Project overview
- This repository implements an LLM inference runtime.
- Read the relevant architecture guide before changing runtime, model, kernel,
  scheduler, cache, or distributed components.

## Non-negotiable rules
- Inspect the existing implementation and open issues/PRs before editing.
- Keep changes scoped to the requested behavior.
- Do not silently change public API, config defaults, or model behavior.
- Do not claim a test or benchmark passed unless it was actually run.
- The human contributor must review and understand every submitted change.

## Source of truth
- Runtime behavior: implementation and tests.
- Public behavior: current user documentation.
- Kernel contracts: kernel API and reference implementation.
- Performance claims: reproducible benchmark artifacts.

## Development
- Use the repository's pinned environment and dependency manager.
- Run the narrowest relevant tests first.
- Run format/lint checks on changed files.
- Add regression tests for bug fixes.
- Update docs for user-visible behavior/configuration changes.

## Inference correctness
- Model changes require model-level validation.
- Kernel changes require numerical comparison and edge-case tests.
- Cache/scheduler changes require lifecycle and concurrency tests.
- Distributed changes require multi-rank validation.
- Performance changes require matched baseline/candidate measurements.

## Reporting
- List changed files and design decisions.
- Report exact commands and results.
- Explicitly list tests not run and why.
- Include hardware/software/workload details for performance claims.
- Disclose AI assistance according to project contribution policy.
```

### 7.2 Skill 模板

```markdown
---
name: benchmark-inference
description: Run reproducible inference benchmarks and prepare evidence for performance PRs.
---

# Benchmark inference

## Required inputs
- Model and revision
- Base and candidate commits
- Hardware topology
- Input/output length distribution
- Concurrency levels

## Workflow
1. Read the benchmark entrypoint and existing baseline.
2. Verify hardware, software and model versions.
3. Use identical request data and runtime configuration.
4. Run warmup rounds.
5. Run multiple measured rounds.
6. Collect TTFT, TPOT, throughput and peak memory.
7. Compare every concurrency level.
8. Investigate regressions and variance.
9. Save raw output and exact commands.

## Output
- Environment manifest
- Exact command
- Raw results
- Summary table
- Regressions and limitations
- Tests not run
```

---

## 8. 建议的落地优先级

### P0：先建立统一事实源和验证底线

- 建立根目录 `AGENTS.md`；
- `CLAUDE.md` 仅引用 `AGENTS.md`；
- 建立 Agent Skills 目录和命名规范；
- PR 必须列出测试命令、结果和未运行项目；
- 模型、Kernel、性能、分布式改动分别设最低验证门槛。

### P1：建立推理系统专项 Skills

优先实现：

1. `add-model`
2. `add-kernel`
3. `benchmark-inference`
4. `validate-accuracy`
5. `optimize-kv-cache`
6. `debug-scheduler`
7. `debug-distributed`
8. `review-pr`

### P2：将高风险规则转为自动化

- pre-commit：Ruff、clang-format、类型检查、版权、Markdown；
- CI：GPU/NPU 测试标记、API Snapshot、Kernel 数值测试；
- 性能 CI：固定硬件和 workload 的基线对比；
- Hooks：禁止危险命令、修改后自动格式检查；
- PR Bot：检查性能证据、硬件信息、模型评测和测试结果。

### P3：引入多 Agent 分工

| Agent | 责任 | 输出 |
|---|---|---|
| Architect | 识别模块边界和接口契约 | 设计说明、受影响模块 |
| Model Integrator | 模型结构、权重、Processor 接入 | 模型实现和加载测试 |
| Kernel Engineer | 算子与 Kernel | 实现、数值测试、性能对比 |
| Runtime Engineer | Scheduler、KV Cache、Executor | Runtime 改动和并发测试 |
| Performance Analyst | Profiling、Benchmark | A/B 数据、瓶颈分析 |
| Test Engineer | 单测、集成、E2E | 测试报告 |
| Reviewer | 独立审查 diff | 按严重度排序的证据型问题 |

多 Agent 不应共享无约束写权限。建议采用“一个主 Agent 编排、多个只读分析 Agent、单一实现 Agent 修改、独立 Reviewer 审查”的方式，减少并行修改冲突。

---

## 9. 参考来源索引

### 推理框架

- vLLM 仓库：[https://github.com/vllm-project/vllm](https://github.com/vllm-project/vllm)
- vLLM Agent 指令：[https://github.com/vllm-project/vllm/blob/main/AGENTS.md](https://github.com/vllm-project/vllm/blob/main/AGENTS.md)
- vLLM Agent 指令维护：[https://github.com/vllm-project/vllm/blob/main/docs/contributing/editing-agent-instructions.md](https://github.com/vllm-project/vllm/blob/main/docs/contributing/editing-agent-instructions.md)
- SGLang 仓库：[https://github.com/sgl-project/sglang](https://github.com/sgl-project/sglang)
- SGLang Kernel Organization Skill：[https://github.com/sgl-project/sglang/blob/main/.agents/skills/kernel-organization/SKILL.md](https://github.com/sgl-project/sglang/blob/main/.agents/skills/kernel-organization/SKILL.md)
- SGLang Docs Agent Guide：[https://github.com/sgl-project/sglang/blob/main/docs/AGENTS.md](https://github.com/sgl-project/sglang/blob/main/docs/AGENTS.md)
- LMDeploy 仓库：[https://github.com/InternLM/lmdeploy](https://github.com/InternLM/lmdeploy)
- LMDeploy pre-commit：[https://github.com/InternLM/lmdeploy/blob/main/.pre-commit-config.yaml](https://github.com/InternLM/lmdeploy/blob/main/.pre-commit-config.yaml)
- TensorRT-LLM 仓库：[https://github.com/NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)
- TensorRT-LLM AGENTS：[https://github.com/NVIDIA/TensorRT-LLM/blob/main/AGENTS.md](https://github.com/NVIDIA/TensorRT-LLM/blob/main/AGENTS.md)
- TensorRT-LLM Coding Guidelines：[https://github.com/NVIDIA/TensorRT-LLM/blob/main/CODING_GUIDELINES.md](https://github.com/NVIDIA/TensorRT-LLM/blob/main/CODING_GUIDELINES.md)
- TensorRT-LLM Contributing：[https://github.com/NVIDIA/TensorRT-LLM/blob/main/CONTRIBUTING.md](https://github.com/NVIDIA/TensorRT-LLM/blob/main/CONTRIBUTING.md)
- Modular MAX：[https://github.com/modular/modular](https://github.com/modular/modular)
- Modular Agent Skills：[https://github.com/modular/skills](https://github.com/modular/skills)
- DeepInfer：[https://github.com/deepseek-ai/DeepInfer](https://github.com/deepseek-ai/DeepInfer)
- DeepInfer Contributing：[https://github.com/deepseek-ai/DeepInfer/blob/main/CONTRIBUTING.md](https://github.com/deepseek-ai/DeepInfer/blob/main/CONTRIBUTING.md)
- vLLM-Omni：[https://github.com/vllm-project/vllm-omni](https://github.com/vllm-project/vllm-omni)
- vLLM-Omni Contributing：[https://github.com/vllm-project/vllm-omni/blob/main/docs/contributing/README.md](https://github.com/vllm-project/vllm-omni/blob/main/docs/contributing/README.md)
- vLLM-Omni PR Checklist：[https://github.com/vllm-project/vllm-omni/blob/main/.claude/skills/precheck-pr/references/checklists.md](https://github.com/vllm-project/vllm-omni/blob/main/.claude/skills/precheck-pr/references/checklists.md)
- SGLang-Omni：[https://github.com/sgl-project/sglang-omni](https://github.com/sgl-project/sglang-omni)
- SGLang-Omni Developer Reference：[https://github.com/sgl-project/sglang-omni/blob/main/docs/developer_reference/main.md](https://github.com/sgl-project/sglang-omni/blob/main/docs/developer_reference/main.md)

### Agent 工具官方文档

- Claude Code：[https://code.claude.com/docs](https://code.claude.com/docs)
- Claude Code Skills：[https://code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)
- Claude Code Hooks：[https://code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- Claude Code Subagents：[https://code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)
- Codex AGENTS.md：[https://learn.chatgpt.com/docs/agent-configuration/agents-md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- Cursor Rules：[https://cursor.com/docs/rules](https://cursor.com/docs/rules)
- OpenAI Skills：[https://github.com/openai/skills](https://github.com/openai/skills)

---

## 10. 调研边界与注意事项

1. 本报告针对公开 GitHub 仓库和官方文档；内部工程规范、私有 CI 配置和未公开的维护流程不在范围内。
2. 某仓库没有检索到根目录 `AGENTS.md`，不代表没有团队内部 Agent 规则；本报告只记录已能核实的文件。
3. Skills、Hooks 和配置文件会随主分支快速变化，落地时应固定到具体 commit SHA。
4. 不同项目的测试命令和性能指标不可直接横向比较；本报告比较的是工程规范和 Agent 工作流，而非框架性能。
5. 对性能结论必须控制硬件、模型、输入输出长度、并发度、版本和测量方法；单次最好成绩不足以支持性能 PR。
6. 对多模态推理，文本生成的 TTFT/TPOT 之外，还应补充音频 RTF、首包延迟、流式间隔、端到端时延、同步误差和显存峰值等任务指标。

**最终建议：** 以 vLLM 的 `AGENTS.md` 作为通用贡献治理参考，以 SGLang 的 Kernel Organization Skill 作为 Kernel 工程规范参考，以 TensorRT-LLM 的子系统 Developer Guide 作为复杂 Runtime 边界参考，以 vLLM-Omni 的 PR 证据清单作为性能与多模态验证参考，再通过 Modular Skills 的跨 Agent 分发方式统一 Claude Code、Codex 和 Cursor 的工作流。

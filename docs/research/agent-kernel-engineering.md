# Agentic Kernel Engineering：生成、优化与验证

本文调研 Kernel 生成、优化工作流与评测基础设施，重点比较任务契约、候选执行、正确性验证、性能测量和结果留存。

> 核查范围：公开 README、文档及已有调研记录，未运行项目、设备评测或完整 CI。未固定 commit 的链接可能变化；项目能力、实现路径和性能数据需按目标版本再次确认。架构建议不代表本仓库或上游已实现相应服务。

## 阅读导航

- [范围与分类](#1-范围与分类)
- [项目对比](#2-项目对比)
- [系统架构建议](#3-agent-kernel-系统架构建议)
- [质量门禁与证据](#4-质量门禁与证据)
- [与训练框架集成](#5-与训练框架研发流程的集成)
- [来源与核查边界](#7-来源与核查边界)

## 1. 范围与分类

Agentic Kernel Engineering 不等于一次性让 LLM 写出一段 Triton/CUDA 代码。成熟系统通常需要完成：

1. 读取 PyTorch/reference 实现，提取数学语义、shape、dtype、stride、layout 和边界条件。
2. 选择后端与 DSL，例如 CUDA、Triton、CuTe DSL、TileLang、Ascend C、PyPTO。
3. 生成候选 Kernel，或拆分/融合原始计算图。
4. 编译并执行候选实现。
5. 与 reference 比较数值正确性。
6. 运行 benchmark 和 profiler，识别 memory-bound、compute-bound、occupancy、launch overhead 等瓶颈。
7. 由 Agent 根据证据提出优化并继续迭代。
8. 按任务验收条件接纳通过验证的实现，并保存代码、配置、日志和测量证据。

应将项目分成四类，避免把 Benchmark、工具集和完整 Agent 混为一谈：

| 类别 | 输入 | 主要输出 | 代表项目 |
| --- | --- | --- | --- |
| 自动生成 Agent | PyTorch 程序、算子定义或 reference | 新的 CUDA/Triton/其他 DSL Kernel | KernelAgent、CANNBot Skills |
| 自动优化 Agent | 已有 Kernel、性能目标和硬件 | 经验证的更快 Kernel | KDA、Atrex Kernel Agent、ForgeKernel |
| Agent 工具/工作流 | Coding Agent、MCP/脚本、硬件工具 | 编译、测试、Profiling、评测能力 | KDA、Atrex 工具链 |
| Benchmark/评测 | reference、候选 Kernel、硬件环境 | 正确率、性能分数和可复现结果 | KernelBench、Atrex-Bench |

## 2. 项目对比

| 项目 | 定位 | 主要技术/后端 | 工作流特点 | 建议研究重点 |
| --- | --- | --- | --- | --- |
| [CANNBot Skills](https://github.com/hicann/cannbot-skills) | CANN/昇腾领域 Agent Skills 与工作流 | Ascend C、Catlass、PyPTO、TileLang、Triton Ascend | Plugin 编排 Agents，Agents 绑定 Skills | 多后端算子路径、领域 Skill 组织、NPU 工具链 |
| [KernelAgent](https://github.com/meta-pytorch/KernelAgent) | 多 Agent GPU Kernel 生成与优化 | PyTorch → Triton | 子图提取、并行生成、运行时验证、组合、硬件反馈优化 | 自动拆图、候选并行搜索、端到端组合验证 |
| [KDA](https://github.com/NVlabs/kda) | Coding Agent 驱动的 CUDA Kernel 研发工作流 | CUDA | 研究、实现、验证、性能迭代 | 如何将通用 Coding Agent 组织成可重复的 Kernel 开发流程 |
| [Atrex Kernel Agent](https://github.com/alibaba/atrex-kernel-agent) | Profile-driven GPU Kernel 实现与优化 Agent | CUDA、Triton、CuTe DSL、FlyDSL、TileLang 等 | 建立基线、候选探索、Profile、证据提交、评测记录与提交检查 | 证据绑定、插件化执行/评测、提交契约与测量边界 |
| [ForgeKernel](https://github.com/OpenBMB/ForgeKernel) | 自进化 GPU Kernel Agent | 以仓库发布的 CuTe DSL Kernel 为代表 | 从 reference 出发，分析架构并建立里程碑；每个被接受的 Kernel 成为下一轮 reference | 迭代式优化、跨算子知识积累、硬件探针认证 |
| [KernelBench](https://github.com/ScalingIntelligence/KernelBench) | Kernel 生成评测框架，不是完整 Agent | PyTorch → CUDA 及其他 DSL 扩展 | 生成候选后执行正确性和性能评测 | 建立统一任务集、评测协议和结果比较 |

> 项目状态与能力以链接指向的仓库当前 README/文档为准。项目的硬件支持、模型支持和可复现结果会随 commit、依赖版本及设备变化。

### 2.1 CANNBot Skills：NPU 算子 Agent 体系

仓库：[hicann/cannbot-skills](https://github.com/hicann/cannbot-skills)

README 将其定位为面向 CANN 开发的 Agent Skills 模块，覆盖 Ascend C、Catlass、PyPTO、TileLang、Triton 算子开发，以及 torch.compile 图模式优化、NPU 模型推理优化和 Runtime 开发适配。

**README 中可定位的目录：**

```text
cannbot-skills/
├── ops/                  # 算子 Skills
├── model/                # 模型推理优化 Skills
├── graph/                # 图模式 Skills
├── runtime/              # Runtime Skills
├── infra/                # 基础设施与协作治理
├── tools/                # CANN 工具链 Skills
├── plugins-official/     # 官方 Plugins，含 Agents/Workflows
├── plugins-community/    # 社区 Plugins
├── docs/
└── tests/
```

README 描述的三层组织方式：

- **Plugin（应用编排层）**：通过 `AGENTS.md` 定义 Agent 的协作顺序。
- **Agent（角色执行层）**：承担方案设计、代码开发、代码检视等任务。
- **Skill（知识能力层）**：提供领域知识、工程模板和具体操作能力。

项目列出的算子路径包括：

| 开发路径 | 场景 | README 中列出的入口 |
| --- | --- | --- |
| Ascend C 直调 | 直接调用核函数 | `ops-direct-invoke` / `ops-direct-invoke-flash` |
| Ascend C 注册调用 | ACLNN/GEIR 标准算子接入 | `ops-registry-invoke` |
| Catlass | Cube/Matmul 模板与 Pipeline | `catlass-op-generator` |
| PyPTO | Python Tile 算子 | `pypto-op-orchestrator` |
| TileLang | DSL 算子开发 | `tilelang-op-orchestrator` |
| Triton | Triton Ascend 算子 | `triton-op-generator` |

**示例任务：**

```text
开发一个 Abs 算子，输入 float16，输出 float16。
```

适合从中研究的问题：

- 如何根据任务、硬件和 DSL 选择 Skill？
- 如何把算子生成拆成方案设计、实现、Review、测试等阶段？
- 如何将 CANN 编译器、环境检查、精度测试和性能工具包装成可调用能力？
- 如何让一个 Skill 同时适配 Claude Code、Cursor、Codex 等不同 Agent 宿主？

注意：目录结构和三层架构是项目 README 的公开描述；不要仅凭架构图推断其每个 Agent 的内部模型调用或运行时实现。

### 2.2 KernelAgent：PyTorch 到 Triton 的多 Agent 生成

仓库：[meta-pytorch/KernelAgent](https://github.com/meta-pytorch/KernelAgent)

KernelAgent README 描述的能力包括：

- 静态分析问题，选择轻量路径或完整生成流程。
- 借助 LLM 重构 PyTorch 程序，隔离可融合子图。
- 并行生成 Triton Kernel，并执行严格的运行时验证。
- 将验证通过的 Kernel 重新组合，重建原始 forward。
- 根据硬件 Profiling 结果迭代优化。

README 中可定位的实现入口：

| 路径/模块 | 职责 |
| --- | --- |
| `Fuser/auto_agent.py` | AutoRouter：分析 AST 和计算模式，选择生成路径 |
| `Fuser/orchestrator.py` | Fuser Orchestrator：重构并验证可融合模块 |
| `Fuser/subgraph_extractor.py` | 提取子图及其 op、shape、dtype、参数信息 |
| `Fuser/dispatch_kernel_agent.py` | 将子图规格分发给并行 Kernel Agent |
| `triton_kernel_agent/` | Triton 候选生成与迭代验证 |
| `Fuser/runner.py` | 通过隔离子进程执行候选测试 |
| `Fuser/compose_end_to_end.py` | 将验证通过的 Kernel 组合成端到端实现 |

README 还描述了硬件优化循环：

1. 使用 NCU 收集硬件指标。
2. 进行 Roofline 分析，判断 compute-bound、memory-bound 或利用率不足。
3. LLM 结合指标和代码诊断瓶颈。
4. 生成优化版本。
5. 对照 PyTorch reference 验证数值正确性。
6. 重新 benchmark，并保留 best-so-far 版本；若性能退化则回退。

这套架构的关键价值是：**生成、执行、验证和性能优化是不同阶段，Agent 不能仅凭“代码看起来正确”宣布任务完成。**

### 2.3 KDA：让通用 Coding Agent 执行 CUDA Kernel 研发

仓库：[NVlabs/kda](https://github.com/NVlabs/kda)

KDA 将自身描述为 agent-centric CUDA Kernel 工作流，面向研究、实现、验证和性能迭代。README 同时说明它是早期研究原型，仍在开发中。

README 明确列出的关键文件：

| 路径 | 作用 |
| --- | --- |
| `docs/agent-flow.md` | 最小端到端 Agent 工作流 |
| `prompts/README.md` | Prompt 模板使用说明 |
| `prompts/basic-flow.md` | 新任务的通用起始 Prompt |
| `CLAUDE.md` | 仓库级 Agent 指令 |
| `CONTRIBUTING.md` | 贡献流程与 DCO sign-off |
| `THIRD_PARTY_NOTICES.md` | 第三方组件和许可披露 |

值得研究的不是某一个 Kernel 生成模型，而是如何将通用 Coding Agent 约束在一套可重复流程内：

```text
任务与约束
   ↓
读取参考实现、硬件和测试条件
   ↓
研究实现方案
   ↓
编写 CUDA Kernel
   ↓
编译与正确性验证
   ↓
性能测量与迭代
   ↓
提交代码、测试和性能证据
```

KDA 特别适合与客户端适配与共享指令设计一起研究：`CLAUDE.md` 负责项目上下文，`docs/agent-flow.md` 和 Prompt 模板承载研发流程，脚本和测试负责执行验证。

### 2.4 Atrex Kernel Agent：绑定候选与评测证据

仓库：[alibaba/atrex-kernel-agent](https://github.com/alibaba/atrex-kernel-agent)

已有核查记录显示，其流程由持续运行的 Coding Session 管理候选与 Git 历史。提交候选时要求精确 commit 已有正确性通过、性能结果可解析的评测记录，并满足所选源码策略检查。

需要区分提交校验与性能晋级：`submit-kernel` 不设置性能提升门槛，也不自行重新评测、运行 ABBA、晋级或回退。Supervisor 提供测量、检查与审计能力，不能据此推断其会自动替换当前最佳实现。详见下方版本差异记录，使用前仍需核对目标版本。

可借鉴的机制包括候选源码与记录绑定、执行和评测边界分离、保留日志与运行环境。自动晋级、独立复测和恢复策略应作为待验证能力或自建设计，不写成上游既有行为。

### 2.5 ForgeKernel：自进化与跨算子知识积累

仓库：[OpenBMB/ForgeKernel](https://github.com/OpenBMB/ForgeKernel)

ForgeKernel README 将其定位为 self-evolving GPU kernel agent。它从一个 reference Kernel 开始，通过运行、计时和 Profiling 理解其架构，将优化过程拆成架构优先的里程碑，再交给 Coding Agent 实现；每个被接受的 Kernel 成为下一轮 reference。经硬件探针认证的发现会积累到跨算子共享知识库。

README 公布了 Hopper 和 Blackwell 上多个算子的评测结果，并在 `kernels/` 目录发布生成的 Kernel。具体性能结论应以仓库 README、对应论文和 `kernels/README.md` 中的设备、版本和基线说明为准。

值得重点研究：

- 如何把优化任务拆成可测量的 milestone。
- 如何让 Agent 先理解已有实现的架构，而不是盲目重写。
- 如何定义候选晋级和回退条件。
- 哪些优化发现可以跨 shape、算子和 GPU 架构复用。
- 知识库如何通过真实硬件实验认证，避免把模型猜测当成事实。

### 2.6 KernelBench：评测基础设施，而不是完整 Agent

仓库：[ScalingIntelligence/KernelBench](https://github.com/ScalingIntelligence/KernelBench)

KernelBench 的目标是评测 LLM 是否能为 PyTorch 程序生成正确且高效的 GPU Kernel。README 将任务划分为四个层级：

- Level 1：单算子。
- Level 2：简单融合模式。
- Level 3：完整模型架构。
- Level 4：Hugging Face 模型。

核心评估：

- **Correctness**：与 PyTorch reference 在随机输入上比较。
- **Performance**：重复计时并与 reference 比较运行时间。

KernelBench README 明确说明它是 Benchmark 和 Toolkit，不提供复杂的 Agentic Scaffold。因此，适合将它作为 Agent 的统一评测环境，而不是误认为它本身就是一个多 Agent Kernel 生成系统。

## 3. Agent Kernel 系统架构建议

建议把自动算子研发系统设计为以下闭环：

```text
                  用户任务 / PyTorch Reference
                              |
                              v
                    [Task Understanding]
                 解析 op / shape / dtype / layout
                              |
                              v
                    [Backend & Plan Agent]
               选择 CUDA / Triton / TileLang / CANN
                              |
                              v
                     [Kernel Developer]
                       生成候选实现
                              |
                              v
                  [Compile & Correctness Gate]
                   编译 / 单测 / 数值误差检查
                       |              |
                    失败              通过
                       |              |
                  修复候选             v
                              [Profiler]
                       NCU / CANN Profiler
                              |
                              v
                       [Optimization Agent]
                   诊断瓶颈、提出优化假设
                              |
                              v
                       [Benchmark Gate]
                   同环境测量、对照 baseline
                              |
                       未提升 / 退化
                         |       |
                         v       v
                       回退   [Supervisor]
                                  |
                                  v
                           晋级并保存证据
                                  |
                                  v
                         [Kernel Knowledge Base]
```

职责应明确分离：

| 角色 | 负责内容 | 不应拥有的权限/职责 |
| --- | --- | --- |
| Task Planner | 解析需求、约束和验收标准 | 不直接宣布 Kernel 正确 |
| Backend Selector | 选择目标 DSL、设备和实现路线 | 不忽略硬件/版本兼容限制 |
| Kernel Developer | 生成与修改候选代码 | 不自行篡改测试基准 |
| Correctness Verifier | 执行 reference 对比和边界测试 | 不依赖 LLM 主观判断通过 |
| Profiler | 收集硬件计数器和耗时 | 不把未经测量的推断写成结果 |
| Optimization Agent | 根据证据提出并实施优化 | 不绕过 correctness gate |
| Supervisor | 检查证据并决定晋级/回退 | 不接受没有源码快照的性能结论 |
| Knowledge Curator | 归纳已验证的硬件/算子知识 | 不将未经验证的模型输出入库 |

## 4. 质量门禁与证据

以下五层是建议的验收模型，按任务和目标项目要求选择适用项；独立算子不机械要求完整模型训练，纯正确性修复也不以性能提升作为通过条件。

| Gate | 检查内容 | 失败处理 |
| --- | --- | --- |
| G0：静态约束 | 任务明确禁止的 fallback、非法 API、依赖和接口约束；静态检查不能证明不存在越界 | 拒绝候选或要求修复 |
| G1：编译 | 目标设备和目标工具链能够编译 | 保存编译日志，返回修复 |
| G2：正确性 | 多组随机输入、边界 shape、dtype、stride、mask、forward；需要训练梯度时验证 backward | 不允许进入性能晋级 |
| G3：模型级验证 | 影响模型路径时验证端到端输出或训练行为与 reference 对齐 | 回退到原始实现 |
| G4：性能 | 相同设备和输入、warmup、重复测量、噪声控制、baseline 对照 | 性能优化未证明收益则不宣称成功；兼容与正确性改动按其验收条件判断 |

建议记录的机器可读证据：

```json
{
  "operator": "example_op",
  "candidate_revision": "git-sha-or-content-hash",
  "backend": "triton",
  "device": "GPU model",
  "software": {
    "driver": "version",
    "runtime": "version",
    "compiler": "version"
  },
  "correctness": {
    "passed": true,
    "max_abs_error": 0.0,
    "max_rel_error": 0.0,
    "test_cases": 100
  },
  "performance": {
    "baseline_us": 12.0,
    "candidate_us": 10.0,
    "speedup": 1.2,
    "warmup": 20,
    "repetitions": 100
  },
  "artifacts": [
    "source/",
    "test-log.txt",
    "profile/",
    "benchmark.json"
  ]
}
```

以上 JSON 仅展示字段关系，数值为虚构示例，不是实测数据或任一项目的原生 schema。真实记录还需包含输入集及 reference 标识、容差、baseline revision、计时边界、缓存策略与样本波动；未执行项使用明确状态，不用零值冒充结果。

## 5. 与训练框架研发流程的集成

| 训练框架/算子栈 | Agent 可辅助的任务 | 必须保留的专项验证 |
| --- | --- | --- |
| Megatron-LM | 融合算子、Attention、Norm、GEMM、MoE Kernel | 并行组语义、数值精度、分布式训练结果 |
| DeepSpeed | Fused Optimizer、通信/内存相关 Kernel | ZeRO 状态一致性、通信正确性、训练收敛 |
| TorchTitan | PyTorch 原生算子与训练路径优化 | eager/compile 对照、模型级 loss 和性能 |
| verl / slime / vime | rollout、logprob、sampling、reward 相关算子 | token 对齐、采样语义、训练与 rollout 一致性 |
| ms-swift / Unsloth | LoRA、量化、激活与优化器相关 Kernel | 量化误差、梯度正确性、模型训练行为 |
| Liger Kernel | Triton fused operators | correctness、convergence、benchmark 三层验证 |
| CANN / Ascend | Ascend C、Catlass、PyPTO、TileLang、Triton Ascend | NPU 编译、精度、设备侧性能和 Runtime 兼容 |

## 6. 推荐阅读顺序

如果要在团队内开展专项技术调研，建议按下面顺序深入读代码：

1. **CANNBot Skills**：先理解多 DSL、多后端算子研发的 Skill/Agent/Plugin 组织方式。
2. **KernelAgent**：研究从 PyTorch 计算图到并行 Triton 生成、组合、验证和优化的完整系统。
3. **KDA**：研究通用 Coding Agent 如何通过项目指令、Prompt 和工具流程承担 CUDA Kernel 研发。
4. **Atrex Kernel Agent**：研究候选源码与评测记录绑定、提交校验及 Supervisor 的实际职责。
5. **ForgeKernel**：研究 milestone curriculum、自进化优化和跨算子知识积累。
6. **KernelBench**：最后建立统一评测基线，比较不同 Agent、模型、Prompt 和搜索策略。

## 7. 来源与核查边界

### 项目与实现入口

- CANNBot Skills README：https://github.com/hicann/cannbot-skills
- KernelAgent README：https://github.com/meta-pytorch/KernelAgent
- KernelFalcon 介绍（PyTorch Blog）：https://pytorch.org/blog/kernelfalcon-autonomous-gpu-kernel-generation-via-deep-agents/
- KDA README：https://github.com/NVlabs/kda
- KDA Agent Flow：https://github.com/NVlabs/kda/blob/main/docs/agent-flow.md
- KDA Prompt Flow：https://github.com/NVlabs/kda/blob/main/prompts/basic-flow.md
- Atrex Kernel Agent README：https://github.com/alibaba/atrex-kernel-agent
- Atrex-Bench：https://github.com/alibaba/atrex-bench
- ForgeKernel README：https://github.com/OpenBMB/ForgeKernel
- KernelBench README：https://github.com/ScalingIntelligence/KernelBench

### 核查边界

- CANNBot 的架构、目录和 DSL 支持来自其公开 README。
- KernelAgent 的模块职责与生成/优化流程来自其公开 README；不同设备支持以当前仓库安装说明为准。
- KDA README 将其定位为早期研究原型，不能把它描述为成熟生产系统。
- Atrex Kernel Agent 的能力和工具后端以当前 README 为准；生产部署前仍需验证目标硬件、工具版本和评测流程。
- ForgeKernel 的性能结论属于项目公开报告，使用时必须同时引用其测试 GPU、软件栈和 baseline。
- KernelBench 是评测框架，不是完整 Agent 系统。
- 对此前提及但本文未取得足够一手仓库证据的 GEAK、KernelFoundry、Cuda-OSS、KernelOPT，不纳入“已核实重点项目”比较；后续如取得明确仓库与实际文件，可作为候选补充调研。

## 8. 工程启示

Agentic Kernel Engineering 应当成为训练框架工程规范中的独立领域。值得沉淀的并非单纯的 Prompt，而是以下工程机制：

- 通过 Skill/Agent 分层封装硬件、编译器和 DSL 知识。
- 通过 reference 和测试输入固定任务语义。
- 通过隔离执行与确定性测试约束候选代码。
- 通过真实硬件 Profiling 建立优化证据。
- 通过 Supervisor 和晋级/回退机制控制质量。
- 通过可追溯 artifact 和知识库积累长期优化经验。

性能优化的验收应包含指定软硬件上的正确性、受影响模型路径的验证，以及可复现的收益测量。证据缺失时明确说明范围；生成成功、编译通过和优化成功是不同结论。

### Atrex 的版本差异记录

2026-11-24 调研复核的 README 描述了轻量工作流：一个持续运行的 Coding Session 管理自身 Git 历史；提交候选需要该 commit 已有完整、正确性通过且性能结果可解析的评测记录，并接受选定的源码策略检查。

`submit-kernel` **不设置性能提升门槛，也不会自行重新评测、运行 ABBA、晋级或回退**。Supervisor 提供测量、检查和审计等能力，不强制将某条轨迹替换为另一条轨迹的代码。不能将旧版流程或本文建议的晋级策略写成当前项目行为。

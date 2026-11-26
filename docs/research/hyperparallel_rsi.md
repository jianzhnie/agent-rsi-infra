# HyperParallel Agent 工作流与 RSI 机制

## 调研范围

对象为 [weich97/hyper-parallel 的 .agent 目录](https://github.com/weich97/hyper-parallel/tree/f8572d714007e52baad16b60096596a510d25114/.agent)，来自 `feat/agent-framework-consolidation` 分支，固定 revision 为 `f8572d714007e52baad16b60096596a510d25114`。后续分支变化不包含在本文结论中。

本文依据目录清单、27 个 Skill 入口，以及关键规则、证据契约和工具源码进行解读；未运行上游测试、模型、设备实验或真实客户端加载。下文区分文件职责、文档规定和执行依赖，不将目录存在或上游历史结果视为本次验证。

## 1. 定位与目录

`.agent/` 是 HyperParallel 的开发、验证和实验工作流资源层。它包含可执行工具和实验控制器，但不构成可脱离目标训练框架、客户端及设备环境运行的通用 Agent Runtime。

```text
.agent/
├── AGENTS.md       资源目录、工作流入口和检查命令
├── agents/         专项角色、角色指南及辅助脚本
├── commands/       8 个命令定义
├── rules/          工程、分布式、测试与数值验收规则
├── skills/         27 个任务入口及参考、脚本、模板
├── scripts/        目录检查和 RSI 经验管理工具
├── learning/       经验注册表
├── examples/       模型接入与复现实验示例
├── tests/          工具与流程的回归测试
├── hooks/          风格、算子 YAML 与提交消息检查
└── settings.json   编辑后 Hook 绑定
```

角色说明谁负责某类问题，Skill 描述如何完成任务，规则约束实现与验收，脚本执行确定性操作。命令和 Hook 能否被发现、角色能否委派，取决于客户端配置；`.agent/` 本身不能证明这些机制已加载。

## 2. 角色与命令

### 角色分工

[agents/](https://github.com/weich97/hyper-parallel/tree/f8572d714007e52baad16b60096596a510d25114/.agent/agents) 的目录索引列出 15 个角色：

| 类别 | 角色 | 关注范围 |
| --- | --- | --- |
| 规划与审查 | planner、code-reviewer、simple-code-reviewer、code-verifier | 实施规划、审查和验证 |
| 正确性调查 | formal-verifier | 训练契约与候选缺陷调查 |
| 张量与并行 | dtensor-dev-expert、tensor-dev-expert、fsdp-dev-expert、pipeline-dev-expert、ep-dev-expert | DTensor、mesh、分片、梯度归约、流水线和专家并行 |
| 激活与模型集成 | activation-dev、llamafactory-hp | 重计算、激活 swap 和 LlamaFactory 集成 |
| 策略与负载 | parallel-strategy-analyzer、sapp-parallel-strategy、moe-load-balancer | 并行策略、搜索和专家负载 |

目录还包含 activation/FSDP 指南和辅助 Python 文件，因此角色数量不能直接按文件数计算。细分角色有助于限定任务，但部分角色与 Skill 职责交叉，是否需要独立角色应依据实际委派效果判断。

### 命令入口

[commands/](https://github.com/weich97/hyper-parallel/tree/f8572d714007e52baad16b60096596a510d25114/.agent/commands) 包含 code-review、commit、create-pr、formal-verify、gen-commit-msg、optimize-strategy、test、validate-strategy。它们是工作流定义，不是跨客户端通用命令。提交、评论、触发门禁和创建 PR 等动作仍需明确授权及相应平台配置。

## 3. Skill 功能分组

以下分组用于阅读，不表示每项都有独立执行器或同等验证程度。

| 分组 | Skill | 主要职责 |
| --- | --- | --- |
| 通用开发 | add-unit-test、code-review、debug、feature-doc、knowledge-retrieval | 测试设计、审查、单机排障、文档与源码检索 |
| 贡献与门禁 | autogit、gate-doctor | Git 工作流和 GitCode/Jenkins 门禁诊断、重试及修复 |
| 分布式算子 | dist-op-analysis、dist-op-dev、cluster-debug | 接口与布局分析、实现测试、多 rank 故障诊断 |
| 模型与数值 | hf-model-integration、hf-model-precision-validation、precision、formal-verification | 接入模型、数值验收、张量差异定位和规格驱动调查 |
| 性能分析 | profiling、memory-analysis、perf-playbook、mfu-riser | Ascend 采集、显存归因、优化方法和受预算约束的 MFU 实验 |
| 并行策略 | parallel-strategy-analyzer、sapp-parallel-strategy、strategy-validator、strategy-optimizer | 布局分析、符号搜索、实测比较与候选迭代 |
| MoE | moe-profiler、routing-validator、moe-optimizer | 提取事实、检查路由与梯度证据、形成优化候选 |
| 实验与资源评估 | autoresearch、bringup-benchmark | 管理实验循环，评估接入流程和工具资产的改进效果 |

几个容易混淆的边界：

- **接入与验收分开。** hf-model-integration 面向功能实现；hf-model-precision-validation 面向相同模型状态、输入与执行模式下的数值比较。能运行不等于验收通过。
- **事实与解释分开。** moe-profiler 的定位是提取事实；routing-validator 判断采集证据是否满足契约；moe-optimizer 负责解释与候选选择。
- **估算与实测分开。** 策略分析或符号搜索不能替代实际训练计时、显存和正确性结果。
- **LLM 推理与证明分开。** formal-verification 适配外部 FM-Agent；其入口明确说明，LLM 推理不是机器检查的形式化证明。

## 4. 三条主要工作流

### 4.1 开发与数值验证

分布式算子流程先分析官方接口、位置参数与 keyword-only 参数、分片和广播约束，再形成实现计划。该上游流程要求确认计划后进入 dist-op-dev，之后执行相关测试；这不是其他仓库必须照搬的审批政策。

模型接入使用阶段产物和退出条件组织任务，并通过运行目录恢复进度。数值验证强调：

1. reference 应来自定义模型语义的权威实现，不能让基线和候选共同调用同一错误实现。
2. 对齐权重、输入、mask、position 和状态，比较输出、输入梯度及训练参数梯度。
3. 核对模型结构与配置条件下的参数，不能只为方便加载而制造同形状参数。
4. 检查跨层状态的生产者与消费者、跨 forward 泄漏，以及重计算 replay 的副作用。
5. 分布式布局自洽、模块数值对照和 checkpoint 恢复分别验证，互不替代。

依据：[模块对照与重计算](https://github.com/weich97/hyper-parallel/blob/f8572d714007e52baad16b60096596a510d25114/.agent/skills/hf-model-precision-validation/references/module-parity-and-recompute.md)。其中具体精度配置、步数和阈值属于目标项目约定，迁移时应重新确定。

### 4.2 性能实验

```text
固定模型、输入、初始状态、设备与验收条件
→ 采集并归因瓶颈
→ Agent 提出候选
→ 控制器运行实验并保存证据
→ 正确性检查与性能比较
→ 保留、丢弃或记录失败
→ 独立确认与复盘
```

[autoresearch](https://github.com/weich97/hyper-parallel/blob/f8572d714007e52baad16b60096596a510d25114/.agent/skills/autoresearch/SKILL.md) 文档规定：实验测量已提交代码；优化路径必须有生效证据；正确性门禁失败后指标无效；失败实验留在历史中，恢复目标文件采用新的前向提交。它会执行命令并创建提交，不能当作只读提示词使用；其保护逻辑本次未运行验证。

[mfu-riser](https://github.com/weich97/hyper-parallel/blob/f8572d714007e52baad16b60096596a510d25114/.agent/skills/mfu-riser/SKILL.md) 将 Agent 规划与控制器执行分开，并要求审计有效模型 FLOPs、HFU 证据覆盖、有效 tokens/s/device 和显存。相同随机种子不足以证明跨布局参数相同，应核对逻辑参数及各 rank 实际执行状态。

[strategy-optimizer](https://github.com/weich97/hyper-parallel/blob/f8572d714007e52baad16b60096596a510d25114/.agent/skills/strategy-optimizer/SKILL.md) 串联分析、配置生成和 benchmark。入口说明当前执行调度器限于单节点，PSA 的 num_nodes 必须为 1，cards_per_node 与设备数量匹配；它不是多节点生产部署系统。候选结果也只能称为本次搜索中满足验收的实测结果，不能称为全局最优。

### 4.3 经验沉淀与资产评估

[experience-consolidation](https://github.com/weich97/hyper-parallel/blob/f8572d714007e52baad16b60096596a510d25114/.agent/skills/autoresearch/references/experience-consolidation.md) 将实验验收与 RSI 改进分别报告，经验按以下方式处理：

| 决定 | 处理 |
| --- | --- |
| new | 新增有证据、可复用且未被覆盖的经验 |
| update | 更新已有规则，补条件、反例或回归 |
| reuse | 引用已有内容，不重复登记 |
| defer | 暂存假设，列出缺失证据 |
| reject | 不推广局部、重复或无依据的结论 |

rsi_learning.py 负责资源清单、检索、证据与覆盖检查、候选应用和报告；registry.json 登记经验归属、claim、fingerprint、证据 hash、qualification 和 revision。登记为 validated 只代表该流程中的记录状态，不构成本次独立复核。语义去重与因果解释仍由 Agent 审查，hash 相同不能代替语义判断。

该流程支持 acceptance 和 continuous 两种更新时机，并可能修改资源或创建本地提交。它比本仓目前的人工评审流程更主动，不能仅复制脚本就获得可靠的自动晋级能力。

[bringup-benchmark](https://github.com/weich97/hyper-parallel/blob/f8572d714007e52baad16b60096596a510d25114/.agent/skills/bringup-benchmark/SKILL.md) 评估的是接入 Skill、清单和通用工具这些资产，不是模型训练速度。方法包括固定提交快照、确定性检查、独立 Agent 试验、重复校准、A/A、A/B 和故障注入。差异低于测量分辨率时报告不可区分；漏检注入故障属于盲点，不能算通过。评估器本身不应由被测候选随意修改。

## 5. 规则、Hook、示例与测试

| 模块 | 内容与边界 |
| --- | --- |
| rules/ | 分布式实现、算子测试、精度验收、成本模型、代码风格和 RL 模块约束；具体路径与阈值按目标版本使用 |
| multi-platform-features.md | 实际正文主要约束列表/集合 API 的 handle 覆盖与非首元素测试，不能仅凭文件名理解为完整多硬件规范 |
| settings.json | 使用 PostToolUse 结构绑定 Write、Edit、MultiEdit 后的风格与算子 YAML 检查；是否生效取决于客户端配置 |
| hooks/commit-msg | 提交消息检查；文件存在不表示已安装为 Git Hook |
| examples/ | HF 文本模型构建、数据准备、训练配置、等价性判断和复现材料，以及 VLM 合成数据脚本；执行需要目标依赖与资源 |
| tests/ | 实验循环、资产评估、显存、profiling、精度、RSI、模型接入及资源契约等工具回归；存在测试文件不等于测试已通过 |

目录入口给出的检查命令如下，仅供在上游 checkout 中核对使用；本文未执行：

```bash
python .agent/scripts/check_agents_catalog.py
PYTHONPATH="$PWD/.agent/examples:$PWD${PYTHONPATH:+:$PYTHONPATH}" python -m pytest -q .agent/tests
```

check_agents_catalog.py 比较目录索引与实际 Skill、角色集合，并排除 -guide 角色指南。它不验证客户端加载、脚本行为或完整的资源链接。

## 6. 阅读时需要警惕的表述

- **routing-validator 的细化契约比入口示例更准确。** 普通参数 checkpoint 不含 routing 或梯度证据。Top-K assignment 数量应对照 input_tokens × top_k，置换应验证 assignment-slot 双射；缺失证据为 UNVERIFIED，而不是 PASS。非零梯度只证明观察到梯度流，不能证明数值等价。见 [证据契约](https://github.com/weich97/hyper-parallel/blob/f8572d714007e52baad16b60096596a510d25114/.agent/skills/routing-validator/references/evidence-contract.md)。
- **精度阈值有适用层级。** loss 轨迹的汇总误差不能直接作为单算子、单张量或每一步的容差；较短运行也不能声称通过更长窗口的标准。见 [precision-acceptance](https://github.com/weich97/hyper-parallel/blob/f8572d714007e52baad16b60096596a510d25114/.agent/rules/precision-acceptance.md)。
- **硬件与软件版本有约束。** profiling、memory-analysis 和性能案例主要面向 Ascend、torch_npu、CANN、HCCL 及 HyperParallel 接口；不能直接推广为 CUDA 或任意框架能力。快照也不一定捕获峰值。
- **门禁与 Git 操作有副作用。** gate-doctor 绑定 GitCode/Jenkins，autogit 和实验控制器可能提交、评论或触发任务。文档还包含破坏性清理建议，使用前应逐项审查；不要将上游指令当作本地授权。
- **配置分层不等于自动化已成立。** commands、roles、Hooks 的实际发现与执行需要真实客户端验证；规则中的期望不能代替执行证据。

## 7. 对本仓的借鉴建议

| 优先级 | 借鉴内容 | 建议落点 |
| --- | --- | --- |
| P0 | 固定资产版本、A/A 校准、故障注入和不可区分判定 | 任务证据规范与 Skill 效果评估 |
| P0 | 独立模型 reference、输出/梯度对照、跨层状态及重计算边界 | training-inference-change 的训练参考 |
| P0 | new/update/reuse/defer/reject 分类，优先更新而非重复新增 | improve-optimization-skills |
| P0 | 各 rank 的实际代码与参数核对、有效 FLOPs 和同工作负载对照 | profile-whole-update、verify-training-semantics |
| P1 | routing 捕获范围、Top-K 计数、置换和缺失证据契约 | moe-ep-communication |
| P1 | 分配归属、跨快照增长及快照与峰值差距 | manage-memory-lifetimes |

优先提炼方法和证据契约，复用本仓现有 Skill。暂不整体迁入角色、GitCode/Jenkins 流程、Ascend 执行器、自动提交或经验更新服务。本文是调研与建议，不是迁入记录，也不代表本仓已实现这些能力。

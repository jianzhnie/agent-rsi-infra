# AI Infra 变更验证

本文用于选择目标项目的数值、分布式、兼容性与性能检查。它是本仓库归纳的验证指南，不表示所列框架、设备或模型已完成验证。先读取目标仓库指令，再按 [任务路由](component-skills.md) 选择 Skill。

通用开发规则见 [AGENTS.md](../AGENTS.md) 和 [贡献指南](../CONTRIBUTING.md)；客户端布局见 [部署说明](deployment.md)。项目概览、公开规范与核查范围见 [训练框架调研](research/training-frameworks-agent-engineering.md)、[推理框架调研](research/inference-frameworks-agent-engineering.md) 和 [Kernel 工程调研](research/agent-kernel-engineering.md)。采用内容与来源见 [来源与项目映射](../.agents/skills/training-inference-change/UPSTREAM.md#调研方法的项目映射)。

<a id="validation"></a>

## 如何选择检查

先说明改动影响的输入输出、状态、执行路径和支持范围。表中的主要验证针对对应行为变更；额外检查按实际影响选择。普通文档或无行为影响的配置维护不因此要求 GPU 或模型评测。

- 使用目标项目已有的测试入口、fixture 与独立 reference，覆盖具体失败场景。
- 区分静态检查、CPU 行为、设备数值、模型集成和性能结果；缺少环境时记录未运行项。
- 新增或修改并行策略时，明确 rank 映射、进程组、通信顺序和拓扑；不能只报告单 rank forward 通过。

<a id="training"></a>

## 训练与 RL

| 变更 | 主要验证 | 按影响补充 |
| --- | --- | --- |
| 模型结构与注册 | 加载、forward、loss、参数与配置 | 多步训练、模型指标 |
| 数据与 packing | 样本、mask、position、label 对齐 | 分布统计与吞吐 |
| 并行策略与通信 | rank 映射、进程组、多卡行为 | 多节点、拓扑、超时与故障 |
| 优化器与训练状态 | 更新公式、状态保存恢复 | 多步数值与长跑稳定性 |
| Checkpoint | 保存、加载、断点恢复 | 版本兼容、重新分片、异常恢复 |
| RL rollout | token、logprob、终止与采样语义 | 多轮交互、权重同步、异步流程 |
| Reward/verifier | 输入输出、边界与异常 | 分布偏差、训练影响 |

<a id="inference"></a>

## 推理与服务

| 变更 | 主要验证 | 按影响补充 |
| --- | --- | --- |
| 模型接入 | 权重映射、processor、forward、注册 | 精度、长上下文、在线服务 |
| KV Cache | 分配、回收、页表与状态生命周期 | Prefix Cache、并发、跨进程传输 |
| 调度器 | 队列、状态转换、抢占与批处理 | 混合请求、突发负载、公平性与尾延迟 |
| 量化 | 层级误差、输出与异常输入 | 模型质量、长上下文、性能 |
| 分布式推理 | 多 rank、通信顺序、错误传播 | 多节点、并行规模与故障恢复 |
| API 与配置 | 请求响应、Schema、默认值 | 旧配置与真实客户端兼容 |
| 多模态流水线 | 阶段协议、流式、取消与资源释放 | 音画同步、背压、端到端任务质量 |

模型质量评测需固定 harness、版本、数据集及划分、样本数和计分方式；评测工具的依赖尽量与服务环境隔离，避免为评测改动被测服务。工具按任务和目标项目选择，不统一要求 `sgl-eval`。

显式记录实际生效的 temperature、top_p、top_k、随机种子、最大输出长度、thinking 设置及 chat-template 参数。评测工具可能覆盖模型默认值，`thinking` 与 `enable_thinking` 等模板键也不通用，应核对最终请求。复现 CI 时使用 CI 的同一设置；部署评测先核对官方模型指南。不同 harness 或设置的分数不能直接归因为模型或代码优劣；更换工具时先建立可比对照。

<a id="kernels"></a>

## Kernel 与编译器

| 变更 | 主要验证 | 按影响补充 |
| --- | --- | --- |
| CUDA/Triton 等 Kernel | 编译、reference 对照、shape/dtype/stride 边界 | 梯度、内存检查、多架构、性能 |
| Kernel 选择或迁移 | 调用覆盖、选择逻辑、支持范围 | 打包、旧路径清理、模型级结果 |
| Compiler IR/Pass | IR 与语义回归 | 多 Target、代码生成、执行结果 |
| 公共 C++/Python 接口 | 编译或导入、单元与接口测试 | ABI/API、依赖版本、生成文档 |

### 计算契约

Kernel 实现与评审至少需要明确：

| 内容 | 需要说明的问题 |
| --- | --- |
| 数学语义 | 参考实现、归约顺序、近似算法及允许误差 |
| 张量约束 | shape、dtype、stride、layout、对齐与动态范围 |
| 边界行为 | 空输入、非整齐尺寸、mask、NaN/Inf；按算子语义选择 |
| 执行条件 | 设备架构、工具链、并发、stream 与图捕获要求 |
| 集成方式 | 调度与选择逻辑、调用者、回退路径、训练时的梯度支持 |

### 验证层级

1. **编译与执行。** 目标工具链能够生成并运行实现；按风险检查越界、竞态与同步问题。
2. **数值正确性。** 在代表性输入和边界条件上与 reference 对比，说明容差。需要反向传播的算子同时验证梯度。
3. **模型集成。** 替换后检查端到端输出或训练行为。训练相关数值路径按影响补充多步 loss、梯度或权重对照。
4. **性能。** 在真实调用形状与相同环境下测量，记录收益、退化、显存以及编译开销。

多组随机输入通过，只能证明这些样本上的表现；涉及模型行为时，仍需模型级验证。

## 性能测量

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

## 结果与证据

报告实际执行的命令、版本、输入、设备、结果与原始产物，按影响说明失败、阻塞和未运行项。使用 [任务契约与验证报告](task-evidence.md) 和 [训练优化任务模板](templates/training-optimization-task.md)，不另维护一套 PR 模板。采集工具及其开销见 [性能诊断](performance-profiling.md)。

评测可比性与部署基线方法参考 SGLang 固定版本的 [prefer-sgl-eval.md](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/prefer-sgl-eval.md) 和 [cookbook-first.md](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/cookbook-first.md)；许可和提炼边界见 [贡献说明](../CONTRIBUTING.md#调研实践的落地)。

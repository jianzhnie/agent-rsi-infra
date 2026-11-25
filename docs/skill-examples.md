# Skill 使用样例

以下是可直接改写的任务输入，不是已完成的真实任务记录。先读目标项目指令，再加载对应 `SKILL.md`；调用方式以目标客户端实际支持为准，可在任务中明确要求“读取并使用指定 Skill”。不要假设所有客户端都有同名斜杠命令。

每次输入至少给出目标 checkout/revision、问题或改动范围、已有日志/测试、允许操作和可用设备。执行后按[任务与证据规范](task-evidence.md)交付命令、结果、产物和未执行原因。

## 按任务选择

表中的路径均位于 `.agents/skills/<名称>/SKILL.md`，可从[资源索引](../.agents/README.md)打开。这些样例覆盖索引中的全部 Skills，不要求一次加载多项。

| Skill | 输入与典型请求 | 排除场景 | 应交付的证据 |
| --- | --- | --- | --- |
| code-reviewer | 给出 base/head 和关注范围：“使用 light 审查该 diff” | 自动修复或没有证据的风格建议 | 位置、触发条件、后果、覆盖边界；无发现也说明范围 |
| install-skill-from-github | 给出 GitHub Skill URL、固定 commit、目标目录：“审查并迁入完整技能” | 安装 Python 包、执行下载的脚本 | 来源、解析 revision、许可、目标路径、安装结果 |
| shell-check | 给出脚本或目录：“检查这些 Shell 文件” | 证明脚本业务逻辑正确 | 选中文件、bash -n/shellcheck 命令与逐项结果 |
| pt2-bug-basher | 给出 PyTorch revision、torch.compile 最小复现及错误：“显式使用此 Skill 排障” | 无复现的泛化编译建议 | 复现、归因实验、失败边界与回归测试 |
| add-or-fix-type-checking | 给出 Transformers checkout 和类型错误日志：“修复这些类型错误” | 将上游工具约定套用任意项目 | 类型检查及受影响行为测试结果 |
| kernel-microbenchmark | 给出算子、baseline/candidate、shape/dtype、设备：“比较延迟” | 服务端端到端吞吐测试 | reference、数值结果、计时设置、原始样本与环境 |
| triton-kernel-writing | 给出 Kernel、调用方和 reference：“优化尾块处理” | 无目标代码的性能承诺 | 数值与边界测试、特化限制、性能证据或未测原因 |
| model-recipes | 给出模型 revision、GPU 型号/数量与目标：“查找适用 vLLM recipe” | 把 recipe 当作已验证性能 | 来源、版本限制、配置建议及未验证项 |
| model-microbenchmark | 给出 vLLM 版本、模型、并行配置与精确 batch：“比较 forward 延迟” | 单 Kernel 或 serving 吞吐测量 | 实际命令、输入形状、原始样本、模型/环境版本 |
| debug-distributed-hang | 给出 SGLang revision、各 rank 日志、堆栈和启动配置：“定位首个分歧” | 未经授权终止进程或重启集群 | 时间线、退出/通信/逻辑分歧证据、待验证假设 |
| llm-torch-profiler-analysis | 给出已有 trace、框架版本和采集设置：“离线分析瓶颈” | 默认启动在线采集或把 trace 当 benchmark | Kernel 汇总、重叠线索、采集限制和复核建议 |
| mechanical-refactor-verify | 给出移动前后 revision 和映射：“证明此文件拆分为指定机械变换” | 证明业务语义完全等价 | 可重放命令、变换差异、剩余差异与行为测试 |
| code-cleanup | 给出疑似死代码、调用与注册路径：“核实后清理” | 仅凭文本搜索无命中删除公共 API | 可达性/注册证据、兼容影响和受影响测试 |
| kernel-organization | 给出目标 SGLang Kernel API、已有实现及调用方：“确认归属后迁移” | 将 SGLang 路径规范强加其他框架 | 实现清单、放置理由、注册/调用迁移与验证 |
| kl-consistency-test | 给出模型、prefill/decode 输入、阈值和 logprob：“定位 KL 偏差” | 未定位差异就放宽阈值 | batch 不变性、路径差异实验及阈值依据 |
| flashinfer-add-cuda-kernel | 给出 FlashInfer revision、CUDA 实现、API 契约和设备：“接入此算子” | 一般框架的 Kernel 注册 | FFI/JIT/API/trace 集成、数值与打包检查 |
| training-inference-change | 给出训练/rollout/推理改动、配置及验收：“选择相关契约并实施” | 普通文档修改或替代专项诊断 | 受影响契约、分层测试、设备/模型限制与结果 |

## Kernel 优化交付示例

任务输入示例：

> 在指定 checkout 和 revision 上优化已有 Triton 算子。先查相同契约实现，保持公开 API，覆盖约定的 shape/dtype 与尾块。使用独立 reference 和项目约定容限；在同一 GPU 上测量 baseline/candidate。先提交测试与测量计划，按现有授权执行；设备不可用时保留未执行项，不以模拟数字替代。

执行顺序见 [README](../README.md#典型任务优化一个-triton-kernel)。以下报告模板中的占位符必须替换为真实产物，不能作为通过证据：

```markdown
# Validation Report
- 任务与范围：<task_id、目标、验收契约、允许改动>
- 代码：<baseline commit、candidate commit 或基准 commit + diff/hash>
- 输入与 reference：<shape/dtype、seed、reference 版本、容限、边界输入>
- 环境：<GPU 型号/数量、驱动、runtime、框架、编译器版本>

| 验收项 | 状态 | 实际命令与结果 | 产物或未执行原因 |
| --- | --- | --- | --- |
| 数值与边界正确性 | <passed/failed/not_run> | <命令、误差与失败输入> | <日志或原因> |
| 性能比较 | <passed/failed/not_run> | <计时边界、预热、重复次数、双方统计> | <原始样本或原因> |
| 集成回归 | <passed/failed/not_run> | <调用方测试> | <日志或原因> |

- 限制：<未覆盖的设备、框架版本、输入与失败项>
- 人工审查：<审查人、日期、结论与依据；未审查则注明待审查>
```

需要机器校验时，另按[任务报告 schema](task-evidence.md)保存 JSON，用 `scripts/validate_task_result.py` 检查；性能 JSON 用 `scripts/validate_benchmark.py` 检查。上述 Markdown 不是 JSON schema，结构校验不会执行 GPU 测试或核实日志真实性。

## 已有离线产物的诊断

- CUDA Graph trace 泳道过多：给出原始 `.json/.json.gz`、采集 run 和 rank 配置，使用[整理工具](../.agents/skills/llm-torch-profiler-analysis/references/cuda-graph-trace.md)生成新副本，交付命令、JSON 摘要与显示限制；不要从显示泳道推断真实 stream。
- 两次训练出现数值漂移：给出同 dtype/seed/输入的逐算子日志、代码和捕获版本，使用[离线比较器](../.agents/skills/training-inference-change/references/offline-numerics.md)生成 HTML，交付排除/未配对项及候选分歧；统计匹配不能代替逐元素或模型级验证。

这两项工具仅有 CPU 合成输入回归，无真实 GPU、模型或客户端加载证据。

## 已验证范围

本仓库验证资源路径、元数据、生成一致性和部分工具的隔离行为，不因此证明上表领域流程有效。当前没有归档的真实 GPU 任务回放或完整客户端加载记录；没有已验证的 GPU/框架版本清单。目标项目中执行的报告应记录精确版本，未测平台保持未验证。

复现成功的使用样例应保留脱敏输入、目标 revision、执行命令、日志和验收结果，再链接到本页。维护状态、依赖和来源入口见[资源索引](../.agents/README.md#维护状态与验证边界)。

## InfraRSI 使用样例

以下请求是输入模板，不是已完成的训练案例。共同前提是目标 revision、日志/配置、允许改动和资源预算已确定；没有 GPU 时只做证据分析并报告未验证。

| Skill | 典型请求 | 反例/排除范围 | 交付证据 |
| --- | --- | --- | --- |
| discover-training-system | “解释这些 rank 的 NUMA/拓扑与实际 backend 差异” | 仅凭机器型号推荐 NCCL 参数 | 有效环境、进程配置和路径证据 |
| choose-parallel-layout | “固定全局 batch，比较可行布局” | 直接照搬 TP≤8 或显存常数 | 合法性、逐 rank 预算、完整 update 与语义对照 |
| profile-whole-update | “组件变快但训练没快，按同 rank/step 对比” | 将阶段最大耗时相加 | 原始窗口、慢 rank、墙钟及噪声 |
| manage-memory-lifetimes | “第一步成功、第二步 OOM，分析分配时序” | reserved-allocated 直接判碎片 | 时序、allocator/驱动与错误记录 |
| recompute-policy | “按当前内存预算比较 full/selective/none” | 不验证就关闭重计算 | 策略、生命周期、数值与时间/显存 |
| moe-ep-communication | “固定路由语义，分析 dispatch/combine 与热点专家” | 减少 top-k 冒充等价加速 | 分布、通信路径、合并数值和完整 update |
| optimize-data-path | “保持样本分配，比较 pinned prefetch” | 跳过数据或移出计时窗口 | 数据契约、copy/buffer 依赖、时间/内存 |
| optimize-training-kernels | “评估当前版本融合开关及逐行梯度误差” | 只报告单 Kernel 加速 | reference、数值、精度及模型/完整 update |
| verify-training-semantics | “核对候选是否保持约定工作量与训练行为” | 套用上游固定容差 | 不变量、实际路径、容差依据与失败项 |
| validate-training-lifecycle | “比较连续训练与新进程恢复，验证适用的导出” | 加载成功即宣布恢复通过 | 状态、轨迹、峰值和 reload/forward |
| learn-optimization-skills | “从失败记录提炼带反例的候选规则” | 自动修改全局规则或训练评测标准 | 根因、条件、反例、固定任务对照与待审结论 |
| weak-model-protocol | “为现有驱动设计动作校验与重试预算” | 自动搭建 runtime 或替换模型 | schema、错误处理、预算记账及验证缺口 |

上游案例见[负结果目录](../.agents/skills/_catalogue/negative-results.md)，本地边界和未验证范围见[适配说明](../.agents/skills/_catalogue/infrarsi-adaptation.md)。本仓库未复现其案例收益，也未验证真实客户端自动发现这些新增 Skill。

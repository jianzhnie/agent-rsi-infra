# InfraRSI 本地适配边界

这组 Skill 用于训练优化方法与原始案例查询，不安装 InfraRSI harness，也不提供 Agent Runtime。各技能保留上游 Frontmatter 和原始正文；正文中的任务契约只适用于其原评测环境。

## 使用前确认

先读目标项目指令，记录代码、模型、数据和硬件版本，约定允许改动、资源预算、计时边界、精度与验收条件。按任务加载一个最相关 Skill；通用训练变更先用 `training-inference-change` 选择验证范围，Kernel 开发和计时继续使用本仓现有专项技能。

`read_env`、`read_receipt`、`run_screen`、`profile_ranges`、`propose_config`、`write_memory`、selfcheck、签名 receipt、FR/ED、plan A/B、E0/E1/E2、L0/L1/L2 等指上游 harness。目标环境没有这些能力时，使用实际可用的日志、命令和验证方式，明确差异，不伪造接口调用、签名或有效性裁决。纯文本中的 reports/、MANUSCRIPT.md、FINAL_PLAN 等均指上游，未作为本仓本地资源迁入。

## 不能泛化的约束

H100-80GB、78 GiB 上限、4 GiB 余量、固定 warmup/步数窗口、3% 收益门槛、2% 一致性、数值容限、并行布局公式和微批次关系依赖原框架与实验。按目标版本核对，不当作通用常数。MCore 0.18.2 的参数、重计算互斥、DeepEP/TE 及 NCCL 设置不代表当前目标版本行为；固定 collective 次数、TP/EP 不跨节点等也不是普遍规则。

分布式计时按明确定义的完整 update 边界记录并检查墙钟一致性；相同 run 的 rank/step 不是独立重复实验。是否重复候选、噪声门槛与统计方法由目标实验预先约定，不照搬上游“一候选只运行一次”。不要为挤出余量自动禁用 coredump、停止其他进程、修改 NUMA/系统配置或注入启动 collective。

数值与语义的冻结范围由任务定义。数据重排、精度变更、router 调整可能是其他任务的合法目标，但必须独立声明与验证，不能隐瞒为同语义性能优化。跨更新缓存是否正确由生命周期与算法契约决定；不得复用失效中间量。历史案例的“exact”、吞吐与收益均是上游报告，不是本仓复现。

## 受控改进与模型调用

learn-optimization-skills 只提出有证据的候选资源改进，不自动写全局指令、个人记忆或上游 memory.db。不得修改预先固定的测试/评测标准来迁就候选；人工审查与回归按本仓 RSI 设计执行。工具/Skill 被加载或调用只说明被使用，不证明产生收益；需要任务对照。重复任务不能算未见任务，评估答案和保留测试不进入改进输入。

weak-model-protocol 是协议参考，不在本仓实现动作执行器。JSON object 模式只保证 JSON 对象形态，不保证符合动作 schema；仍需独立 schema/参数校验。预算、菜单、重试、上下文和模型选择按现有授权及实际 API 能力配置，不硬编码上游默认数字；失败调用、未知费用和不完整结果要保留，不擅自升级模型或安装服务。

## 交付与验证状态

采用 [任务证据规范](../../../docs/task-evidence.md)，给出实际命令、结果、版本、日志/原始样本、设备、失败和未执行原因；数值正确、完整 update 性能、恢复与导出分别报告。不因原文“Allowed actions”而获得设备、网络、系统修改、提交或发布权限。

12 个 Skill 均为 experimental：只完成本地发现、元数据、来源与引用检查及仓库回归；没有真实 GPU/模型任务、InfraRSI harness 或客户端加载验证。共享负结果见 [negative-results.md](negative-results.md)，许可与来源见 [UPSTREAM.md](UPSTREAM.md)。

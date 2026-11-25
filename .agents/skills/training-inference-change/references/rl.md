# RL 训练与 Rollout 边界

先确定改动属于 trainer、rollout backend/router、data buffer、reward/verifier 或 environment。沿请求追踪 prompt、token、mask、logprob、reward 与模型权重版本，检查接口处的 shape、设备、顺序和生命周期。

- 样本与奖励：检查 token 对齐、截断/终止、重复或遗漏样本、reward 聚合与异常处理；工具调用和多轮环境将成功/失败条件写成可验证契约。
- 权重同步：明确训练和 rollout 使用的权重版本、一致性要求、同步完成点与失败策略。异步吞吐变化同时检查允许的 staleness、背压和队列增长。
- 扩展接口：通过现有 generation/reward/verifier/environment 边界扩展，避免把 Agent loop、模型后端和训练调度揉成一个大抽象。库使用项目日志机制，不随意 print 或吞异常。
- 状态归属：actor、缓存、恢复进度与当前权重版本由所属组件管理；内部重构保留用户 Hook 契约，具体要求见[配置与运行状态](training.md#配置与运行状态)。
- 恢复与重放：保存失败请求、配置、种子、样本及版本；验证 checkpoint 恢复后状态与生成路径是否一致。重放证据不能替代完整训练效果评估。
- 硬件：明确 GPU/NPU 差异在 backend、编译还是调度层解决，遵守目标项目的分支和支持政策，不强制所有项目建立同一硬件抽象。

性能对照保持模型、输入分布、并行配置与评测口径一致，至少证明没有通过减少工作量或改变采样语义获得伪加速。只支持可测试、可评审且维护成本明确的扩展。

本参考提炼自 verl、slime、vime 的贡献治理与架构调研，未复制专用签名、PR 标签、硬件分支政策或启动命令。项目映射见[迁移记录](../../../../docs/framework-practices.md)。

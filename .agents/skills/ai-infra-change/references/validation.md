# 按影响选择验证

此表用于选择检查，不提供虚构的通用测试命令。实际命令从目标仓库的测试、CI 和贡献指南中取得。

| 变化 | 最小检查 | 扩展条件与检查 |
| --- | --- | --- |
| 模型结构、加载或注册 | 权重映射、forward、配置与注册 | 输出或训练路径变化：模型质量、loss/梯度、多步对照 |
| 数据、packing、RL rollout | token、mask、position、label、logprob 与终止对齐 | 采样或权重同步变化：多轮、异步和训练/生成一致性 |
| Optimizer、checkpoint | 更新公式、状态保存加载与恢复 | 格式或并行度变化：版本兼容、reshard、异常恢复 |
| 进程组与分布式执行 | rank、通信顺序、多 rank 行为 | 拓扑或并行维度变化：多节点、超时与失败传播 |
| Scheduler、KV Cache | 状态转换、分配回收与生命周期 | 并发、抢占、prefix cache 或传输变化：混合负载与压力测试 |
| 量化 | reference 对照、容差、dtype 与异常输入 | 模型路径变化：真实任务指标、长上下文和显存 |
| 多模态与多阶段服务 | 阶段协议、流式顺序、终止与取消 | 跨阶段变化：背压、资源释放、音画同步和端到端质量 |
| Kernel | 编译、真实 shape、stride、layout 与数值边界 | 训练/图捕获/新架构：梯度、模型集成和适用设备路径 |
| Compiler IR、Pass | IR 和语义回归 | 代码生成或后端变化：多 Target 编译、执行与结果对照 |
| API、配置、生成文件 | 签名、默认值、Schema 与旧输入 | 外部行为变化：真实客户端、配置快照及文档同步 |

## 性能证据

至少保存以下内容，并绑定确切源码版本；编辑代码后不能直接沿用旧结果。

- baseline/candidate commit 或内容哈希，模型及 revision。
- 设备型号、数量、互连；驱动、运行时、框架与编译器版本。
- 输入、shape、dtype、并发、并行配置和数据来源。
- 预热、重复次数、同步与计时方式、缓存条件、统计方法。
- 绝对耗时、吞吐、显存及波动；覆盖范围与退化项。
- 可运行命令、原始日志和结果文件。

测量指标按任务选择：训练 step time/tokens per second；文本推理 TTFT、TPOT 与尾延迟；音视频首包、实时率与同步；Kernel 延迟及相关硬件计数器。说明编译、传输与预处理是否计入。

## 依据

本表归纳自仓库的 [训练调研](../../../../docs/research/training-frameworks-agent-engineering.md)、[推理调研](../../../../docs/research/inference-frameworks-agent-engineering.md) 和 [工程规范总览](../../../../docs/research/github-ai-infra-engineering-standards.md)。属于本仓库采用的流程，不表示这些项目具有完全相同的规则。

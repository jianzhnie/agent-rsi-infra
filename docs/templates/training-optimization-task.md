# 训练吞吐优化任务模板

填写后作为任务描述交给客户端；这不是可执行配置，也不要求客户端支持 `/goal`。路径和命令指向目标训练仓库，不是在本资源仓库启动训练。未确定的设备、预算、工作负载或执行授权应明确标记，先完成不依赖它们的调查。

```text
优化任务：<task_id>

在 <目标仓库绝对路径> 的 <commit + 工作区 diff/hash> 上，优化
<模型与任务类型> 的 <主指标及公式，例如有效训练 tokens/s/GPU>。
基线为 <recipe 路径及摘要>，启动方式为 <已验证的命令与解释器>。

固定条件：
- 模型初始权重、tokenizer/chat template：<路径、revision、摘要>。
- 数据：<路径、摘要、样本顺序/seed、packing 与 loss mask>。
- 训练语义：<有效 batch、序列长度、optimizer、LR schedule、精度及训练步数>。
- 环境：<框架 revision、依赖/镜像 digest、GPU 型号/数量/已分配设备、拓扑>。
- 测量：<warmup、评分窗口、独立重复次数、噪声/收益门槛与计时边界>。

允许操作：<只读诊断 / 指定参数变更 / 指定代码路径与执行命令>。
冻结范围：<数据、初始权重、评测器、验收阈值及其他不可改资产>。
执行授权：<本地/远程目标、可用设备、网络与依赖安装范围；未授权项列明>。
预算：<总 GPU-hour、trial 上限、单次超时、墙钟上限、最终复验保留额>。
成本包含基线、失败、OOM、超时、profiling 和最终复验。

先读取目标项目指令、基线与现有失败材料，再按任务路由选择 Skill。
先确认基线可运行、参数实际生效和数据/模型一致，再提出带证据的优化假设。
候选记录父版本、参数或 diff、预期机制和验证方法；独立 attempt 分别记账。
Profiling 用于诊断，正式性能在无 profiler 的同一工作负载下测量。
按预先约定的配置、数值与行为 Gate 验证；初始 loss 接近不代替梯度/更新验证。
在现有授权和预算内执行，预算不足或环境阻塞时保留状态，不扩大权限继续运行。
只清理本任务创建且身份已确认的进程/作业，不停止其他任务。

交付到 <独立产物目录>：
- 基线与候选 recipe/diff、代码和环境标识。
- 每次 attempt 的实际命令、原始日志、指标、成本及失败/未执行原因。
- 最佳候选的独立复验结果；若无有效提升，保留基线并如实报告。
- Validation Report 和带条件、反例、证据的候选经验；经验经人工审核后合并。

不自动提交、推送、部署或修改共享规则。已有授权若包含这些动作，按授权范围执行。
```

任务报告和状态定义见[任务与证据规范](../task-evidence.md)，Skill 选择见[任务路由](../component-skills.md)。本模板不提供执行器、资源调度或正确性验证实现，尚未经过真实 GPU 任务和客户端对照验证。

## 来源与适配

参考 [ATTUNE goal_prompt.example.txt](https://github.com/amazon-science/attune/blob/c07fe30dcf2e16cae0ae47f62d1f857ce2a634b6/harness/goal_prompt.example.txt)，固定 revision `c07fe30dcf2e16cae0ae47f62d1f857ce2a634b6`。

上游声明：ATTUNE，Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. 许可为 Apache-2.0，本仓库提供同许可[全文](../../LICENSE)。本地重新组织为中文任务模板，保留目标、基线、工作负载、资源预算、结果与作业归属约束；移除 `/goal`、固定 8K/GBS、RayJob、kubectl、日志 Pod 和环境变量依赖，补充本仓库的证据与人工审核要求。未复制或启用上游 launcher、Hooks 或自动调优程序。

# 性能诊断参考

用于定位耗时、资源竞争和性能退化。先明确观察指标：单 Kernel 延迟、模型前向耗时与端到端服务吞吐量是不同的测量范围。

## 按问题选择工具

| 问题 | 工具 | 采集重点与限制 |
| --- | --- | --- |
| 哪个 PyTorch 算子、输入形状或调用栈占用资源 | PyTorch Profiler | 从最少活动开始，按需开启 shapes、memory、stack；额外采集会增加开销和 trace 体积 |
| CPU 调度、CUDA API、Kernel、通信和拷贝如何交错 | NVIDIA Nsight Systems | 查看时间线、空隙、同步与重叠；活动、采样和 graph 跟踪配置决定开销，不保证固定比例 |
| Triton Kernel 的调用层级、聚合耗时或 graph 归属 | Triton Proton | 核对 Triton、设备和后端支持，以及 tree/trace 与 CUDA graph 归属的兼容性；不能假定 vLLM 集成支持所有 Proton 后端 |
| Python 调用或垃圾回收耗时 | cProfile 或目标项目的 GC 诊断工具 | Python 调用时间不等于异步 GPU 执行时间；需要时与设备时间线关联 |

Nsight Systems 用于系统时间线；需要单 Kernel 的占用率、指令或内存访问细节时，再选择 Nsight Compute 等工具。缺少工具或设备时报告限制，不套用其他平台的结论。

## 控制采集范围

1. 先核对目标框架的官方模型部署指南及软硬件适用范围；CI 配置用于复现，不自动代表推荐部署。偏离部署基线时说明原因。保存无 profiler 的基线，记录代码版本、软硬件、输入、并发、预热、缓存与 graph 模式。
2. 只采集回答当前问题所需的活动和少量代表性请求；区分启动、编译与稳态阶段。
3. 多进程与多卡按主机、进程、rank 和会话命名产物，核实采到了受影响的 worker。聚合表不能替代各 rank 的时间线。
4. 正常停止采集并等待 trace 写出，写盘时间不计入推理耗时。保存命令、配置与可提取的产物位置。
5. 使用 CUPTI 的工具可能争用采集资源；组合采集前核对兼容性，必要时对同一负载分次采集。

vLLM 的 profiler 参数、启停端点和 Proton graph 支持随版本变化，按安装版本与[上游使用说明](https://github.com/vllm-project/vllm/blob/3f86db3b2df84dc2e4d10b81da43afad132d66c6/docs/contributing/profiling.md)核对。本文不自动安装工具、启动服务或调用管理端点。

## 区分诊断与 benchmark

- trace 用于解释现象。采集可能改变调度、同步、显存和延迟，不把带 profiler 的数字直接作为正式性能结果。
- Kernel 时间之和不等于请求延迟：并发流会重叠，CPU、排队和调度可能未包含在设备统计内。
- 根据 trace 提出假设，用消融或受控对照验证；退出采集后以相同负载重新测量，报告重复次数、波动及未覆盖范围。
- graph 模式或输入分布为采集而改变时，注明与生产路径的差别；局部加速仍需在目标服务负载下验证。

## 来源

提炼自 [vLLM profiling.md](https://github.com/vllm-project/vllm/blob/3f86db3b2df84dc2e4d10b81da43afad132d66c6/docs/contributing/profiling.md)，固定 commit `3f86db3b2df84dc2e4d10b81da43afad132d66c6`；许可见已保留的 [Apache-2.0 全文](../.agents/skills/kernel-microbenchmark/LICENSE)。工具选择与诊断方法做通用化整理，不复制安装脚本、性能数字和持续 profiling 的组织配置。本仓库未执行设备采集或验证采集开销。

## 编译优化：先测量再选择区域

针对 torch.compile 的局部优化，先固定 eager、当前项目已启用编译和候选编译策略，确认实际 attention/算子 backend 与精度设置，避免在缺少可选依赖的回退路径上比较。区分冷编译时间、稳态墙钟时间、Kernel 时间和峰值内存。

从真实 profile 找出慢于合理带宽/计算下界的中间算子与数据搬运；理论下界只用于排序，不是可达收益承诺。选择能捕获融合收益的最小区域，并记录不同 shape、调用点及 no_grad 等模式触发的图数量/重编译，不能只提高编译上限掩盖变体增长。

先快速筛选，再在空闲设备和独立新进程中重复确认；分别比较普通 launch 与 CUDA Graph replay，区分主机 launch 开销和设备计算收益。按影响验证 forward/backward、激活重计算及 TP/EP 等组合，确认所有继承配置或 recipe 的影响。失败方案与停止原因也保留，避免重复投入无收益方向；预算和停止阈值由任务约定，不照搬固定百分比。

方法提炼自 TorchTitan [local_compile_perf](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/skills/local_compile_perf/SKILL.md)，固定 revision `72e5566782bbdafaa9bafd422733a307319213c5`；许可见[保留的 BSD-3-Clause](../.agents/skills/training-inference-change/references/torchtitan/LICENSE)。未迁入其 local_compile API、案例性能数字、自动提交、并行 Agent 或 PR 排版要求。编译失败仍使用 `pytorch-compiler-debugging` 排障。

CUDA Graph trace 的显示整理见[可视化参考](../.agents/skills/llm-torch-profiler-analysis/references/cuda-graph-trace.md)；整理后的显示泳道不代表原始 stream。

## 本仓离线工具

| 目标 | 入口 | 主要结果 |
| --- | --- | --- |
| 训练逐 rank 与流水线诊断 | [autoresearch](../autoresearch/README.md) | 计算、通信、主机等待、显存和耗时守恒 |
| 推理 Kernel 融合与重叠调查 | [profiler Skill](../.agents/skills/llm-torch-profiler-analysis/SKILL.md) | Kernel 归属、重叠机会与融合模式 |
| CUDA Graph 显示整理 | [trace 整理](../.agents/skills/llm-torch-profiler-analysis/references/cuda-graph-trace.md) | 用于查看的新副本，不改变原始证据 |

前两套分析的用途不同，保留独立实现。所有入口只分析已有本地产物；真实采集、模型运行和性能验收由目标项目负责。

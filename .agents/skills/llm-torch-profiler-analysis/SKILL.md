---
name: llm-torch-profiler-analysis
description: 离线分析 LLM 的 PyTorch profiler trace，汇总 Kernel 耗时、潜在重叠与融合模式，支持 SGLang、vLLM、TensorRT-LLM 和 TokenSpeed。用于已有 trace 或 profile 目录诊断，默认不进行在线采集。
---

# LLM Torch Profiler 分析

默认读取本地已有 trace，不连接服务。先确认框架、版本、采集配置、rank、负载及是否启用 graph/compile。工具需要 Python 3.10+；按安装目录定位脚本，不依赖作者的主机或容器路径。

## 离线使用

```bash
python <skill-directory>/scripts/analyze_llm_torch_profile.py triage \
  --framework sglang --input /path/to/trace.json.gz
```

也接受 profile 目录；有逐 rank 与合并 trace 时，优先分析逐 rank 产物。

已有两份 trace 时可分别传入 `--mapping-input` 和 `--formal-input`。mapping 用于恢复调用映射，formal 用于观察真实优化配置；两者配置不同，不能直接比较耗时或据 mapping 宣称性能收益。

## 解读结果

报告 Kernel、重叠机会、融合模式三张表和主要瓶颈，注明过滤阈值及未覆盖部分。图中的重叠空隙或模式匹配只是调查线索，不证明操作可并行、融合一定有效或端到端会加速。核对数据依赖、stream、通信与源代码，再做受控验证。

按需读取 [heuristics](references/heuristics.md)、[融合与重叠目录](references/fuse-overlap-catalog.md)及 [source map](references/source-map.md)。目录中的 mainline、开放 PR 和历史性能数据都需核对目标版本。

## CUDA Graph 时间线

Graph replay 泳道过多或需要合并 PP rank trace 时，读取 [trace 可视化参考](references/cuda-graph-trace.md)。它生成显示副本，不恢复真实 stream，也不替代原始 trace 的分析。

## 在线与历史资源

[上游流程](references/upstream-workflow.md)保留在线采集说明和历史验证上下文；其中机器路径、容器名与固定模型不是本地默认值。附属 `run_*_host.sh`、probe 和 override 脚本可能连接服务、启动进程或写配置；仅在用户明确要求在线采集且目标与资源范围已确定后审查使用，不从离线分析自动切换过去。

采集开销与正式计时的区分见[性能诊断参考](../../../docs/performance-profiling.md)。来源、许可与适配见 [UPSTREAM.md](UPSTREAM.md)。

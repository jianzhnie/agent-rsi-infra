# 离线分析工作流

本地保留 SGLang、vLLM、TensorRT-LLM 和 TokenSpeed 的已有 trace 分析，不提供服务探测、在线采集、容器启动或 override 生成。需要采集时使用目标框架官方工具，方法与开销见 [性能诊断](../../../../docs/performance-profiling.md)。

```bash
python <skill-directory>/scripts/analyze_llm_torch_profile.py triage --framework auto --input <trace-file-or-directory>
python <skill-directory>/scripts/analyze_llm_torch_profile.py triage --mapping-input <mapping-trace> --formal-input <formal-trace>
```

单 trace 模式分析已有记录；双 trace 模式用 mapping 恢复调用归属，在 formal 中观察实际执行。配置不同的 trace 不能作为性能前后对照。优先输入逐 rank 文件，核对采集版本、负载、graph/compile 配置和覆盖范围。

输出 Kernel、重叠机会与融合模式三张表；默认过滤阈值为累计 GPU 时间占比 1%。表格上限可用 --kernel-table-limit 和 --overlap-table-limit 设置，0 表示不限制数量。

案例事实见 [统一目录](fuse-overlap-catalog.md)，仅查 overlap 时使用 [专题索引](overlap-catalog.md)。模式匹配不证明数据依赖允许并行、模型结果不变或端到端加速。用独立数值测试和受控 benchmark 验证候选。

[Markdown 汇总工具](../scripts/render_triage_markdown_bundle.py) 用于整理结果；[CUDA Graph 整理参考](cuda-graph-trace.md) 只生成显示副本，原始 trace 仍是分析依据。

上游历史在线流程见 [固定版本原文](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.agents/skills/llm-torch-profiler-analysis/SKILL.md)，其中机器、模型和验证记录不构成本仓结果。

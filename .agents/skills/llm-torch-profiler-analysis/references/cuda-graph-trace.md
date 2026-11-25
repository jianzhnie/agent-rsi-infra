# CUDA Graph trace 可视化

当 graph replay 产生大量单 Kernel stream 行时，使用 [compact_cuda_graph_trace.py](../scripts/compact_cuda_graph_trace.py) 整理 Perfetto 泳道；仅依赖 Python 标准库，不采集 trace、不连接服务。

```bash
python3 <skill-directory>/scripts/compact_cuda_graph_trace.py input.json.gz -o view.json.gz
python3 <skill-directory>/scripts/compact_cuda_graph_trace.py trace_directory --merge-pp-ranks -o merged.json.gz
```

输入为 PyTorch Chrome trace JSON 对象（含 `traceEvents`），支持 `.json`/`.json.gz`。GPU slice 需有合法 `pid/tid/ts/dur/args.stream`，原始 `tid` 应等于 stream；不兼容格式应报告，不能靠修改原 trace 伪造。

单 rank 重新分配显示用 `tid`/`args.stream`，保留 GPU slice 的名称、pid、时间戳、时长和其他参数；也会整理 annotation、metadata 和 flow。脚本验证 slice 不变和每个显示泳道不重叠，输出 JSON 摘要。原 trace 用于正式分析，生成副本只用于阅读：显示泳道不是运行时真实 stream。

多 rank 模式读取 `rank<N>_trace.json[.gz]`，需要可靠的 `distributedInfo.rank` 和 `baseTimeNanoseconds`。按共同基准平移时间并重映射 pid，因此合并结果的 pid/时间戳不再与单份输入逐字相同。基准字段不证明跨节点时钟同步，采集方式和时钟误差需另行核实；不要混合不同 run。

PP 顺序优先使用上游 `torchtitan_real_pp` 或 `mesh_pp` 组说明，缺失时回退 global rank 顺序，只有它与 PP 顺序一致时才正确。通信箭头依赖 `PP:<stage><op><microbatch>` 注解；无注解、截断窗口或未匹配箭头不直接说明通信错误，也不能证明真实因果或重叠收益。

默认拒绝已有输出；`--overwrite` 只允许替换输出副本，不能替换输入（包括链接别名）。保留输入与处理命令、版本、摘要及显示限制。来源、许可和本地修正见 [TorchTitan 来源](torchtitan/UPSTREAM.md)。回归使用合成 trace，尚未验证真实 GPU/多节点 trace 或 Perfetto 加载。

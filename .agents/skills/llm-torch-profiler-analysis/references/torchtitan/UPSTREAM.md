# TorchTitan trace 工具来源

- 固定 revision：`72e5566782bbdafaa9bafd422733a307319213c5`。
- 来源：[cuda_graph_trace_compaction](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/skills/cuda_graph_trace_compaction/SKILL.md)。
- 复制文件：上游 `scripts/compact_cuda_graph_trace.py` 到本 Skill 同名脚本；上游 `scripts/test_compact_cuda_graph_trace.py` 到根 `tests/test_cuda_graph_trace.py`，测试由统一入口收集。
- 许可：[BSD-3-Clause](LICENSE)，脚本与测试保留上游版权；本目录的许可仅覆盖此次 TorchTitan 资源，不改变原 SGLang 资源许可。
- 本地适配：测试按本地路径加载；Ruff 风格；拒绝非有限 GPU 时间；即使指定 overwrite 也拒绝覆盖输入或链接别名。参考文档区分单 rank 保真与合并时间平移、pid 重映射。
- 验证范围：合成 trace 的 CPU 回归与 CLI 文件保护；未执行 GPU、真实多节点采集或 Perfetto 客户端测试。

# 离线训练数值诊断

用于已有的两份逐算子 activation 文本日志；不自动修改训练代码或在线采集。使用 [compare_numerics.py](../scripts/compare_numerics.py)，只依赖 Python 标准库：

```bash
python3 <skill-directory>/scripts/compare_numerics.py run_A.log run_B.log \
  --name1 baseline --name2 candidate -o comparison.html
```

日志使用上游 `activation_tracer.dump_captures_to_file` 格式，例如：

```text
Excluded ops dispatched: (none)
[layers.0.norm/op_0_mul]
  Shape: torch.Size([2, 4]), Dtype: torch.float32
  L2 norm: 2.0
  Min: -1.0
  Max: 1.0
  Mean: 0.0
  Output hash: 4.0
  Input hashes: 4.0
  Location: model.py:10
  Phase: forward
```

此例仅展示格式，不是实测数据。同 dtype、seed、输入、逻辑 rank 和捕获时点是有意义对照的前提；同时固定或记录编译模式、并行配置、重计算与依赖版本。可先比较 FP32 路径定位，再回到生产 dtype 验证，不用 FP32 成功替代低精度正确性。

## 解读报告

工具依次尝试人工 override、归一化 key、忽略计数器的 fuzzy key、统计签名匹配，并显示各行匹配方式、forward/backward、单侧出现和排除操作。自动匹配是启发式，不同操作可能具有相同统计量；应按依赖路径核对首个可疑分歧，而非把第一个红色显示行直接认作根因。

`--override pairs.csv` 每行 `<run_A_key>, <run_B_key>` 强制配对，只在人工确认语义相同后使用。它不能修复数值差异；缺失 key 不会配对，保留并复核单侧项。当前 parser 忽略无逗号的 override 行，人工需检查格式和实际配对结果。

“matched”仅表示已捕获统计量在诊断阈值下无明显差异，**不证明逐元素一致**；L1/L2、极值或均值都可能碰撞。同为 NaN 的摘要可能来自未完成通信，不能据此验收算子。该工具固定的显示阈值不是项目容差；缺字段、排除操作、单侧条目和 fuzzy/stats 匹配都应保留在报告中。CLI 返回 0 仅表示成功生成报告，存在差异也不会作为数值测试返回失败。

空日志、无 activation 统计量或未知 phase 拒绝生成报告；默认拒绝覆盖已有报告，`--overwrite` 也不能覆盖输入日志或 override 文件（包括链接别名）。HTML 自包含，无远端资源，包含日志中的模型与源码信息，分享前脱敏。

## 捕获与验证边界

在线捕获仍参考[上游 numerics_debugging](torchtitan/UPSTREAM.md)，本仓库未迁入 activation tracer 或临时 patch。其依赖 PyTorch 私有 DebugMode 和目标 Profiler 接入，须按版本审查；采集会改变内存和执行行为，不将采集性能用于正式 benchmark。临时改动只撤销本次引入的部分，保留用户已有修改。

本仓库仅验证合成日志的解析、配对、差异、HTML 转义与 CLI 文件保护；未执行真实模型、分布式或特定 PyTorch 版本捕获。交付时提供双方 revision、捕获配置、原始日志和 HTML，并列出未配对/排除项与待核实假设。

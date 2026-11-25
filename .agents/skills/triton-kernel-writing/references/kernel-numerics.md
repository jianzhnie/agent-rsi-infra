# Kernel 数值验证

用于手写 CUDA/Triton 算子的 forward/backward 验证。先核对公式、支持的 shape/stride/dtype、mask、累积与中间 dtype，以及 NaN/Inf 语义；模型级未知偏差先定位路径，不直接放宽算子容差。

## 三方对照

- **golden**：按相同数学语义构造独立高精度实现，优先 FP64；硬件或算子不支持时说明 FP32 的限制。
- **reference**：与目标相同输入/输出 dtype 的 eager 实现。
- **target**：待验证 Kernel。

先生成一份低精度输入，再将这些确切值无损上转给 golden，避免把输入量化误差混入算术误差。比较前先检查 shape、dtype、NaN 位置和正负 Inf 位置；有限值误差检查不能掩盖非有限值语义差异。

已有项目容差优先。需要定义新门槛时，可在 golden 精度下逐输出、逐梯度记录：

```text
reference_error = max(abs(reference - golden))
target_error = max(abs(target - golden))
rounding_floor = max(abs(cast_to_golden(cast_to_target(golden)) - golden))
threshold = factor * reference_error + max(project_atol, rounding_floor)
```

`factor`、`project_atol` 和 reference 质量标准在测试 target 前声明并解释依据。上游 2 倍误差、10% 诊断触发值及 1—2 ULP 示例不是本仓库的通用门禁；不能为通过失败样例而增加容限。

## 先判断门槛是否有效

reference 对 golden 本身误差很大时，倍数门槛可能允许真实 bug 通过。对强抵消的归约，检查出错元素的逐项贡献与 `sum(abs(terms)) / abs(sum(terms))`；分母为零时单独报告，不能硬算成有限指标。

用合法的不同累积顺序、多个 seed 与归约长度复核误差分布、偏差和增长趋势。大条件数或近似平方根增长只提供线索，不能单独证明正确。无法区分病态输入误差与实现缺陷时报告 inconclusive，暂不验收该范围。

## 覆盖与报告

使用同一上游梯度检查各输入及参数梯度，不能仅验证 forward。覆盖真实形状、最小合法形状、tile 边界两侧、非连续/偏移输入（若支持），以及与算子有关的极值、近零方差和抵消输入。非确定性算子在相同输入下重复检查，不挑选成功样本。

逐张量报告 reference/golden 误差、target 误差、门槛、门槛是否有效、shape/dtype/seed 与结果。`PASS WITH LIMITATIONS` 和 `INCONCLUSIVE` 仅为数值诊断结论：限制范围及原因写入任务报告，未决验收项不能映射为 passed。通过已声明范围的数值验收后再做正式 benchmark；模型集成仍需目标项目验证。

来源与许可见 [TorchTitan 适配说明](torchtitan/UPSTREAM.md)。本参考未附 GPU 实现或数值测试结果。

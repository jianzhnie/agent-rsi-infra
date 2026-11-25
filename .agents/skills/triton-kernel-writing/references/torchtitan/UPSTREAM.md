# TorchTitan 数值验证参考来源

- 固定 revision：`72e5566782bbdafaa9bafd422733a307319213c5`。
- 来源：[kernel-numerics-verifier/SKILL.md](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/skills/kernel-numerics-verifier/SKILL.md)。
- 许可：[BSD-3-Clause 原文](LICENSE)，保留 Meta Platforms, Inc. and affiliates. 版权声明。
- 本地适配：中文提炼为 `../kernel-numerics.md`；保留三方比较、条件分析及 forward/backward 范围，不将示例常数推广为统一容限。
- 验证边界：仅文档、引用与资源检查；未执行 GPU、模型或指定 PyTorch/Triton 版本验证。

# TorchTitan 工程与数值诊断来源

- 固定 revision：`72e5566782bbdafaa9bafd422733a307319213c5`。
- 来源：[numerics_debugging](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/skills/numerics_debugging/SKILL.md)、[distributed](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/rules/distributed.md)、[config](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/rules/config.md)、[design](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/rules/design.md)、[experiments](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/rules/experiments.md)。
- 代码：只迁入 `numerics_debugging/scripts/compare_numerics.py`；未迁入 `activation_tracer.py` 或私有 API 接入 patch。`tests/test_compare_numerics.py` 是本地补充回归。
- 许可：[BSD-3-Clause](LICENSE)，保留脚本中的 Meta Platforms, Inc. and affiliates. 版权；其他本地原创流程继续适用原许可。
- 本地适配：拒绝空/无统计日志与未知 phase；自动配对隔离 forward/backward；统计差异与缺失项参与分类；非有限数值不破坏 HTML；转义 phase；默认禁止覆盖报告，永不覆盖输入或 override。HTML 明确仅作诊断，退出码不代表数值验收。按 Ruff 整理风格。
- 领域提炼：mesh 与梯度 placement、并行组合、隐式同步、配置所有权和实验边界；不迁入 spmd_types 实现、DTensor 禁令、fake 后端、无向后兼容承诺、系统指令覆盖或自动提交策略。
- 验证范围：CPU 合成日志和文件保护；真实训练、GPU、多节点和私有 API 接入均未验证。

# FlashInfer benchmark 用法

用于在兼容的目标 FlashInfer checkout 中比较已有算子后端。本仓库不包含其 benchmark 实现；先核对版本和 `benchmarks/flashinfer_benchmark.py --help`。

1. 选择真实调用的 routine、后端、shape、dtype 和布局；先检查设备支持，不把不支持或跳过的后端视作有效结果。
2. 使用对应版本的 `--refcheck` 验证输出，记录参考与容差。允许 mismatch 继续运行只适合诊断，错误结果不能用于宣称优化有效。
3. 固定预热、重复次数、graph 和缓存策略，记录实际使用的 timer；CUPTI 不可用时可能回退到 CUDA events，依赖和回退行为按安装版本核实。不要为跑 benchmark 自动升级 CUDA 或安装包。
4. 比较相同算子边界。autotuner 的 tactic 计时与公开 benchmark 的计时选择可能独立，不能把某个 timer 环境变量当作所有测量的设置。
5. 保存原始结果、CSV 与复现命令，报告 baseline/candidate 的绝对耗时、波动、设备及输入规模，再给加速比。

上游支持 testlist、`--output_path` 和 `--generate_repro_command` 等参数；具体命令与当前支持的 routine 见[固定版本教程](https://github.com/flashinfer-ai/flashinfer/blob/4d5a6ce322587d247fb192f97a0d23eeba9e3412/.claude/skills/benchmark-kernel/SKILL.md)。示例参数不是跨版本稳定 API，生成命令也需检查是否包含全部环境与配置。

本文选择性提炼计时与结果报告流程；缓存、正确性及多卡方法统一见[主 Skill](../SKILL.md)。许可见 [LICENSE](../LICENSE)，未运行真实 GPU benchmark。

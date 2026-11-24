# 来源与适配

- 上游：[vllm-project/vllm](https://github.com/vllm-project/vllm)。
- 固定版本：`3f86db3b2df84dc2e4d10b81da43afad132d66c6`。
- 技能：[原始目录](https://github.com/vllm-project/vllm/tree/3f86db3b2df84dc2e4d10b81da43afad132d66c6/.agents/skills/kernel-microbenchmark)。
- 许可：随目录保留 [Apache-2.0 全文](LICENSE)；保留上游已有版权信息，不推断个人作者。

本地适配：泛化触发范围；按 CUDA/ROCm 与负载选择计时和缓存策略；移除硬件性能参考表；明确示例依赖、自检边界和微基准不能替代端到端验证。示例保留上游版权；本地风格与输入校验改动以 Git diff 为准。

迁入时验证文档链接、格式与可在本机运行的辅助脚本。未执行 GPU、CUDA/ROCm、多卡、模型或真实服务验证；未重新核实上游引用的全部安全公告、性能结论及外部服务可用性。

后续适配：链接本仓库性能诊断参考，区分采集与正式计时。

缓存与工具选择补充适配自 SGLang [kernel-benchmark.md](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/kernel-benchmark.md)，固定 commit `049bf85d931c9633d26094ae5ff9a7dbac6723b4`；许可见[保留全文](../kernel-organization/LICENSE)。按目标架构核实缓存行为，不将固定 buffer 大小或单一计时工具设为通用要求。

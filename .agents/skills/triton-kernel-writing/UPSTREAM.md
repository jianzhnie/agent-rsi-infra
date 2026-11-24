# 来源与适配

- 上游：[vllm-project/vllm](https://github.com/vllm-project/vllm)。
- 固定版本：`3f86db3b2df84dc2e4d10b81da43afad132d66c6`。
- 技能：[原始目录](https://github.com/vllm-project/vllm/tree/3f86db3b2df84dc2e4d10b81da43afad132d66c6/.agents/skills/triton-kernel-writing)。
- 许可：随目录保留 [Apache-2.0 全文](LICENSE)；保留上游已有版权信息，不推断个人作者。

本地适配：泛化触发范围和 UI 描述；保留 vLLM JIT 监控作为可选手段；跨线程读写按目标版本验证同步要求；用相对链接连接 Kernel 测量流程。

迁入时验证文档链接、格式与可在本机运行的辅助脚本。未执行 GPU、CUDA/ROCm、多卡、模型或真实服务验证；未重新核实上游引用的全部安全公告、性能结论及外部服务可用性。

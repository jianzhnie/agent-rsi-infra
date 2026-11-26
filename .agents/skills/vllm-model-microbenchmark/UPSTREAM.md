# 来源与适配

- 上游：[vllm-project/vllm](https://github.com/vllm-project/vllm)。
- 固定版本：`3f86db3b2df84dc2e4d10b81da43afad132d66c6`。
- 技能：[原始目录](https://github.com/vllm-project/vllm/tree/3f86db3b2df84dc2e4d10b81da43afad132d66c6/.agents/skills/model-microbenchmark)。
- 许可：随目录保留 [Apache-2.0 全文](LICENSE)；保留上游已有版权信息，不推断个人作者。

本地适配：保留 vLLM 专用流程；补充目标环境、版本和资源边界；默认值及限制需按安装版本核实，不自动安装或启动任务。

补充修正：包含通配符的 --case 参数加引号，兼容 zsh。

迁入时验证文档链接、格式与可在本机运行的辅助脚本。未执行 GPU、CUDA/ROCm、多卡、模型或真实服务验证；未重新核实上游引用的全部安全公告、性能结论及外部服务可用性。

后续适配：链接本仓库性能诊断参考，区分采集与正式计时。

本地命名：model-microbenchmark 改为 vllm-model-microbenchmark，名称明确目标框架；上游 URL、原始路径、许可和 revision 保持不变。

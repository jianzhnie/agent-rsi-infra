# 来源与适配

- 上游：[vllm-project/vllm](https://github.com/vllm-project/vllm)。
- 固定版本：`3f86db3b2df84dc2e4d10b81da43afad132d66c6`。
- 技能：[原始目录](https://github.com/vllm-project/vllm/tree/3f86db3b2df84dc2e4d10b81da43afad132d66c6/.agents/skills/model-recipes)。
- 许可：随目录保留 [Apache-2.0 全文](LICENSE)；保留上游已有版权信息，不推断个人作者。

本地适配：保留查询脚本；上游 recipes 相对链接改为固定版本链接；区分本仓库的技能目录与目标 vLLM 配置源码目录，查询不启动服务。

补充修正：章节提取按代码围栏类型与长度识别结束标记，避免合法嵌套示例截断章节。

迁入时验证文档链接、格式与可在本机运行的辅助脚本。未执行 GPU、CUDA/ROCm、多卡、模型或真实服务验证；未重新核实上游引用的全部安全公告、性能结论及外部服务可用性。

部署基线与 CI 复现的区分提炼自 SGLang [cookbook-first.md](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/cookbook-first.md)，许可见[已保留的全文](../sglang-code-cleanup/LICENSE)，不要求目标项目采用 SGLang 目录。

本地命名：model-recipes 改为 vllm-model-recipes，名称明确目标框架；上游 URL、原始路径、许可和 revision 保持不变。

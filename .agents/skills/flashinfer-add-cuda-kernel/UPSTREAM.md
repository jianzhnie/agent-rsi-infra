# 来源与适配

- 上游：[FlashInfer add-cuda-kernel](https://github.com/flashinfer-ai/flashinfer/blob/4d5a6ce322587d247fb192f97a0d23eeba9e3412/.claude/skills/add-cuda-kernel/SKILL.md)。
- 固定 commit：`4d5a6ce322587d247fb192f97a0d23eeba9e3412`。
- 保留上游 [LICENSE](LICENSE) 与 [NOTICE](NOTICE)，不推断个人作者。

本地将技能名改为 `flashinfer-add-cuda-kernel`，中文提炼集成契约和验证边界。示例实现、长 API 教程和架构表保留为固定版本链接，避免将教程代码当作可直接投入生产的通用模板。不迁入安装、自动编译或运行 GPU 任务的默认动作。按用户偏好不保留安装来源 JSON。

相关调试、benchmark 与 self-review 方法分别融入仓库调试参考、现有微基准 Skill 和贡献/审查流程；未重复注册同名技能。结构和文档验证不代表 FFI、CUDA、JIT、AOT 或真实设备路径已验证。

# slime 工程方法来源

- 固定 revision：`79aa41a884ab0bf65222c94418f6357d3c31192b`。
- [slime-code-review-preferences](https://github.com/THUDM/slime/blob/79aa41a884ab0bf65222c94418f6357d3c31192b/.claude/skills/slime-code-review-preferences/SKILL.md)：仅提炼配置与运行状态分离、状态生命周期归属、内部重构保持自定义 Hook 契约，落点为 `../training.md`、`../rl.md` 及 code-reviewer 的严格审查清单。
- [add-tests-and-ci](https://github.com/THUDM/slime/blob/79aa41a884ab0bf65222c94418f6357d3c31192b/.claude/skills/add-tests-and-ci/SKILL.md)：仅提炼 CI 实际调用方式、测试发现/注册、硬件需求与生成 workflow 的模板事实来源，落点为根 CONTRIBUTING.md。
- 许可：[保留的 Apache-2.0 全文](LICENSE)，包含 `Copyright 2025 Zhipu AI`。本地为中文方法提炼，未复制完整 Skill、脚本或工作流。
- 未迁入：README 生态条目编辑限制、重复的薄包装/抽象规则、专用 `NUM_GPUS`、默认 8 卡、测试入口样板及 workflow 路径。
- 验证边界：文档、资源引用和仓库静态检查；没有执行 slime、真实 Hook、GPU 或上游 CI。

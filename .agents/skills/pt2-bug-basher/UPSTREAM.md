# 上游来源与适配

- 来源：PyTorch `pt2-bug-basher`。
- 原文件：https://github.com/pytorch/pytorch/blob/1d28e3a704d1d634d240e8fe0566c0c6df975458/.agents/skills/pt2-bug-basher/SKILL.md
- 固定 commit：`1d28e3a704d1d634d240e8fe0566c0c6df975458`。
- 许可：保留上游 [LICENSE](LICENSE) 全文与版权信息；不是本仓库 Apache-2.0 许可的重新授权。
- 迁入日期：2026-11-24。上游技能目录仅含 `SKILL.md`，没有附属脚本。

同版本 [PyTorch CLAUDE.md](https://github.com/pytorch/pytorch/blob/1d28e3a704d1d634d240e8fe0566c0c6df975458/CLAUDE.md) 的配置作用域与结构化诊断建议也已吸收。

## 本地改动

- 环境检查遵循目标项目和用户已选择的解释器，不强制 Conda 或反复询问已有信息。
- 将 `EnterWorktree` / `ExitWorktree` 绑定改为可用工具或独立 Git worktree，并要求 baseline 对应实际加载的 PyTorch 构建。
- 自审不强依赖未迁入的 `/pr-review`；可使用已有审查角色或直接审查。
- 以根因、变更和真实验证结果报告替代庆祝、彩蛋要求。
- 保留上游 `disable-model-invocation: true`，并通过 `agents/openai.yaml` 保持 Codex 显式调用策略。

编译器架构、错误分类、minifier、日志与源码导航保留上游内容。内部 API、默认值、标志和源码路径可能随 PyTorch 版本变化；迁入和本地检查不代表已在 GPU 或目标模型上复现这些流程。

补充本地性能诊断参考的导航，不复制 TorchTitan local_compile 实现；该参考的固定来源和独立许可记录在文档中。

本地维护：删除指向不存在的 Architectural Knowledge 章节的导航，保留 Key Source Files 入口。

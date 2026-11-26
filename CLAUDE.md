@AGENTS.md

# Claude Code 适配

共享规范见根目录 `AGENTS.md`；Agent 资源索引见 `.agents/README.md`。

- `.claude/agents/` 保存生成的 Claude 角色适配，源文件为 `.agents/roles/`。
- `.claude/skills` 指向 `.agents/skills`，共享同一份技能正文。
- 工程、环境、诊断与提交约定统一维护在 `AGENTS.md`；角色正文只在共享源文件维护。
- Hooks 与状态栏保留为可选示例，启用步骤见 `docs/deployment.md`。

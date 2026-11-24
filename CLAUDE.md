@AGENTS.md

# Claude Code 适配

共享规范见根目录 `AGENTS.md`；Agent 资源索引见 `.agents/README.md`。

- `.claude/agents` 指向 `.agents/agents`，角色按 Claude 格式维护。
- `.claude/skills` 指向 `.agents/skills`，共享同一份技能正文。
- 工程、环境、诊断与提交约定统一维护在 `AGENTS.md`；角色按 Claude 格式维护。
- Hooks 与状态栏保留为可选示例，启用步骤见 `docs/deployment.md`。

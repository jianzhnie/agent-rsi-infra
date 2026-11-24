@AGENTS.md

# Claude Code 适配

共享规范见根目录 `AGENTS.md`；Claude 资源索引见 `.claude/README.md`。

- `.claude/skills` 指向 `.agents/skills`，共享同一份技能正文。
- `.claude/rules/` 导入共享规则；角色与输出风格按 Claude 格式维护。
- Hooks 与 MCP 保留为可选示例，启用步骤见 `docs/deployment.md`。

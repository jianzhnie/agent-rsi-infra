# 入口与部署说明

本仓库维护共享规范和工具适配。目录存在、链接有效与真实客户端已加载是不同的验证范围。

## 1. 共享资源

根目录 `AGENTS.md` 是指向 `.ai/AGENTS.md` 的相对符号链接，两处使用相同正文。`.agents/skills/` 是技能唯一来源。

迁移或复制仓库时保留隐藏目录和符号链接。Windows 或不支持符号链接的环境需采用客户端支持的导入或生成副本方案，并自行管理同步；不能将链接目标字符串误当作文件正文。

向其他项目采用规范时，保留适用的工程要求，替换本仓库的目录导航和检查命令。

## 2. Claude Code

- 根 `CLAUDE.md` 使用 `@AGENTS.md` 导入共享指令。
- `.claude/rules/shared.md` 导入 `.ai/rules/`，规则不复制正文。
- `.claude/skills` 链接到 `../.agents/skills`，共享技能与其附属资源。
- 角色与输出风格使用 `.claude/agents/`、`.claude/output-styles/`。

可选 Hooks 和状态栏的步骤：

1. 阅读 `.claude/settings.example.json`，选择所需设置；原模板含较宽权限和外部通知能力，不作为默认启用方案。
2. 将选定项合并到目标项目 `.claude/settings.json`，保留已有配置；核对客户端支持的事件和字段。
3. 脚本按 `.claude/hooks/` 与 `.claude/scripts/` 路径部署。`notifications/common.sh` 随目录一起复制，不单独注册为 Hook。
4. 在目标客户端验证所选事件与命令；本仓库 unittest 只验证隔离脚本行为与文件路径。

本仓库未提供 MCP 服务器配置。设置示例中的外部工具授权需要使用者自行核对，不表示相应服务已安装或启用。

本次迁移未创建活动的 `.claude/settings.json`，未启用示例中的通知、权限和外部服务。

## 3. Codex

根 `AGENTS.md` 提供仓库指令，Skills 位于 `.agents/skills/`。无需额外的仓库级 Codex 配置；执行权限与工具设置沿用运行环境。

在所用 Codex 版本确认根指令与共享 Skills 的实际发现结果。Claude 的角色、Hooks 和输出风格不会因此自动变成 Codex 配置。

## 4. Gemini

`GEMINI.md` 使用 `@AGENTS.md` 作为共享入口。使用时确认目标客户端的导入与 Skills 加载行为。

Cursor 与 Copilot 适配已移除，当前仓库不提供专用入口。

## 5. 维护

共享规则维护在 `.ai/`，Skills 维护在 `.agents/skills/`，Claude 专用资源维护在 `.claude/`，测试维护在 `tests/`。

变更公共路径时同步更新客户端入口、索引和测试。升级客户端或启用新的配置项时，重新检查实际加载行为。

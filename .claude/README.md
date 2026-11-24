# Claude 资源

这里维护 Claude 专用角色、可选 Hooks 与状态栏。共享指令见根目录 `AGENTS.md`，共享 Skill 位于 `.agents/skills/`。

## 资源索引

路径相对本文件。角色与 Skill 的作者、版本、许可保留在各自 Frontmatter 中；未独立署名的脚本不推断具体作者，按仓库 Apache-2.0 许可维护。

| 名称 | 文件 | 用途 |
| --- | --- | --- |
| code-reviewer | [角色](agents/code-reviewer.md) | 只读审查，按严重程度报告有证据的问题 |
| debugger | [角色](agents/debugger.md) | 复现、定位和修复问题 |
| performance-analyzer | [角色](agents/performance-analyzer.md) | 根据性能测量分析瓶颈 |
| shell-check | [共享 Skill](../.agents/skills/shell-check/SKILL.md) | 可执行 Shell 检查与结果汇总 |
| ai-infra-change | [共享 Skill](../.agents/skills/ai-infra-change/SKILL.md) | 选择领域验证并整理可复现证据 |
| pt2-bug-basher | [上游适配 Skill](../.agents/skills/pt2-bug-basher/SKILL.md) | 显式调用的 PyTorch 2 编译器排障流程 |
| add-or-fix-type-checking | [上游 Skill](../.agents/skills/add-or-fix-type-checking/SKILL.md) | Transformers 类型检查流程，保留上游原文 |
| context | [脚本](hooks/session/context.sh) | 初始化会话，compact/resume 时保留已有记录 |
| record-event | [脚本](hooks/logging/record-event.sh) | 命令、Agent、配置及异常日志 |
| guard-tool | [脚本](hooks/tools/guard-tool.sh) | 工具调用前的补充拦截 |
| format-file | [脚本](hooks/tools/format-file.sh) | 编辑后的 pre-commit 与 Shell 检查 |
| notify | [脚本](hooks/notifications/notify.sh) | 可选桌面、语音与 Server酱通知 |
| summarize | [脚本](hooks/session/summarize.sh) | 可选会话摘要通知 |
| status-line | [脚本](scripts/status-line.sh) | 上下文用量、模型与 Git 状态 |
| settings | [设置示例](settings.example.json) | 可选 Hook 事件绑定与状态栏 |

工程与提交约定由根 `CLAUDE.md` 导入 `AGENTS.md`；`skills` 链接到 `../.agents/skills`。

## 部署

参见 [部署说明](../docs/deployment.md)。`settings.example.json` 仅保留 Hooks 和状态栏，不预设模型、权限豁免、插件或外部工具授权；选择需要的事件再合并到目标设置。

- `hooks/notifications/common.sh` 随脚本部署，不单独注册为 Hook。
- 基础依赖为 Bash、Git、jq；格式检查使用 pre-commit 和 shellcheck。
- 通知密钥从目标项目 `.claude/.env` 的 `SCT_SENDKEY` 读取，不执行该文件内容。无密钥时不发送网络通知。
- 测试替换 curl、osascript 和 say，不发送真实通知。真实客户端加载与事件触发需另行确认。
- `guard-tool` 仅补充已定义的拦截，不是完整的 Shell 安全边界。

## 维护来源

本地脚本、状态栏和原始设置可追溯到仓库 Git 历史，如 `80faff2`、`a241329`、`1cf2354`、`65be515`、`f52ed88`。共享资源保留各自署名与许可；不因目录迁移改写来源。

# Claude 配置索引

说明性文字统一使用中文；配置字段、有效名称、分类标签、命令、路径和产品名称保留原始标识，以保证加载与引用兼容。

此索引以当前 `.claude/` 与共享目录的文件为准，涵盖配置入口；技能的 references、templates、scripts 随所属技能维护，不重复计为独立配置。路径均相对本文件。

## 目录组织

```text
.claude/
├── agents/                 # 9 个角色定义
├── rules/                  # 共享规则导入入口
├── output-styles/          # 3 种输出风格
├── skills/                 # 链接到 ../.agents/skills
│   └── <skill-name>/       # SKILL.md 与附属资源
├── hooks/
│   ├── session/            # context.sh、summarize.sh
│   ├── tools/              # guard-tool.sh、format-file.sh
│   ├── logging/            # record-event.sh
│   └── notifications/      # notify.sh 与 common.sh 公共函数
├── scripts/                # status-line.sh 等非 Hook 运行脚本
├── settings.example.json   # 可选设置示例
└── README.md               # Claude 资源与共享配置索引
```

技能按本页功能分类查找，按 `name` 定位磁盘目录。检查技能归入 Check，技术文档翻译归入 Documentation。保留角色、规则、输出风格和技能的名称；Hooks 按职责分组，settings 中使用显式路径注册。

这里维护 Claude 专用资源；共享 Skills 与规则另有唯一来源。按 [部署说明](../docs/deployment.md) 选用配置。

角色 `name` 与文件名一致，文档与性能角色现使用 `documentation-writer`、`performance-analyzer`；调用时需使用新名称。

命名约定：目录和 Shell 文件采用小写 kebab-case，技能入口固定为 `SKILL.md`，Python 测试采用 `test_*.py`。Hook 脚本按职责命名；事件绑定由 settings 维护。

## 来源与维护约定

- 本地 Markdown 的依据为现有文件署名、仓库 Apache-2.0 许可及已有索引；Hooks、状态栏和设置的本地维护依据为 Git 历史（如 `80faff2`、`a241329`、`1cf2354`、`65be515`、`f52ed88`），未独立署名的文件不推断具体作者。
- 技能采用 `.agents/skills/<skill-name>/SKILL.md`，每个技能与附属资源整体迁移；仅修改仓库分类标签和迁移相关路径，保留运行时字段、外部署名与许可。不向脚本、JSON、模板或参考文档添加 Frontmatter。
- 分类标题以技能首个标签 Check、Documentation 为标识，并附中文释义。分类通过标签和本索引表达，不增加技能发现所需的目录层级。

## 智能体角色

| 名称 | 路径 | 版本 | 作者 | 许可证 | 来源类型 | 外部来源信息 | 功能说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| architect | [agents/architect.md](agents/architect.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 负责高层设计决策的系统架构师。 |
| code-reviewer | [agents/code-reviewer.md](agents/code-reviewer.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 审查代码的正确性、安全性、性能和可维护性。 |
| debugger | [agents/debugger.md](agents/debugger.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 诊断错误、测试失败、崩溃和意外行为。 |
| documentation-writer | [agents/documentation-writer.md](agents/documentation-writer.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 编写和更新文档、文档字符串及行内注释。 |
| library-integration | [agents/library-integration.md](agents/library-integration.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 将第三方库、SDK 和 API 集成到项目中。 |
| performance-analyzer | [agents/performance-analyzer.md](agents/performance-analyzer.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 分析性能瓶颈并提出优化建议。 |
| refactor | [agents/refactor.md](agents/refactor.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 在保持行为不变的前提下安全重构代码。 |
| shell-expert | [agents/shell-expert.md](agents/shell-expert.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 编写、调试和审查 Shell 脚本。 |
| test-writer | [agents/test-writer.md](agents/test-writer.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 编写单元测试和集成测试。 |

## 输出风格

| 名称 | 路径 | 版本 | 作者 | 许可证 | 来源类型 | 外部来源信息 | 功能说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Chinese-Concise | [output-styles/chinese-concise.md](output-styles/chinese-concise.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 中文回复，简洁直接，不啰嗦不总结。适合日常开发交互。 |
| Code-Only | [output-styles/code-only.md](output-styles/code-only.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 只输出代码和必要的 shell 命令，不解释不总结。适合明确知道要什么的快速实现场景。 |
| Diagrams-First | [output-styles/diagrams-first.md](output-styles/diagrams-first.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 解释架构、数据流或代码结构时，先用 Mermaid 图展示，再文字说明。 |

## 规则

| 名称 | 路径 | 版本 | 作者 | 许可证 | 来源类型 | 外部来源信息 | 功能说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| git-conventions | [rules/git-conventions.md](../.ai/rules/git-conventions.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 项目 Git 提交规范，包括 Conventional Commits 格式和提交规则。 |
| python-style | [rules/python-style.md](../.ai/rules/python-style.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 基于 Google Python 风格指南，适用于 Python 3.10 及以上版本的编码规范。 |
| shell-style | [rules/shell-style.md](../.ai/rules/shell-style.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 基于 Google Shell 风格指南，适配 Bash 4.2 及以上版本的 Shell 编码规范。 |

## 技能

技能入口统一位于 `.agents/skills/<skill-name>/SKILL.md`。每个目录内的 `scripts/`、`references/`、`templates/` 保持原相对结构。

### Check（检查）

运行项目检查与 Shell 语法、静态分析。

| 名称 | 路径 | 版本 | 作者 | 许可证 | 来源类型 | 外部来源信息 | 功能说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shell-check | [skills/shell-check/SKILL.md](../.agents/skills/shell-check/SKILL.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 使用 bash -n 检查 Shell 语法，使用 shellcheck 执行静态分析。 |

### Documentation（文档）

技术文档翻译与本地化。

| 名称 | 路径 | 版本 | 作者 | 许可证 | 来源类型 | 外部来源信息 | 功能说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tech-doc-translator | [skills/tech-doc-translator/SKILL.md](../.agents/skills/tech-doc-translator/SKILL.md) | 1.0.0 | Robin | Apache-2.0 | 本地 | — | 将英文技术文档（AI/ML、开发者工具、API 文档等）翻译为中文 Markdown。 |

## 钩子

| 名称 | 路径 | 版本 | 作者 | 许可证 | 来源类型 | 外部来源信息 | 功能说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| record-event | [hooks/logging/record-event.sh](hooks/logging/record-event.sh) | — | 待确认 | Apache-2.0（仓库许可） | 本地 | — | 分流命令、代理、配置审计及异常事件，保留各类日志格式。 |
| notify | [hooks/notifications/notify.sh](hooks/notifications/notify.sh) | — | 待确认 | Apache-2.0（仓库许可） | 本地 | — | Claude 需要用户关注时，通过微信、桌面和语音发送通知。 |
| format-file | [hooks/tools/format-file.sh](hooks/tools/format-file.sh) | — | 待确认 | Apache-2.0（仓库许可） | 本地 | — | 工具调用后自动格式化已编辑文件，并对 .sh 文件运行 shellcheck。 |
| guard-tool | [hooks/tools/guard-tool.sh](hooks/tools/guard-tool.sh) | — | 待确认 | Apache-2.0（仓库许可） | 本地 | — | 工具调用前拦截危险命令，保护敏感文件。 |
| context | [hooks/session/context.sh](hooks/session/context.sh) | — | 待确认 | Apache-2.0（仓库许可） | 本地 | — | 初始化会话或恢复 compact 上下文，仅 startup 重置会话记录。 |
| summarize | [hooks/session/summarize.sh](hooks/session/summarize.sh) | — | 待确认 | Apache-2.0（仓库许可） | 本地 | — | 会话结束时，通过 Server酱将会话摘要发送至微信。 |

## 设置与状态栏

| 名称 | 路径 | 版本 | 作者 | 许可证 | 来源类型 | 外部来源信息 | 功能说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| settings.example.json | [settings.example.json](settings.example.json) | — | 待确认 | Apache-2.0（仓库许可） | 本地 | — | Claude Code 权限、Hooks、插件与状态栏配置。 |
| scripts/status-line.sh | [scripts/status-line.sh](scripts/status-line.sh) | — | 待确认 | Apache-2.0（仓库许可） | 本地 | — | 显示上下文用量、Git 状态与模型信息。 |

## 前置元数据规范

以下示例适用于加载器兼容的本地 Markdown 配置入口；合并元数据时保留运行时字段和未知字段。外部配置保留原作者、版本、许可、平台和归属声明。

```yaml
---
name: <配置名称>
description: <简短说明>
version: <语义化版本>
author: <作者姓名>
license: <SPDX许可证标识>
platforms: [linux, macos, windows]
metadata:
  tags: [<主分类>, <标签1>, <标签2>]
  related_skills: [<技能名称1>, <技能名称2>]
---
```

## 当前布局与部署边界

- 共享规则在 `../.ai/rules/`，共享 Skills 在 `../.agents/skills/`；`skills` 为兼容符号链接。
- `settings.example.json` 是可选设置模板，不作为本仓库活动设置。权限、插件、事件和外部工具授权需按目标环境审查。
- 未对各客户端完成实际加载与事件触发验证。详见 [部署说明](../docs/deployment.md)。
- Shell 平台列表不代表已完成所有操作系统实测；没有独立署名的文件保留原索引的作者状态。

## 运行与维护

- 基础依赖：Bash、Git、jq。格式化需要 pre-commit，Shell 静态分析需要 shellcheck；macOS 桌面和语音通知仅在 osascript、say 存在时启用。
- `hooks/notifications/common.sh` 是共享函数文件，不注册为 Hook；部署时须随 hooks 目录一起复制。通知密钥从部署项目 `.claude/.env` 的 `SCT_SENDKEY=...` 读取，不执行该文件内容。
- Server酱请求使用表单编码，连接超时 2 秒、总超时 4 秒；无密钥时跳过网络通知。即时通知失败不阻断桌面通知，会话摘要发送失败不阻断退出。
- PostToolUse 将相对文件路径解析到 `CLAUDE_PROJECT_DIR`，从项目根目录运行 pre-commit；缺少 pre-commit 时返回跳过说明。
- 根目录 `tests/` 和 `hooks/notifications/common.sh` 属于维护资源，不计入配置入口数量。测试使用临时 Git 仓库并替换 curl、osascript、say，不发送真实通知。

```bash
python3 -m unittest discover -s tests -v
find .claude/hooks .claude/scripts -name '*.sh' -exec shellcheck {} +
```

尚未进行实际客户端的事件触发验证；配置中的权限、插件和事件名称保持原样。

## 路径迁移与部署

| 旧路径 | 当前路径 |
| --- | --- |
| `agents/doc-writer.md` | `agents/documentation-writer.md` |
| `agents/perf-analyzer.md` | `agents/performance-analyzer.md` |
| `hooks/session-init.sh、hooks/compact-restore.sh、session/start.sh、session/restore-context.sh` | `hooks/session/context.sh` |
| `hooks/session-summary.sh` | `hooks/session/summarize.sh` |
| `hooks/pre-tool-use.sh、hooks/security/guard-tool.sh` | `hooks/tools/guard-tool.sh` |
| `hooks/post-tool-use.sh、hooks/formatting/format-file.sh` | `hooks/tools/format-file.sh` |
| `hooks/log-events.sh、hooks/config-audit.sh、hooks/stop-failure.sh` | `hooks/logging/record-event.sh` |
| `hooks/notify.sh` | `hooks/notifications/notify.sh` |
| `hooks/helpers/notifications.sh、hooks/shared/notifications.sh` | `hooks/notifications/common.sh` |
| `statusline.sh` | `scripts/status-line.sh` |

- 更新部署时，将 hooks（含 common.sh）、scripts 和选定的 settings 一起复制到项目 `.claude/`，避免新旧配置混用。
- 状态栏入口现为 `.claude/scripts/status-line.sh`。Hook 命令使用加引号的显式路径，支持项目路径含空格。
- 更新 settings 后，再按迁移表清理已部署的旧文件；本次没有操作已安装配置。
- 仓库不再提供 MCP 服务器配置；示例中的外部工具授权不代表已安装或启用服务。

### 合并后的行为约定

- `session/start.sh` 与 `session/restore-context.sh` 合并为 `session/context.sh`，使用 SessionStart 输入的 `source` 区分 startup 与 compact；compact 不重置时间、命令基线或编辑记录。
- `logging/log-events.sh`、`logging/audit-config.sh`、`logging/log-failure.sh` 合并为 `logging/record-event.sh`，按 `hook_event_name` 分流，继续分别写入 command-log.txt、config-audit.log、stop-failure.log。
- 提交前检查直接运行 `pre-commit run --all-files`，不依赖已移除的 `/check`。
- 环境重载脚本已移除，settings 不再注册 CwdChanged / FileChanged；需要环境变量时由启动环境提供。

# agent-rsi-infra

面向 Coding Agent 递归自我改进（Recursive Self-Improvement，RSI）的工程基础设施，集中维护共享规范、Skills、工具适配与验证流程。

Engineering infrastructure for recursive self-improvement of coding agents: shared standards, skills, tool adapters, and validation workflows.

当前提供 Claude Code、Codex 与 Gemini 入口，以及面向 AI Infra 开发的工程指南。持续改进以可复现的检查结果和人工审查为依据；自动学习与自我修改机制尚未实现。

## 目录

| 路径 | 内容 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | 共享开发指令入口，链接到 `.ai/AGENTS.md` |
| [.ai/](.ai/architecture/overview.md) | 工程规范、贡献政策、领域指南 |
| [.agents/skills/](.agents/skills/README.md) | 跨工具 Skills |
| [.claude/](.claude/README.md) | Claude 角色、Hooks、输出风格与设置示例 |
| [docs/](docs/README.md) | 规划、部署、调研资料 |
| `tests/` | 配置布局、技能发现与隔离运行测试 |

## 现有资源

- 2 个共享 Skills：`shell-check`、`tech-doc-translator`。
- 9 个 Claude 角色：架构、审查、调试、文档、依赖集成、性能、重构、Shell 和测试。
- 3 份共享规则：Python、Shell、Git。
- Claude 可选资源：输出风格、会话与工具 Hooks、通知、状态栏和设置示例。

训练、推理、分布式和 Kernel 指南位于 `.ai/architecture/`。领域 Skills 按真实任务逐步补充，当前未提供完整的 AI Infra 自动化实现。

## 使用

先阅读 [部署说明](docs/deployment.md)，按所用客户端选取入口与资源。跨工具目录布局不代表各客户端都已完成加载验证。

Claude 的 `settings.example.json` 保留为模板。采用前选择所需权限、事件、插件和服务，再放入目标项目的有效配置位置；不要直接覆盖已有设置。

## 本地检查

基础工具：Python 3.10+、Bash、Git、jq。Shell 静态分析需要 shellcheck，Python 静态检查使用 Ruff。

```bash
python3 -m unittest discover -s tests -v
ruff check tests
ruff format --check tests
```

可选开发依赖与 Git 提交检查：

```bash
python3 -m pip install -e '.[dev]'
pre-commit install
pre-commit run --all-files
```

这里的 Python 安装用于管理开发依赖，不安装或部署 Agent 资源；配置仍从 Git 工作区选用。

测试使用临时 Git 仓库，替换 curl、桌面与语音通知命令。不会发送真实通知。

## 维护

- 当前目录职责见上方索引；工具使用方式见 [部署说明](docs/deployment.md)。
- 配置索引、来源及署名：[Claude 资源索引](.claude/README.md)。
- 修改共享 Skill 时保留元数据和资源相对路径；工具适配层不复制正文。

许可证：[Apache-2.0](LICENSE)。外部资源保留各自声明。

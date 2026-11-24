# agent-rsi-infra

面向 Coding Agent 递归自我改进（Recursive Self-Improvement，RSI）的工程基础设施，集中维护共享规范、Skills、工具适配与验证流程。

Engineering infrastructure for recursive self-improvement of coding agents: shared standards, skills, tool adapters, and validation workflows.

当前提供 Claude Code、Codex 与 Gemini 入口，以及面向 AI Infra 开发的验证流程。通过实际结果、人工审查和回归测试改进工具与 Skills。

## 目录

| 路径 | 内容 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | 共享开发指令 |
| [.agents/skills/](.agents/skills/install-skill-from-github/SKILL.md) | GitHub 技能迁入、Shell 检查与领域流程 |
| [.agents/](.agents/README.md) | 角色、Skills 与适配资源索引 |
| `.claude/` | Claude 兼容链接、Hooks 与设置示例 |
| [docs/](docs/README.md) | 规划、部署、调研资料 |
| `scripts/`、`tests/` | 可重复运行的检查与隔离回归 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献流程、证据要求与调研实践的落地 |

## 现有资源

- `install-skill-from-github`：从 GitHub 迁入完整技能，保留许可和来源，默认安装到本仓库。
- `shell-check`：脚本化选择文件、执行语法和静态检查，失败后继续并汇总。
- `add-or-fix-type-checking`：迁入 Transformers 的类型检查流程；[来源与适用范围](.agents/skills/add-or-fix-type-checking/UPSTREAM.md)。
- `pt2-bug-basher`：显式调用的 PyTorch 2 编译器排障；[来源与适配](.agents/skills/pt2-bug-basher/UPSTREAM.md)。
- `code-reviewer`：只读代码审查，默认 light、按需 strict，使用共享清单。
- 2 个 Claude 角色：调试、性能分析。
- Python 检查配置与 Git 提交约定。
- Claude 可选资源：会话与工具 Hooks、通知、状态栏和设置示例。

训练、推理、分布式和 Kernel 的参考资料集中在 [AI Infra 工程实践](docs/ai_infra_agent.md)。领域 Skills 按真实任务逐步补充。

## 使用

先阅读 [部署说明](docs/deployment.md)，按所用客户端选取入口与资源。跨工具目录布局不代表各客户端都已完成加载验证。

Claude 的 `settings.example.json` 保留为模板。选择需要的 Hook 事件与状态栏配置，再合并到目标项目设置；不要直接覆盖已有设置。

## 本地检查

基础工具：Python 3.10+、Bash、Git、jq。Shell 静态分析需要 shellcheck，Python 静态检查使用 Ruff。

```bash
python3 scripts/check.py --check
```

需要自动修复 Python 风格时使用 `python3 scripts/check.py --fix`；修复后会完整重新验证。默认或 `--check` 不修改源码。

安装开发依赖后运行上述入口；Git 提交检查按需安装：

```bash
python3 -m pip install -e '.[dev]'
pre-commit install
pre-commit run --all-files
```

CI 在 Linux/Python 3.10、Linux/Python 3.13 和 macOS/Python 3.13 上运行同一入口；本地结果不代表远端 CI 已通过。

这里的 Python 安装用于管理开发依赖，不安装或部署 Agent 资源；配置仍从 Git 工作区选用。

测试使用临时 Git 仓库，替换 curl、桌面与语音通知命令。不会发送真实通知。

## 维护

- 当前目录职责见上方索引；工具使用方式见 [部署说明](docs/deployment.md)。
- 配置索引、来源及署名：[Agent 资源索引](.agents/README.md)。
- 修改共享 Skill 时保留元数据和资源相对路径；工具适配层不复制正文。

许可证：[Apache-2.0](LICENSE)。外部资源保留各自声明。

# 仓库开发指令

本仓库为 `agent-rsi-infra`，提供面向 Coding Agent 递归自我改进（RSI）的共享工程规范、Skills、工具适配与验证流程。没有训练、推理或 Kernel 业务实现；相关资料用于指导目标项目中的工作。

## 目录与事实来源

- `.ai/`：本指令、`.ai/AI_POLICY.md`、通用规则与架构指南。
- `.agents/skills/`：共享 Skills，保留技能名、署名、许可和附属资源。
- `.claude/`：Claude 角色、Hooks、脚本、输出风格与配置示例。
- `AGENTS.md`、`CLAUDE.md`、`GEMINI.md`：客户端入口，不复制通用规范正文。
- `tests/`：布局、技能发现与隔离运行回归。
- `docs/`：规划、部署和调研资料。

本文件通过根目录 `AGENTS.md` 符号链接提供给客户端；所有路径以仓库根目录为基准。

## 工作要求

- 先检查现有实现、调用路径与相关测试，再修改；控制变更范围。
- 修改共享规范时同步检查各客户端入口，不假设它们有相同的加载与继承行为。
- Python、Shell 和 Git 变更分别遵循 `.ai/rules/python-style.md`、`.ai/rules/shell-style.md`、`.ai/rules/git-conventions.md` 规则；现有工具配置优先于文档中的通用工具建议。
- 迁移 Skill 时整体移动目录，保留 Frontmatter、来源和相对资源路径。
- 修改 Hooks 或通知时，用隔离测试替换网络、桌面和语音命令。
- `.claude/settings.example.json` 是可选模板。启用前按目标环境选择权限、事件、服务和插件；不将其内容自动复制为活动配置。
- 用户可见的路径、命令或部署方式变化，同步更新 README、部署文档及测试。
- 报告实际命令、结果、未运行项及原因；未经测量不宣称性能收益。

## 常用检查

从仓库根目录运行：

```bash
python3 -m unittest discover -s tests -v
ruff check tests
ruff format --check tests
pre-commit run --all-files
```

Shell 检查按变更文件运行 `bash -n` 与 `shellcheck`；缺少工具应说明，不算通过。pre-commit 的 `--all-files` 处理 Git 跟踪文件，新文件还应单独检查。

## 进一步阅读

- `.ai/architecture/overview.md`
- `.ai/architecture/training.md`、`.ai/architecture/inference.md`、`.ai/architecture/distributed.md`、`.ai/architecture/kernel.md`
- `docs/deployment.md`

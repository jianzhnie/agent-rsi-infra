# 入口与部署说明

本仓库维护共享规范和工具适配。目录存在、链接有效与真实客户端已加载是不同的验证范围。

## 1. 共享资源

根目录 `AGENTS.md` 是共享开发指令的唯一来源。`.agents/skills/` 是技能唯一来源。

迁移或复制仓库时保留隐藏目录和符号链接。Windows 或不支持符号链接的环境需采用客户端支持的导入或生成副本方案，并自行管理同步；不能将链接目标字符串误当作文件正文。

向其他项目采用规范时，保留适用的工程要求，替换本仓库的目录导航和检查命令。

GPU 与 vLLM Skills 的依赖在目标项目环境中准备，不加入本仓库开发依赖。`model-microbenchmark` 依赖支持 `vllm bench forward` 的 CUDA 环境；`model-recipes` 查询脚本使用 Bash、jq 和 awk；Kernel 示例的 PyTorch、pandas、FlashInfer、vLLM 与多卡要求见对应 Skill。安装技能不启动模型服务或运行 GPU 任务。

## 2. Claude Code

- 根 `CLAUDE.md` 使用 `@AGENTS.md` 导入共享指令。
- `.claude/skills` 链接到 `../.agents/skills`，共享技能与其附属资源，包括可执行的 Shell 检查脚本。
- `.claude/agents` 链接到 `../.agents/agents`，角色源文件统一维护在 `.agents/agents/`。

可选 Hooks 和状态栏的步骤：

1. 阅读 `.claude/settings.example.json`，选择需要的 Hook 事件与状态栏配置。通知事件按需启用。
2. 将选定项合并到目标项目 `.claude/settings.json`，保留已有配置；核对客户端支持的事件和字段。
3. 脚本按 `.claude/hooks/` 与 `.claude/scripts/` 路径部署。`notifications/common.sh` 随目录一起复制，不单独注册为 Hook。
4. 在目标客户端验证所选事件与命令；本仓库 unittest 只验证隔离脚本行为与文件路径。

本仓库未提供 MCP 服务器配置，也未预设插件或外部工具授权。

本次迁移未创建活动的 `.claude/settings.json`，未启用示例中的通知、权限和外部服务。

## 3. Codex

根 `AGENTS.md` 提供仓库指令，Skills 位于 `.agents/skills/`。无需额外的仓库级 Codex 配置；执行权限与工具设置沿用运行环境。

在所用 Codex 版本确认根指令与共享 Skills 的实际发现结果。Claude 的角色与 Hooks 不会因此自动变成 Codex 配置。

## 4. Gemini

`GEMINI.md` 使用 `@AGENTS.md` 作为共享入口。使用时确认目标客户端的导入与 Skills 加载行为。

Cursor 与 Copilot 适配已移除，当前仓库不提供专用入口。

## 5. 本地与 CI 验证

从完整 Git 工作区运行 `python3 scripts/check.py --check`，执行 Python lint/格式、隔离回归与 Shell 检查。安装依赖见根 README。缺少工具或 Shell 检查未选中文件会返回非零。

需要 Python 自动修复时显式使用 `python3 scripts/check.py --fix`，应用安全 Ruff 修复与格式化后重新运行全部验证。pre-commit 中的修复 hooks 需单独检查其修改。

CI 使用显式 `--check` 入口验证 Linux 与 macOS；实际客户端加载、目标模型与 GPU/NPU 验证仍需对应环境。

## 6. 维护

共享开发指令维护在根目录 `AGENTS.md`，Python 检查以 `pyproject.toml` 为准。资源索引维护在 `.agents/README.md`，角色与 Skills 分别维护在 `.agents/agents/` 和 `.agents/skills/`，Claude Hooks 与设置维护在 `.claude/`，测试维护在 `tests/`。

变更公共路径时同步更新客户端入口、索引和测试。升级客户端或启用新的配置项时，重新检查实际加载行为。

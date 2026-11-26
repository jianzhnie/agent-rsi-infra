# 入口与部署说明

本仓库维护共享规范和工具适配。目录存在、链接有效与真实客户端已加载是不同的验证范围。 当前逐能力状态及加载验证要求见 [Agent 能力矩阵](agent-compatibility.md)。

## 1. 共享资源

根目录 `AGENTS.md` 是共享开发指令的唯一来源。`.agents/skills/` 是技能唯一来源。

迁移或复制仓库时保留隐藏目录和符号链接。Windows 或不支持符号链接的环境需采用客户端支持的导入或生成副本方案，并自行管理同步；不能将链接目标字符串误当作文件正文。

向其他项目采用规范时，保留适用的工程要求，替换本仓库的目录导航和检查命令。

GPU 与 vLLM Skills 的依赖在目标项目环境中准备，不加入本仓库开发依赖。`model-microbenchmark` 依赖支持 `vllm bench forward` 的 CUDA 环境；`model-recipes` 查询脚本使用 Bash、jq 和 awk；Kernel 示例的 PyTorch、pandas、FlashInfer、vLLM 与多卡要求见对应 Skill。安装技能不启动模型服务或运行 GPU 任务。

## 2. Claude Code

- 根 `CLAUDE.md` 使用 `@AGENTS.md` 导入共享指令。
- `.claude/skills` 链接到 `../.agents/skills`，共享技能与其附属资源，包括可执行的 Shell 检查脚本。
- `.claude/agents/` 是 Claude 格式的生成适配；通用角色正文维护在 `.agents/agents/`。

可选 Hooks 和状态栏的步骤：

1. 阅读 `.claude/settings.example.json`，选择需要的 Hook 事件与状态栏配置。通知事件按需启用。
2. 将选定项合并到目标项目 `.claude/settings.json`，保留已有配置；核对客户端支持的事件和字段。
3. 脚本按 `.claude/hooks/` 与 `.claude/scripts/` 路径部署。`notifications/common.sh` 随目录一起复制，不单独注册为 Hook。
4. 在目标客户端验证所选事件与命令；本仓库 pytest 只验证隔离脚本行为与文件路径。

本仓库未提供 MCP 服务器配置，也未预设插件或外部工具授权。

本次迁移未创建活动的 `.claude/settings.json`，未启用示例中的通知、权限和外部服务。

## 3. Codex

根 `AGENTS.md` 提供仓库指令，Skills 位于 `.agents/skills/`。`.codex/config.toml` 注册角色，`.codex/agents/*.toml` 保存生成的角色指令；不预设模型、网络或权限豁免。性能分析角色使用只读 sandbox，调试角色继承运行环境权限。

在所用 Codex 版本确认根指令与共享 Skills 的实际发现结果。角色通过 Codex 专用配置接入，Hooks 仍属于 Claude 专用资源；项目配置受客户端版本和项目信任机制约束，真实加载需在目标客户端确认。

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

## SGLang 专项 Skills

分布式挂起、Kernel 组织、代码清理和 KL 一致性技能中的源码路径与框架接口指目标 SGLang checkout；不要求本仓库安装 SGLang。`llm-torch-profiler-analysis` 默认分析已有本地 trace，在线采集脚本保留为按需审查的上游资源。`mechanical-refactor-verify` 依赖 Git、Python 3.10+ 和目标仓库的格式化工具，附属测试使用 pytest；执行证明脚本及 hooks 前检查其内容，机械变换通过不代表业务行为正确。

## 角色适配维护

`.agents/agents/*.md` 只保存 name、description、署名、许可及职责正文，不包含客户端工具名、模型或权限字段。修改后运行 `python3 scripts/sync_agents.py`，提交共享源文件与两端生成结果；`--check` 检查是否同步。生成器只管理角色配置，不修改 Claude 活动设置或用户级 Codex 配置。

将适配用于其他项目时保持共享参考路径，检查目标客户端支持的配置格式；合并 `.codex/config.toml` 的角色表到已有配置，不直接覆盖。角色可用不等于自动委派已获授权；工具与 sandbox 是客户端边界，Bash 工具列表也不是完整的只读保障。

Codex 格式依据：[官方多 Agent 文档](https://developers.openai.com/codex/multi-agent) 与 [配置 schema](https://github.com/openai/codex/blob/main/codex-rs/core/config.schema.json)。本仓库仅验证生成一致性与格式，未启动真实客户端验证角色发现。

## TorchTitan 离线诊断资源

`llm-torch-profiler-analysis` 增加 CUDA Graph trace 整理，`training-inference-change` 增加已有 activation 日志的 HTML 比较。脚本随原 Skill 部署，使用 Python 3.10+ 标准库，不安装 TorchTitan/PyTorch、不启用在线采集。分别按 [trace 参考](../.agents/skills/llm-torch-profiler-analysis/references/cuda-graph-trace.md)和[数值比较参考](../.agents/skills/training-inference-change/references/offline-numerics.md)调用，保留对应 `references/torchtitan/` 的来源与 BSD 许可。客户端适配路径不变，未新增真实客户端加载验证。

## InfraRSI 资源

12 个 Skill 仍放在共享 `.agents/skills/`，客户端沿用现有发现方式，无需新增角色或配置。完整复制资源时保留兄弟目录 `_catalogue/`（适配说明、负结果、来源与许可），单独复制一个 Skill 时也需带上该目录并保持相对路径。它不是额外的 Skill 入口。

[适配边界](../.agents/skills/_catalogue/infrarsi-adaptation.md)说明哪些接口只存在于上游 harness；本仓库没有安装该 runtime、GPU 工具链或模型，也未自动改写系统环境。所有资源为 experimental；实际客户端发现、目标版本数值与性能必须另行验证。

## ATTUNE Skill

`autotune-training-throughput` 提供本地日志测量、trace 分析和数值检查，通过共享目录发现；训练由目标项目现有入口执行。先读[来源与边界](../.agents/skills/autotune-training-throughput/UPSTREAM.md)。

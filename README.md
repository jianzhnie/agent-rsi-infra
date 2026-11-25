# agent-rsi-infra

面向 Coding Agent 递归自我改进（Recursive Self-Improvement，RSI）的工程基础设施，集中维护共享规范、Skills、工具适配与验证流程。

本仓库提供共享规则、Skill 资源和客户端适配，不提供 Agent Runtime、训练框架或自动规则晋级服务。改进由任务证据、回归测试和人工审查驱动。

## 从这里开始

| 你要做什么 | 入口 |
| --- | --- |
| 配置 Claude Code | 根 `CLAUDE.md` 导入 `AGENTS.md`，`.claude/skills` 共享技能；Hooks 按需启用 |
| 配置 Codex | 根 `AGENTS.md`、`.agents/skills/` 与生成的 `.codex/` 角色配置 |
| 配置 Gemini | 根 `GEMINI.md` 提供导入入口；目标版本的导入与技能发现仍需验证 |
| 选择 Skill 完成任务 | [任务路由](docs/component-skills.md) → [使用样例](docs/skill-examples.md) → 对应 `SKILL.md` |
| 检查并交付结果 | 下方检查命令与[任务契约、验证报告](docs/task-evidence.md)；逐项记录未执行原因 |

具体部署步骤见[部署说明](docs/deployment.md)。[兼容矩阵](docs/agent-compatibility.md)区分静态检查和真实加载；当前未记录已验证的客户端精确版本。

## 典型任务：优化一个 Triton Kernel

1. 阅读目标项目指令、相关实现和调用方，加载 `triton-kernel-writing`；测量时再加载 `kernel-microbenchmark`。若目标为 SGLang，先用 `kernel-organization` 查找相同契约的实现。
2. 固定目标 revision、输入 shape/dtype、设备和优化范围；定义独立 reference、误差容限及边界输入，先约定验收条目。
3. 运行 baseline 数值测试，再实现候选并重跑相同测试，检查越界、尾块及不支持的输入。
4. 在相同环境、计时边界和缓存策略下预热并重复测量双方，保留原始样本；profiler 只用于诊断。
5. 按[完整示例](docs/skill-examples.md#kernel-优化交付示例)生成 Validation Report，记录失败、未执行项和原因；没有 GPU 结果时不宣称加速。
6. 人工核对代码、数值和性能证据，决定接受、继续试验或拒绝。读取 Skill、报告结构通过都不等于优化验收通过。

离线诊断还提供 [CUDA Graph trace 整理](.agents/skills/llm-torch-profiler-analysis/references/cuda-graph-trace.md)与[逐算子数值日志比较](.agents/skills/training-inference-change/references/offline-numerics.md)，均无需启动模型；真实设备与客户端验证边界见各参考。

训练优化还可按[专项路由](docs/component-skills.md#训练优化专项路由)选用 InfraRSI 的完整 update、内存、并行、语义与恢复等技能；它们均为 experimental，上游 harness 与设备任务未在本仓库验证。

## 资源与设计

- [资源索引](.agents/README.md)：角色、Skills、来源与维护入口。
- [RSI 设计](docs/RSI_DESIGN.md)：架构边界与改进闭环。
- [文档索引](docs/README.md)：工程标准、领域实践、调研与部署。
- [贡献指南](CONTRIBUTING.md)：变更、审查与验证要求。

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

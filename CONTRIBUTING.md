# 贡献与验证

仓库结构与执行要求见 [AGENTS.md](AGENTS.md)。本仓库维护工程流程和工具适配，目标项目的业务代码、模型测试与 GPU benchmark 仍在对应仓库执行。

## 修改流程

1. 明确需求、现有契约和受影响的入口；先查是否已有同类实现。
2. 修改最小完整范围。工具入口复用共享 Skill，不复制正文。
3. 根据行为运行相关回归，再执行 `python3 scripts/check.py` 与 `pre-commit run --all-files`。
4. 报告真实命令、结果与未执行项。路径或部署变化同步文档与索引。

本地开发环境需 Python 3.10+、Bash、Git、jq、shellcheck；Python 工具通过 `python3 -m pip install -e '.[dev]'` 安装。Shell 脚本兼容 macOS 自带 Bash，文件选择需要支持 `git ls-files --deduplicate` 的 Git。

提交说明包含动机、兼容性、验证结果，以及 AI 工具的参与范围。保留外部资源的来源和许可，不把格式检查通过当作模型行为或性能已验证。

## 从反馈改进流程

发现重复失败后，保存失败输入、日志、代码版本与预期结果；定位原因，再选择最小修正：

- 实现或接口问题：修代码，并补相关回归。
- 可机械检查的问题：改脚本、测试或 CI。
- 任务特有且值得复用的知识：更新对应 Skill，写清证据和适用边界。

更新规则和 Skill 需审查；不因一次偶发问题增加永久限制，不自动将日志内容改写为指令。对性能、数值或硬件结论保留原始证据。

## 调研实践的落地

| 参考 | 采用的实践 | 本仓库实现 |
| --- | --- | --- |
| [工程规范总览](docs/research/github-ai-infra-engineering-standards.md) | 指令、Skill、Hooks 和 CI 分工 | 根指令、共享 Skills、可选 Claude Hooks、[CI](.github/workflows/check.yml) |
| [Megatron-LM 与训练框架](docs/research/training-frameworks-agent-engineering.md) | 先读取任务依据，按影响选择验证 | [ai-infra-change](.agents/skills/ai-infra-change/SKILL.md) |
| [SGLang 与推理框架](docs/research/inference-frameworks-agent-engineering.md) | Kernel 去重、契约、并发和多阶段验证 | Skill 的契约步骤与[验证矩阵](.agents/skills/ai-infra-change/references/validation.md) |
| [Liger Kernel 与训练验证](docs/research/training-frameworks-agent-engineering.md) | 正确性、模型行为与 benchmark 分开 | 验证矩阵中的训练、Kernel 与性能要求 |
| [PyTorch CLAUDE.md](https://github.com/pytorch/pytorch/blob/1d28e3a704d1d634d240e8fe0566c0c6df975458/CLAUDE.md) | 环境定位、显式状态、生成文件、回归与诊断、完整 CI 结果 | 根指令中的工作、环境与提交约定；PT2 Skill 的日志和配置指导 |
| 上述报告中的确定性检查实践 | 同一入口可本地运行或用于 CI | [scripts/check.py](scripts/check.py)、可执行 Shell 检查和隔离测试 |

调研文件保留原有核查范围。这里采用工程方法，不将上游某个版本的命令、产品能力或性能数字视为本仓库已经实测的结果。

PyTorch 指令采用固定版本的方法性约定，保留来源；许可见随 PT2 Skill 保留的 [上游 LICENSE](.agents/skills/pt2-bug-basher/LICENSE)。其构建、测试框架与 GitHub 政策不替代本仓库的实际命令和用户授权。

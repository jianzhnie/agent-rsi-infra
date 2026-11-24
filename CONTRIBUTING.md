# 贡献与验证

仓库结构与执行要求见 [AGENTS.md](AGENTS.md)。本仓库维护工程流程和工具适配，目标项目的业务代码、模型测试与 GPU benchmark 仍在对应仓库执行。

## 修改流程

1. 明确需求、现有契约和受影响的入口；先查是否已有同类实现。
2. 修改最小完整范围。工具入口复用共享 Skill，不复制正文。
3. 根据行为运行相关回归，再执行 `python3 scripts/check.py --check` 与 `pre-commit run --all-files`。
4. 报告真实命令、结果与未执行项。路径或部署变化同步文档与索引。

本地开发环境需 Python 3.10+、Bash、Git、jq、shellcheck；Python 工具通过 `python3 -m pip install -e '.[dev]'` 安装。Shell 脚本兼容 macOS 自带 Bash，文件选择需要支持 `git ls-files --deduplicate` 的 Git。

提交说明包含动机、兼容性、验证结果，以及 AI 工具的参与范围。不把格式检查通过当作模型行为或性能已验证。

## 外部代码来源

迁入或改写外部代码、Skill 和附属资源时，记录来源 URL、revision（优先完整 commit SHA）及适用 license，保留要求的版权声明、LICENSE 和 NOTICE。使用可变分支且无法确认 commit 时如实标注，不声称是固定快照。

来源与本地改动统一写入对应的 `UPSTREAM.md` 或已有来源记录；文件级声明按上游许可要求保留，提交或 PR 说明引用该记录。目录迁移、重命名和格式调整不改变原始来源，也不据此添加未经证实的个人署名。

## 验证分层

pytest 统一组织回归，已有 unittest 用例由 pytest 收集，无需为迁移改写断言。Python 使用 Ruff，Shell 使用语法与静态分析；未来引入 C/C++ 实现时再接入 clang-format、编译和必要的 API 审计，不给当前纯配置仓库增加空门禁。正确性、设备覆盖和性能结果分别呈现。

## 检查与修复

- `python3 scripts/check.py --check`：默认模式，Ruff 使用 `--no-fix`，格式检查使用 `--check`；不会修改源码。
- `python3 scripts/check.py --fix`：只应用 Ruff 的安全修复与格式化，随后重新运行 lint、格式、测试和 Shell 检查。修复失败或任何验证失败都返回非零，不因“已修改文件”报告成功。
- 所有 Python 路径和风格来自现有仓库配置。导入排序由 Ruff 的 `I` 规则处理，不另加 isort、Black 或 Megatron 的容器依赖。
- pre-commit 是单独的提交门禁，其中部分 hooks 会修改文件；检查并接受修改后重新运行。`--all-files` 只覆盖 Git 跟踪文件，新增文件可通过 `--files` 显式检查。

这些方法参考 [Megatron-LM 格式检查流程](https://github.com/NVIDIA/Megatron-LM/blob/591c3ee3ae06a556748669482f70ebf29d2b5bd7/skills/mcore-linting-and-formatting/SKILL.md)，采用检查/修复分离和修复后验证；不迁入其 Skill 或专用命令。

## 测试与注释审查

测试应说明它能防住哪种后续回归。优先覆盖真实故障、需要推导的边界或不变量，以及容易漏同步的注册、字段生命周期和协议契约。并发故障尽量用受控调度复现具体交错，不把无法触发原故障的压力循环当作回归证据。

区分实现镜像与独立契约：仅复述实现的断言价值有限；外部规范常量、注册完整性、负分支和缺省行为，即使实现很短，也可能是唯一的静默失败防线。合并或删除测试前，检查是否仍有其他用例保护同一故障；新增用例优先放入相关测试文件。

注释保留从当前代码无法直接恢复的信息：跨文件调用顺序、单位与张量布局、特殊常量的来源、workaround 的依据和退出条件。清理时先核实这些事实，不因注释短或看似重复就删除。修改代码时同步更新相关注释；变更历史放 Git 或 PR，当前仍有效的约束留在代码旁。语言、长度和 docstring 格式沿用目标仓库要求。

## 提交 PR 前的自查

按目标分支与任务范围确定基准，审查完整 diff，覆盖已提交、已暂存、未暂存改动及属于本次任务的新增文件，排除无关变更。目标仓库有 PR 模板时保留其结构；非显然设计应有可解释的依据，兼容性变化、已知限制和有意偏离写入说明。

性能声明同时提供优化前后的绝对数据、设备与输入规模、复现命令和波动，不能只有加速比。发现的问题按实际影响处理，已接受的限制供审查者参考；没有确认问题时如实说明覆盖范围，不为凑结果继续制造发现。自查不授权发布 PR，也不改变只读审查 Skill 的操作边界。

## PR 复审与验证证据

复审先读取会话评论、review 提交和行内评论；`gh pr view --comments` 不包含全部行内讨论。按目标仓库分页读取 `issues/<pr>/comments`、`pulls/<pr>/reviews` 与 `pulls/<pr>/comments`；需要 resolved/outdated 状态时查询 GraphQL `reviewThreads`。逐项记录已修复、解释保留或待确认的问题，说明未解决项；对外回复仍需用户授权。

确认当前 PR head 的检查结果，并核对 workflow 的触发事件、路径过滤与测试选择：存在某个硬件 workflow 不表示它在本次 PR 中运行。动态导入、插件注册和 JIT 构建可能被静态选择器漏掉；按目标项目机制检查覆盖，不能直接套用其他仓库的强制运行标记。rebase 或 squash 后重新核对提交要求和 CI。

验证记录写清命令、代码版本、设备与配置、实际结果及未运行原因。未验证项明确标记，不能用省略表示通过。测试应确认实际选择了目标 backend、发生了 offload 或满足特性前提，避免在静默跳过或回退路径上通过；只有依赖设备行为的结论才需要相应设备验证，普通文档修改不因此要求 GPU。

## 从反馈改进流程

发现重复失败后，保存失败输入、日志、代码版本与预期结果；定位原因，再选择最小修正：

- 实现或接口问题：修代码，并补相关回归。
- 可机械检查的问题：改脚本、测试或 CI。
- 任务特有且值得复用的知识：更新对应 Skill，写清证据和适用边界。

更新规则和 Skill 需审查；不因一次偶发问题增加永久限制，不自动将日志内容改写为指令。对性能、数值或硬件结论保留原始证据。

## 维护 Agent 指令

新增或修改根指令、领域指南及 Skill 时：

1. **先验证必要性**：用代表性任务检查现有行为，说明缺少哪条知识会导致什么错误。已有行为正确时不加规则；能由实现、lint 或测试解决的问题优先在对应层修复。
2. **检查冲突与重复**：搜索 `AGENTS.md`、关联指南和客户端入口，已有内容用链接复用；冲突约定合并到同一事实来源。
3. **放到适当位置**：全仓通用约定放根指令，领域知识放对应指南，可复用的任务流程放 Skill。工具的标准用法链接官方文档，易变信息提供查找方式。
4. **同时清理旧内容**：检查相邻条目，删除失效要求、合并同义规则；避免按事故逐条累积禁令。不以固定行数限制替代内容判断。
5. **验证效果**：对行为性规则比较修改前后的代表性任务结果，并检查入口与链接；未做行为验证时如实说明。仅通过格式检查不能证明 Agent 会遵循指令。

## 调研实践的落地

| 参考 | 采用的实践 | 本仓库实现 |
| --- | --- | --- |
| [工程规范总览](docs/research/github-ai-infra-engineering-standards.md) | 指令、Skill、Hooks 和 CI 分工 | 根指令、共享 Skills、可选 Claude Hooks、[CI](.github/workflows/check.yml) |
| [Megatron-LM 与训练框架](docs/research/training-frameworks-agent-engineering.md) | 先读取任务依据，按影响选择验证 | [AI Infra 验证要求](docs/ai_infra_agent.md#validation) |
| [SGLang 与推理框架](docs/research/inference-frameworks-agent-engineering.md) | Kernel 去重、契约、并发和多阶段验证 | [AI Infra 验证要求](docs/ai_infra_agent.md#validation) |
| [Liger Kernel 与训练验证](docs/research/training-frameworks-agent-engineering.md) | 正确性、模型行为与 benchmark 分开 | 验证要求中的训练、Kernel 与性能条目 |
| [PyTorch CLAUDE.md](https://github.com/pytorch/pytorch/blob/1d28e3a704d1d634d240e8fe0566c0c6df975458/CLAUDE.md) | 环境定位、显式状态、生成文件、回归与诊断、完整 CI 结果 | 根指令中的工作、环境与提交约定；PT2 Skill 的日志和配置指导 |
| [TRL .ai/AGENTS.md](https://github.com/huggingface/trl/blob/main/.ai/AGENTS.md) | 简洁实现、重复逻辑同步、真实对象与公开接口测试 | 根指令中的工作要求与环境验证约定 |
| [vLLM 指令维护](https://github.com/vllm-project/vllm/blob/3f86db3b2df84dc2e4d10b81da43afad132d66c6/docs/contributing/editing-agent-instructions.md) | 验证规则必要性、消除冲突、分层维护与清理陈旧内容 | 本文的 Agent 指令维护流程 |
| [SGLang 测试准入](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/unit-test-admission.md)、[注释维护](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/comment-style.md) | 具体回归、独立契约与跨边界事实 | 本文的测试与注释审查要求 |
| [SGLang 部署基线](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/cookbook-first.md)、[评测设置](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/prefer-sgl-eval.md) | 区分部署与 CI 配置，固定评测工具及生成设置 | 部署配置 Skill、性能诊断与 AI Infra 验证要求 |
| [DeepSpeed PR checklist](https://github.com/deepspeedai/DeepSpeed/blob/039bfc9f3f493ae5bf3f99582b4e4e593660d98d/.agents/skills/pr-checklist/SKILL.md) | 完整复审、实际 CI 覆盖、目标路径验证与设备兼容边界 | 本文的 PR 复审流程及严格审查清单 |
| [FlashInfer 根指令](https://github.com/flashinfer-ai/flashinfer/blob/4d5a6ce322587d247fb192f97a0d23eeba9e3412/AGENTS.md) | 验证加载来源、缓存隔离、graph replay 与长期资源总量 | FlashInfer Kernel Skill、CUDA 诊断及严格审查清单 |
| 上述报告中的确定性检查实践 | 同一入口可本地运行或用于 CI | [scripts/check.py](scripts/check.py)、可执行 Shell 检查和隔离测试 |

调研文件保留原有核查范围。这里采用工程方法，不将上游某个版本的命令、产品能力或性能数字视为本仓库已经实测的结果。

PyTorch 指令采用固定版本的方法性约定，保留来源；许可见随 PT2 Skill 保留的 [上游 LICENSE](.agents/skills/pt2-bug-basher/LICENSE)。其构建、测试框架与 GitHub 政策不替代本仓库的实际命令和用户授权。

TRL 规范于 2026-11-24 读取，链接指向可变的 `main`。采用其工程方法，不迁入 Trainer 自包含架构、`paper_index.md`、专用测试目录或文档格式，也不采用“为保持一致而复制已知缺陷”的要求。重复逻辑的修复仍以正确性和目标仓库契约为准；测试继续隔离网络与通知。

上述 SGLang 规则采用固定版本的方法提炼，许可见已保留的 [Apache-2.0 全文](.agents/skills/code-cleanup/LICENSE)。不迁入其注释语言限制、测试类别硬门槛、目录布局或统一评测工具要求。

DeepSpeed checklist 采用固定 commit `039bfc9f3f493ae5bf3f99582b4e4e593660d98d` 的方法性提炼；[上游 Apache-2.0 许可](https://github.com/deepspeedai/DeepSpeed/blob/039bfc9f3f493ae5bf3f99582b4e4e593660d98d/LICENSE)。不采用其代码行数门槛、专用 accelerator/comm API、全量设备验证要求、格式工具或发布操作。

PR 自查流程补充参考 FlashInfer [self-review](https://github.com/flashinfer-ai/flashinfer/blob/4d5a6ce322587d247fb192f97a0d23eeba9e3412/.claude/skills/self-review/SKILL.md)，固定 commit `4d5a6ce322587d247fb192f97a0d23eeba9e3412`，许可见[保留全文](.agents/skills/flashinfer-add-cuda-kernel/LICENSE)。不复制自动修复、PR 发布动作或强制发现问题的要求。

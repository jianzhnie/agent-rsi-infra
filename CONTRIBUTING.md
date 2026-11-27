# 贡献与验证

仓库结构与执行要求见 [AGENTS.md](AGENTS.md)。本仓库维护工程流程和工具适配，目标项目的业务代码、模型测试与 GPU benchmark 仍在对应仓库执行。

## 协作行为

以下要求适用于 Issue、PR、代码审查及其他项目协作：

- 围绕问题、代码和证据讨论，尊重不同背景、经验与观点；不使用侮辱、歧视、人身攻击或骚扰表达。
- 提供具体、可行动的反馈，认真核对不同意见；确认错误后说明影响、及时更正，并对受影响者承担责任。
- 未经明确许可，不公开他人的邮箱、地址等私人信息；提交日志、截图和复现材料前移除个人信息。
- 遇到不当行为时保留必要事实供维护者核实，不通过公开传播私人信息或攻击当事人的方式处理。

本节参考 [ms-swift CODE_OF_CONDUCT.md](https://github.com/modelscope/ms-swift/blob/9a1155e53a0ba136c4cbeebf4dd9fb7e9b80b541/CODE_OF_CONDUCT.md)，固定 revision `9a1155e53a0ba136c4cbeebf4dd9fb7e9b80b541`。上游基于 [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct.html)，其执法分级参考 Mozilla；本节为中文原则摘要，未复制完整准则、上游联系地址或处罚承诺。该文件是社区行为准则，不作为代码风格或技术验证要求的来源。

## 修改流程

1. 明确需求、现有契约和受影响的入口；先查是否已有同类实现。
2. 修改最小完整范围。工具入口复用共享 Skill，不复制正文。
3. 根据行为运行相关回归，再执行 `python3 scripts/check.py --check` 与 `pre-commit run --all-files`。
4. 报告真实命令、结果与未执行项。路径或部署变化同步文档与索引。

本地开发环境需 Python 3.10+、Bash、Git、jq、shellcheck；Python 工具通过 `python3 -m pip install -e '.[dev]'` 安装。Shell 脚本兼容 macOS 自带 Bash，文件选择需要支持 `git ls-files --deduplicate` 的 Git。

提交说明包含动机、兼容性、验证结果，以及 AI 工具的参与范围。不把格式检查通过当作模型行为或性能已验证。

## 代码规范与依赖

- 新增 Python 变量和函数使用 `snake_case`，类名使用 `PascalCase`。遵循所在模块的既有约定；外部 API、协议字段和迁入代码不为统一命名而破坏兼容或制造无关重命名。
- Python 缩进使用四个空格，不使用 Tab。格式与 lint 由 [pyproject.toml](pyproject.toml) 中的 Ruff 配置执行，不另建平行工具配置。
- 实现前先检查标准库、现有依赖及已有模块能否满足需求。需要新增依赖时，优先采用维护活跃、接口稳定、许可兼容的开源库，说明实际用途与维护成本，不为简单功能引入重型依赖。
- 行为变更使用现有或新增测试保护：冒烟测试验证主要路径，必要的边界与失败用例验证契约。沿用下文的[测试准入要求](#测试与注释审查)，不为普通文档修改机械增加测试。
- 提交前分别完成[静态检查](#检查与修复)与相关行为测试；lint 通过不能代替测试，尚未执行的 CI 或设备检查不能写成通过。

本节提炼自 [ms-swift CONTRIBUTING_CN.md](https://github.com/modelscope/ms-swift/blob/9a1155e53a0ba136c4cbeebf4dd9fb7e9b80b541/CONTRIBUTING_CN.md) 的“代码规范和开发方式”“Running CI Tests”，固定 revision `9a1155e53a0ba136c4cbeebf4dd9fb7e9b80b541`，上游仓库许可为 [Apache-2.0](https://github.com/modelscope/ms-swift/blob/9a1155e53a0ba136c4cbeebf4dd9fb7e9b80b541/LICENSE)，本仓库保留同许可[全文](LICENSE)。本地适配复用 Ruff、pytest 和统一检查入口，补充既有接口与依赖成本边界；未迁入其首次贡献必须关联 Issue、Fork 流程或算力支持政策。AI 贡献的人类责任沿用现有要求，不重复维护。

## 接口、配置与模块边界

- 名称表达实际含义；时间、字节、样本/帧/token 数等易混淆量注明单位或对象，例如 `timeout_seconds`、`audio_frames`。外部接口、checkpoint 键和既有领域术语按契约保留，不为风格进行无关改名。
- 修改接口时让类型说明参数、容器元素和返回结构；跨组件记录需要字段契约时使用项目已有的数据类型。外部 JSON、请求和服务返回值在进入可信内部路径前校验，不用强制类型转换或忽略注解代替运行时验证；不为此统一引入新验证库。
- 配置默认值在所属层定义一次并向下传递，底层不重复维护同一策略。部署路径和地址来自目标环境配置，经验常量记录单位、来源与适用条件。
- 共享调度或运行逻辑放在职责合适的公共模块，不从兄弟模型的专用包借用实现。导入遵循现有依赖方向；可选依赖按项目约定延迟加载，不用导入技巧掩盖循环依赖。
- 错误处理保留真实失败，不用零值、空结果或默认成功掩盖异常；日志复用项目机制，避免重复初始化。局部恢复或回退须对应真实支持契约。

本节选择性提炼自 SGLang-Omni coding-style；固定来源、许可和排除项见[适配记录](.agents/skills/code-reviewer/references/sglang-omni/UPSTREAM.md)。简洁实现、注释、Hook 兼容与测试要求沿用已有章节，不另建平行规范。

## 外部代码来源

迁入或改写外部代码、Skill 和附属资源时，记录来源 URL、revision（优先完整 commit SHA）及适用 license，保留要求的版权声明、LICENSE 和 NOTICE。使用可变分支且无法确认 commit 时如实标注，不声称是固定快照。

来源与本地改动统一写入对应的 `UPSTREAM.md` 或已有来源记录；文件级声明按上游许可要求保留，提交或 PR 说明引用该记录。目录迁移、重命名和格式调整不改变原始来源，也不据此添加未经证实的个人署名。

## 验证分层

pytest 统一组织根 tests/ 的回归，已有 unittest 用例由 pytest 收集，无需为迁移改写断言。Python 使用 Ruff，Shell 使用语法与静态分析；未来引入 C/C++ 实现时再接入 clang-format、编译和必要的 API 审计，不给当前纯配置仓库增加空门禁。正确性、设备覆盖和性能结果分别呈现。

## 检查与修复

- `python3 scripts/check.py --check`：默认模式，Ruff 使用 `--no-fix`，格式检查使用 `--check`；不会修改源码。
- `python3 scripts/check.py --fix`：只应用 Ruff 的安全修复与格式化，随后重新运行 lint、格式、资源契约、角色适配、测试和 Shell 检查。修复失败或任何验证失败都返回非零，不因“已修改文件”报告成功。
- 所有 Python 路径和风格来自现有仓库配置。导入排序由 Ruff 的 `I` 规则处理，不另加 isort、Black 或 Megatron 的容器依赖。
- pre-commit 是单独的提交门禁，其中部分 hooks 会修改文件；检查并接受修改后重新运行。`--all-files` 只覆盖 Git 跟踪文件，新增文件可通过 `--files` 显式检查。

这些方法参考 [Megatron-LM 格式检查流程](https://github.com/NVIDIA/Megatron-LM/blob/591c3ee3ae06a556748669482f70ebf29d2b5bd7/skills/mcore-linting-and-formatting/SKILL.md)，采用检查/修复分离和修复后验证；不迁入其 Skill 或专用命令。

## 测试与注释审查

测试应说明它能防住哪种后续回归。优先覆盖真实故障、需要推导的边界或不变量，以及容易漏同步的注册、字段生命周期和协议契约。并发故障尽量用受控调度复现具体交错，不把无法触发原故障的压力循环当作回归证据。

区分实现镜像与独立契约：仅复述实现的断言价值有限；外部规范常量、注册完整性、负分支和缺省行为，即使实现很短，也可能是唯一的静默失败防线。合并或删除测试前，指出保留的具体用例及其保护的同一故障；新增用例优先放入相关测试文件。

注释保留从当前代码无法直接恢复的信息：跨文件调用顺序、单位与张量布局、特殊常量的来源、workaround 的依据和退出条件。清理时先核实这些事实，不因注释短或看似重复就删除。修改代码时同步更新相关注释；变更历史放 Git 或 PR，当前仍有效的约束留在代码旁。语言、长度和 docstring 格式沿用目标仓库要求。

GPU 测试需由实际设备作业选中并执行，不能长期放在纯 CPU suite 中静默跳过。更新 golden 数值时解释预期变化，重新生成受影响 backend/suite 的结果，不放宽容差使失败通过；按实际运行报告覆盖范围。

表征重构保持公共输入输出时，不以私有元组、缓存布局等快照阻止变更，除非该表征本身就是协议契约。删除测试需证明保留用例保护同一失败，不能仅凭行覆盖重合判断冗余；不靠删除断言、替换被测逻辑或扩大 skip 使测试通过。此处补充来源同上文 SGLang-Omni 适配记录。

## 测试接入 CI

新增、移动或重命名测试时，先核对目标仓库的发现/注册机制和实际调用命令：pytest 能收集不代表显式文件矩阵或直接执行脚本的 CI 会运行。需要注册时同步更新矩阵；刻意保留为手动或辅助测试时说明原因。按 CI 的调用方式运行受影响测试，不只验证另一种本地入口。

明确 CPU/GPU、设备数量、依赖和模型需求，检查选择器的缺省行为，避免 CPU 测试误占 GPU 或设备测试静默跳过。工作流由模板生成时修改模板、运行生成器并同时提交模板与产物；直接维护的 workflow 不因此新增模板。

本仓库的 [CI](.github/workflows/check.yml) 直接维护，通过 `python scripts/check.py --check` 调用 pytest 发现 `tests/`，无需逐文件注册或添加 GPU 常量。按实际收集结果确认新测试被选中；报告注册位置或发现依据、执行命令、硬件前提和未执行原因。

方法提炼自 slime 的 add-tests-and-ci，固定来源、许可和适配边界见 [slime 来源记录](.agents/skills/training-inference-change/references/slime/UPSTREAM.md)。

## 提交 PR 前的自查

按目标分支与任务范围确定基准，审查完整 diff，覆盖已提交、已暂存、未暂存改动及属于本次任务的新增文件，排除无关变更。目标仓库有 PR 模板时保留其结构；非显然设计应有可解释的依据，兼容性变化、已知限制和有意偏离写入说明。

PR 说明先给出具体输入或用户工作流、已有行为与预期行为，解释根因所属层及选择该修复的依据。机械移动与逻辑修改分别标明；若临时绕过上游问题，记录上游 Issue 和退出条件。先确认目标分支及进行中的迁移/PR 是否已解决该问题，不把缺少 Issue 本身视为拒绝依据。

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
| [工程实践标准](docs/engineering-standards.md) | 指令、Skill、Hooks 和 CI 分工 | 根指令、共享 Skills、可选 Claude Hooks、[CI](.github/workflows/check.yml) |
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

PyTorch 指令采用固定版本的方法性约定，保留来源；许可见随 PT2 Skill 保留的 [上游 LICENSE](.agents/skills/pytorch-compiler-debugging/LICENSE)。其构建、测试框架与 GitHub 政策不替代本仓库的实际命令和用户授权。

TRL 规范于 2026-11-24 读取，链接指向可变的 `main`。采用其工程方法，不迁入 Trainer 自包含架构、`paper_index.md`、专用测试目录或文档格式，也不采用“为保持一致而复制已知缺陷”的要求。重复逻辑的修复仍以正确性和目标仓库契约为准；测试继续隔离网络与通知。

上述 SGLang 规则采用固定版本的方法提炼，许可见已保留的 [Apache-2.0 全文](.agents/skills/sglang-code-cleanup/LICENSE)。不迁入其注释语言限制、测试类别硬门槛、目录布局或统一评测工具要求。

DeepSpeed checklist 采用固定 commit `039bfc9f3f493ae5bf3f99582b4e4e593660d98d` 的方法性提炼；[上游 Apache-2.0 许可](https://github.com/deepspeedai/DeepSpeed/blob/039bfc9f3f493ae5bf3f99582b4e4e593660d98d/LICENSE)。不采用其代码行数门槛、专用 accelerator/comm API、全量设备验证要求、格式工具或发布操作。

PR 自查流程补充参考 FlashInfer [self-review](https://github.com/flashinfer-ai/flashinfer/blob/4d5a6ce322587d247fb192f97a0d23eeba9e3412/.claude/skills/self-review/SKILL.md)，固定 commit `4d5a6ce322587d247fb192f97a0d23eeba9e3412`，许可见[保留全文](.agents/skills/flashinfer-add-cuda-kernel/LICENSE)。不复制自动修复、PR 发布动作或强制发现问题的要求。

训练与推理报告的项目实践按 [来源与项目映射](.agents/skills/training-inference-change/UPSTREAM.md#调研方法的项目映射) 落地到共享工作流及按需参考；架构遵循 [RSI 设计](docs/RSI_DESIGN.md)，不自动创建目标框架配置或代替设备验证。

跨 Agent 或 Skill 比较结果时采用[任务契约与验证报告](docs/task-evidence.md)，保留未执行项及原始证据。报告结构检查不代表实际行为已验证。

检查入口保持顺序编排：`--only lint,tests` 运行选定项，`--timeout 300` 设置每项超时，`--json <path>` 保存命令、执行环境和状态。`--fix` 要求完整验证，不能与 `--only` 合用。缺依赖标记 blocked，执行非零或超时标记 failed；未选中项不宣称通过。JSON 仅含已选项，CI 继续运行完整入口。工具版本探测有独立短超时，不作为检查通过证据。

TorchTitan 的测试成本、golden 数值与 PR 必要性审查方法分别提炼自固定版本的 [tests.md](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/rules/tests.md)、[pr-review](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/skills/pr-review/SKILL.md) 和 [pr-description](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/skills/pr-description/SKILL.md)，revision `72e5566782bbdafaa9bafd422733a307319213c5`，许可见[保留的 BSD-3-Clause](.agents/skills/training-inference-change/references/torchtitan/LICENSE)。不迁入自动发布、强制人工摘要占位、固定审查裁决或无向后兼容政策。

角色适配可单独运行 `python3 scripts/check.py --only adapters`；发现漂移后修改共享源并运行 `python3 scripts/sync_agents.py`，再检查生成差异。统一检查不会自动重写客户端配置。

# Agent 资源索引

这里集中索引角色、共享 Skills 与 Claude 适配资源。共享指令见根目录 `AGENTS.md`。角色源文件位于 `agents/`，采用 Claude 格式；Skills 位于 `skills/`。

## 资源索引

路径相对本文件。角色与 Skill 的作者、版本、许可保留在各自 Frontmatter 中；未独立署名的脚本不推断具体作者，按仓库 Apache-2.0 许可维护。

| 名称 | 文件 | 用途 |
| --- | --- | --- |
| code-reviewer | [共享 Skill](skills/code-reviewer/SKILL.md) | 默认 light、按需 strict，只读报告有证据的问题 |
| debugger | [角色](agents/debugger.md) | 复现、定位和修复问题 |
| performance-analyzer | [角色](agents/performance-analyzer.md) | 根据性能测量分析瓶颈 |
| install-skill-from-github | [共享 Skill](skills/install-skill-from-github/SKILL.md) | GitHub Skill 迁入、许可与来源记录 |
| shell-check | [共享 Skill](skills/shell-check/SKILL.md) | 可执行 Shell 检查与结果汇总 |
| pt2-bug-basher | [上游适配 Skill](skills/pt2-bug-basher/SKILL.md) | 显式调用的 PyTorch 2 编译器排障流程 |
| add-or-fix-type-checking | [上游 Skill](skills/add-or-fix-type-checking/SKILL.md) | Transformers 类型检查流程，保留上游原文 |
| kernel-microbenchmark | [上游适配 Skill](skills/kernel-microbenchmark/SKILL.md) | GPU Kernel 正确性、计时与多卡基准 |
| triton-kernel-writing | [上游适配 Skill](skills/triton-kernel-writing/SKILL.md) | Triton 索引、特化、同步与调优 |
| model-recipes | [上游适配 Skill](skills/model-recipes/SKILL.md) | 按模型与硬件查询 vLLM 部署配置 |
| model-microbenchmark | [上游适配 Skill](skills/model-microbenchmark/SKILL.md) | 使用 vllm bench forward 测量模型前向 |
| debug-distributed-hang | [上游适配 Skill](skills/debug-distributed-hang/SKILL.md) | SGLang 多卡挂起、rank 分歧与通信诊断 |
| llm-torch-profiler-analysis | [上游适配 Skill](skills/llm-torch-profiler-analysis/SKILL.md) | 离线 LLM trace 分析与融合、重叠线索 |
| mechanical-refactor-verify | [上游适配 Skill](skills/mechanical-refactor-verify/SKILL.md) | 可重放机械变换验证，不替代行为测试 |
| code-cleanup | [上游适配 Skill](skills/code-cleanup/SKILL.md) | 有证据的代码清理与兼容边界检查 |
| kernel-organization | [上游适配 Skill](skills/kernel-organization/SKILL.md) | SGLang Kernel 契约、归属与去重 |
| kl-consistency-test | [上游适配 Skill](skills/kl-consistency-test/SKILL.md) | SGLang prefill/decode 与缓存状态一致性 |
| flashinfer-add-cuda-kernel | [上游适配 Skill](skills/flashinfer-add-cuda-kernel/SKILL.md) | FlashInfer CUDA、FFI、JIT 与 trace 集成 |
| context | [脚本](../.claude/hooks/session/context.sh) | 初始化会话，compact/resume 时保留已有记录 |
| record-event | [脚本](../.claude/hooks/logging/record-event.sh) | 命令、Agent、配置及异常日志 |
| guard-tool | [脚本](../.claude/hooks/tools/guard-tool.sh) | 工具调用前的补充拦截 |
| format-file | [脚本](../.claude/hooks/tools/format-file.sh) | 编辑后的 pre-commit 与 Shell 检查 |
| notify | [脚本](../.claude/hooks/notifications/notify.sh) | 可选桌面、语音与 Server酱通知 |
| summarize | [脚本](../.claude/hooks/session/summarize.sh) | 可选会话摘要通知 |
| status-line | [脚本](../.claude/scripts/status-line.sh) | 上下文用量、模型与 Git 状态 |
| settings | [设置示例](../.claude/settings.example.json) | 可选 Hook 事件绑定与状态栏 |

Claude 通过 `.claude/agents -> ../.agents/agents` 和 `.claude/skills -> ../.agents/skills` 使用同一份源文件。迁移目录不代表其他客户端能自动发现 Claude 角色。工程与提交约定由根 `CLAUDE.md` 导入 `AGENTS.md`。

`code-reviewer` 与两档清单统一维护在 `.agents/skills/code-reviewer/`，通过 `skills` 链接供 Claude 使用；不再维护重复 Agent。

## 部署

参见 [部署说明](../docs/deployment.md)。`settings.example.json` 仅保留 Hooks 和状态栏，不预设模型、权限豁免、插件或外部工具授权；选择需要的事件再合并到目标设置。

- `hooks/notifications/common.sh` 随脚本部署，不单独注册为 Hook。
- 基础依赖为 Bash、Git、jq；格式检查使用 pre-commit 和 shellcheck。
- 通知密钥从目标项目 `.claude/.env` 的 `SCT_SENDKEY` 读取，不执行该文件内容。无密钥时不发送网络通知。
- 测试替换 curl、osascript 和 say，不发送真实通知。真实客户端加载与事件触发需另行确认。
- `guard-tool` 仅补充已定义的拦截，不是完整的 Shell 安全边界。

## 维护来源

本地脚本、状态栏和原始设置可追溯到仓库 Git 历史，如 `80faff2`、`a241329`、`1cf2354`、`65be515`、`f52ed88`。共享资源保留各自署名与许可；不因目录迁移改写来源。

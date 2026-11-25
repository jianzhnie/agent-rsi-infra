# Agent 能力与验证矩阵

本表记录本仓库配置的验证程度，不代表客户端完整产品能力。状态按能力分别记录，整行不取最高等级；配置未提供也不等于客户端不支持。

| 客户端 | 共享指令 | Skills 发现 | 角色加载 | Hooks | 最近真实验证版本 | 真实客户端状态 |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Code | static-checked：入口导入路径存在 | static-checked：共享链接、索引与资源有效；实际发现未测 | static-checked：生成适配一致；实际角色可用性未测 | static-checked：可选模板、路径及隔离脚本回归；事件加载未测 | 未记录 | not-tested |
| Codex | static-checked：根指令存在 | static-checked：共享资源及索引有效；实际发现未测 | static-checked：TOML 可解析、配置路径和生成一致；实际加载未测 | not-tested：本仓库未提供 Codex Hook 适配，不判断客户端能力 | 未记录 | not-tested |
| Gemini | static-checked：导入目标路径存在，不证明客户端语法或加载已验证 | not-tested：提供共享资源，发现机制待目标版本核实 | not-tested：未提供专用角色适配 | not-tested：未提供专用 Hook 适配 | 未记录 | not-tested |

## 状态定义

- `declared`：仓库提供对应资源或入口，尚无检查证据。
- `static-checked`：相应路径、格式、引用或生成一致性已检查，不代表真实加载。
- `client-tested`：在明确客户端版本、环境与仓库 revision 上执行了对应能力的 Smoke Test，并留存可核对产物。
- `not-tested`：尚无对应验证，或该能力未提供适配且未判断支持情况。
- `unsupported`：有明确版本范围和依据证明不支持；不能由缺少配置或一次运行失败推断。

## 静态检查记录

2026-11-25 对当前工作区执行：

- `python scripts/sync_agents.py --check`：角色生成一致性。
- `python -m pytest tests/test_layout.py tests/test_runtime.py tests/test_skills.py -q`：入口引用、索引、共享链接、资源与隔离 Hook 行为。
- 使用 Python 3.13 的 `tomllib` 解析 `.codex/config.toml` 与 `.codex/agents/*.toml`：只证明 TOML 语法可解析，不是特定 Codex 版本的 schema 校验。

静态检查结果可由当前源码重放；本记录不是一次真实客户端会话证据。当前无满足下述要求的真实客户端验证记录，不能根据开发过程中使用了某客户端推定全部能力通过。

## 最小加载 Smoke Test

在独立临时工作区、现有授权与可用客户端中执行，不修改个人全局配置。记录客户端精确版本、操作系统、项目 revision/工作区 diff、配置文件与信任状态。不要为 Smoke Test 自动安装、登录、启用网络通知或放宽权限。

1. **共享指令**：放置一个无副作用的临时指令标记，确认新会话实际加载导入内容；仅能打开文件不算通过。
2. **Skills**：通过客户端实际支持的发现方式定位一个临时无副作用 Skill，显式调用并核对其内容生效，记录发现机制和输出。检查内置技能列表不能替代项目 Skill 验证。
3. **角色**：在用户允许委派的环境中确认项目角色被识别，并用无副作用的小任务检查职责生效。若只检查了角色列表，记录为“可见性”，不声称执行通过。
4. **Hooks**：只测试选定事件，使用写临时标记文件的测试替身；确认事件触发、参数与退出行为，通知命令使用替身。没有测试的事件分别保留 not-tested。
5. **清理**：停止仅本次启动的进程，移除临时资源；不删除用户配置、不停止已有服务。

不支持某种操作时，按精确版本的官方依据记录 unsupported；环境或权限不足时记录 not-tested 及原因。

## 记录与失效

每项真实验证记录包含：客户端与精确版本、日期、OS、目标 revision、能力、实际步骤/命令、结果、日志或报告位置、限制和执行者。按[任务与证据规范](task-evidence.md)保留通过、失败和未执行项。

适配、相关 Skill 路径或客户端版本变化后，先重跑静态检查，再重做受影响能力的真实 Smoke Test。旧记录作为历史证据保留，不能直接用于新版本或新配置的 client-tested 声明。未受影响能力也需注明历史记录的 revision，而非暗示在当前版本重测。

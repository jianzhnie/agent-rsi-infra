# Skill 最小契约

采用两层治理，不统一重写上游 Frontmatter 或章节。

## 最低可发现性

每个技能目录包含 `SKILL.md`，Frontmatter 可解析且包含唯一、与目录一致的 name 和非空 description。description 应说明适用任务；容易误选的场景说明排除条件，不机械要求固定措辞。仓库索引覆盖所有 Skill，正文及参考中的本地 Markdown 资源链接有效且不逃出仓库。

## 正文与本地侧车

最低内容为适用范围、输入与前置条件、工作流、验证和交付证据。不要求上游使用统一标题；本地 `.agents/skill-contracts.json` 以技能名记录 when_to_use、preconditions、workflow、validation、deliverables，补齐本仓库使用边界。它不覆盖上游许可、署名和原始语义，具体命令仍查目标版本。

新增或调整 Skill 同时维护侧车与索引。侧车不放客户端工具权限；risk_level 即使存在也只是审查提示，不授权执行。

可选 version、author、license、platforms、tags、related_skills、requires/preconditions、validation 等字段沿用上游格式，不施加统一字段白名单或批量迁移。保留来源、LICENSE 与 NOTICE。相关技能与客户端实际加载继续由专项回归和目标客户端检查。

## 自动检查与限制

`python scripts/check_skills.py` 已接入统一检查入口，检查发现、YAML、侧车章节、Markdown 内联/引用式本地资源和索引完整性。Frontmatter YAML、侧车目录与来源 JSON 快照拒绝重复映射键，避免解析器静默采用后值。侧车目录和 `INSTALL_SOURCE.json` 必须是 JSON 对象；来源快照要求包含有效的 GitHub 仓库地址、仓库相对 path、requested_ref 和可空的 40 位 resolved_commit。未知扩展字段允许保留，代码围栏内的示例不作资源引用。纯文本中的路径、动态生成资源、链接锚点和外部 URL 可达性不在此检查范围。

非空侧车字段不能证明文字充分或流程正确；适用性、排除场景、验证方法及证据质量仍需 Review 和真实任务对照。客户端适配生成一致性也不代表真实客户端已加载。

## 来源职责

`INSTALL_SOURCE.json` 是安装器的机器快照，记录 repository、path、requested_ref 和 resolved_commit；无法解析 commit 时使用 null。它必须能被解析为 JSON 对象，字段与路径结构由自动检查验证。它不证明当前文件未修改。 `UPSTREAM.md` 是人工适配说明，记录本地修改、许可与验证边界。快照不证明当前文件未修改，人工说明也不能伪称可变分支是固定版本。本仓库按既有偏好可不保留安装 JSON，保留时检查器会核对其格式与显式 commit 是否明显冲突；不同版本的适配历史需人工判断。LICENSE/NOTICE 不从 commit 推断，继续保留并审查。

当前自动检查不推断 Markdown 自由文本中的 shell 命令是否可执行，也不验证所有脚本权限和来源法律一致性；这些仍是迁入 Review 项。客户端适配由布局回归和 `sync_agents.py --check` 验证。

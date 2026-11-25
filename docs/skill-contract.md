# Skill 最小契约

采用两层治理，不统一重写上游 Frontmatter 或章节。

## 最低可发现性

每个技能目录包含 `SKILL.md`，Frontmatter 可解析且包含唯一、与目录一致的 name 和非空 description。description 应说明适用任务；容易误选的场景说明排除条件，不机械要求固定措辞。仓库索引覆盖所有 Skill，正文及参考中的本地 Markdown 资源链接有效且不逃出仓库。

## 正文与本地侧车

最低内容为适用范围、输入与前置条件、工作流、验证和交付证据。不要求上游使用统一标题；本地 `.agents/skill-contracts.json` 以技能名记录 when_to_use、preconditions、workflow、validation、deliverables，补齐本仓库使用边界。它不覆盖上游许可、署名和原始语义，具体命令仍查目标版本。

新增或调整 Skill 同时维护侧车与索引。侧车不放客户端工具权限；risk_level 即使存在也只是审查提示，不授权执行。

可选 version、author、license、platforms、tags、related_skills、requires/preconditions、validation 等字段沿用上游格式，不施加统一字段白名单或批量迁移。保留来源、LICENSE 与 NOTICE。相关技能与客户端实际加载继续由专项回归和目标客户端检查。

## 自动检查与限制

`python scripts/check_skills.py` 已接入统一检查入口，检查发现、YAML、侧车章节、Markdown 内联/引用式本地资源和索引完整性。未知扩展字段允许保留，代码围栏内的示例不作资源引用。纯文本中的路径、动态生成资源、链接锚点和外部 URL 可达性不在此检查范围。

非空侧车字段不能证明文字充分或流程正确；适用性、排除场景、验证方法及证据质量仍需 Review 和真实任务对照。客户端适配生成一致性也不代表真实客户端已加载。

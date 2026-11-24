# 来源与提炼范围

本地清单提炼自 NVIDIA Megatron-LM，固定 commit：`22f07ae9cebe0b974cfaa34615ba0e6932e996d6`。

- [light.md](https://github.com/NVIDIA/Megatron-LM/blob/22f07ae9cebe0b974cfaa34615ba0e6932e996d6/skills/pr-review/references/light.md)
- [strict.md](https://github.com/NVIDIA/Megatron-LM/blob/22f07ae9cebe0b974cfaa34615ba0e6932e996d6/skills/pr-review/references/strict.md)

上游审查技能声明 Apache-2.0；本仓库提供同一[许可证全文](../../../../LICENSE)。未推断两份上游清单的个人作者。

本地改动：中文提炼、按需读取深度、问题按影响排序、区分数值容差与 bit-exact 门禁；不复制上游自动发布评论和批准 PR 的动作。Megatron 专用路径、进程组与测试注册要求保留为有条件的检查项，其他仓库以自身契约为准。

两份清单由共享 Skill `code-reviewer` 按需读取，不单独注册。原 Claude Agent 的审查正文迁入 `SKILL.md`，移除模型、记忆、颜色、轮次与专用工具字段；作者、许可和版本保留在技能元数据中。提炼和静态检查不等于验证了模型对所有审查场景的行为。

# 来源与提炼范围

本地清单提炼自 NVIDIA Megatron-LM，固定 commit：`22f07ae9cebe0b974cfaa34615ba0e6932e996d6`。

- [light-review-checklist.md](https://github.com/NVIDIA/Megatron-LM/blob/22f07ae9cebe0b974cfaa34615ba0e6932e996d6/skills/pr-review/references/light.md)
- [strict-review-checklist.md](https://github.com/NVIDIA/Megatron-LM/blob/22f07ae9cebe0b974cfaa34615ba0e6932e996d6/skills/pr-review/references/strict.md)

上游审查技能声明 Apache-2.0；本仓库提供同一[许可证全文](../../../../LICENSE)。未推断两份上游清单的个人作者。

本地改动：中文提炼、按需读取深度、问题按影响排序、区分数值容差与 bit-exact 门禁；不复制上游自动发布评论和批准 PR 的动作。Megatron 专用路径、进程组与测试注册要求保留为有条件的检查项，其他仓库以自身契约为准。

两份清单由共享 Skill `code-reviewer` 按需读取，不单独注册。原 Claude Agent 的审查正文迁入 `SKILL.md`，移除模型、记忆、颜色、轮次与专用工具字段；作者、许可和版本保留在技能元数据中。提炼和静态检查不等于验证了模型对所有审查场景的行为。

测试与注释审查补充提炼自 SGLang [unit-test-admission.md](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/unit-test-admission.md) 与 [comment-style.md](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.claude/rules/comment-style.md)。许可见[已保留的全文](../../sglang-code-cleanup/LICENSE)；详细适配边界与共享要求统一维护在根贡献文档。

设备接口、共享执行路径及 PR 复审方法补充提炼自 [DeepSpeed pr-checklist](https://github.com/deepspeedai/DeepSpeed/blob/039bfc9f3f493ae5bf3f99582b4e4e593660d98d/.agents/skills/pr-checklist/SKILL.md)，固定 commit `039bfc9f3f493ae5bf3f99582b4e4e593660d98d`，许可为[上游 Apache-2.0](https://github.com/deepspeedai/DeepSpeed/blob/039bfc9f3f493ae5bf3f99582b4e4e593660d98d/LICENSE)。不复制专用命令、设备调用禁令、硬件矩阵或自动发布动作；复审流程统一维护在贡献文档。

完整 diff 与性能证据自查补充参考 FlashInfer [self-review](https://github.com/flashinfer-ai/flashinfer/blob/4d5a6ce322587d247fb192f97a0d23eeba9e3412/.claude/skills/self-review/SKILL.md)，固定 commit `4d5a6ce322587d247fb192f97a0d23eeba9e3412`；许可见[保留全文](../../flashinfer-add-cuda-kernel/LICENSE)，不迁入自动修复或强制发现问题的规则。

长期资源复用的聚合保留量、负载变化及应用显存余量检查，提炼自 FlashInfer 同版本 [AGENTS.md](https://github.com/flashinfer-ai/flashinfer/blob/4d5a6ce322587d247fb192f97a0d23eeba9e3412/AGENTS.md)；许可见[已保留全文](../../flashinfer-add-cuda-kernel/LICENSE)，不将局部预热结果外推为完整服务可用性。

问题必要性和归属审查提炼自 [TorchTitan pr-review](https://github.com/pytorch/torchtitan/blob/72e5566782bbdafaa9bafd422733a307319213c5/.claude/skills/pr-review/SKILL.md)，固定 revision `72e5566782bbdafaa9bafd422733a307319213c5`，许可见[保留的 BSD-3-Clause](../../training-inference-change/references/torchtitan/LICENSE)。仅补充 strict 的证据判断，不复制自动发布、固定裁决、委派或无 BC 政策。

配置与运行状态分离、状态生命周期归属和内部重构保持 Hook 契约，选择性提炼自 slime-code-review-preferences；固定 revision、上游链接、本地范围与保留版权的 Apache-2.0 许可见 [slime 来源记录](../../training-inference-change/references/slime/UPSTREAM.md)。不迁入整个 Skill 或重复的抽象原则。

SGLang-Omni code-review 的接口、配置、模块边界及行为测试方法选择性合并到贡献指南与严格审查，固定来源、许可及排除项见 [SGLang-Omni 适配记录](sglang-omni/UPSTREAM.md)。未新增重复审查 Skill。

参考文件命名整理：light.md → light-review-checklist.md；strict.md → strict-review-checklist.md。仅调整本地文件名及引用。

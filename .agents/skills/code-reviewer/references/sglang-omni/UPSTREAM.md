# SGLang-Omni 方法来源

- 固定 revision：`8214c57840051924ffb6da4e0315a44e6f69dc9d`。
- [code-review/coding-style.md](https://github.com/sgl-project/sglang-omni/blob/8214c57840051924ffb6da4e0315a44e6f69dc9d/.claude/skills/code-review/coding-style.md)：中文选择性提炼到根 CONTRIBUTING.md、严格审查清单及推理参考；原文件还引用了 sglang-diffusion-routing Issue #32 的风格讨论，不推断个人作者。
- [running-eval-suite/SKILL.md](https://github.com/sgl-project/sglang-omni/blob/8214c57840051924ffb6da4e0315a44e6f69dc9d/.claude/skills/running-eval-suite/SKILL.md)：仅提炼逐项命令、原始结果、失败原因、独立项继续及 smoke/完整评测区分，落点为 docs/task-evidence.md。
- 许可：[保留的 Apache-2.0 全文](LICENSE)。原文快照适用此许可；未迁入 runner 或模型配置。
- 本地适配：复用现有 Ruff、pytest、配置与证据规范；按语义和维护风险判断，不以固定行数、调用点数量或风格偏好拒绝改动。
- 未采用：所有 if 强制 else、禁止 TYPE_CHECKING/泛型/Callable/Any、禁止局部导入、固定注释格式和署名、禁止来源注释、默认公开属性、强制 Pydantic、固定文件长度与测试目录/marker；运行时校验仍使用明确异常，许可与来源声明保留。
- 评测边界：不迁入自动改表/提交、私有校准依赖、机器路径、默认模型、环境覆盖、固定双终端或仅取首轮更新结果的策略；未执行真实评测或 Agent 行为验证。

## coding-style 原文快照

- 文件：[coding-style.md](coding-style.md)。
- 原始 URL：[固定版本](https://github.com/sgl-project/sglang-omni/blob/8214c57840051924ffb6da4e0315a44e6f69dc9d/.claude/skills/code-review/coding-style.md)。
- revision：`8214c57840051924ffb6da4e0315a44e6f69dc9d`。
- 上游原文 SHA-256：`caa2ed96412ed5c2fedc57d39d3c552d989641b4ce5d24009710e9b7ad81cac2`。
- 本地改动：保留完整正文与来源链接，仅将 `/.pre-commit-config.yaml` 根路径链接改为固定 revision 的上游 URL，避免在本仓库解析为无效资源。
- 用途：按需查阅上游风格或比较后续变化，不自动成为本仓库规则。有效的本地要求见根 CONTRIBUTING.md；上文排除项仍不采用。只有目标任务明确要求遵循上游风格时，才按目标项目和适用范围读取。

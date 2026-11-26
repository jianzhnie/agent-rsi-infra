# 来源与适配

- 上游：[TokenRhythm/InfraRSI](https://github.com/TokenRhythm/InfraRSI/blob/512f8ea784054f4ca3331d03cc6589267a4cbdf5/skills/profile-whole-update/SKILL.md)。
- 固定 revision：`512f8ea784054f4ca3331d03cc6589267a4cbdf5`；来源路径：`skills/profile-whole-update/SKILL.md`。
- 上游 SKILL.md SHA-256：`a8fc6e6d15031b53ad82c0e704c8d5c254633e0952e889f26fb3f3bdbc8b79a6`。
- 保留上游 Frontmatter 中的 name、description、when_to_use、metadata 和署名。仅在 Frontmatter 后补充本地适配入口，原始正文保留。
- 许可声明为 Apache-2.0；[LICENSE](LICENSE) 为本地提供的标准全文，上游该版本未提供独立许可文件。
- 历史案例与负结果仅作上游研究证据；本地不再维护共享案例目录。未迁入业务实现、harness、模型、数据或 memory 数据库。
- 使用前核对目标版本和以下本地边界：上游 harness、固定阈值与历史收益不构成本仓库能力或执行授权。本地仅验证资源结构与发现，未执行目标框架、GPU、训练任务或真实客户端加载测试；维护状态 experimental。

## ATTUNE 测量参考合并

原 autotune-training-throughput 的测量、记录、拓扑与术语参考合并到 references/，取消重复发现入口。来源为 [amazon-science/attune](https://github.com/amazon-science/attune/tree/c07fe30dcf2e16cae0ae47f62d1f857ce2a634b6/skill)，revision c07fe30dcf2e16cae0ae47f62d1f857ce2a634b6，Apache-2.0。中文参考为本地适配，术语沿用上游内容；没有迁入 harness、调度或训练执行工具。许可全文见 [ATTUNE LICENSE](references/ATTUNE_LICENSE)。未经目标训练环境验证，不将上游固定窗口或历史收益当作本仓实测结论。

参考文件命名整理：ledger.md → experiment-records.md。仅调整本地文件名及引用。

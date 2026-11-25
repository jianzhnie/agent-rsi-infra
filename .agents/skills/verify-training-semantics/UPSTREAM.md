# 来源与适配

- 上游：[TokenRhythm/InfraRSI](https://github.com/TokenRhythm/InfraRSI/blob/512f8ea784054f4ca3331d03cc6589267a4cbdf5/skills/verify-training-semantics/SKILL.md)。
- 固定 revision：`512f8ea784054f4ca3331d03cc6589267a4cbdf5`；来源路径：`skills/verify-training-semantics/SKILL.md`。
- 上游 SKILL.md SHA-256：`62c550b37a8ae004c1675166b742049816efd973110bc133a0bbcdb9fc9ba77c`。
- 保留上游 Frontmatter 中的 name、description、when_to_use、metadata 和署名。仅在 Frontmatter 后补充本地适配入口，原始正文保留。
- 许可声明为 Apache-2.0；[LICENSE](LICENSE) 为本地提供的标准全文，上游该版本未提供独立许可文件，详细记录见[共享来源](../_catalogue/UPSTREAM.md)。
- 共享负结果目录完整迁入 `_catalogue/`；实验引用仍指上游，未下载业务实现、harness、模型或数据。按既有仓库约定不保留安装器生成的 INSTALL_SOURCE.json，来源快照由本文记录。
- 使用前读[共同适配](../_catalogue/infrarsi-adaptation.md)。本地仅验证资源结构与发现，未执行目标框架、GPU、训练任务或真实客户端加载测试；维护状态 experimental。

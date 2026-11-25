# 来源与适配

本 Skill 是依据本仓库两份调研归纳的原创工作流，不是任何上游 Skill 的原文快照：

- [训练框架调研](../../../docs/research/training-frameworks-agent-engineering.md)：9 个项目的 Agent 工作顺序、贡献治理、训练/RL/Kernel 验证。
- [推理框架调研](../../../docs/research/inference-frameworks-agent-engineering.md)：8 个项目的配置契约、硬件分层、模型接入和多阶段运行时。

项目名称、采用内容、实际文件与未迁入约束见[迁移记录](../../../docs/framework-practices.md)。上游链接由报告保留；可变分支不伪装成固定 commit，报告未确认的配置不补写成上游事实。本次未下载或复制上游源代码、工具脚本与配置，许可沿用本仓库 [Apache-2.0](../../../LICENSE)。已有迁入 Skill 保留各自来源与许可。

适配采用本仓库的共享源、按需参考和客户端分层；不复制其他项目的权限、提交、签名、fork、CI bot 或设备运行命令。本地验证不证明目标框架或硬件行为，真实任务应记录目标代码 revision 与实际结果。

# 来源与适配

- 上游：[sgl-project/sglang](https://github.com/sgl-project/sglang)。
- 固定 commit：`049bf85d931c9633d26094ae5ff9a7dbac6723b4`。
- [原始技能目录](https://github.com/sgl-project/sglang/blob/049bf85d931c9633d26094ae5ff9a7dbac6723b4/.agents/skills/kl-consistency-test)；完整资源随目录迁入。
- 许可见 [LICENSE](LICENSE)，保留上游署名，不推断个人作者。

本地适配：补充目标环境与操作边界，修复技能外引用，按本仓库配置整理 Python 风格。默认不启动服务、远程任务或发布 PR；迁入不表示已授权执行附属脚本。未保留安装器生成的来源 JSON；此文件记录快照与适配。

本机验证只覆盖可离线执行的脚本、测试及结构检查，不代表 GPU、真实服务、线上采集或目标框架行为已验证。上游示例、路径、历史数据和结论需按目标版本核实。

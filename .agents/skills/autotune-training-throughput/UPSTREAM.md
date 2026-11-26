# 来源与本地适配

- 上游：[amazon-science/attune](https://github.com/amazon-science/attune/tree/c07fe30dcf2e16cae0ae47f62d1f857ce2a634b6/skill)，revision `c07fe30dcf2e16cae0ae47f62d1f857ce2a634b6`。
- 保留 [LICENSE](LICENSE)、源码对应的 NOTICE 和第三方声明（位于仓库 autotuner/） 及源码署名。
- 本地适配删除容量查询、任务生成/提交/轮询/清理、资源用量记账、部署 Hook 链及相应测试；原始 attune/ 目录未修改。
- 本地仅保留调优指南和框架参考；原 scripts/ 与测试已移除。离线 trace 分析实现在仓库 autotuner/profile_analyzer/，不再随 Skill 独立安装。日志测量、校准和数值验证由目标项目负责。
- 维护状态 experimental。按使用路径准备 PyTorch、numpy、pyarrow、transformers 等依赖；未验证真实 GPU、模型或客户端加载。不执行新迁入的训练或 patch 工具。

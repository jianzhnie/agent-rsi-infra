# 离线性能分析工具

`profile_analyzer/` 分析已有 PyTorch profiler trace，汇总每个 rank 的计算、通信、内存与流水线耗时。不启动训练、不采集 trace，也不提供调度或自动调优服务。

从仓库根目录运行，解释器需安装 numpy；orjson 为可选解析加速依赖：

```bash
python3 -m autoresearch.profile_analyzer --help
python3 -m autoresearch.profile_analyzer --profile-dir <trace-dir> --json --no-cache
python3 -m autoresearch.profile_analyzer rank 0 --profile-dir <trace-dir>
```

默认缓存写入 trace 附近，无法写入时尝试用户缓存目录；可用 `--cache-dir <dir>` 指定位置，或用 `--no-cache` 禁止读写缓存。缓存按源文件大小、纳秒修改时间和分析选项校验。JSON 写入 stdout，运行日志写入 stderr。

时间字段沿用既有输出协议：`_us` 为微秒，`_ms` 为毫秒；显存字段 `_gib` 为 GiB。结果描述 trace 中观察到的事件，不能替代完整训练 benchmark 或数值验证。

代码源自 [amazon-science/attune](https://github.com/amazon-science/attune/tree/c07fe30dcf2e16cae0ae47f62d1f857ce2a634b6/skill/scripts/profile_analyzer)，保留源码版权声明。本地未保留独立许可与声明文件；固定版本原文见上游 [LICENSE](https://github.com/amazon-science/attune/blob/c07fe30dcf2e16cae0ae47f62d1f857ce2a634b6/LICENSE)、[NOTICE](https://github.com/amazon-science/attune/blob/c07fe30dcf2e16cae0ae47f62d1f857ce2a634b6/NOTICE) 和 [THIRD_PARTY_NOTICES](https://github.com/amazon-science/attune/blob/c07fe30dcf2e16cae0ae47f62d1f857ce2a634b6/THIRD_PARTY_NOTICES)。

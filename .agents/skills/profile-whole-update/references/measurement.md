# 吞吐测量

先固定版本、数据、batch、序列长度、精度与设备。测量窗口和预热长度由目标任务确定；重复基线估计噪声，候选采用同一协议。记录完整 update 的最慢 rank 耗时，不能把局部 Kernel 加速当作训练收益。

使用目标项目的日志工具统计完整窗口，记录有效 token 数、update 耗时和 GPU 数。重复基线估计噪声，不将未经验证的固定阈值当作收益门槛。

从仓库根目录运行 `python3 -m autoresearch.profile_analyzer --profile-dir <local-dir> --json`，分析已有 trace。采集方法由目标项目决定；profiler 会带来开销，不用采集运行代替正式 benchmark。保存所有相关 rank 的 trace，检查通信等待、流水线空泡、主机等待和内存管理。

记录原始结果、重复次数与离散程度；异常值先定位原因，不只报告最佳单次结果。

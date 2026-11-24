# CUDA 崩溃诊断

适用于已能复现的 FlashInfer 调用故障；其他框架先查其日志和调试接口。记录代码与依赖版本、设备、输入 shape/dtype/stride、当前 stream 及 graph 模式，保存最小复现。

## 先记录调用边界

FlashInfer 对带 `@flashinfer_api` 的 API 提供日志。按目标版本核实覆盖范围与环境变量，在复现进程启动前设置：

```bash
FLASHINFER_LOGLEVEL=3 FLASHINFER_LOGDEST='crash_%i.log' python repro.py
```

上游约定级别 1 记录函数名、3 记录张量元数据、5 增加统计，`%i` 表示进程 ID，不是 rank。多机采集还需用主机和会话目录隔离文件，并记录 PID 与 rank 的对应关系。

先用元数据检查 shape、dtype、设备和布局；数值问题再按需采集统计。统计可能触发同步并改变执行时序，graph capture 中也可能被跳过。缺少日志或统计不代表调用未发生或输入正确。日志与 dump 可能含请求数据，应限定范围和保存位置。

## 区分日志线索与故障证据

CUDA 异步执行可能把错误推迟到后续 API 才报告；最后一条输入日志或缺少输出日志只能缩小范围，不能独立证明故障 Kernel。必要时在独立复现中增加同步或使用 `CUDA_LAUNCH_BLOCKING=1` 定位，注明这些操作改变了性能与时序，不能用于正式 benchmark。

在已配置 CUDA 工具的环境中，可针对最小复现使用：

```bash
compute-sanitizer --tool memcheck python repro.py
cuda-gdb --args python repro.py
```

记录工具报告中的访问位置、线程和输入契约，区分越界、生命周期、竞态与数值错误。不要假设 memcheck 能发现所有同步问题；调试器附加、core dump 或重新运行服务应限于用户授权目标。不要为采集自动安装工具或停止无关进程。

Kernel 内 `printf` 只在少量合法线程上输出；warp-specialized 代码按实际角色选择代表线程，不把 block 的线程 0 当作所有角色的代表。结束后移除临时插桩和诊断环境变量，在原配置下验证修复与相关回归。

## 来源

提炼自 FlashInfer [debug-cuda-crash](https://github.com/flashinfer-ai/flashinfer/blob/4d5a6ce322587d247fb192f97a0d23eeba9e3412/.claude/skills/debug-cuda-crash/SKILL.md)，固定 commit `4d5a6ce322587d247fb192f97a0d23eeba9e3412`。许可见[保留的全文](../.agents/skills/flashinfer-add-cuda-kernel/LICENSE)。不采用“最后一条日志就是故障位置”或“关闭日志必然零开销”的结论；未执行 CUDA 调试验证。

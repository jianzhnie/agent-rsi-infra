---
name: flashinfer-add-cuda-kernel
description: 在目标 FlashInfer 仓库新增或集成 CUDA Kernel，覆盖 FFI、JIT、Python API、设备限制、trace 模板及验证。不用于一般 Triton 开发或其他框架的 Kernel 注册。
license: Apache-2.0
---

# FlashInfer CUDA Kernel 集成

使用目标 FlashInfer checkout 的指令与现有算子作为依据。本仓库仅保存流程，不包含 FlashInfer 构建系统；加载 Skill 不自动安装包、编译或启动 GPU 任务。

## 先确定契约

搜索是否已有相同计算契约的实现。明确数学语义、shape/dtype/stride、设备与架构、空输入和大索引、alias/in-place 行为、stream 和 graph capture 约束。不要从教程示例推断生产实现已覆盖所有 dtype、边界或未来 GPU。

## 集成层次

| 层次 | 需要核对的内容 |
| --- | --- |
| CUDA 实现与 launcher | 遵循 `include/flashinfer/` 的框架无关边界，避免引入 Torch；核对索引宽度、mask、对齐及 launch 错误 |
| FFI 与 stream | 在 `csrc/` 适配 TensorView、校验 shape/dtype/布局及设备一致性；按当前 device/stream 约定发射，沿用项目异常传播 |
| JIT 生成 | 沿用 `flashinfer/jit/` 机制与配置标识，生成文件写入指定缓存目录，不改安装包目录；架构列表以实际实现和工具链支持为准 |
| Python API | 按现有模式缓存模块，核对 `@flashinfer_api` 与 `@backend_requirement`；支持 `out` 时校验容量、设备和别名契约，避免不必要分配 |
| Trace 模板 | 按目标版本注册 `TraceTemplate`，核对变量/常量轴、输入参数映射、输出与 reference；共享 op_type 的模板名称避免冲突 |
| 导出与打包 | 检查公共 API 导出、需要的 AOT 枚举和源码打包；能在开发目录 JIT 不代表发布包完整 |

教程中的 `skip_check` 或 bypass 不应成为新接口的默认捷径；只有调用者契约已保证输入约束时，才沿用项目支持的跳过校验路径。

## 确认代码与缓存来源

验证 Kernel 修改前，确认实际加载模块的来源。新进程能清除已加载模块的进程内状态，但不保证绕过预编译包；该版本的 `flashinfer-jit-cache` 产物可能优先于修改后的源码。先检查安装与加载路径，在隔离的验证环境中按目标版本流程排除旧产物，不自动卸载用户环境中的包。

生成源码写入 `FLASHINFER_GEN_SRC_DIR`，编译产物写入 `FLASHINFER_JIT_DIR`；冷缓存实验使用独立 workspace，避免删除共享缓存。构建故障保留生成源码、`build.ninja` 与环境信息。调试构建和正式性能构建分开记录；该版本 verbose 模式可能连带启用 debug，需优化构建日志时显式核对 `FLASHINFER_JIT_VERBOSE=1 FLASHINFER_JIT_DEBUG=0`。

实验后端的显式使用、自动选择和发布范围按目标版本政策验证，不因实验已通过就将其加入稳定默认路径。详细约定见[上游根指令](https://github.com/flashinfer-ai/flashinfer/blob/4d5a6ce322587d247fb192f97a0d23eeba9e3412/AGENTS.md)。

## 验证与交付

- 与独立 reference 对比，覆盖声明支持的 dtype、代表性和非整齐 shape、空输入、大 offset 及非连续布局；不支持的情况明确拒绝，容差按语义选择。
- 验证预分配输出、别名、非默认 stream 和 graph 行为中受改动影响的部分；在输入、plan 或 backend 改变后检查 graph replay 与捕获 buffer 生命周期，eager 通过不能替代 replay 验证。运行目标版本的 trace 模板一致性检查，确认 API 与模板可发现。
- 新增硬件限制时检查测试 guard 和实际后端选择；缺少设备时报告未验证范围，不以 fallback 通过宣称新路径正确。
- 性能测量使用[Kernel 微基准流程](../kernel-microbenchmark/SKILL.md)，FlashInfer CLI 用法按需读取其附属参考。报告绝对耗时、硬件、输入与编译开销，局部加速不等于模型端到端收益。

完整示例及当前快照的专用 API 见[上游教程](https://github.com/flashinfer-ai/flashinfer/blob/4d5a6ce322587d247fb192f97a0d23eeba9e3412/.claude/skills/add-cuda-kernel/SKILL.md)。选择测试和构建命令前核对目标版本，不直接复制示例中的架构表或依赖版本。

来源、许可和适配范围见 [UPSTREAM.md](UPSTREAM.md)。

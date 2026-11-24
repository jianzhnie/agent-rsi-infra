# JIT Kernel 预热

用于新增 JIT Kernel、调整特化逻辑或排查首请求编译。编译预热的目标是提前准备运行时会使用的变体；它不等同于执行预热、autotune 或正确性验证。

## 编译键与运行时一致

- 从目标后端的缓存键、特化参数及编译日志确认真实编译维度，例如 tile、dtype、head dimension、指针对齐类别与后端选择。仅在影响特化时纳入，不枚举纯运行时数值。
- 运行时选择与预热复用同一特化映射，避免独立维护两套规则。输入范围覆盖 bucket 边界、offset view 和相关 strides；关联输入成组构造，无效组合先过滤。
- 对映射后的编译键去重，而非只对原始输入去重。编译键保持稳定且可哈希，检查是否遗漏变体或生成过多变体。

## 分离三个阶段

| 阶段 | 职责 |
| --- | --- |
| 注册 | 记录当前配置实际选中的 Kernel 与元数据，避免注册触发编译或模型计算 |
| 编译准备 | 按编译键编译或加载已有产物；后端支持时用编译专用描述符、假张量及代表性布局，避免为编译键构造真实推理负载 |
| 运行 | 使用同一选择逻辑发射 Kernel；正确性、执行预热和 autotune 按各自目的独立验证 |

不要将 compile-only 约定强加到不支持它的后端；需要实际执行的调优或初始化应显式分开，记录分配、执行和启动成本。

## 验证覆盖

先准备变体，再运行代表性输入并观察编译日志或缓存变化；若仍产生新编译，核查映射、对齐与布局。分别报告启动编译、首次执行与稳态耗时。完成预编译不代表 Kernel 正确，也不代表性能更好。

## vLLM 专用接口与来源

固定版本的 [jit_kernel_warmup.md](https://github.com/vllm-project/vllm/blob/3f86db3b2df84dc2e4d10b81da43afad132d66c6/docs/contributing/jit_kernel_warmup.md) 说明 `VllmJitKernel`、`CompileKey`、`dispatch`、`_trace_dispatch`、`register_warmup()` 与 `kernel_warmup()` 的契约；`WarmupIntRange`、`zip_inputs`、`_when` 和 `TritonWarmupTensor` 的具体用法也在该文档中。

这些名称属于对应版本的 vLLM，不是通用 Triton API。迁移到目标项目时先确认现有机制，不据此要求新增同名封装。本文为中文方法提炼，许可见 [Apache-2.0 全文](../LICENSE)，未执行 JIT 或 GPU 验证。

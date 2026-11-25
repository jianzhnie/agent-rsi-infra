# 训练与状态验证

## 确定性与数值

记录模型、tokenizer、数据与 revision、种子、精度、算子/编译后端及并行配置。确定性要求与误差容限由算法及目标项目定义，不强制所有硬件逐位一致。固定输入比较 forward、loss、梯度和必要的权重更新；区分一次 forward 正确与多步训练行为稳定。

修改 LoRA/量化、patch 或参数映射时，检查模型架构覆盖、被替换模块和未命中的路径，比较 logits/loss/梯度。小样本 smoke 验证接入，独立评测验证模型行为；不能互相替代。

逐算子已有捕获日志可用[离线数值诊断](offline-numerics.md)定位线索；最终仍需独立输出与梯度验证。

## 并行与 Checkpoint

明确 TP/PP/DP/CP/EP 等受影响维度、rank/进程组和通信顺序。分片验证选择非平凡且能暴露不均匀分区的形状与 world size；单 rank 不足以证明分片正确。只在目标框架要求处显式传递进程组，Megatron Core 的例外按其当前指令执行。

不要假设 mesh 是一维或轴顺序固定；区分张量维度、mesh 轴、局部和全局量。DTensor 转换按目标 API 核对梯度 placement（尤其 Replicate/Partial），多轴 collective 后确认各 rank 的全局量语义一致。

按受影响路径组合验证 FSDP/HSDP、TP/SP、PP（含交错调度）、CP、EP，以及梯度累积、激活重计算、图捕获和恢复；不要求无依据穷举全部组合。训练热路径检查 `.item()`、`.tolist()`、`.cpu()` 等隐式同步及数据依赖形状，不把源码模式命中直接当作已测性能问题。

状态变更同时核对参数、优化器、scheduler、RNG 与数据迭代状态。按支持承诺验证旧 checkpoint 读取、保存加载 round-trip、中断恢复，以及并行度变化时的重分片。格式变化说明版本和迁移；不假定所有格式都支持跨 stage/world size 转换。

Offload 与预取检查异步 copy 的完成依赖、buffer 复用、释放与峰值内存；训练吞吐提升需同时报告显存及模型数值影响。设备接口变化检查其他实现是否仍可实例化，设备专用分支不随意扩散到共享代码。

## 实验、模型接入与训练 Kernel

研究实验先使用目标项目的实验边界，进入稳定核心前补齐维护契约、可运行配置、测试、文档和评审。不在本仓库为此创建空的 experiments 目录。

组件只接收实际读取的配置，不传整棵 trainer 配置；衍生字段在所属配置构建时确定，不依靠运行中多处补写。新开关需要实际使用者、选择依据与不支持组合的明确报错；沿用目标项目配置体系，不强制引入 TorchTitan 的 Configurable。可选重依赖留在所属模块，避免默认导入触发。实验特有逻辑、测试和 CI 按目标项目边界隔离，不能为单一实验向核心训练循环散布分支。

新模型接入追踪注册表、模板、config、权重映射、导出、文档与现有测试；修改一个注册点后检查其他索引是否同步。命名和格式由目标配置决定，不复制另一项目的 formatter。

训练 Kernel 依次验证独立算子 reference、forward/backward、模型训练对照和独立 benchmark。按受影响路径选择逐层 weights/logits/loss 或等价多步对照，容差需有依据。性能采样、吞吐/延迟和峰值内存单独保存，未复现的单次测量不构成收益证据。

本参考提炼自 Megatron-LM、DeepSpeed、TorchTitan、ms-swift、Liger Kernel 的调研；Unsloth 部分仅采用报告列出的待验证数值风险，不将未经核实的配置当作事实。项目映射见[迁移记录](../../../../docs/framework-practices.md)。

后续补充的 mesh、配置与实验边界提炼自 [TorchTitan 固定来源](torchtitan/UPSTREAM.md)，保留 BSD 许可；不将其专用 API 和兼容政策推广为通用约束。

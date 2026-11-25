# 推理服务与多模态验证

## 请求、配置与公共 API

从输入模型追踪参数到真正执行路径；声明字段不代表它已生效。核对省略/null、默认值、错误类型、流式终止、取消与兼容范围。OpenAI 兼容性按目标官方协议版本验证，不用当前实现自证正确。

配置/schema 或受保护 API 变化检查项目已有 snapshot/golden manifest 与生成器，同步默认值、嵌套字段、导出与文档。TensorRT-LLM 的 manifest、Telemetry/Privacy owner 与签名规则只在目标版本要求时适用，不在本仓库创建伪造的同名产物。

## 调度、缓存与硬件

- 用真实负载追踪排队、batch 形成、prefill/decode、取消及输出，核对边界 shape、长上下文、空任务、抢占/恢复与公平性。
- 缓存变化检查布局、页表、所有权、回收及跨进程传输，尤其是重用后的请求隔离、graph replay 与持久资源生命周期。
- 区分硬件无关测试、平台实现与资源密集型验证。目标框架有 GPU/NPU marker 时按其注册与 CI 选择方式运行，不新建无法运行的空测试矩阵。
- 共享路径用目标抽象，平台实现保留专用约束；不为跳过真实回归而扩大 skip。记录实际设备、backend 与被选中的路径。

## 多阶段多模态

明确 API、client、coordinator、stage、scheduler、model runner 与通信层的实际职责；模型逻辑不私自接管公共生命周期或 relay 协议。

验证阶段间 shape/dtype/设备、fan-in、流路由、SSE 顺序、时间戳和终止；取消要传播到参与阶段，失败后释放任务与 buffer。比较离线/在线路径及相关 relay 后端，必要时使用真实模型验证端到端输出。音视频报告首包延迟、实时率或同步误差，不直接套用文本指标。

阶段配置默认值在所属层定义并传递，避免 factory 或底层模块重新定义策略；多个模型使用的 scheduler/运行逻辑放入职责合适的共享模块，不通过导入兄弟模型包建立隐藏依赖。方法及固定来源见[接口与配置规范](../../../../CONTRIBUTING.md#接口配置与模块边界)。

模型接入同时检查 stage/model 注册、pipeline 拓扑、input processor、部署默认值、recipe 与索引；优先复用共享入口，不复制每个模型一套运行脚本。

## 性能与工具治理

性能报告绑定设备数量/显存、driver/runtime/framework 版本、模型 revision、输入/输出长度、并行和并发配置、warmup、轮次、波动与峰值内存。吞吐优化用有代表性的多个并发点检查收益和退化；不将某项目固定的并发数量门槛泛化到所有改动。

Python、C++/CUDA、Mojo 和编译器接口分别使用目标项目的格式、构建与测试配置。公共测试不自动运行昂贵模型示例；模型评测、correctness 和 benchmark 分开。

本参考提炼自 vLLM、SGLang、LMDeploy、TensorRT-LLM、MAX/Modular、DeepInfer、vLLM-Omni、SGLang-Omni 的调研。官方 Skill 分发方式是部署选项，不授权执行安装命令；MCP、hook 与 provider 设置不因本参考存在而启用。项目映射见[迁移记录](../../../../docs/framework-practices.md)。

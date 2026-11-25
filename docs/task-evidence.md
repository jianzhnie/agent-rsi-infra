# 任务契约与验证报告

先约定任务目标、目标 revision、允许修改与执行范围、验收条目和资源预算；执行后逐项补充结果。报告不授权运行命令，也不代替人工审查。

使用 JSON version 1：根字段为 `task_id`、`objective`、`revision` 和 `criteria`。每项 criterion 包含唯一 `id`、`expected` 和 `status`。状态只允许 passed、failed、not_run、not_applicable；执行项必须提供 evidence 对象（command、result、artifact），未执行或不适用项提供 reason。保留失败和未执行项，不从报告中删除。

运行 `python scripts/validate_task_result.py <report.json>` 检查结构。验证器不会执行命令、打开产物或证明证据真实性；人工需核对日志与实际代码版本。工作区未提交时记录基准 commit、diff 或源码 hash，不能仅以分支名代表候选。

## 性能与环境

性能证据另行记录 baseline/candidate、模型与输入 revision、硬件数量和拓扑、驱动/runtime/compiler/framework 版本、dtype、shape、并发与并行配置、计时边界、缓存和 graph 模式、warmup、重复次数、原始样本及波动。禁止把 profiler 数据直接代替正式 benchmark。环境指纹只采集明确列出的非敏感字段，不保存全部环境变量或凭证。

性能记录字段的合成示例见 `tests/test_benchmark.py` 的 `sample()`，仅用于格式测试，不是硬件测量。运行 `python scripts/validate_benchmark.py <report.json>`，校验 latency 记录的单位、重复样本、版本及固定环境字段，输出 median、范围和环境 SHA-256。当前仅支持延迟，不将吞吐量倒数当加速比。环境 hash 表示字段一致性，不证明环境真实或完整；硬件证据仍需实际采集。

## Skill 回归与人工晋级

真实任务样例保存原始输入、失败证据、预期行为、允许操作、资源需求与评价方法；不把期望答案直接泄露给执行者。代码检查、脚本回归与 Agent 行为评测分别报告。尚未执行真实 Agent 对照时标记未验证，不以结构测试宣称 Skill 有效。

候选规则或 Skill 改进比较同一任务集的完成情况、正确性、时间/资源成本和退化项；人类审查证据及适用范围后决定接受、继续试验或拒绝。晋级不自动修改规则或发布代码。先积累可复现样例，再考虑自动评估服务。

## 建设状态

| 优先级 | 当前落点 | 尚需完成 |
| --- | --- | --- |
| P0 任务与证据格式 | 结构验证器及负例测试 | 真实任务中的格式试用与证据复核 |
| P0 Skill 和适配回归 | YAML 解析、发现名称、资源链接、索引、共享链接及生成一致性测试 | 新客户端版本的实际加载验证 |
| P0 工具边界 | 检查失败聚合、安装路径和 ZIP 边界、回滚、保留元数据冲突与链接拒绝回归 | 随实际缺陷继续增加有效用例，不宣称穷尽 |
| P1 真实任务回归集 | 已定义样例输入、资源与评价要求 | 可复现样例文件与真实 AI Infra 设备失败、Agent 对照仍待采集 |
| P1 性能环境规范 | 已实现 latency 记录校验、原始样本汇总与固定环境字段 hash | 在目标硬件上验证与归档报告 |
| P2 人工晋级 | 已定义对照、成本与退化审查原则 | 真实候选的独立评估记录；尚无自动晋级服务 |

元数据解析依赖开发依赖 PyYAML；不对未知客户端字段施加统一白名单，避免误拒绝合法上游元数据。静态资源与客户端适配测试由统一 pytest 入口运行，不能证明 Agent 会正确执行技能。

## 固定验收与候选比较

执行前独立保存 contract：`task_id`、`objective` 和仅含 `id`、`expected` 的 criteria。执行报告不得省略或改写约定条目。契约文件由具体任务提供；当前仓库未提供可用的任务契约样例，真实任务还须记录授权范围、输入、资源和失败依据。

```bash
python scripts/validate_task_result.py result.json --contract contract.json
python scripts/compare_task_results.py contract.json baseline.json candidate.json
```

比较器要求两个结果分别匹配同一契约且 revision 不同，输出状态变化、原通过项的退化、候选失败及未验证项。合法比较返回成功仅表示格式与契约匹配，不表示候选通过验收。它不检验证据真实性、成本或统计显著性，也不会执行证明脚本、写回规则或晋级。

人工评审记录以下字段后再决定：候选与基准 revision、contract 及输入标识、比较结果与原始日志位置、正确性和性能变化、时间/费用/设备成本、适用范围、残余风险、审查人、日期、结论（接受/拒绝/继续试验）与理由。候选 failed 或 not_run 项不能靠省略或变成 not_applicable 消失；不适用需审查理由，必要时修订契约并重新比较双方。

当前已提供契约绑定与比较工具，尚无真实 Agent 候选晋级记录。结构和状态检查是人工评估的输入，不能伪装成人工批准。

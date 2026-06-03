# Direct SQL Execution-Feedback Refiner 实验报告

## 实验性质

本实验作为 SQL+ 层反馈修正的对照组，验证 Direct NL2SQL 生成的标准 SQL 在非 gold 执行反馈下是否能够被 Refiner Agent 修复。

模型输入不包含 gold SQL、gold result rows 或字段级 gold differences。gold 只用于离线评估修复后的 SQL 执行结果是否正确。

## 输入与输出

- 输入构造脚本：`scripts/agents/build_direct_feedback_refiner_inputs.py`
- 输入数据：`data/direct_feedback_refiner_inputs.jsonl`
- Prompt：`prompts/agents/direct_sql_feedback_refiner.md`
- 运行脚本：`scripts/agents/run_openai_direct_feedback_refiner.py`
- 初始输出：`outputs/refiner/direct_feedback_refiner_model.jsonl`
- 重跑输出：`outputs/refiner/direct_feedback_refiner_model_retry.jsonl`
- 合并输出：`outputs/refiner/direct_feedback_refiner_model_merged.jsonl`

## 实验命令

```powershell
python scripts/agents/build_direct_feedback_refiner_inputs.py
python scripts/agents/run_openai_direct_feedback_refiner.py --dry-run --limit 1
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_direct_feedback_refiner.py --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1800
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_direct_feedback_refiner.py --inputs data/direct_feedback_refiner_inputs_retry.jsonl --output outputs/refiner/direct_feedback_refiner_model_retry.jsonl --model gpt-5-mini --max-output-tokens 2600 --resume --retries 8 --delay-seconds 3
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/direct_feedback_refiner_model_merged.jsonl --sqlplus-output outputs/refiner/empty_sqlplus.jsonl --label "gpt-5-mini direct-sql execution-feedback refiner merged" --report docs/agents/direct_feedback_refiner_report_raw_merged.md
```

## 输入集规模

| 项目 | 数量 |
| --- | --- |
| Direct NL2SQL baseline 样例 | 30 |
| 初始正确跳过样例 | 16 |
| 进入反馈修正样例 | 14 |

## 粗粒度反馈分类

| 类别 | 数量 |
| --- | --- |
| filter_or_value_suspected | 7 |
| aggregation_suspected | 4 |
| order_or_limit_suspected | 3 |

## 实验结果

| 指标 | 结果 |
| --- | --- |
| Refiner 输出数 | 14/14 |
| JSON 解析失败 | 0/14 |
| SQL 可执行 | 14/14 |
| 修复成功 | 6/14 |
| API input tokens | 12000 |
| API output tokens | 10531 |
| API total tokens | 22531 |

## 难度分布

| 难度 | 样例数 | 修复成功 |
| --- | --- | --- |
| simple | 4 | 3/4 |
| medium | 8 | 2/8 |
| hard | 2 | 1/2 |

## 成功样例

| ID | 观察 |
| --- | --- |
| q002 | 修正中文乱码城市值为 `Beijing` |
| q003 | 修正排序字段为价格降序 |
| q005 | 修正字段/排序相关问题 |
| q007 | 修正过滤值或查询条件 |
| q019 | 修正聚合排序方向 |
| q023 | 修正复杂查询中的部分语义问题 |

## 与 SQL+ 非 gold Refiner 对比

| 方法 | 初始失败样例 | 可执行率 | 修复成功率 | 说明 |
| --- | --- | --- | --- | --- |
| Direct SQL Feedback Refiner | 14 | 14/14 | 6/14 | 直接修标准 SQL |
| SQL+ Feedback Refiner v2 merged | 13 | 12/13 | 4/13 | 修 SQL+ 中间表示 |

## 结论

在当前小数据集和单 Refiner prompt 设置下，Direct SQL 层非 gold 修复成功率为 6/14，高于 SQL+ 层非 gold 修复的 4/13。这不说明 SQL+ 路线失败，而说明当前 SQL+ Refiner 输入和 Critic 诊断仍然太粗，尚未发挥 SQL+ 分步表示的优势。

开题中可以这样表述：Direct SQL 修复作为必要对照组，当前结果显示 SQL+ 方法需要进一步引入 Schema Agent 和 Critic Agent，将执行反馈映射到 SQL+ 局部步骤，才能体现可解释、可定位、可修复的优势。

## 下一步

- 构建非 gold Critic Agent，输出具体错误定位但不泄露 gold answer。
- 对 Direct SQL 和 SQL+ 使用相同 Critic 信息，再比较两者修复成功率。
- 分析 SQL+ 剩余失败样例，优化 SQL+ Refiner 的局部修正策略。

# Execution-Feedback-Only Refiner Agent 实验报告

## 实验性质

本实验验证在不提供 gold SQL、gold SQL+、gold result rows、字段级 gold differences 的条件下，Refiner Agent 是否能够仅根据执行反馈、schema、原始 SQL+、结果预览和粗粒度错误类型修复 SQL+。

这比 `diagnosis-assisted refiner` 更接近真实反馈修正场景。

## 输入与输出

- 输入构造脚本：`scripts/agents/build_feedback_refiner_inputs.py`
- 输入数据 v1：`data/feedback_refiner_inputs.jsonl`
- 输入数据 v2：`data/feedback_refiner_inputs_v2.jsonl`
- Prompt：`prompts/agents/sqlplus_feedback_refiner.md`
- 运行脚本：`scripts/agents/run_openai_feedback_refiner.py`
- 第一轮输出：`outputs/refiner/sqlplus_feedback_refiner_model.jsonl`
- 第二轮合并输出：`outputs/refiner/sqlplus_feedback_refiner_model_v2_merged.jsonl`

## 实验命令

```powershell
python scripts/agents/build_feedback_refiner_inputs.py --output data/feedback_refiner_inputs_v2.jsonl --report docs/agents/feedback_refiner_inputs_v2.md
python scripts/agents/run_openai_feedback_refiner.py --inputs data/feedback_refiner_inputs_v2.jsonl --output outputs/refiner/sqlplus_feedback_refiner_model_v2.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3
python scripts/agents/run_openai_feedback_refiner.py --inputs data/feedback_refiner_inputs_v2_retry.jsonl --output outputs/refiner/sqlplus_feedback_refiner_model_v2_retry.jsonl --model gpt-5-mini --max-output-tokens 2500 --resume --retries 8 --delay-seconds 3
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_feedback_refiner_model_v2_merged.jsonl --label "gpt-5-mini execution-feedback-only refiner v2 merged" --report docs/agents/feedback_refiner_model_report_raw_v2_merged.md
python scripts/agents/diagnose_sqlplus_mismatches.py --predictions outputs/refiner/sqlplus_feedback_refiner_model_v2_merged.jsonl --jsonl-output data/feedback_refiner_model_diagnostics_v2_merged.jsonl --report docs/agents/feedback_refiner_model_diagnostics_v2_merged.md
```

## 输入集规模

| 项目 | 数量 |
| --- | --- |
| 原始 SQL+ prompt v2 样例 | 30 |
| 已正确跳过样例 | 17 |
| 进入反馈修正样例 | 13 |

## v2 输入粗粒度反馈分类

| 类别 | 数量 |
| --- | --- |
| filter_or_value_suspected | 6 |
| order_or_limit_suspected | 6 |
| aggregation_suspected | 1 |

## 结果对比

| 实验 | SQL+ 有效 | SQL 可执行 | 修复成功 | JSON 解析失败 | 说明 |
| --- | --- | --- | --- | --- | --- |
| Diagnosis-assisted Refiner | 13/13 | 13/13 | 13/13 | 0/13 | 使用 gold-derived differences |
| Execution-feedback Refiner v1 | 10/13 | 9/13 | 3/13 | 1/13 | 粗粒度反馈初版 |
| Execution-feedback Refiner v2 merged | 13/13 | 12/13 | 4/13 | 0/13 | 优化分类、禁止 LEFT JOIN、重跑截断样例 |

## v2 merged 难度分布

| 难度 | 样例数 | 修复成功 |
| --- | --- | --- |
| simple | 5 | 1/5 |
| medium | 7 | 3/7 |
| hard | 1 | 0/1 |

## v2 merged 成功样例

| ID | 类型 | 观察 |
| --- | --- | --- |
| q006 | order_or_limit_suspected | top-k 查询保持正确 |
| q017 | filter_or_value_suspected | 将 `canceled` 修正为数据库值 `cancelled` |
| q019 | order_or_limit_suspected | 修正聚合排序方向 |
| q026 | filter_or_value_suspected | 将 `canceled` 修正为 `cancelled` |

## v2 merged 剩余失败类型

| 类型 | 数量 |
| --- | --- |
| order_or_limit_mismatch | 3 |
| filter_or_value_linking | 2 |
| aggregation_planning | 2 |
| schema_or_join_planning | 1 |
| execution_error | 1 |

## Token 成本

| 实验 | Input tokens | Output tokens | Total tokens |
| --- | --- | --- | --- |
| Execution-feedback Refiner v1 | 13511 | 8810 | 22321 |
| Execution-feedback Refiner v2 merged | 14919 | 11370 | 26289 |

## 结论

非 gold 的真实执行反馈修正明显难于诊断辅助修正。当前 Refiner Agent 可以稳定输出合法 SQL+，也能修复部分值链接和排序问题，但对隐含排序、聚合语义、投影列和 join 路径仍不稳定。

这个结果对开题很有价值：它证明了仅靠单个 Refiner prompt 不足以完成复杂反馈修正，后续需要引入 Schema Agent、Planner Agent 和 Critic Agent，把错误定位、语义解释和局部修正拆开处理。

## 下一步

- 设计 Schema Agent 输出：相关表、字段、join 路径、数据库值。
- 设计 Critic Agent 输出：不使用 gold 字段差异，但给出更结构化的错误定位。
- 将 Refiner 输入从粗粒度 category 升级为 `execution feedback + schema linking + critic diagnosis`。

# SQL+ Schema-Critic-Refiner 多智能体实验报告

## 实验目的

本实验将 SQL+ 非 gold 反馈修正拆成三个阶段：

1. `Schema Agent`：基于问题和 SQL+ 输出相关表、字段、join 路径、候选数据库值。
2. `Critic Agent`：基于执行反馈、Schema Agent 输出和结果预览进行错误定位。
3. `Refiner Agent`：根据 Critic 诊断对 SQL+ 做局部修正。

实验目标是验证：相比单个 Refiner prompt，拆分错误定位和修复是否能提升 SQL+ 非 gold 反馈修正能力。

## 输入限制

模型输入不包含：

- gold SQL
- gold SQL+
- gold result rows
- 字段级 gold differences

Gold 仅用于离线评估修复后的 SQL 执行结果是否正确。

## 实验文件

- Schema Agent 输入构造：`scripts/agents/build_sqlplus_schema_agent_inputs.py`
- Critic prompt：`prompts/agents/sqlplus_critic.md`
- Critic 运行脚本：`scripts/agents/run_openai_sqlplus_critic.py`
- Critic-guided Refiner prompt：`prompts/agents/sqlplus_critic_refiner.md`
- Refiner 输入构造：`scripts/agents/build_critic_refiner_inputs.py`
- Schema Agent 输出：`data/sqlplus_schema_agent_inputs.jsonl`
- Critic 输出：`outputs/agents/sqlplus_critic_model_merged.jsonl`
- Refiner 输出：`outputs/refiner/sqlplus_critic_refiner_model.jsonl`

## 实验命令

```powershell
python scripts/agents/build_sqlplus_schema_agent_inputs.py
python scripts/agents/run_openai_sqlplus_critic.py --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1800
python scripts/agents/run_openai_sqlplus_critic.py --inputs data/sqlplus_schema_agent_inputs_retry.jsonl --output outputs/agents/sqlplus_critic_model_retry.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 3000
python scripts/agents/build_critic_refiner_inputs.py --critic-output outputs/agents/sqlplus_critic_model_merged.jsonl --output data/sqlplus_critic_refiner_inputs_merged.jsonl --report docs/agents/sqlplus_critic_refiner_inputs_merged.md
python scripts/agents/run_openai_feedback_refiner.py --inputs data/sqlplus_critic_refiner_inputs_merged.jsonl --prompt-template prompts/agents/sqlplus_critic_refiner.md --output outputs/refiner/sqlplus_critic_refiner_model.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1800
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_critic_refiner_model.jsonl --label "gpt-5-mini schema-critic-refiner sqlplus" --report docs/agents/sqlplus_schema_critic_refiner_report_raw.md
python scripts/agents/diagnose_sqlplus_mismatches.py --predictions outputs/refiner/sqlplus_critic_refiner_model.jsonl --jsonl-output data/sqlplus_schema_critic_refiner_diagnostics.jsonl --report docs/agents/sqlplus_schema_critic_refiner_diagnostics.md
```

## Critic Agent 输出统计

| 指标 | 结果 |
| --- | --- |
| Critic 输入样例 | 13 |
| Critic 输出 | 13/13 |
| Critic JSON 解析失败 | 0/13 |
| Critic error type: filter_or_value | 7 |
| Critic error type: order_or_limit | 6 |
| Critic total tokens | 31367 |

观察：Critic Agent 将所有错误都归为 `filter_or_value` 或 `order_or_limit`，没有识别出 aggregation、schema_or_join、projection 等真实复杂错误，说明当前 Critic prompt 和 Schema Agent 信息不足。

## Refiner 评估结果

| 指标 | 结果 |
| --- | --- |
| Refiner 输入样例 | 13 |
| SQL+ 有效 | 13/13 |
| SQL 可执行 | 13/13 |
| 修复成功 | 3/13 |
| JSON 解析失败 | 0/13 |
| Refiner total tokens | 26313 |

成功样例：

| ID | 说明 |
| --- | --- |
| q002 | 补齐或保持北京客户查询的正确结果 |
| q017 | 修正 `canceled` / `cancelled` 类型的状态值问题 |
| q026 | 修正非取消订单中的状态值问题 |

剩余失败类型：

| 类型 | 数量 |
| --- | --- |
| schema_or_join_planning | 3 |
| filter_or_value_linking | 3 |
| order_or_limit_mismatch | 2 |
| aggregation_planning | 1 |
| projection_mismatch | 1 |

## 与已有实验对比

| 方法 | 初始失败样例 | SQL+ 有效 | SQL 可执行 | 修复成功 |
| --- | --- | --- | --- | --- |
| SQL+ 非 gold 单 Refiner v2 | 13 | 13/13 | 12/13 | 4/13 |
| SQL+ Schema-Critic-Refiner | 13 | 13/13 | 13/13 | 3/13 |
| Direct SQL 非 gold Refiner | 14 | - | 14/14 | 6/14 |
| SQL+ 诊断辅助 Refiner | 13 | 13/13 | 13/13 | 13/13 |

## 结论

本轮多智能体实验没有提升修复成功率，反而从单 Refiner 的 4/13 降到 3/13。原因不是多智能体方向错误，而是当前 Critic Agent 的错误定位质量不足：它过度集中在过滤和值链接、排序问题，没有有效识别聚合口径、投影列和 join 路径问题。

该结果对开题仍然有价值：它说明多智能体不能只是形式上串联 Agent，而必须让每个 Agent 输出高质量、可验证、可约束的中间结果。尤其是 Critic Agent 必须具备更强的结构化错误定位能力，否则会误导 Refiner。

## 对开题的意义

可以在开题中将该实验作为“多智能体原型初步验证与问题发现”：

- 已经实现了 Schema Agent、Critic Agent、Refiner Agent 的最小链路。
- 证明了 Agent 间中间结果可以被记录和评估。
- 暴露出当前 Critic Agent 诊断不足的问题。
- 为后续研究问题提供依据：如何设计非 gold 条件下更可靠的错误诊断机制。

## 下一步优化方向

1. 优化 Schema Agent：不要只给候选 schema，还要明确自然语言中提到的实体、指标、排序意图和输出列。
2. 优化 Critic Agent：强制按 `WHERE/JOIN/GROUP/AGG/SELECT/ORDER/LIMIT` 逐步检查，而不是只输出一个粗分类。
3. 给 Critic 增加反事实执行工具：例如尝试不同 ORDER、候选值替换、候选聚合表达，比较结果变化，但不使用 gold answer。
4. 先在失败类型上做分治实验：分别优化 order、value linking、aggregation、join 四类错误。

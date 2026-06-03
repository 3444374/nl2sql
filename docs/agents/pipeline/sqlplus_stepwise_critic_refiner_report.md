# SQL+ Step-wise Critic-Refiner 改良实验报告

## 实验目的

在上一轮 `Schema-Critic-Refiner` 初版中，Critic Agent 只输出粗粒度错误类型，且没有识别出聚合、投影、连接路径等复杂错误。本轮改良将 Critic Agent 改为 step-wise 诊断：强制按 SQL+ 步骤逐项检查。

检查步骤包括：

```text
FROM / JOIN / WHERE / GROUP / AGG / SELECT / ORDER / LIMIT
```

每个步骤输出：

```text
correct / suspicious / missing / not_applicable
```

## 目录整理

本轮同时将 agents 相关文件按角色重新分类：

```text
prompts/agents/schema
prompts/agents/critic
prompts/agents/refiner

scripts/agents/schema
scripts/agents/critic
scripts/agents/refiner
scripts/agents/diagnostics
scripts/agents/pipeline

docs/agents/schema
docs/agents/critic
docs/agents/refiner
docs/agents/diagnostics
docs/agents/pipeline

outputs/agents/critic
```

## 输入限制

模型输入仍然不包含：

- gold SQL
- gold SQL+
- gold result rows
- 字段级 gold differences

Gold 只用于离线执行结果评估。

## 实验文件

| 类型 | 文件 |
| --- | --- |
| Step-wise Critic prompt | `prompts/agents/critic/sqlplus_critic.md` |
| Critic-guided Refiner prompt | `prompts/agents/refiner/sqlplus_critic_refiner.md` |
| Schema Agent 脚本 | `scripts/agents/schema/build_sqlplus_schema_agent_inputs.py` |
| Critic 运行脚本 | `scripts/agents/critic/run_openai_sqlplus_critic.py` |
| Refiner 输入构造 | `scripts/agents/pipeline/build_critic_refiner_inputs.py` |
| Refiner 运行脚本 | `scripts/agents/refiner/run_openai_feedback_refiner.py` |
| Step-wise Critic 输出 | `outputs/agents/critic/sqlplus_critic_stepwise_model_merged.jsonl` |
| Step-wise Refiner 输出 | `outputs/refiner/sqlplus_stepwise_critic_refiner_model_merged.jsonl` |

## 实验命令

```powershell
python scripts/agents/schema/build_sqlplus_schema_agent_inputs.py --output data/sqlplus_schema_agent_inputs_stepwise.jsonl --report docs/agents/schema/sqlplus_schema_agent_inputs_stepwise.md
python scripts/agents/critic/run_openai_sqlplus_critic.py --inputs data/sqlplus_schema_agent_inputs_stepwise.jsonl --output outputs/agents/critic/sqlplus_critic_stepwise_model.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 2600
python scripts/agents/critic/run_openai_sqlplus_critic.py --inputs data/sqlplus_schema_agent_inputs_stepwise_retry.jsonl --output outputs/agents/critic/sqlplus_critic_stepwise_model_retry.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 4200
python scripts/agents/pipeline/build_critic_refiner_inputs.py --schema-inputs data/sqlplus_schema_agent_inputs_stepwise.jsonl --critic-output outputs/agents/critic/sqlplus_critic_stepwise_model_merged.jsonl --output data/sqlplus_critic_refiner_inputs_stepwise_merged.jsonl --report docs/agents/pipeline/sqlplus_critic_refiner_inputs_stepwise_merged.md
python scripts/agents/refiner/run_openai_feedback_refiner.py --inputs data/sqlplus_critic_refiner_inputs_stepwise_merged.jsonl --prompt-template prompts/agents/refiner/sqlplus_critic_refiner.md --output outputs/refiner/sqlplus_stepwise_critic_refiner_model.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 2000
python scripts/agents/refiner/run_openai_feedback_refiner.py --inputs data/sqlplus_critic_refiner_inputs_stepwise_retry.jsonl --prompt-template prompts/agents/refiner/sqlplus_critic_refiner.md --output outputs/refiner/sqlplus_stepwise_critic_refiner_model_retry.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 3600
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_stepwise_critic_refiner_model_merged.jsonl --label "gpt-5-mini stepwise-critic-refiner sqlplus merged" --report docs/agents/pipeline/sqlplus_stepwise_critic_refiner_report_raw_merged.md
```

## Step-wise Critic 输出统计

| 指标 | 结果 |
| --- | --- |
| Critic 输入样例 | 13 |
| Critic 输出 | 13/13 |
| JSON 解析失败 | 0/13 |
| likely_error_type: order_or_limit | 6 |
| likely_error_type: filter_or_value | 6 |
| likely_error_type: aggregation | 1 |
| Critic total tokens | 49581 |

Step-wise localized step 统计：

| SQL+ step | suspicious/missing 次数 |
| --- | --- |
| ORDER | 6 |
| WHERE | 6 |
| JOIN | 2 |
| LIMIT | 1 |
| GROUP | 1 |
| AGG | 1 |
| SELECT | 1 |

## Refiner 评估结果

| 指标 | 结果 |
| --- | --- |
| Refiner 输入样例 | 13 |
| SQL+ 有效 | 13/13 |
| SQL 可执行 | 12/13 |
| 修复成功 | 3/13 |
| JSON 解析失败 | 0/13 |
| Refiner total tokens | 35688 |

成功样例：

| ID | 说明 |
| --- | --- |
| q002 | 北京客户查询结果正确 |
| q017 | 修正 `canceled` / `cancelled` 状态值问题 |
| q026 | 修正非取消订单状态值问题 |

## 与前序实验对比

| 方法 | SQL+ 有效 | SQL 可执行 | 修复成功 |
| --- | --- | --- | --- |
| SQL+ 非 gold 单 Refiner v2 | 13/13 | 12/13 | 4/13 |
| SQL+ Schema-Critic-Refiner 初版 | 13/13 | 13/13 | 3/13 |
| SQL+ Step-wise Critic-Refiner | 13/13 | 12/13 | 3/13 |
| Direct SQL 非 gold Refiner | - | 14/14 | 6/14 |
| SQL+ 诊断辅助 Refiner | 13/13 | 13/13 | 13/13 |

## 结论

Step-wise Critic 相比初版 Critic 提供了更细粒度的诊断，能够输出 JOIN、GROUP、AGG、SELECT 等局部步骤的可疑状态。但修复成功率仍为 3/13，没有超过单 Refiner 的 4/13。

这说明当前瓶颈不只是“诊断格式不够细”，还包括：

1. Schema Agent 对自然语言意图的解析仍然不足。
2. Critic 虽能标出步骤，但 repair_hint 不够精确。
3. Refiner 对多个 suspicious/missing 步骤的联合修复不稳定。
4. 没有反事实执行机制，Critic 无法验证候选修复是否更合理。

## 对开题的价值

该实验可以作为多智能体研究路线的初步证据：

- 已完成按 agent 类型组织的实验链路。
- 已实现 Schema、Critic、Refiner 的可替换模块。
- 证明了中间输出可以被记录和评估。
- 暴露出 Critic 诊断质量和 Refiner 局部修复策略是后续研究重点。

## 下一步

不建议继续盲目增加 agent。下一步应做更小的分治实验：

1. 只针对 `ORDER` 类错误优化 Critic/Refiner。
2. 只针对 `value linking` 类错误优化候选值替换。
3. 对 aggregation/join 错误引入候选 SQL+ patch 和反事实执行。
4. 再将分治策略合并回完整多智能体流程。

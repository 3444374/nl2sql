# SQL+ 分治反馈修正实验报告

## 实验目的

前序完整多智能体实验中，不同错误类型混在一起，导致 Critic 和 Refiner 难以稳定定位错误。本实验采用分治策略，将错误按类型拆开，分别设计局部修复 prompt，并限制 Refiner 只能修改对应 SQL+ 步骤。

本轮先验证两类最清晰的错误：

1. `ORDER-only`：只修排序错误，只允许修改 `ORDER` / `LIMIT`。
2. `value-linking-only`：只修 WHERE 中的字面值和简单边界条件，只允许修改 `WHERE`。

## 输入限制

模型输入不包含：

- gold SQL
- gold SQL+
- gold result rows
- 字段级 gold differences

Gold 只用于离线评估修复后的执行结果是否正确。

## 实验文件

| 类型 | 文件 |
| --- | --- |
| ORDER-only prompt | `prompts/agents/refiner/sqlplus_order_only_refiner.md` |
| value-only prompt | `prompts/agents/refiner/sqlplus_value_only_refiner.md` |
| 输入构造脚本 | `scripts/agents/pipeline/build_divide_refiner_inputs.py` |
| ORDER-only 输入 | `data/sqlplus_order_only_refiner_inputs.jsonl` |
| value-only 输入 | `data/sqlplus_value_only_refiner_inputs.jsonl` |
| ORDER-only 输出 | `outputs/refiner/sqlplus_order_only_refiner_model_merged.jsonl` |
| value-only 输出 | `outputs/refiner/sqlplus_value_only_refiner_model.jsonl` |

## 实验命令

```powershell
python scripts/agents/pipeline/build_divide_refiner_inputs.py --kind order
python scripts/agents/pipeline/build_divide_refiner_inputs.py --kind value
python scripts/agents/refiner/run_openai_feedback_refiner.py --inputs data/sqlplus_order_only_refiner_inputs.jsonl --prompt-template prompts/agents/refiner/sqlplus_order_only_refiner.md --output outputs/refiner/sqlplus_order_only_refiner_model.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1200
python scripts/agents/refiner/run_openai_feedback_refiner.py --inputs data/sqlplus_value_only_refiner_inputs.jsonl --prompt-template prompts/agents/refiner/sqlplus_value_only_refiner.md --output outputs/refiner/sqlplus_value_only_refiner_model.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1400
python scripts/agents/refiner/run_openai_feedback_refiner.py --inputs data/sqlplus_order_only_refiner_inputs_retry.jsonl --prompt-template prompts/agents/refiner/sqlplus_order_only_refiner.md --output outputs/refiner/sqlplus_order_only_refiner_model_retry.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1200
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_order_only_refiner_model_merged.jsonl --label "gpt-5-mini sqlplus order-only refiner merged" --report docs/agents/pipeline/sqlplus_order_only_refiner_report_raw_merged.md
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_value_only_refiner_model.jsonl --label "gpt-5-mini sqlplus value-only refiner" --report docs/agents/pipeline/sqlplus_value_only_refiner_report_raw.md
```

## ORDER-only 实验

输入样例：

| ID | 错误表现 | 允许修改 |
| --- | --- | --- |
| q002 | 缺少客户名称排序 | ORDER/LIMIT |
| q003 | 缺少价格降序排序 | ORDER/LIMIT |
| q005 | 缺少数量降序排序 | ORDER/LIMIT |

结果：

| 指标 | 结果 |
| --- | --- |
| 样例数 | 3 |
| SQL+ 有效 | 3/3 |
| SQL 可执行 | 3/3 |
| 修复成功 | 2/3 |
| 成功样例 | q002、q003 |
| 失败样例 | q005 |
| Token | 3863 |

失败分析：

q005 的自然语言为“查询单价低于200元的订单明细编号、商品编号和数量”。模型两次都倾向于补充 `ORDER oi.item_id ASC`，而不是 `ORDER oi.quantity DESC`。这说明即使限制只修 ORDER，模型仍难以从“数量”这一输出字段推断排序意图。

## value-linking-only 实验

输入样例：

| ID | 错误表现 | 允许修改 |
| --- | --- | --- |
| q004 | 日期边界错误 | WHERE |
| q017 | `canceled` 应为 `cancelled` | WHERE |
| q026 | `canceled` 应为 `cancelled` | WHERE |

结果：

| 指标 | 结果 |
| --- | --- |
| 样例数 | 3 |
| SQL+ 有效 | 3/3 |
| SQL 可执行 | 3/3 |
| 修复成功 | 3/3 |
| 成功样例 | q004、q017、q026 |
| Token | 3973 |

观察：

value-linking-only prompt 能稳定修复数据库值拼写和日期边界问题，说明当错误类型清晰且候选值有限时，局部 Refiner 可靠性明显高于全局 Refiner。

## 与完整实验对比

| 方法 | 样例数 | 修复成功 |
| --- | --- | --- |
| SQL+ 非 gold 单 Refiner v2 | 13 | 4/13 |
| SQL+ Step-wise Critic-Refiner | 13 | 3/13 |
| ORDER-only 分治 | 3 | 2/3 |
| value-linking-only 分治 | 3 | 3/3 |

## 结论

分治实验验证了一个关键判断：将错误类型拆开后，局部修复效果明显更稳定。尤其是 value-linking 类错误，在限制只修改 WHERE 并提供已知数据库值后，可以达到 3/3 修复成功。

ORDER 类错误仍有一个失败样例，说明排序意图识别需要进一步加强，尤其是当自然语言没有显式说“按数量降序”但标准结果要求按数量排序时，模型容易选择确定性 id 排序。

## 对开题的意义

该实验可以支撑“多智能体反馈修正需要错误类型分治”的研究思路：

- 不同错误类型需要不同 Critic 和 Refiner 策略。
- SQL+ 的步骤化表达便于限制局部修改范围，如只改 WHERE 或只改 ORDER。
- 分治策略比单一全局 Refiner 更可控、更可解释。

## 下一步

1. 强化 ORDER 意图识别：从输出列、数值列、业务语义中推断排序字段。
2. 扩展 value-linking 候选值替换机制，加入城市、类别、状态、日期边界。
3. 继续做 aggregation-only 和 join-only 分治实验。

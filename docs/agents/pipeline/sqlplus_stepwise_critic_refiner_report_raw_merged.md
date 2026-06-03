# Baseline 评估报告

实验标签：gpt-5-mini stepwise-critic-refiner sqlplus merged
评估模式：仅评估已有预测
完整评估集规模：30

说明：如果实验标签为 oracle sanity check，结果只表示评估管线正确，不代表真实 LLM 生成能力。

## 总体结果

| 方法 | 已评估样例数 | SQL+有效 | SQL可执行 | 执行结果一致 |
| --- | --- | --- | --- | --- |
| Direct NL2SQL | 0 | - | 0/0 | 0/0 |
| NL2SQL+ | 13 | 13/13 | 12/13 | 3/13 |

## Direct NL2SQL 难度分布

| 难度 | 已评估样例数 | 执行结果一致 |
| --- | --- | --- |
| - | 0 | 0/0 |

## NL2SQL+ 难度分布

| 难度 | 已评估样例数 | 执行结果一致 |
| --- | --- | --- |
| hard | 1 | 0/1 |
| medium | 7 | 2/7 |
| simple | 5 | 1/5 |

## 失败样例

| 方法 | ID | 难度 | 错误 |
| --- | --- | --- | --- |
| sqlplus | q003 | simple |  |
| sqlplus | q004 | simple |  |
| sqlplus | q005 | simple |  |
| sqlplus | q006 | simple |  |
| sqlplus | q013 | medium |  |
| sqlplus | q015 | medium |  |
| sqlplus | q019 | medium |  |
| sqlplus | q021 | medium |  |
| sqlplus | q022 | hard | no such column: customer_id |
| sqlplus | q025 | medium |  |

## 后续使用方式

1. 将真实模型输出保存为 JSONL，每行包含 `id` 和 `prediction`。
2. Direct NL2SQL 输出传给 `--direct-output`。
3. NL2SQL+ 输出传给 `--sqlplus-output`。
4. 默认只评估已有预测；完整 30 条跑完后，报告中的已评估样例数应为 30。
5. 如需把缺失预测计入失败，添加 `--include-missing`。

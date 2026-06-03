# Baseline 评估报告

实验标签：gpt-5-mini sqlplus value-only refiner
评估模式：仅评估已有预测
完整评估集规模：30

说明：如果实验标签为 oracle sanity check，结果只表示评估管线正确，不代表真实 LLM 生成能力。

## 总体结果

| 方法 | 已评估样例数 | SQL+有效 | SQL可执行 | 执行结果一致 |
| --- | --- | --- | --- | --- |
| Direct NL2SQL | 0 | - | 0/0 | 0/0 |
| NL2SQL+ | 3 | 3/3 | 3/3 | 3/3 |

## Direct NL2SQL 难度分布

| 难度 | 已评估样例数 | 执行结果一致 |
| --- | --- | --- |
| - | 0 | 0/0 |

## NL2SQL+ 难度分布

| 难度 | 已评估样例数 | 执行结果一致 |
| --- | --- | --- |
| medium | 2 | 2/2 |
| simple | 1 | 1/1 |

## 失败样例

| 方法 | ID | 难度 | 错误 |
| --- | --- | --- | --- |
| - | - | - | 无 |

## 后续使用方式

1. 将真实模型输出保存为 JSONL，每行包含 `id` 和 `prediction`。
2. Direct NL2SQL 输出传给 `--direct-output`。
3. NL2SQL+ 输出传给 `--sqlplus-output`。
4. 默认只评估已有预测；完整 30 条跑完后，报告中的已评估样例数应为 30。
5. 如需把缺失预测计入失败，添加 `--include-missing`。

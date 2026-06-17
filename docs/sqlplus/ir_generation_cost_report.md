# IR 生成成本与执行效果对比实验

## 实验目的

本实验比较同一批自然语言问题在 Direct SQL、SQL+、NatSQL-style proxy 和 SemQL-style proxy 四种生成目标下的 token 成本、生成延迟、表示有效率、SQL 可执行率和执行结果一致率。

## 实验设置

- 模型：`gpt-5-mini`。
- 样例数：30。
- 数据集：自建订单分析数据集。
- 执行环境：SQLite 内存数据库。
- SemQL-style 与 NatSQL-style 为受控 proxy，不代表完整复现原系统。
- 原始输出：`outputs/ir_generation/ir_generation_outputs.jsonl`。
- 详细结果：`data/ir_generation_cost_detail.csv`。
- 汇总结果：`data/ir_generation_cost_summary.csv`。

## 汇总结果

| Method | Cases | Valid repr | Valid SQL | Exec match | Avg input tok | Avg output tok | Avg total tok | Avg latency s | Avg chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| direct_sql | 30 | 30/30 | 30/30 | 12/30 | 287.6 | 311.5667 | 599.1667 | 6.5851 | 202.9667 |
| sqlplus | 30 | 28/30 | 28/30 | 14/30 | 319.1333 | 493.9 | 813.0333 | 9.2197 | 204.0 |
| natsql_style_proxy | 30 | 30/30 | 30/30 | 13/30 | 319.1333 | 421.6333 | 740.7667 | 6.2802 | 185.5 |
| semql_style_proxy | 30 | 30/30 | 25/30 | 12/30 | 343.1333 | 685.8333 | 1028.9667 | 9.9684 | 222.3333 |

## 失败样例

| Method | ID | Error |
| --- | --- | --- |
| direct_sql | q002 | execution result mismatch |
| direct_sql | q003 | execution result mismatch |
| direct_sql | q004 | execution result mismatch |
| direct_sql | q005 | execution result mismatch |
| direct_sql | q006 | execution result mismatch |
| direct_sql | q007 | execution result mismatch |
| direct_sql | q008 | execution result mismatch |
| direct_sql | q012 | execution result mismatch |
| direct_sql | q013 | execution result mismatch |
| direct_sql | q015 | execution result mismatch |
| direct_sql | q016 | execution result mismatch |
| direct_sql | q017 | execution result mismatch |
| direct_sql | q019 | execution result mismatch |
| direct_sql | q021 | execution result mismatch |
| direct_sql | q022 | execution result mismatch |
| direct_sql | q023 | execution result mismatch |
| direct_sql | q025 | execution result mismatch |
| direct_sql | q027 | execution result mismatch |
| sqlplus | q002 | execution result mismatch |
| sqlplus | q003 | execution result mismatch |
| sqlplus | q004 | execution result mismatch |
| sqlplus | q005 | execution result mismatch |
| sqlplus | q007 | execution result mismatch |
| sqlplus | q008 | execution result mismatch |
| sqlplus | q013 | Unsupported SQL+ step: LEFT |
| sqlplus | q015 | execution result mismatch |
| sqlplus | q016 | execution result mismatch |
| sqlplus | q018 | execution result mismatch |
| sqlplus | q019 | execution result mismatch |
| sqlplus | q021 | execution result mismatch |
| sqlplus | q022 | execution result mismatch |
| sqlplus | q023 | execution result mismatch |
| sqlplus | q025 | execution result mismatch |
| sqlplus | q027 | Unsupported SQL+ step: LEFT |
| natsql_style_proxy | q002 | execution result mismatch |
| natsql_style_proxy | q003 | execution result mismatch |
| natsql_style_proxy | q004 | execution result mismatch |
| natsql_style_proxy | q005 | execution result mismatch |
| natsql_style_proxy | q007 | execution result mismatch |
| natsql_style_proxy | q008 | execution result mismatch |
| natsql_style_proxy | q012 | execution result mismatch |
| natsql_style_proxy | q013 | execution result mismatch |
| natsql_style_proxy | q015 | execution result mismatch |
| natsql_style_proxy | q017 | execution result mismatch |
| natsql_style_proxy | q018 | execution result mismatch |
| natsql_style_proxy | q019 | execution result mismatch |
| natsql_style_proxy | q021 | execution result mismatch |
| natsql_style_proxy | q022 | execution result mismatch |
| natsql_style_proxy | q023 | execution result mismatch |
| natsql_style_proxy | q025 | execution result mismatch |
| natsql_style_proxy | q027 | execution result mismatch |
| semql_style_proxy | q002 | execution result mismatch |
| semql_style_proxy | q003 | execution result mismatch |
| semql_style_proxy | q004 | execution result mismatch |
| semql_style_proxy | q005 | execution result mismatch |
| semql_style_proxy | q007 | execution result mismatch |
| semql_style_proxy | q008 | execution result mismatch |
| semql_style_proxy | q009 | execution result mismatch |
| semql_style_proxy | q012 | near "c": syntax error |
| semql_style_proxy | q013 | near ".": syntax error |
| semql_style_proxy | q015 | execution result mismatch |
| semql_style_proxy | q016 | near "p": syntax error |
| semql_style_proxy | q017 | execution result mismatch |
| semql_style_proxy | q021 | execution result mismatch |
| semql_style_proxy | q022 | near ".": syntax error |
| semql_style_proxy | q023 | execution result mismatch |
| semql_style_proxy | q024 | execution result mismatch |
| semql_style_proxy | q025 | execution result mismatch |
| semql_style_proxy | q027 | near ".": syntax error |

## 解释边界

- 该实验衡量的是开题阶段受控表示的生成成本，不是完整 SemQL 或 NatSQL 系统复现。
- execution match 通过生成 SQL 与 gold SQL 在同一 SQLite 数据库上的执行结果比较得到。
- 若某方法 valid representation 低，说明模型没有稳定遵守该中间表示的输出格式；若 valid SQL 低，说明转换或执行阶段存在问题。

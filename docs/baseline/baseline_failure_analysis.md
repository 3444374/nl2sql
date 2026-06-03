# Baseline 失败样例分析

## 错误类型统计

| 方法 | 错误类型 | 数量 |
| --- | --- | --- |
| Direct NL2SQL | semantic_mismatch | 14 |
| NL2SQL+ | semantic_mismatch | 17 |

## 失败明细

| 方法 | ID | 难度 | 错误类型 | 说明 |
| --- | --- | --- | --- | --- |
| direct_sql | q002 | simple | semantic_mismatch | execution result differs |
| direct_sql | q003 | simple | semantic_mismatch | execution result differs |
| direct_sql | q004 | simple | semantic_mismatch | execution result differs |
| direct_sql | q005 | simple | semantic_mismatch | execution result differs |
| direct_sql | q007 | medium | semantic_mismatch | execution result differs |
| direct_sql | q008 | medium | semantic_mismatch | execution result differs |
| direct_sql | q013 | medium | semantic_mismatch | execution result differs |
| direct_sql | q016 | medium | semantic_mismatch | execution result differs |
| direct_sql | q019 | medium | semantic_mismatch | execution result differs |
| direct_sql | q021 | medium | semantic_mismatch | execution result differs |
| direct_sql | q022 | hard | semantic_mismatch | execution result differs |
| direct_sql | q023 | hard | semantic_mismatch | execution result differs |
| direct_sql | q025 | medium | semantic_mismatch | execution result differs |
| direct_sql | q027 | medium | semantic_mismatch | execution result differs |
| sqlplus | q002 | simple | semantic_mismatch | execution result differs |
| sqlplus | q003 | simple | semantic_mismatch | execution result differs |
| sqlplus | q004 | simple | semantic_mismatch | execution result differs |
| sqlplus | q005 | simple | semantic_mismatch | execution result differs |
| sqlplus | q007 | medium | semantic_mismatch | execution result differs |
| sqlplus | q008 | medium | semantic_mismatch | execution result differs |
| sqlplus | q009 | medium | semantic_mismatch | execution result differs |
| sqlplus | q010 | medium | semantic_mismatch | execution result differs |
| sqlplus | q013 | medium | semantic_mismatch | execution result differs |
| sqlplus | q015 | medium | semantic_mismatch | execution result differs |
| sqlplus | q016 | medium | semantic_mismatch | execution result differs |
| sqlplus | q019 | medium | semantic_mismatch | execution result differs |
| sqlplus | q021 | medium | semantic_mismatch | execution result differs |
| sqlplus | q022 | hard | semantic_mismatch | execution result differs |
| sqlplus | q023 | hard | semantic_mismatch | execution result differs |
| sqlplus | q025 | medium | semantic_mismatch | execution result differs |
| sqlplus | q027 | medium | semantic_mismatch | execution result differs |

## 观察

1. Direct NL2SQL 的失败主要是 semantic_mismatch，说明 SQL 可执行但结果与 gold SQL 不一致。
2. NL2SQL+ 当前失败主要是 semantic_mismatch，说明 SQL+ 已能转换为可执行 SQL，但查询语义仍可能偏离 gold SQL。
3. 如果出现 schema_column_or_alias_error，优先检查 SQL+ 转换器对 AGG 别名、ORDER/HAVING 和聚合后 SELECT 的处理。


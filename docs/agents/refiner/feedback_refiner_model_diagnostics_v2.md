# SQL+ Semantic Mismatch Diagnostics

## Category Counts

| Category | Count |
| --- | --- |
| aggregation_planning | 1 |
| execution_error | 3 |
| filter_or_value_linking | 2 |
| order_or_limit_mismatch | 3 |

## Details

| ID | Difficulty | Category | Gold Rows | Pred Rows | Changed Fields |
| --- | --- | --- | --- | --- | --- |
| q002 | simple | order_or_limit_mismatch | 2 | 2 | order_by |
| q003 | simple | order_or_limit_mismatch | 3 | 3 | order_by |
| q004 | simple | filter_or_value_linking | 4 | 3 | wheres |
| q005 | simple | order_or_limit_mismatch | 2 | 2 | order_by |
| q013 | medium | execution_error | - | - |  |
| q015 | medium | aggregation_planning | 3 | 3 | agg, order_by |
| q021 | medium | filter_or_value_linking | 1 | 1 | wheres, group_by, agg |
| q022 | hard | execution_error | - | - |  |
| q025 | medium | execution_error | - | - |  |

## Refiner Agent Input

Use `data/sqlplus_mismatch_diagnostics.jsonl` as structured input for a Refiner Agent. Each record includes the user question, gold/predicted SQL+ difference fields, row count differences, and result previews.

# SQL+ Semantic Mismatch Diagnostics

## Category Counts

| Category | Count |
| --- | --- |
| aggregation_planning | 1 |
| execution_error | 4 |
| order_or_limit_mismatch | 3 |
| schema_or_join_planning | 2 |

## Details

| ID | Difficulty | Category | Gold Rows | Pred Rows | Changed Fields |
| --- | --- | --- | --- | --- | --- |
| q002 | simple | order_or_limit_mismatch | 2 | 2 | order_by |
| q003 | simple | order_or_limit_mismatch | 3 | 3 | order_by |
| q004 | simple | execution_error | - | - |  |
| q005 | simple | order_or_limit_mismatch | 2 | 2 | order_by |
| q013 | medium | execution_error | - | - |  |
| q015 | medium | aggregation_planning | 3 | 3 | agg, order_by |
| q019 | medium | schema_or_join_planning | 6 | 6 | joins, order_by |
| q021 | medium | execution_error | - | - |  |
| q022 | hard | execution_error | - | - |  |
| q025 | medium | schema_or_join_planning | 3 | 3 | joins, select, order_by |

## Refiner Agent Input

Use `data/sqlplus_mismatch_diagnostics.jsonl` as structured input for a Refiner Agent. Each record includes the user question, gold/predicted SQL+ difference fields, row count differences, and result previews.

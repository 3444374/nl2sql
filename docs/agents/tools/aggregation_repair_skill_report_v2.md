# Aggregation Repair Skill Report

| Metric | Result |
| --- | --- |
| Cases | 3 |
| SQL+ valid | 3/3 |
| SQL executable | 3/3 |
| Repair success | 3/3 |

## Details

| ID | Candidate Count | Selected Score | Success | Actions |
| --- | --- | --- | --- | --- |
| q013 | 7 | (1, 2, 5) | True | Remove redundant identifier dimension(s) `c.customer_id` from GROUP/AGG.; Normalize `COUNT(id)` to `COUNT(*)` for row-count aggregation.; Order grouped results by aggregate alias `paid_order_count` descending. |
| q015 | 3 | (1, 2, 3) | True | Normalize `COUNT(id)` to `COUNT(*)` for row-count aggregation.; Order grouped results by aggregate alias `customer_count` descending. |
| q021 | 5 | (1, 2, 1) | True | Add filtered dimension `p.category` to GROUP/AGG so the aggregate keeps its business label.; Order grouped results by aggregate alias `total_quantity` descending. |

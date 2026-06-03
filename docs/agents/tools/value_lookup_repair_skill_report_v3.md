# Value Lookup Repair Skill Report

| Metric | Result |
| --- | --- |
| Cases | 3 |
| SQL+ valid | 3/3 |
| SQL executable | 3/3 |
| Repair success | 3/3 |

## Details

| ID | Candidate Count | Selected Score | Success | Actions |
| --- | --- | --- | --- | --- |
| q004 | 1 | (1, 8) | True | Normalize month boundary to `o.order_date >= '2025-03-01'`. |
| q017 | 1 | (1, 2) | True | Replace literal `canceled` with known value `cancelled` for `o.status`. |
| q026 | 1 | (1, 18) | True | Replace literal `canceled` with known value `cancelled` for `o.status`. |

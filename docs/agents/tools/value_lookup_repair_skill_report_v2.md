# Value Lookup Repair Skill Report

| Metric | Result |
| --- | --- |
| Cases | 3 |
| SQL+ valid | 3/3 |
| SQL executable | 3/3 |
| Repair success | 2/3 |

## Details

| ID | Candidate Count | Selected Score | Success | Actions |
| --- | --- | --- | --- | --- |
| q004 | 2 | (1, 6) | False | Replace literal `2025-03-31` with known value `2025-03-21` for `o.order_date`. |
| q017 | 1 | (1, 2) | True | Replace literal `canceled` with known value `cancelled` for `o.status`. |
| q026 | 1 | (1, 18) | True | Replace literal `canceled` with known value `cancelled` for `o.status`. |

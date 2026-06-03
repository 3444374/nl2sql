# ORDER Repair Skill Report

| Metric | Result |
| --- | --- |
| Cases | 3 |
| SQL+ valid | 3/3 |
| SQL executable | 3/3 |
| Repair success | 3/3 |

## Details

| ID | Candidate Count | Selected Score | Success | Actions |
| --- | --- | --- | --- | --- |
| q002 | 2 | (1, 2) | True | Set ORDER to `c.customer_name ASC` because the column is a stable textual/date sort key. |
| q003 | 3 | (1, 3) | True | Set ORDER to `p.price DESC` because the projected numeric measure is the most likely missing ORDER target. |
| q005 | 3 | (1, 2) | True | Set ORDER to `oi.quantity DESC` because the projected numeric measure is the most likely missing ORDER target. |

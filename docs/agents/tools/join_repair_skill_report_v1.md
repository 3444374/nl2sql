# JOIN Repair Skill Report

| Metric | Result |
| --- | --- |
| Cases | 3 |
| SQL+ valid | 3/3 |
| SQL executable | 3/3 |
| Repair success | 2/3 |

## Details

| ID | Candidate Count | Selected Score | Success | Actions |
| --- | --- | --- | --- | --- |
| q019 | 3 | (1, 2, 6) | True | Normalize JOIN predicate direction using schema foreign keys.; Order amount-like output by `order_amount` descending. |
| q022 | 15 | (1, 2, 5) | True | Remove products join after replacing category-count with product-id count.; Add paid-order filter for order analysis joins.; Remove redundant identifier dimension(s) `c.customer_id`.; Count distinct product ids instead of product categories for product-type quantity. |
| q025 | 0 | (1, 6, 3) | False | No join patch improved execution feedback. |

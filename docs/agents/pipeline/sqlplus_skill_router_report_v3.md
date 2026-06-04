# SQL+ Skill Router End-to-End Report

| Metric | Result |
| --- | --- |
| Cases | 13 |
| SQL+ valid | 13/13 |
| SQL executable | 13/13 |
| Repair success | 13/13 |

## Route Summary

| Route | Cases | Success |
| --- | --- | --- |
| join -> aggregation -> projection | 1 | 1/1 |
| order | 3 | 3/3 |
| order -> aggregation | 2 | 2/2 |
| order -> projection | 1 | 1/1 |
| value | 1 | 1/1 |
| value -> aggregation -> join -> order | 1 | 1/1 |
| value -> join -> aggregation -> order -> projection | 1 | 1/1 |
| value -> join -> projection | 1 | 1/1 |
| value -> order | 2 | 2/2 |

## Details

| ID | Critic Type | Route | Success | Actions |
| --- | --- | --- | --- | --- |
| q002 | order_or_limit | order | True | order: Set ORDER to `c.customer_name ASC` because the column is a stable textual/date sort key. |
| q003 | order_or_limit | order | True | order: Set ORDER to `p.price DESC` because the projected numeric measure is the most likely missing ORDER target. |
| q004 | filter_or_value | value | True | value: Normalize month boundary to `o.order_date >= '2025-03-01'`. |
| q005 | order_or_limit | order | True | order: Set ORDER to `oi.quantity DESC` because the projected numeric measure is the most likely missing ORDER target. |
| q006 | order_or_limit | order -> projection | True | order: Set ORDER to `p.price DESC` because the projected numeric measure is the most likely missing ORDER target.; projection: Remove projection identifier(s) `p.product_id` not required by the question. |
| q013 | filter_or_value | value -> join -> aggregation -> order -> projection | True | value: No value lookup patch improved execution feedback.; join: Remove redundant identifier dimension(s) `c.customer_id`.; join: Order grouped results by aggregate alias `paid_order_count` descending.; aggregation: Normalize `COUNT(id)` to `COUNT(*)` for row-count aggregation.; order: Set ORDER to `paid_order_count DESC` because the projected numeric measure is the most likely missing ORDER target.; projection: No projection patch improved execution feedback. |
| q015 | order_or_limit | order -> aggregation | True | order: Set ORDER to `customer_count DESC` because the projected numeric measure is the most likely missing ORDER target.; aggregation: Normalize `COUNT(id)` to `COUNT(*)` for row-count aggregation. |
| q017 | filter_or_value | value -> order | True | value: Replace literal `canceled` with known value `cancelled` for `o.status`.; order: Set ORDER to `o.order_id ASC` because order id is the primary chronological/stable key for order records. |
| q019 | order_or_limit | order -> aggregation | True | order: Set ORDER to `order_amount DESC` because the projected numeric measure is the most likely missing ORDER target.; aggregation: No aggregation patch improved execution feedback. |
| q021 | filter_or_value | value -> aggregation -> join -> order | True | value: No value lookup patch improved execution feedback.; aggregation: Add filtered dimension `p.category` to GROUP/AGG so the aggregate keeps its business label.; aggregation: Order grouped results by aggregate alias `total_quantity` descending.; join: No join patch improved execution feedback.; order: Set ORDER to `total_quantity DESC` because the projected numeric measure is the most likely missing ORDER target. |
| q022 | aggregation | join -> aggregation -> projection | True | join: Remove products join after replacing category-count with product-id count.; join: Add paid-order filter for order analysis joins.; join: Remove redundant identifier dimension(s) `c.customer_id`.; join: Count distinct product ids instead of product categories for product-type quantity.; aggregation: No aggregation patch improved execution feedback.; projection: No projection patch improved execution feedback. |
| q025 | filter_or_value | value -> join -> projection | True | value: No value lookup patch improved execution feedback.; join: Add missing products join for product attributes.; join: Use product name from joined products table and normalize item amount alias.; projection: No projection patch improved execution feedback. |
| q026 | filter_or_value | value -> order | True | value: Replace literal `canceled` with known value `cancelled` for `o.status`.; order: Set ORDER to `o.order_id ASC` because order id is the primary chronological/stable key for order records. |

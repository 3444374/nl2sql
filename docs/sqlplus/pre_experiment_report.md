# SQL+ 前期实验记录

## 实验目的

验证“自然语言问题 -> SQL+ 中间表示 -> 标准 SQL -> SQLite 执行”的闭环是否可行，并统计 SQL+ 子集对常见查询操作的覆盖情况。

## 数据准备

- 数据库场景：企业订单分析，包含 customers、orders、order_items、products 4 张表。
- 查询样例：30 条自然语言、标准 SQL、SQL+ 三元组。
- 查询类型：单表查询、多表 JOIN、过滤、分组聚合、HAVING、排序、Top-K。

## 覆盖统计

| 维度 | 统计 |
| --- | --- |
| 难度分布 | hard: 6, medium: 18, simple: 6 |
| 操作覆盖 | agg: 20, group: 20, having: 6, join: 21, limit: 3, order: 26, select: 10, where: 24 |

## 实验结果

- SQL+ 语法通过率：30/30
- 转换 SQL 可执行率：30/30
- 与标准 SQL 执行结果一致率：30/30

## 样例明细

| ID | 难度 | 操作标签 | SQL+有效 | SQL有效 | 结果一致 | 结果行数 |
| --- | --- | --- | --- | --- | --- | --- |
| q001 | simple | select, where | 是 | 是 | 是 | 2 |
| q002 | simple | select, where | 是 | 是 | 是 | 2 |
| q003 | simple | select, where, order | 是 | 是 | 是 | 3 |
| q004 | simple | select, where, order | 是 | 是 | 是 | 4 |
| q005 | simple | select, where | 是 | 是 | 是 | 2 |
| q006 | simple | select, order, limit | 是 | 是 | 是 | 2 |
| q007 | medium | join, where, group, agg, order | 是 | 是 | 是 | 2 |
| q008 | medium | join, where, group, agg, order, limit | 是 | 是 | 是 | 3 |
| q009 | medium | join, where, group, agg, having, order | 是 | 是 | 是 | 2 |
| q010 | medium | join, where, select, order | 是 | 是 | 是 | 2 |
| q011 | medium | join, where, group, agg, order | 是 | 是 | 是 | 2 |
| q012 | hard | join, where, group, agg, having, order | 是 | 是 | 是 | 2 |
| q013 | medium | join, where, group, agg, order | 是 | 是 | 是 | 5 |
| q014 | medium | group, agg, order | 是 | 是 | 是 | 2 |
| q015 | medium | group, agg, order | 是 | 是 | 是 | 3 |
| q016 | medium | join, where, group, agg, order | 是 | 是 | 是 | 5 |
| q017 | medium | join, where, select, order | 是 | 是 | 是 | 1 |
| q018 | medium | group, agg, order | 是 | 是 | 是 | 3 |
| q019 | medium | join, where, group, agg, order | 是 | 是 | 是 | 6 |
| q020 | hard | join, where, group, agg, having, order | 是 | 是 | 是 | 3 |
| q021 | medium | join, where, group, agg | 是 | 是 | 是 | 1 |
| q022 | hard | join, where, group, agg, order | 是 | 是 | 是 | 5 |
| q023 | hard | join, where, group, agg, having, order | 是 | 是 | 是 | 2 |
| q024 | medium | join, where, group, agg, order | 是 | 是 | 是 | 3 |
| q025 | medium | join, where, select, order, limit | 是 | 是 | 是 | 3 |
| q026 | medium | join, where, select, order | 是 | 是 | 是 | 6 |
| q027 | medium | join, group, agg, order | 是 | 是 | 是 | 5 |
| q028 | medium | join, group, agg, order | 是 | 是 | 是 | 2 |
| q029 | hard | join, where, group, agg, having, order | 是 | 是 | 是 | 2 |
| q030 | hard | join, where, group, agg, having, order | 是 | 是 | 是 | 2 |

## 代表样例

自然语言问题：找出总消费超过10000元的客户及其消费金额。

SQL+：

```sql
FROM customers c
| JOIN orders o ON c.customer_id = o.customer_id
| JOIN order_items oi ON o.order_id = oi.order_id
| WHERE o.status = 'paid'
| GROUP c.customer_name
| AGG c.customer_name, SUM(oi.quantity * oi.unit_price) AS total_sales
| HAVING SUM(oi.quantity * oi.unit_price) > 10000
| ORDER total_sales DESC
```

转换后的 SQL：

```sql
SELECT c.customer_name, SUM(oi.quantity * oi.unit_price) AS total_sales
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE (o.status = 'paid')
GROUP BY c.customer_name
HAVING SUM(oi.quantity * oi.unit_price) > 10000
ORDER BY total_sales DESC;
```

## 可用于开题的结论

1. SQL+ 可以把复杂查询拆成线性步骤，便于展示 schema linking、查询规划和局部修正位置。
2. 扩充后的样例覆盖单表查询、多表 JOIN、过滤、聚合、HAVING、排序和 Top-K，能够支撑开题阶段的可行性论证。
3. 规则转换器可以把 SQL+ 子集稳定转换为可执行 SQL，说明 SQL+ 可作为自然语言数据库查询的中间表示。

# SQL+ 层反馈修正前期实验

## 实验目的

构造字段名、表名和 JOIN 键错误类 SQL+ 查询，验证执行错误可以映射回 SQL+ 局部步骤，并通过局部修正恢复为可执行查询。

## 错误覆盖

- 错误样例数量：15
- 错误类型分布：join_key: 3, schema_column: 10, table_name: 2

## 实验结果

- 初始失败样例：15/15
- 修正后可执行样例：15/15
- 修正成功率：15/15

## 修正明细

| ID | 错误类型 | 初始可执行 | 修正动作 | 修正后可执行 | 初始错误摘要 |
| --- | --- | --- | --- | --- | --- |
| r001 | schema_column | 否 | c.area -> c.city | 是 | no such column: c.area |
| r002 | schema_column | 否 | o.state -> o.status | 是 | no such column: o.state |
| r003 | schema_column | 否 | p.cat -> p.category | 是 | no such column: p.cat |
| r004 | schema_column | 否 | c.client_name -> c.customer_name | 是 | no such column: c.client_name |
| r005 | schema_column | 否 | p.name -> p.product_name | 是 | no such column: p.name |
| r006 | schema_column | 否 | o.order_time -> o.order_date | 是 | no such column: o.order_time |
| r007 | schema_column | 否 | c.rank -> c.level | 是 | no such column: c.rank |
| r008 | schema_column | 否 | p.type -> p.category | 是 | no such column: p.type |
| r009 | schema_column | 否 | oi.unit_cost -> oi.unit_price | 是 | no such column: oi.unit_cost |
| r010 | join_key | 否 | c.id -> c.customer_id | 是 | no such column: c.id |
| r011 | join_key | 否 | o.id -> o.order_id | 是 | no such column: o.id |
| r012 | join_key | 否 | oi.product -> oi.product_id | 是 | no such column: oi.product |
| r013 | table_name | 否 | clients -> customers | 是 | no such table: clients |
| r014 | table_name | 否 | FROM product p -> FROM products p | 是 | no such table: product |
| r015 | schema_column | 否 | o.amount -> o.order_id | 是 | no such column: o.amount |

## 可用于开题的结论

1. 字段名、表名和 JOIN 键错误等执行反馈能够定位到 SQL+ 的局部步骤，适合作为 Refiner Agent 的输入。
2. SQL+ 层局部修正可以避免整条 SQL 重生成，符合本课题“可解释、可修复”的研究定位。
3. 后续可以把规则修正替换为 Schema Agent 与 Refiner Agent 协作修正，并继续加入类型、函数和语义异常。

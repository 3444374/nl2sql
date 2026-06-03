# 开题前期实验计划

## 当前可展示内容

本目录已经准备一个最小可复现实验，用于证明 SQL+ 中间表示的可执行闭环：

1. `data/schema.sql`：企业订单分析数据库，包含 4 张表和样例数据。
2. `data/sqlplus_cases.jsonl`：自然语言问题、标准 SQL、SQL+ 三元组。
3. `src/sqlplus.py`：SQL+ 子集解析器和 SQL 转换器。
4. `scripts/sqlplus/run_experiment.py`：执行 SQL+ 转换、SQLite 验证和报告生成。

## SQL+ 子集

当前 SQL+ 以 `FROM` 开始，后续步骤使用管道形式组织：

```sql
FROM customers c
| JOIN orders o ON c.customer_id = o.customer_id
| WHERE o.status = 'paid'
| GROUP c.customer_name
| AGG c.customer_name, SUM(oi.quantity * oi.unit_price) AS total_sales
| ORDER total_sales DESC
```

已覆盖操作：

- `FROM`
- `JOIN`
- `WHERE`
- `GROUP`
- `AGG`
- `SELECT`
- `HAVING`
- `ORDER`
- `LIMIT`

## 后续扩展

1. 接入 Spider/BIRD：抽取部分 SQL 样例，人工或规则改写为 SQL+。
2. 加入单 Agent baseline：自然语言直接生成 SQL，以及自然语言生成 SQL+。
3. 加入多 Agent：Intent、Schema、Planner、SQL+ Generator、Translator、Validator/Refiner。
4. 加入反馈修正：将执行错误映射回 SQL+ 步骤，比较 SQL 层整体重生成和 SQL+ 层局部修正。


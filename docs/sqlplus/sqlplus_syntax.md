# SQL+ 语法说明

## 定位

SQL+ 是本课题为自然语言数据库查询生成设计的中间查询表示。它不试图替代标准 SQL，也不是完整数据库方言，而是把常见分析型查询拆成线性、分步、可解释的流程，再由转换器生成标准 SQL 或后续适配达梦 SQL。

核心目标：

- 降低复杂 SQL 的表达复杂度。
- 让 LLM 更容易按步骤生成查询。
- 让执行错误更容易映射回局部步骤。
- 支持从 SQL+ 到标准 SQL 的确定性转换。

## 与 GoogleSQL Pipe Syntax 的关系

本课题 SQL+ 参考了 GoogleSQL Pipe Syntax 的研究思想，尤其是“用线性管道结构组织查询步骤”的方向。

GoogleSQL Pipe Syntax 的关键启发：

- GoogleSQL Pipe Syntax 是 GoogleSQL 的扩展，支持更线性的查询结构。
- 官方文档说明 pipe syntax 可以从 `FROM` 开始，并在后续追加 pipe operator。
- Pipe operator 消费前一步输入表并输出新表，形成数据流式查询过程。
- 其支持与标准语法类似的操作，例如 `SELECT`、`WHERE`、`AGGREGATE`、`JOIN`、`ORDER BY`、`LIMIT` 等。
- 相关论文《SQL Has Problems. We Can Fix Them: Pipe Syntax In SQL》指出，管道式数据流语法可以缓解传统 SQL 在学习、使用和扩展上的问题。

本课题 SQL+ 与 GoogleSQL Pipe Syntax 的区别：

| 维度 | GoogleSQL Pipe Syntax | 本课题 SQL+ |
| --- | --- | --- |
| 定位 | GoogleSQL 数据库方言扩展 | NL2SQL 中间表示 |
| 目标 | 改善 SQL 可读性、可写性和可维护性 | 降低 LLM 生成难度并支持反馈修正 |
| 执行方式 | BigQuery 可直接执行 | 先转换为标准 SQL/达梦 SQL 再执行 |
| 语法范围 | 支持较完整 pipe operator 集合 | 先覆盖开题实验所需最小子集 |
| 修正机制 | 文档重点不在 NL2SQL 修正 | 强调错误映射到 SQL+ 局部步骤 |

参考资料：

- Google Cloud BigQuery Pipe Syntax Reference: https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/pipe-syntax
- Google Cloud BigQuery Pipe Syntax Guide: https://docs.cloud.google.com/bigquery/docs/pipe-syntax-guide
- VLDB 2024 Paper: https://vldb.org/pvldb/vol17/p4051-shute.pdf

## 基本形式

SQL+ 查询以 `FROM` 起始，后续每一步以管道符号 `|` 开头：

```sql
FROM customers c
| JOIN orders o ON c.customer_id = o.customer_id
| WHERE o.status = 'paid'
| GROUP c.customer_name
| AGG c.customer_name, COUNT(o.order_id) AS paid_orders
| ORDER paid_orders DESC
```

当前实现中，SQL+ 每一行表示一个查询步骤。转换器按步骤收集查询信息，再生成标准 SQL。

## 支持的操作

| SQL+ 操作 | 含义 | 标准 SQL 对应 |
| --- | --- | --- |
| `FROM source` | 指定起始表或表别名 | `FROM source` |
| `JOIN table ON condition` | 连接其他表 | `JOIN table ON condition` |
| `WHERE condition` | 添加过滤条件 | `WHERE condition` |
| `GROUP columns` | 指定分组字段 | `GROUP BY columns` |
| `AGG expressions` | 指定聚合输出 | `SELECT expressions` + `GROUP BY` |
| `SELECT expressions` | 指定非聚合输出 | `SELECT expressions` |
| `HAVING condition` | 添加分组后过滤 | `HAVING condition` |
| `ORDER expressions` | 排序 | `ORDER BY expressions` |
| `LIMIT n` | 限制输出行数 | `LIMIT n` |

## 转换规则

SQL+ 转标准 SQL 的当前规则：

1. `FROM` 必须存在。
2. 多个 `JOIN` 按出现顺序追加。
3. 多个 `WHERE` 用 `AND` 合并。
4. `GROUP` 转为 `GROUP BY`。
5. `AGG` 或 `SELECT` 转为最终 `SELECT` 列表。
6. `HAVING`、`ORDER`、`LIMIT` 按标准 SQL 子句顺序输出。

示例：

```sql
FROM products p
| JOIN order_items oi ON p.product_id = oi.product_id
| JOIN orders o ON oi.order_id = o.order_id
| WHERE o.status = 'paid'
| GROUP p.category
| AGG p.category, SUM(oi.quantity * oi.unit_price) AS total_sales
| ORDER total_sales DESC
```

转换为：

```sql
SELECT p.category, SUM(oi.quantity * oi.unit_price) AS total_sales
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE (o.status = 'paid')
GROUP BY p.category
ORDER BY total_sales DESC;
```

## 反馈修正定位

SQL+ 的每一步都可以作为错误定位单元：

| 错误类型 | 可能步骤 | 示例 |
| --- | --- | --- |
| 表名错误 | `FROM` / `JOIN` | `FROM clients c` |
| 字段名错误 | `WHERE` / `SELECT` / `AGG` / `ORDER` | `c.area = 'Shanghai'` |
| JOIN 键错误 | `JOIN` | `c.id = o.customer_id` |
| 聚合错误 | `AGG` / `HAVING` | `SUM(o.amount)` |
| 排序字段错误 | `ORDER` | `ORDER total_amount DESC` |

这使得反馈修正可以采用：

```text
执行错误 -> 定位 SQL+ 步骤 -> 修正局部表达 -> 转换 SQL -> 重新执行
```

## 当前限制

当前 SQL+ 子集暂不覆盖：

- CTE。
- 嵌套子查询。
- 窗口函数。
- 集合操作。
- PIVOT/UNPIVOT。
- 达梦 SQL 方言函数差异。

这些限制是开题阶段有意收敛范围，后续可以根据实验需要逐步扩展。


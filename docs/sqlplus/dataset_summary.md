# SQL+ 前期实验数据集说明

## 数据库场景

当前使用企业订单分析场景，包含 4 张表：

- `customers`：客户信息，包括客户名称、城市、等级。
- `products`：商品信息，包括商品名称、类别、标价。
- `orders`：订单主表，包括客户、订单日期、订单状态。
- `order_items`：订单明细，包括商品、数量、成交单价。

## SQL+ 查询样例

文件：`data/sqlplus_cases.jsonl`

样例数量：30 条。

每条样例包含：

- `id`：样例编号。
- `question`：自然语言问题。
- `difficulty`：复杂度标签，取值为 `simple`、`medium`、`hard`。
- `tags`：涉及的 SQL+ 操作标签。
- `gold_sql`：人工标准 SQL。
- `sqlplus`：SQL+ 中间表示。

复杂度分布：

| 难度 | 数量 |
| --- | --- |
| simple | 6 |
| medium | 18 |
| hard | 6 |

操作覆盖：

| 操作 | 数量 |
| --- | --- |
| where | 24 |
| join | 21 |
| group | 20 |
| agg | 20 |
| order | 26 |
| having | 6 |
| limit | 3 |
| select | 10 |

## 反馈修正样例

文件：`data/repair_cases.jsonl`

样例数量：15 条。

每条样例包含：

- `id`：样例编号。
- `error_type`：错误类型。
- `question`：自然语言问题。
- `broken_sqlplus`：含错误的 SQL+。
- `expected_fix`：期望修正动作。

错误类型分布：

| 错误类型 | 数量 |
| --- | --- |
| schema_column | 10 |
| join_key | 3 |
| table_name | 2 |

## 当前验证结果

SQL+ 转换实验：

- SQL+ 语法通过率：30/30。
- 转换 SQL 可执行率：30/30。
- 与标准 SQL 执行结果一致率：30/30。

反馈修正实验：

- 初始失败样例：15/15。
- 修正后可执行样例：15/15。
- 修正成功率：15/15。

## 开题使用方式

该数据集适合放在开题报告的“前期实验基础”部分，用于说明：

1. 已经构造了面向 SQL+ 的自然语言查询样例。
2. SQL+ 子集覆盖了常见分析型查询操作。
3. SQL+ 到 SQL 的转换和执行验证已经形成最小闭环。
4. SQL+ 层反馈修正已经覆盖字段名、表名和 JOIN 键三类错误。


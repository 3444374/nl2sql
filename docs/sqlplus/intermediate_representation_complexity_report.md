# SQL+ 与中间表示表达复杂度对比实验

## 实验目的

本实验用于回答“为什么使用 SQL+”这一问题。实验比较同一批查询在 Standard SQL、SQL+、SemQL-style proxy、NatSQL-style proxy 和 Pipe-style proxy 下的表达复杂度与转换开销。SemQL-style、NatSQL-style 和 Pipe-style 均为开题阶段的简化 proxy，不代表完整复现原论文或 GoogleSQL 实现。

## 实验设置

- 数据集：自建订单分析数据集，共 30 条查询。
- 输入：每条样例包含自然语言问题、gold SQL 和 gold SQL+。
- 对比表示：standard_sql、sqlplus、semql_style_proxy、natsql_style_proxy、pipe_style_proxy。
- 主要指标：token_count、line_count、step_or_clause_count、nesting_depth、join_path_length、schema_item_count、alias_dependency_count、cross_clause_reference_count、parse_time_ms、conversion_time_ms。
- 详细结果：`data/ir_complexity_detail.csv`。
- 汇总结果：`data/ir_complexity_summary.csv`。

## 汇总结果

| Representation | Cases | Avg tokens | Avg lines | Avg steps/clauses | Avg nesting | Avg joins | Avg schema items | Avg alias deps | Avg cross-clause refs | Avg parse ms | Avg conversion ms | Conversion success |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| natsql_style_proxy | 30 | 31.5 | 5.4333 | 5.4333 | 0.9667 | 0.0 | 5.5 | 1.3667 | 1.6667 | 0.0032 |  | N/A |
| pipe_style_proxy | 30 | 40.8 | 6.1333 | 6.1333 | 0.6667 | 1.1667 | 5.5 | 1.3667 | 1.6667 | 0.0039 |  | N/A |
| semql_style_proxy | 30 | 50.5667 | 1.0 | 10.7333 | 3.6667 | 0.7 | 5.5 | 0.9 | 1.2 | 0.0046 |  | N/A |
| sqlplus | 30 | 35.0333 | 6.1333 | 6.1333 | 0.6667 | 1.1667 | 5.5 | 0.7 | 1.0 | 0.0034 | 0.0072 | 30/30 |
| standard_sql | 30 | 31.5333 | 5.9 | 5.9 | 0.6667 | 1.1667 | 5.5 | 2.0333 | 2.3333 | 0.0033 | 0.0 | 30/30 |

## 观察

- SQL+ 的平均 token 数为 35.0333，高于 Standard SQL 的 31.5333。这说明 SQL+ 并不是通过压缩长度获得优势，而是把查询过程显式拆成步骤。
- SQL+ 的平均行数为 6.1333，高于 Standard SQL 的 5.9，与 Pipe-style proxy 的 6.1333 接近。这符合线性步骤化表达的预期。
- SQL+ 的平均 step_or_clause_count 为 6.1333，高于 Standard SQL 的 5.9。该指标可作为后续错误定位和局部 patch 的步骤边界。
- SemQL-style proxy 的平均 nesting_depth 为 3.6667，高于 SQL+ 的 0.6667。这反映 tree-style 表示更强调语义结构，但未必天然适合步骤级修复。
- NatSQL-style proxy 的平均 token 数为 31.5，可作为后续生成成本对照。但本实验仅评估 proxy 表达复杂度，不声称完整 NatSQL 转换能力。
- SQL+ 到 SQL 的平均转换时间为 0.0072 ms，30/30 转换成功。当前样例下，SQL+ 的确定性转换开销较小。

## 对开题报告的意义

本实验支持一个更谨慎的结论：SQL+ 不一定比标准 SQL 或 NatSQL-style proxy 更短，但它提供了更明确的步骤边界和较低的确定性转换成本。后续需要在错误定位准确率、patch minimality 和修复轮数上继续验证 SQL+ 的 repairability 优势。

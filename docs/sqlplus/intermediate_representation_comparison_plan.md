# SQL+ 与中间表示对比实验设计

## 实验目的

该实验用于回答开题答辩中最核心的问题：为什么本课题选择 SQL+，而不是直接使用标准 SQL、SemQL、NatSQL 或 GoogleSQL Pipe Syntax。实验不只比较最终准确率，还比较表达复杂度、生成成本、转换效率、错误定位能力和局部修复能力。

## 对比对象

| 表示形式 | 主要来源 | 核心目标 | 本课题对比方式 | 边界说明 |
| --- | --- | --- | --- | --- |
| Standard SQL | 传统 SQL | 数据库直接执行 | Direct NL2SQL 和 SQL 层修复 baseline | 表达完整，但嵌套、别名和跨子句依赖较多 |
| SemQL-style IR | IRNet/SemQL | 隐藏 SQL 实现细节，生成语义结构 | 开题阶段先实现简化 tree-style proxy | 不声称复现完整 IRNet 系统 |
| NatSQL-style IR | NatSQL | 减少 FROM/JOIN/GROUP 等预测负担 | 实现 simplified SQL-like proxy | 不声称覆盖 NatSQL 全部规则 |
| Pipe-style query | GoogleSQL Pipe Syntax | 用线性数据流改善 SQL 阅读与维护 | 设计与 SQL+ 接近的 pipe baseline | 作为语言扩展参考，不等同 GoogleSQL 完整实现 |
| SQL+ | 本课题 | 生成、转换、诊断、局部修复统一 | 当前核心方法 | 重点评估 repairability，而不只评估生成准确率 |

## 核心假设

H1：与标准 SQL 相比，SQL+ 能减少嵌套、跨子句引用和隐式依赖，使模型更容易生成可检查的查询步骤。

H2：与 SemQL-style 和 NatSQL-style 表示相比，SQL+ 的优势不一定体现在最短 token 或最高初次生成准确率，而体现在错误定位、局部 patch 和修复轮数上。

H3：与 Pipe-style query 相比，SQL+ 更面向 NL2SQL 反馈修正任务。它不仅线性表达查询，还显式服务于 Critic、Skill Router 和 Repair Skill。

H4：SQL+ 的收益需要抵消它带来的转换成本。因此实验必须同时记录 token cost、latency、IR parse time 和 IR-to-SQL conversion time。

## 实验设计

### 实验一：表达复杂度对比

输入同一批自然语言问题和 gold SQL，分别构造 Standard SQL、SemQL-style、NatSQL-style、Pipe-style 和 SQL+ 表示。评价 token 长度、嵌套深度、子查询/CTE 数量、跨子句引用数量、join 路径长度、别名依赖数量、步骤数和 schema item 数量。

### 实验二：生成效率与成本对比

使用同一模型和同一批样例，比较不同表示作为生成目标时的表现。评价 valid representation rate、valid SQL rate、execution accuracy、prompt tokens、completion tokens、total latency 和 candidate pass rate。

### 实验三：转换与执行效率对比

对各类中间表示实现可复现的转换脚本或 proxy converter，记录 parse success rate、conversion success rate、IR parse time、conversion time、SQL executable rate 和 conversion failure type。

### 实验四：错误定位与局部修复对比

针对同一批失败查询，比较 SQL 层整体修复、SQL+ 单 Refiner、SQL+ Critic-Refiner、SQL+ Skill Router + Repair Skills 等方法。评价 error localization accuracy、router accuracy、repair success rate、average repair rounds、patch minimality、unchanged-correct-step rate、token cost 和 latency。

### 实验五：消融实验

消融设置包括去掉 SQL+、去掉多智能体、去掉 Schema/value lookup、去掉 Critic Agent、去掉 Skill Router、关闭 Executor、用 SQL 层整体重写替代 SQL+ 局部 patch。目标是判断收益来自 SQL+、Agent、工具调用还是 repair skill。

## 开题阶段可报告结果与边界

当前可以报告的事实：SQL+ conversion 在自建订单数据集上为 30/30 execution match；Direct NL2SQL baseline 为 16/30；NL2SQL+ prompt v2 为 17/30；SQL+ non-gold single Refiner 为 4/13；Direct SQL non-gold Refiner 为 6/14；SQL+ Skill Router + Repair Skills v3 在当前 13 条已知 SQL+ 失败样例上为 13/13；Spider smoke test 在 `concert_singer` 受支持 20 条子集上为 20/20。

不能报告为：完整 Spider/BIRD benchmark 成绩、生产级达梦 SQL 适配结果、或大规模真实企业场景结论。

## 实验一已完成：表达复杂度对比

产物：

- `scripts/sqlplus/run_ir_complexity_eval.py`
- `data/ir_complexity_detail.csv`
- `data/ir_complexity_summary.csv`
- `docs/sqlplus/intermediate_representation_complexity_report.md`

主要结果：

| 指标 | Standard SQL | SQL+ | SemQL-style proxy | NatSQL-style proxy | Pipe-style proxy |
| --- | ---: | ---: | ---: | ---: | ---: |
| 平均 token 数 | 31.5333 | 35.0333 | 50.5667 | 31.5 | 40.8 |
| 平均行数 | 5.9 | 6.1333 | 1.0 | 5.4333 | 6.1333 |
| 平均步骤/子句数 | 5.9 | 6.1333 | 10.7333 | 5.4333 | 6.1333 |
| 平均嵌套深度 | 0.6667 | 0.6667 | 3.6667 | 0.9667 | 0.6667 |
| 平均别名依赖数 | 2.0333 | 0.7 | 0.9 | 1.3667 | 1.3667 |
| 平均跨子句引用数 | 2.3333 | 1.0 | 1.2 | 1.6667 | 1.6667 |
| 转换成功 | 30/30 | 30/30 | N/A | N/A | N/A |

阶段性解释：

SQL+ 当前不比 Standard SQL 更短，因此后续报告中不能把 SQL+ 的优势写成“压缩长度”。更合理的表述是：SQL+ 用略高的步骤显式化成本，换取更清晰的查询阶段边界、更低的别名/跨子句依赖，以及可确定转换为 SQL 的中间表示。这一结论需要继续通过错误定位准确率、patch minimality、修复轮数、token cost 和 latency 实验验证。

## 实验二已完成：生成成本与执行效果对比

已生成以下产物：

- `scripts/sqlplus/run_ir_generation_cost_eval.py`
- `outputs/ir_generation/ir_generation_outputs.jsonl`
- `data/ir_generation_cost_detail.csv`
- `data/ir_generation_cost_summary.csv`
- `docs/sqlplus/ir_generation_cost_report.md`

主要结果：

| 方法 | 表示有效 | SQL 可执行 | 执行一致 | 平均输入 token | 平均输出 token | 平均总 token | 平均延迟 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct SQL | 30/30 | 30/30 | 12/30 | 287.6 | 311.5667 | 599.1667 | 6.5851s |
| SQL+ | 28/30 | 28/30 | 14/30 | 319.1333 | 493.9 | 813.0333 | 9.2197s |
| NatSQL-style proxy | 30/30 | 30/30 | 13/30 | 319.1333 | 421.6333 | 740.7667 | 6.2802s |
| SemQL-style proxy | 30/30 | 25/30 | 12/30 | 343.1333 | 685.8333 | 1028.9667 | 9.9684s |

阶段性判断：

SQL+ 在本实验中的执行一致率为 14/30，略高于 NatSQL-style proxy 的 13/30 和 Direct SQL、SemQL-style proxy 的 12/30，但差距很小，不能作为显著准确率优势来表述。同时，SQL+ 的平均总 token 和平均延迟高于 Direct SQL 与 NatSQL-style proxy，说明 SQL+ 的步骤化表示存在生成成本。后续实验应重点验证 SQL+ 是否能通过更高的错误定位准确率、更小的 patch 范围、更少的修复轮数和更低的修复阶段成本来抵消生成阶段的额外开销。

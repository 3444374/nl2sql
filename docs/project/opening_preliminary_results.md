# 开题初步实验结果总结

课题方向：面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究

## 1. 当前实验目的

开题阶段的实验目标不是追求完整 benchmark 跑分，而是验证三个核心问题：

1. SQL+ 能否作为自然语言到 SQL 的中间查询表示。
2. SQL+ 是否能稳定转换为可执行 SQL。
3. 在生成错误后，反馈修正是否可以在 SQL+ 层或 SQL 层完成，并为多智能体方法提供实验依据。

因此，当前实验围绕一个小型企业订单数据库构建，包括客户、商品、订单和订单明细四类表，覆盖单表查询、多表连接、过滤、排序、聚合、分组、Top-K 和部分复杂统计查询。

## 2. 数据与实验环境

当前使用自建小型实验数据集，主要用于开题阶段验证方法可行性。

| 项目 | 内容 |
| --- | --- |
| 数据库 | 企业订单分析样例库 |
| 表数量 | 4 张表：customers、products、orders、order_items |
| 自然语言查询样例 | 30 条 |
| SQL+ 标准样例 | 30 条 |
| 错误修正样例 | 15 条 |
| 执行环境 | SQLite 内存数据库 |
| 模型 | gpt-5-mini |
| 评估方式 | 执行生成 SQL，并与标准 SQL 执行结果比较 |

说明：gold SQL 只用于离线评估，不进入非 gold 反馈修正模型输入。

## 3. SQL+ 表达与转换实验

该实验验证 SQL+ 作为中间表示是否可解析、可转换、可执行。

| 指标 | 结果 |
| --- | --- |
| SQL+ 样例数 | 30 |
| SQL+ 语法通过 | 30/30 |
| 转换 SQL 可执行 | 30/30 |
| 与标准 SQL 执行结果一致 | 30/30 |

初步结论：

SQL+ 可以覆盖当前样例库中的常见查询结构，并能够稳定转换为标准 SQL 执行。这说明 SQL+ 不只是概念设计，而是具备原型验证基础。

## 4. SQL+ 规则修正实验

该实验构造了错误 SQL+，验证执行错误能否映射回 SQL+ 局部步骤并通过规则方式修正。

| 指标 | 结果 |
| --- | --- |
| 错误样例数 | 15 |
| 初始失败样例 | 15/15 |
| 修正后 SQL 可执行 | 15/15 |
| 修正成功 | 15/15 |

初步结论：

SQL+ 的分步表达有利于错误定位。例如字段错误、条件错误、连接错误可以映射到对应 SQL+ 步骤，为后续 Refiner Agent 做局部修正提供依据。

## 5. 单 Agent Baseline 实验

对比两种基本生成路径：

1. Direct NL2SQL：自然语言直接生成 SQL。
2. NL2SQL+：自然语言生成 SQL+，再由转换器转为 SQL。

| 方法 | 样例数 | SQL/SQL+ 有效 | SQL 可执行 | 执行结果一致 |
| --- | --- | --- | --- | --- |
| Direct NL2SQL | 30 | - | 30/30 | 16/30 |
| NL2SQL+ prompt v1 | 30 | 30/30 | 30/30 | 13/30 |
| NL2SQL+ prompt v2 | 30 | 30/30 | 30/30 | 17/30 |

说明：v2 prompt 优化了 AGG 别名、ORDER/HAVING 引用、聚合输出列等约束。

初步结论：

SQL+ prompt v2 的执行一致率略高于 Direct NL2SQL，说明 SQL+ 中间表示具有一定潜力。但在简单查询、隐含排序、值链接和聚合语义上仍存在明显错误。

## 6. SQL+ 失败诊断结果

对 SQL+ prompt v2 的 13 条失败样例进行错误分类。

| 错误类型 | 数量 |
| --- | --- |
| filter_or_value_linking | 5 |
| order_or_limit_mismatch | 3 |
| aggregation_planning | 2 |
| schema_or_join_planning | 2 |
| projection_mismatch | 1 |

初步结论：

SQL+ 生成失败主要不是语法问题，而是语义问题，包括值链接错误、排序遗漏、聚合口径错误、连接路径错误和投影列不一致。这说明后续多智能体不能只做语法修复，还需要 schema linking、语义诊断和执行反馈分析。

## 7. 反馈修正实验

反馈修正实验分为三类：

1. 诊断辅助 Refiner：输入包含 gold-derived mismatch differences，用于验证修正链路可行性。
2. SQL+ 非 gold 执行反馈 Refiner：不提供 gold 差异，只给执行反馈、schema、结果预览和粗粒度错误类型。
3. Direct SQL 非 gold 执行反馈 Refiner：作为 SQL+ 修正的对照组，直接修标准 SQL。

| 方法 | 初始失败样例 | SQL+ 有效 | SQL 可执行 | 修复成功 | 说明 |
| --- | --- | --- | --- | --- | --- |
| SQL+ 诊断辅助 Refiner | 13 | 13/13 | 13/13 | 13/13 | 使用 gold-derived differences |
| SQL+ 非 gold Refiner v2 | 13 | 13/13 | 12/13 | 4/13 | 只使用执行反馈和粗粒度诊断 |
| Direct SQL 非 gold Refiner | 14 | - | 14/14 | 6/14 | 直接修标准 SQL |
| SQL+ Skill Router + Repair Skills | 13 | 13/13 | 13/13 | 12/13 | Critic 路由到四类局部 skill |

这里的“修复成功”指：修复后的 SQL 或 SQL+ 转换 SQL 可以执行，并且执行结果与标准 SQL 的执行结果完全一致。

初步结论：

诊断辅助 Refiner 的 13/13 证明了 SQL+ 层局部修正链路是可行的。但在真实非 gold 条件下，SQL+ 单 Refiner 只有 4/13，Direct SQL 单 Refiner 为 6/14。这说明仅靠粗粒度执行反馈和单个 Refiner prompt 不足以稳定完成复杂修复。进一步引入 Skill Router 后，在同样 13 条 SQL+ 失败样例上达到 12/13，说明“Critic Agent 错误定位 + Skill Router 路由 + 局部 repair skill + 执行验证”比纯 prompt 修复更稳定。

## 8. 当前实验对课题的支撑

当前实验可以支撑开题报告中的三个判断。

### 8.1 SQL+ 作为中间表示具备可行性

SQL+ 到 SQL 的转换实验达到 30/30，说明 SQL+ 能够覆盖当前常见查询类型，并能稳定执行。

### 8.2 SQL+ 层反馈修正具备可行性

规则修正实验 15/15，诊断辅助 Refiner 13/13，说明如果错误能够被定位到 SQL+ 步骤，SQL+ 层局部修正是可行的。

### 8.3 多智能体是必要的

非 gold 条件下，SQL+ Refiner 只有 4/13，Direct SQL Refiner 为 6/14。该结果说明单一 Refiner prompt 难以完成真实语义修正，需要引入 Schema Agent、Critic Agent 和 Planner Agent，将 schema linking、错误诊断和局部修正拆开处理。

### 8.4 Tool/Skill 增强是必要补充

进一步的分治实验表明，value-linking-only prompt Refiner 在 3 条样例上达到 3/3。将该类错误改为 value lookup tool + repair skill 后，同样达到 SQL+ 有效 3/3、SQL 可执行 3/3、修复成功 3/3，并且修复过程能够给出候选值替换、日期边界归一化和执行验证记录。ORDER repair skill 在 3 条 ORDER-only 样例上也达到 SQL+ 有效 3/3、SQL 可执行 3/3、修复成功 3/3，高于此前 prompt-only ORDER Refiner 的 2/3。aggregation repair skill 在 3 条聚合样例上达到 SQL+ 有效 3/3、SQL 可执行 3/3、修复成功 3/3，覆盖冗余 id 分组、COUNT 口径、缺 GROUP 维度、AGG 别名和 ORDER 聚合别名引用。join repair skill 在 3 条 join 相关样例上达到 SQL+ 有效 3/3、SQL 可执行 3/3、修复成功 3/3，覆盖 JOIN 方向规范化、冗余 JOIN 删除、缺失 JOIN 补全、缺少 paid 过滤和 join 影响的投影/聚合修复。

这说明多智能体系统不应只是多个 prompt 串联，而应为不同 Agent 配置工具能力。例如 Schema Agent 需要检索表结构、字段说明和候选字段值；Critic Agent 需要 SQL+ parser、SQL executor 和结果预览；Skill Router 需要根据错误类型选择 value-linking、ORDER、aggregation、join 等 repair skill；Refiner/Executor 需要执行候选 patch 并选择可执行结果。

## 9. 当前不足

1. 当前数据集规模较小，主要用于开题阶段可行性验证。
2. 公开 benchmark 如 Spider、BIRD 还未接入，后续需要选取小规模子集适配。
3. SQL+ 语法子集仍较小，暂不支持 LEFT JOIN、子查询、窗口函数等复杂结构。
4. 非 gold 反馈修正仍依赖粗粒度错误类型，错误定位能力不足。
5. 当前多智能体还处于 Refiner 阶段，Schema Agent、Critic Agent、Planner Agent 尚未完整实现。

## 10. 下一步计划

开题前建议继续做三件事：

1. 实现工具增强 Schema Agent：输出相关表、字段、join 路径和候选数据库值，优先服务 value-linking 与 join 错误。
2. 实现工具增强 Critic Agent：根据 SQL+ parser、执行反馈、结果预览和 schema 输出结构化错误定位，但不泄露 gold answer。
3. 补充 projection repair skill：当前 Skill Router 已达到 12/13，唯一失败样例是 projection mismatch，需要处理结果列多/少的问题。

## 11. 开题报告中可直接使用的表述

当前初步实验表明，SQL+ 作为自然语言数据库查询生成的中间表示具有可执行性和可转换性。在自建企业订单样例库上，30 条 SQL+ 查询均可成功转换为 SQL 并与标准 SQL 执行结果一致。进一步的错误修正实验表明，SQL+ 的分步表达有助于将错误映射到局部查询步骤，在规则修正和诊断辅助 Refiner 条件下均能实现较高修复成功率。

同时，非 gold 执行反馈实验显示，仅依靠单个 Refiner Agent 和粗粒度执行反馈时，SQL+ 层修复成功率为 4/13，Direct SQL 层修复成功率为 6/14，说明真实场景下的反馈修正仍然具有挑战。进一步引入 Critic Agent、Skill Router 和四类局部 repair skill 后，端到端修复成功率提升到 12/13。该结果表明，本课题后续应构建由 Schema Agent、Critic Agent、Skill Router、Repair Skill 和 Executor 组成的多智能体协作框架，将自然语言理解、schema linking、错误诊断、工具检索、错误类型路由和 SQL+ 层局部修正分阶段完成。

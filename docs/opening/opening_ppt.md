# 开题汇报 PPT 稿

> 题目：面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究
>
> 使用方式：本文件按 PPT 页组织，可直接复制到 PowerPoint / WPS；每一页包含标题、要点和讲稿提示。

---

## 第 1 页：题目页

**面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究**

- 研究方向：达梦 SQL+ / Text-to-SQL / 多智能体 / 反馈修正
- 汇报人：待填写
- 专业与导师：待填写
- 时间：待填写

讲稿提示：本课题不是单纯做一个 NL2SQL 工程 Demo，而是研究如何通过 SQL+ 中间表示和多智能体反馈修正提高自然语言数据库查询的成功率和可修复性。

---

## 第 2 页：研究背景

- 企业数据分析需求增长，非专业用户希望用自然语言查询数据库。
- Text-to-SQL 旨在将自然语言问题转化为可执行 SQL，降低数据库使用门槛。
- 大语言模型提升了 SQL 生成能力，但真实数据库场景仍然困难。
- 复杂 schema、多表 join、聚合、排序、方言差异和业务语义仍是主要挑战。

讲稿提示：自然语言数据库查询是数据库智能化的重要方向，但真实场景不能只依赖一次性自然语言到 SQL 的直接生成。

---

## 第 3 页：现有 Text-to-SQL 面临的问题

- 标准 SQL 语法复杂，嵌套、join、group by、having 等结构容易出错。
- 自然语言查询意图通常是逐步表达，而 SQL 书写顺序不完全符合构造过程。
- LLM 生成 SQL 常见错误：字段选错、表连接错误、过滤值错误、聚合口径错误、排序遗漏。
- 直接整体重生成 SQL 缺少局部定位和可解释修复能力。

讲稿提示：问题不仅是模型不够强，也和 SQL 表达方式、错误定位方式有关。

---

## 第 4 页：SQL+ 的研究动机

- 借鉴 GoogleSQL Pipe Syntax 思想：通过管道式表达使 SQL 更线性。
- SQL+ 不替代标准 SQL，而作为自然语言生成和反馈修正的中间表示。
- 目标：降低复杂查询表达难度，提高可读性、可解释性和局部修复能力。

示例：

```text
FROM orders o
| JOIN order_items oi ON o.order_id = oi.order_id
| WHERE o.status = 'paid'
| GROUP o.order_id
| AGG o.order_id, SUM(oi.quantity * oi.unit_price) AS order_amount
| ORDER order_amount DESC
```

讲稿提示：SQL+ 的关键价值在于把复杂 SQL 拆成可检查的步骤。

---

## 第 5 页：国内外研究现状

- 传统 Text-to-SQL：语义解析、Seq2Seq、schema linking、语法约束解码。
- LLM-based Text-to-SQL：prompt engineering、few-shot、chain-of-thought、RAG、自修正。
- 代表工作：DAIL-SQL、DIN-SQL、MAC-SQL、CHASE-SQL、SQLCritic。
- Benchmark 从 Spider 发展到 BIRD、Spider 2.0，更关注真实企业环境和复杂 workflow。
- SQL 扩展方向：GoogleSQL Pipe Syntax 证明线性查询表达具有研究和产品价值。

讲稿提示：本课题处在 SQL 扩展、多智能体 Text-to-SQL、执行反馈修正的交叉点。

---

## 第 6 页：研究问题

1. SQL+ 如何设计成适合大模型生成的中间查询表示？
2. 如何构建面向 SQL+ 的多智能体查询生成和修正框架？
3. 如何将执行反馈映射到 SQL+ 局部步骤？
4. 如何按错误类型调用不同 repair skill 进行局部修复？
5. SQL+ + 多智能体 + 反馈修正是否优于直接生成 SQL 或单 Agent 修复？

讲稿提示：研究问题从表达设计、系统框架、反馈定位和实验验证四个层面展开。

---

## 第 7 页：总体技术路线

```text
自然语言问题
  -> SQL+ 初始生成
  -> SQL+ 转 SQL
  -> 数据库执行
  -> Critic Agent 错误诊断
  -> Skill Router 错误类型路由
  -> Repair Skill 局部修复
  -> Executor 执行验证
  -> 最终 SQL / 查询结果 / 修复解释
```

关键组件：

- SQL+ Parser / Translator
- Schema Agent
- Critic Agent
- Skill Router
- Repair Skills
- Executor

讲稿提示：框架强调闭环，不是单向生成。

---

## 第 8 页：SQL+ 语法设计

当前 SQL+ 最小子集：

| 步骤 | 作用 |
| --- | --- |
| FROM | 指定数据源 |
| JOIN | 指定连接路径 |
| WHERE | 过滤条件 |
| GROUP | 分组维度 |
| AGG | 聚合输出 |
| HAVING | 聚合后过滤 |
| SELECT | 最终投影 |
| ORDER | 排序 |
| LIMIT | 结果限制 |

设计原则：

- 线性数据流
- 中间步骤可解释
- 局部可修复
- 可转换为标准 SQL / 达梦 SQL

---

## 第 9 页：多智能体设计

| Agent / 模块 | 作用 |
| --- | --- |
| Intent Agent | 识别查询目标、条件、聚合需求 |
| Schema Agent | 选择表、字段、join 路径、候选字段值 |
| SQL+ Generator | 生成 SQL+ 查询 |
| Translator | SQL+ 转 SQL |
| Critic Agent | 根据执行反馈定位错误 |
| Skill Router | 根据错误类型选择 repair skill |
| Repair Skill | 局部修复 SQL+ |
| Executor | 执行和验证结果 |

讲稿提示：多智能体不是形式上多个 prompt，而是明确分工，并结合工具执行。

---

## 第 10 页：错误类型与 Repair Skill

当前错误类型：

- value-linking：字段值拼写、日期边界、状态值不匹配。
- ORDER/LIMIT：排序遗漏、排序字段错误、排序方向错误。
- aggregation：GROUP 维度、COUNT 口径、AGG 别名、ORDER/HAVING 引用。
- join：JOIN 路径、冗余 JOIN、缺失 JOIN、paid 过滤、连接方向。
- projection：结果列多、少或列顺序错误。

已完成 repair skill：

- value-linking repair skill
- ORDER repair skill
- aggregation repair skill
- join repair skill

待补充：projection repair skill。

---

## 第 11 页：实验数据与环境

| 项目 | 内容 |
| --- | --- |
| 数据库 | 企业订单分析样例库 |
| 表数量 | 4 张表 |
| 表结构 | customers、products、orders、order_items |
| 自然语言查询样例 | 30 条 |
| SQL+ 标准样例 | 30 条 |
| 错误修正样例 | 15 条 |
| 执行环境 | SQLite 内存数据库 |
| 模型 | gpt-5-mini |
| 评估方式 | 与标准 SQL 执行结果比较 |

讲稿提示：当前实验是开题阶段可行性验证，后续会接入 Spider/BIRD 子集和达梦场景。

---

## 第 12 页：SQL+ 转换实验结果

| 指标 | 结果 |
| --- | --- |
| SQL+ 样例数 | 30 |
| SQL+ 语法通过 | 30/30 |
| 转换 SQL 可执行 | 30/30 |
| 与标准 SQL 执行结果一致 | 30/30 |

结论：

- SQL+ 不是概念设计，已经实现 parser 和 SQL 转换器。
- 当前 SQL+ 能覆盖常见查询结构。
- 具备继续作为中间表示研究的基础。

---

## 第 13 页：Baseline 与失败分析

| 方法 | 样例数 | SQL/SQL+ 有效 | SQL 可执行 | 执行一致 |
| --- | --- | --- | --- | --- |
| Direct NL2SQL | 30 | - | 30/30 | 16/30 |
| NL2SQL+ prompt v1 | 30 | 30/30 | 30/30 | 13/30 |
| NL2SQL+ prompt v2 | 30 | 30/30 | 30/30 | 17/30 |

SQL+ prompt v2 失败类型：

| 错误类型 | 数量 |
| --- | --- |
| filter/value-linking | 5 |
| ORDER/LIMIT | 3 |
| aggregation planning | 2 |
| schema/join planning | 2 |
| projection mismatch | 1 |

结论：主要错误是语义错误，不是语法错误。

---

## 第 14 页：反馈修正实验结果

| 方法 | 失败样例 | SQL+ 有效 | SQL 可执行 | 修复成功 |
| --- | --- | --- | --- | --- |
| SQL+ 非 gold Refiner v2 | 13 | 13/13 | 12/13 | 4/13 |
| Direct SQL 非 gold Refiner | 14 | - | 14/14 | 6/14 |
| SQL+ Schema-Critic-Refiner 初版 | 13 | 13/13 | 13/13 | 3/13 |
| SQL+ Step-wise Critic-Refiner | 13 | 13/13 | 12/13 | 3/13 |
| SQL+ Skill Router + Repair Skills | 13 | 13/13 | 13/13 | 12/13 |

结论：

- 单 Refiner prompt 不稳定。
- 简单串联多个 Agent 也不一定提升。
- `Critic Agent -> Skill Router -> Repair Skill -> Executor` 明显提升修复成功率。

---

## 第 15 页：分治 Repair Skill 实验

| Repair Skill | 样例数 | 修复成功 |
| --- | --- | --- |
| value-linking repair skill | 3 | 3/3 |
| ORDER repair skill | 3 | 3/3 |
| aggregation repair skill | 3 | 3/3 |
| join repair skill | 3 | 3/3 |

说明：

- value-linking：修复 `canceled` -> `cancelled`、日期边界。
- ORDER：修复排序字段和排序方向。
- aggregation：修复 GROUP、COUNT、AGG 别名和 ORDER 引用。
- join：修复 JOIN 路径、冗余 JOIN、缺失 JOIN 和 paid 过滤。

---

## 第 16 页：Spider 小规模 Benchmark Smoke Test

实验目的：

- 验证 SQL+ 表达与转换链路能否迁移到公开 Text-to-SQL benchmark。
- 不做完整排行榜跑分，只做开题阶段可行性验证。

| 指标 | 结果 |
| --- | --- |
| 数据集 | Spider dev 子集 |
| 数据库 | concert_singer |
| 样例数 | 20 |
| 覆盖结构 | count、select、where、order、limit、group、aggregation、simple join |
| SQL+ 有效 | 20/20 |
| SQL 可执行 | 20/20 |
| 执行一致 | 20/20 |

结论：

- 当前 SQL+ 子集在 Spider 简单/中等查询结构上具备初步迁移可行性。
- 该结果不是完整 Spider benchmark 跑分，后续需扩展到更多数据库和复杂 SQL 结构。

---

## 第 17 页：预期创新点

创新点一：面向大模型生成友好的 SQL+ 中间查询表示

- 线性、分步、可解释。
- 降低复杂 SQL 生成与修复难度。

创新点二：面向 SQL+ 的多智能体查询生成与反馈修正框架

- Schema Agent、Critic Agent、Skill Router、Repair Skill、Executor 协同工作。

创新点三：基于执行反馈的 SQL+ 层局部修正机制

- 将错误映射到 SQL+ 局部步骤。
- 按错误类型调用 repair skill。
- 候选 patch 通过执行验证选择。

---

## 第 18 页：研究计划

| 阶段 | 内容 |
| --- | --- |
| 阶段一 | 完善 SQL+ 语法、parser、converter |
| 阶段二 | 完善 Schema Agent 和 Critic Agent |
| 阶段三 | 补充 projection repair skill，完善 Skill Router |
| 阶段四 | 接入 Spider/BIRD 小规模子集 |
| 阶段五 | 适配达梦 SQL 方言并完成实验评估 |
| 阶段六 | 完成论文撰写和系统整理 |

---

## 第 19 页：总结

本课题研究一种面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法。

当前初步实验说明：

- SQL+ 表达与转换链路可行：30/30。
- SQL+ 初始生成略优于 Direct NL2SQL：17/30 vs 16/30。
- 单 Refiner 和简单多 Agent 串联不足：4/13、3/13。
- 引入 Skill Router 和 repair skill 后明显提升：12/13。
- Spider 小规模公开子集 smoke test：20/20。

结论：

SQL+ 中间表示 + 多智能体错误诊断 + Skill Router + 局部修复，是一个具有研究价值和实验可行性的方向。

---

## 第 20 页：参考文献

1. SQL Has Problems. We Can Fix Them: Pipe Syntax In SQL. Google Research / VLDB.
2. GoogleSQL Pipe Query Syntax Guide. Google Cloud BigQuery Documentation.
3. MAC-SQL: A Multi-Agent Collaborative Framework for Text-to-SQL. arXiv:2312.11242.
4. DAIL-SQL: Text-to-SQL Empowered by Large Language Models. arXiv:2308.15363.
5. DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction. arXiv:2304.11015.
6. Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows. arXiv:2411.07763.
7. BIRD: A Big Bench for Large-Scale Database Grounded Text-to-SQL Evaluation.
8. SQLCritic: Correcting Text-to-SQL Generation via Clause-wise Critic.

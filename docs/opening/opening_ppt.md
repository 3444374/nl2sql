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

- 传统 Text-to-SQL：Seq2SQL、RAT-SQL、PICARD、RESDSQL 等工作关注 schema linking、结构化解码和可执行性约束。
- 中间表示路线：SemQL 和 NatSQL 说明标准 SQL 不是唯一生成目标，但主要服务于初次生成准确率。
- 大模型路线：DAIL-SQL、DIN-SQL、CHESS、CHASE-SQL、ReFoRCE、XiYan-SQL 等引入样例选择、任务分解、多候选生成、列探索和自修正。
- Agentic NL2SQL：MAC-SQL、Tool-Assisted Agent、LEVER、SQLCritic 等工作说明执行反馈和多角色协作有价值。
- 现有不足：多数方法仍在标准 SQL 层做候选选择或整体修复，缺少面向中间步骤的错误定位、技能路由和局部 patch 评估。

讲稿提示：相关工作不要只罗列论文。这里要说明研究空缺：已有方法证明“中间表示”和“Agent”都有价值，但还没有充分回答“错误发生后如何定位到可修复步骤”。
---

## 第 6 页：研究问题

1. SQL+ 为什么有必要：与标准 SQL、SemQL、NatSQL、Pipe-style 表示相比，它在生成、转换、诊断和修复上新增了什么价值。
2. SQL+ 如何设计：怎样在简化表达、可转换、可解释和局部修复之间取得平衡。
3. 如何生成 SQL+：怎样处理 schema linking、value linking、join path、aggregation planning 和 projection。
4. 如何修复 SQL+：怎样把执行反馈和结果异常映射到 SQL+ 步骤，并路由到对应 repair skill。
5. 如何证明有效：需要比较准确率、可执行率、修复成功率、定位准确率、token cost、latency 和转换时间。

讲稿提示：研究问题要从“做系统”转成“验证机制”。SQL+ 的价值必须通过对比实验和消融实验说明。
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

| 步骤 | 作用 | 容易出错的位置 |
| --- | --- | --- |
| FROM | 指定数据源 | 主表选择错误 |
| JOIN | 指定连接路径 | 连接方向、冗余 join、缺 join |
| WHERE | 过滤条件 | 值链接、日期边界、隐含条件 |
| GROUP | 分组维度 | 维度多余或缺失 |
| AGG | 聚合输出 | COUNT/SUM 口径、别名 |
| HAVING | 聚合后过滤 | 聚合别名引用 |
| SELECT | 最终投影 | 列多、列少、顺序不一致 |
| ORDER | 排序 | 排序字段、方向、聚合别名 |
| LIMIT | 结果限制 | top-k 数量 |

研究难点：

- 语法太接近 SQL，简化价值不足。
- 语法太抽象，转换和方言适配困难。
- 必须把表达设计和后续错误定位、局部修复联系起来。

评估指标：SQL+ valid rate、SQL executable rate、execution match、覆盖查询类型、表达复杂度、错误定位可用性。
---

## 第 9 页：多智能体设计

| Agent / 模块 | 研究难点 | 可观察输出 |
| --- | --- | --- |
| Schema Agent | 表、字段、值和 join 路径选择 | 相关表列、候选值、连接路径 |
| Planner Agent | 自然语言意图到查询步骤 | SQL+ 步骤草图 |
| SQL+ Generator | 稳定生成合法 SQL+ | 初始 SQL+ |
| Translator | SQL+ 到 SQL 的确定性转换 | 可执行 SQL 或转换错误 |
| Critic Agent | 错误类型和步骤定位 | likely_error_type、疑似步骤、证据 |
| Skill Router | 选择正确 repair skill | repair skill 路由结果 |
| Repair Skill | 局部 patch 生成 | 候选 SQL+ patch |
| Executor | 执行验证和候选筛选 | 执行结果、错误、最终选择 |

讲稿提示：多智能体不是简单串 prompt。每个 Agent 都要有可检查输出，后续通过 router accuracy、error localization accuracy 和 repair success rate 评价。
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
- projection repair skill

当前重点：

- projection/SELECT 诊断稳定性
- 无报错但结果语义不匹配的诊断
- 复合错误下多个 repair skill 的调用顺序

---

## 第 11 页：实验数据、对比方法与指标

数据层次：

| 层次 | 用途 |
| --- | --- |
| 自建订单分析数据集 | 控制变量、错误类型分析、SQL+ 转换验证 |
| SQL+ 已知失败集 | 评估错误定位、Skill Router 和局部修复 |
| Spider 小规模受支持子集 | 验证公开 benchmark 初步迁移能力 |
| BIRD / 达梦样例后续子集 | 验证真实 schema、外部知识和方言差异 |

对比方法：Direct NL2SQL、NL2SQL+ single agent、SemQL-style IR、NatSQL-style IR、Pipe-style query、standard SQL multi-agent、SQL layer global repair、multi-agent NL2SQL+、SQL+ Skill Router + Repair Skills。

指标：execution accuracy、valid SQL rate、SQL+ valid rate、repair success rate、average repair rounds、error localization accuracy、router accuracy、patch minimality、schema/value/join accuracy、token cost、latency、IR parse time、IR-to-SQL conversion time。

讲稿提示：这里回应老师的意见。实验不只证明系统能跑，还要证明 SQL+ 相比其他表示是否更容易定位和修复错误。
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
| SQL+ Skill Router + Repair Skills v3 | 13 | 13/13 | 13/13 | 13/13 |

结论：

- 单 Refiner prompt 不稳定。
- 简单串联多个 Agent 也不一定提升。
- `Critic Agent -> Skill Router -> Repair Skill -> Executor` 在 13 条已知 SQL+ 失败样例上达到 13/13。
- 该结果仍是开题阶段小规模验证，后续需要扩展到复合错误和公开子集。

---

## 第 15 页：分治 Repair Skill 实验

| Repair Skill | 样例数 | 修复成功 |
| --- | --- | --- |
| value-linking repair skill | 3 | 3/3 |
| ORDER repair skill | 3 | 3/3 |
| aggregation repair skill | 3 | 3/3 |
| join repair skill | 3 | 3/3 |
| projection repair skill | 1 | 1/1 |

说明：

- value-linking：修复 `canceled` -> `cancelled`、日期边界。
- ORDER：修复排序字段和排序方向。
- aggregation：修复 GROUP、COUNT、AGG 别名和 ORDER 引用。
- join：修复 JOIN 路径、冗余 JOIN、缺失 JOIN 和 paid 过滤。
- projection：修复结果列多、少或列顺序错误，例如删除问题未要求的 `product_id`。

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

1. 面向生成和修复的 SQL+ 中间表示

SQL+ 不只是 SQL 的另一种写法，而是面向 NL2SQL 生成、SQL 转换、执行反馈诊断和局部修复共同设计的中间层。相比 SemQL/NatSQL，它更强调步骤级错误定位和 repairability；相比 Pipe Syntax，它更强调 Text-to-SQL 场景下的诊断和修复接口。

2. 面向 SQL+ 的多智能体诊断与技能路由机制

将 Critic Agent、Skill Router、Repair Skill 和 Executor 组织成反馈闭环。系统不直接整体重写 SQL，而是根据错误类型路由到 value-linking、ORDER、aggregation、join、projection 等局部技能。

3. 面向修复能力的评估体系

除 execution accuracy 外，增加 error localization accuracy、router accuracy、patch minimality、average repair rounds、token cost、latency、IR parse time 和 conversion time，用于评估 SQL+ 是否真正提高可修复性。
---

## 第 18 页：研究计划

| 阶段 | 内容 |
| --- | --- |
| 阶段一 | 完善 SQL+ 语法、parser、converter |
| 阶段二 | 完善 Schema Agent 和 Critic Agent |
| 阶段三 | 扩展无报错语义错诊断，完善复合错误路由 |
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
- 引入 Skill Router v3 和五类 repair skill 后明显提升：13/13。
- Spider 小规模公开子集 smoke test：20/20。

结论：

SQL+ 中间表示 + 多智能体错误诊断 + Skill Router + 局部修复，是一个具有研究价值和实验可行性的方向。下一步重点是把当前小规模闭环扩展到无报错语义错、复合错误和更多公开数据集样例。

---

## 第 20 页：参考文献

1. Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task.
2. RAT-SQL: Relation-Aware Schema Encoding and Linking for Text-to-SQL Parsers.
3. PICARD: Parsing Incrementally for Constrained Auto-Regressive Decoding from Language Models.
4. RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL.
5. DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction.
6. MAC-SQL: A Multi-Agent Collaborative Framework for Text-to-SQL.
7. CHESS / CHASE-SQL: Multi-agent and multi-path Text-to-SQL reasoning.
8. LEVER: Learning to Verify Language-to-Code Generation with Execution.
9. SQL-Factory: A Multi-Agent Framework for High-Quality and Large-Scale SQL Generation.
10. BIRD / Spider 2.0: Real-world and enterprise Text-to-SQL benchmarks.
11. GoogleSQL Pipe Syntax: SQL Has Problems. We Can Fix Them.

# 研究生开题报告草稿

## 题目

面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究

## 1. 研究背景与意义

随着大语言模型和企业数据分析需求的发展，自然语言数据库查询逐渐成为数据库智能交互的重要方向。传统数据库查询依赖用户掌握 SQL，但业务人员、管理人员和普通数据分析人员通常更希望用自然语言表达查询需求，再由系统自动生成可执行查询语句。Text-to-SQL 技术的目标正是降低数据库使用门槛，使用户能够通过自然语言完成数据检索、统计分析和辅助决策。

近年来，大语言模型显著提升了自然语言理解和代码生成能力，使 Text-to-SQL 从早期的语义解析、Seq2Seq、schema linking 和语法约束解码，逐步发展到基于大模型的 prompt engineering、few-shot learning、chain-of-thought、检索增强和执行反馈修正。但是，在真实企业场景中，Text-to-SQL 仍然存在明显困难：数据库 schema 复杂、多表 join 关系多、查询常包含聚合和嵌套逻辑，不同数据库方言存在差异，并且自然语言问题经常包含业务语义和隐含约束。

传统 SQL 本身也存在表达顺序和组合复杂度问题。SQL 的书写顺序通常是 `SELECT-FROM-WHERE-GROUP BY-HAVING-ORDER BY`，但用户理解查询或构造查询时往往是从数据源、过滤条件、连接关系、分组聚合到最终输出逐步推进。GoogleSQL Pipe Syntax 的研究指出，可以通过在 SQL 中引入管道式表达，使查询按照数据流顺序逐步构造，从而提升 SQL 的可读性、可维护性和扩展性。这为本课题中的 SQL+ 扩展语法提供了重要参考。

因此，本课题不是单纯实现一个自然语言生成 SQL 的工程 Demo，而是研究一种“自然语言 -> SQL+ 中间表示 -> 可执行 SQL -> 执行反馈 -> SQL+ 层局部修正”的闭环方法。通过 SQL+ 降低复杂 SQL 的表达和修正难度，再通过多智能体完成意图理解、schema linking、错误诊断、技能路由和反馈修正，从而提升复杂查询生成的成功率、可解释性和可修复性。

本课题具有以下意义：

1. 理论意义：探索 SQL+ 作为 Text-to-SQL 中间表示的可行性，研究查询表达形式对大模型生成和反馈修正的影响。
2. 方法意义：将自然语言数据库查询生成拆解为多智能体协作流程，避免单轮直接生成 SQL 的不可控问题。
3. 应用意义：面向达梦 SQL+ 和国产数据库智能化需求，为企业数据分析、数据库自然语言交互和查询错误修复提供原型支撑。

## 2. 国内外研究现状

### 2.1 Text-to-SQL 传统方法与大模型方法

早期 Text-to-SQL 主要依赖语义解析、模板匹配、Seq2Seq、schema linking、语法约束解码等技术。其核心难点是如何将自然语言问题映射到数据库 schema，并生成符合 SQL 语法和语义的查询语句。Spider 等数据集推动了跨数据库 Text-to-SQL 的研究，使模型需要面对未知数据库 schema 和复杂 SQL 结构。

大语言模型出现后，Text-to-SQL 研究逐渐转向基于上下文学习和提示工程的方法。DAIL-SQL 系统研究了 LLM-based Text-to-SQL 中的问题表示、样例选择和样例组织方式，证明 prompt 设计对生成质量具有显著影响。DIN-SQL 将 Text-to-SQL 任务拆解为 schema linking、问题分解、SQL 生成和自修正等阶段，通过分解式上下文学习提升复杂查询生成能力。

但是，大模型方法仍然存在几个问题：一是模型可能生成语法正确但语义错误的 SQL；二是 schema linking 错误会导致表和字段选择错误；三是复杂 join、聚合、排序和隐含条件容易出错；四是执行反馈常被用于整体重生成，缺少可解释的局部修复机制。

### 2.2 Benchmark 与真实场景挑战

传统 Text-to-SQL benchmark 以 Spider 为代表，强调跨数据库、复杂 SQL 和执行正确性。近年来，研究逐渐转向更接近真实企业场景的 benchmark，例如 BIRD 和 Spider 2.0。BIRD 更关注真实数据库、外部知识和查询执行效率；Spider 2.0 则进一步强调企业级 Text-to-SQL workflow，包括复杂数据环境、多 SQL 方言、项目代码和真实业务分析流程。

这些 benchmark 说明，自然语言数据库查询已经不再是简单的“自然语言 -> SQL”单轮生成问题，而是需要理解 schema、业务知识、方言文档、执行反馈甚至数据分析流程的复杂任务。因此，构建多阶段、多智能体、可反馈修正的生成框架具有现实必要性。

### 2.3 SQL 扩展与 SQL+ 表达

SQL 是数据库查询的事实标准，但其表达形式存在一定复杂性。例如嵌套子查询、多表 join、聚合过滤、窗口函数和方言差异都会增加生成难度。GoogleSQL Pipe Syntax 的研究提出，在不抛弃 SQL 生态的前提下，通过管道式扩展使查询表达更加线性，更符合数据处理流程。

本课题中的 SQL+ 借鉴这类思想，但定位不是替代 SQL，而是作为面向自然语言生成与反馈修正的中间查询表示。其核心目标包括：

1. 用 FROM 起始、管道式步骤表达查询流程。
2. 将 WHERE、JOIN、GROUP、AGG、HAVING、ORDER、LIMIT 拆成局部步骤。
3. 使每一步具备可解释性和局部修复能力。
4. 能够转换为标准 SQL 或达梦 SQL 执行。

### 2.4 多智能体 Text-to-SQL 与反馈修正

现有多智能体 Text-to-SQL 研究表明，将任务拆分给不同 Agent 可以提升复杂问题处理能力。例如 MAC-SQL 将任务拆解为 selector、decomposer、refiner 等角色；CHASE-SQL 使用多路径候选生成和选择机制；SQLCritic 关注 clause-wise critic 和结构化反馈修正。

不过，现有方法多数仍然直接面向标准 SQL 层修复。标准 SQL 通常结构紧凑，错误定位难度较高。相比之下，SQL+ 将查询拆成线性步骤，更适合将错误映射到局部步骤。本课题的研究空间在于：不是仅仅让多个 Agent 生成 SQL，而是让 Agent 围绕 SQL+ 中间表示进行生成、诊断、路由、局部修复和执行验证。

## 3. 研究问题与研究目标

### 3.1 研究问题

本课题主要研究以下问题：

1. 如何设计一种适合大模型生成和局部修正的 SQL+ 中间查询表示？
2. 如何构建面向 SQL+ 的多智能体自然语言数据库查询生成框架？
3. 如何将执行错误、结果异常和语义偏差映射回 SQL+ 局部步骤？
4. 如何通过 Skill Router 将不同错误类型路由到不同 repair skill，实现可控修复？
5. SQL+ + 多智能体 + 反馈修正是否优于直接生成 SQL 或单 Agent 修复？

### 3.2 研究目标

本课题面向自然语言数据库查询生成任务，研究一种基于 SQL+ 扩展语法和多智能体协作的查询生成与反馈修正方法。通过设计面向大模型生成友好的 SQL+ 中间表示，构建自然语言理解、schema linking、SQL+ 生成、SQL 转换、执行验证、错误诊断、Skill Router 和局部 repair skill 组成的多智能体协作流程，提升复杂数据库查询生成的准确率、可执行率、可解释性和可修复性。最终实现原型系统，并在自建数据集、公开 Text-to-SQL 子集及达梦数据库场景下进行实验验证。

## 4. 研究内容

### 4.1 SQL+ 查询表达与转换机制

研究 SQL+ 的最小可行语法子集，包括：

- `FROM`：指定数据源。
- `JOIN`：指定连接路径。
- `WHERE`：表达过滤条件。
- `GROUP`：表达分组维度。
- `AGG`：表达聚合输出。
- `HAVING`：表达聚合后过滤。
- `SELECT`：表达最终投影。
- `ORDER`：表达排序。
- `LIMIT`：表达 Top-K 或结果限制。

当前已实现 SQL+ parser 和 SQL+ 到标准 SQL 的规则转换器，并验证其能够覆盖单表查询、多表 join、聚合、排序、Top-K 等常见查询。

### 4.2 面向 SQL+ 的多智能体生成框架

计划构建以下 Agent：

| Agent | 作用 | 输出 |
| --- | --- | --- |
| Intent Agent | 理解自然语言问题 | 查询目标、过滤条件、聚合需求 |
| Schema Agent | 选择相关表、字段、join 路径和候选字段值 | schema linking 结果 |
| SQL+ Generator Agent | 生成 SQL+ 查询 | SQL+ 表达 |
| Translator Agent | SQL+ 转换为 SQL | 可执行 SQL |
| Critic Agent | 根据执行反馈定位错误 | 错误类型、局部步骤诊断 |
| Skill Router | 按错误类型选择修复技能 | repair skill 调用计划 |
| Repair Skill / Refiner | 局部修复 SQL+ | 修正后的 SQL+ |
| Executor | 执行验证和结果比较 | 执行结果、错误信息 |

### 4.3 基于执行反馈的 SQL+ 层局部修正

错误类型初步划分为：

1. value-linking 错误：字段值拼写、日期边界、状态值不匹配。
2. ORDER/LIMIT 错误：缺少排序、排序字段或方向错误、Top-K 不稳定。
3. aggregation 错误：GROUP 维度、AGG 口径、COUNT 口径、别名、HAVING/ORDER 引用错误。
4. join 错误：JOIN 路径错误、冗余 JOIN、缺失 JOIN、连接方向不规范、缺少 paid 过滤。
5. projection 错误：结果列多、少或列顺序错误。

当前已实现四类 repair skill：value-linking、ORDER、aggregation、join。后续将补充 projection repair skill。

### 4.4 原型系统与实验评估

系统流程如下：

```text
自然语言问题
  -> SQL+ 初始生成
  -> SQL+ 转 SQL
  -> 数据库执行
  -> Critic Agent 错误诊断
  -> Skill Router 错误类型路由
  -> Repair Skill 局部候选修复
  -> Executor 执行验证
  -> 最终 SQL+ / SQL / 查询结果 / 修复解释
```

实验评估指标包括：Execution Accuracy、Valid SQL Rate、SQL+ Valid Rate、Repair Success Rate、Average Repair Rounds、Schema Linking Accuracy、复杂查询准确率、Token Cost 和 Latency。

## 5. 技术路线

本课题采用逐步推进路线：

1. 设计 SQL+ 最小语法子集，实现 parser 和 SQL 转换器。
2. 构建自建企业订单数据集，覆盖基本查询和复杂查询。
3. 设计 Direct NL2SQL 与 NL2SQL+ baseline。
4. 运行大模型 baseline，分析失败类型。
5. 构建 Critic Agent，对 SQL+ 失败样例进行结构化诊断。
6. 设计四类局部 repair skill：value-linking、ORDER、aggregation、join。
7. 实现 Skill Router，将 Critic 输出路由到 repair skill。
8. 扩展 projection repair skill，接入公开 benchmark 子集，后续适配达梦 SQL 方言。

## 6. 当前初步实验

### 6.1 数据与环境

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

### 6.2 SQL+ 转换实验

| 指标 | 结果 |
| --- | --- |
| SQL+ 样例数 | 30 |
| SQL+ 语法通过 | 30/30 |
| 转换 SQL 可执行 | 30/30 |
| 与标准 SQL 执行结果一致 | 30/30 |

结论：SQL+ 可以作为可解析、可转换、可执行的中间查询表示。

### 6.3 单 Agent Baseline

| 方法 | 样例数 | SQL/SQL+ 有效 | SQL 可执行 | 执行结果一致 |
| --- | --- | --- | --- | --- |
| Direct NL2SQL | 30 | - | 30/30 | 16/30 |
| NL2SQL+ prompt v1 | 30 | 30/30 | 30/30 | 13/30 |
| NL2SQL+ prompt v2 | 30 | 30/30 | 30/30 | 17/30 |

结论：SQL+ prompt v2 略优于 Direct NL2SQL，但仍存在语义错误，说明需要反馈修正和多智能体协作。

### 6.4 错误类型分析

SQL+ prompt v2 失败 13 条，错误分布如下：

| 错误类型 | 数量 |
| --- | --- |
| filter/value-linking | 5 |
| ORDER/LIMIT | 3 |
| aggregation planning | 2 |
| schema/join planning | 2 |
| projection mismatch | 1 |

### 6.5 反馈修正对比实验

| 方法 | 失败样例 | SQL+ 有效 | SQL 可执行 | 修复成功 |
| --- | --- | --- | --- | --- |
| SQL+ 诊断辅助 Refiner | 13 | 13/13 | 13/13 | 13/13 |
| SQL+ 非 gold Refiner v2 | 13 | 13/13 | 12/13 | 4/13 |
| Direct SQL 非 gold Refiner | 14 | - | 14/14 | 6/14 |
| SQL+ Schema-Critic-Refiner 初版 | 13 | 13/13 | 13/13 | 3/13 |
| SQL+ Step-wise Critic-Refiner | 13 | 13/13 | 12/13 | 3/13 |
| SQL+ Skill Router + Repair Skills | 13 | 13/13 | 13/13 | 12/13 |

结论：单个 Refiner prompt 和简单多 Agent 串联效果有限；引入 Critic Agent、Skill Router、局部 repair skill 和执行验证后，修复成功率明显提升。

### 6.6 Repair Skill 分治实验

| Repair Skill | 样例数 | 修复成功 |
| --- | --- | --- |
| value-linking repair skill | 3 | 3/3 |
| ORDER repair skill | 3 | 3/3 |
| aggregation repair skill | 3 | 3/3 |
| join repair skill | 3 | 3/3 |

结论：按错误类型进行分治，并通过工具检索、候选 patch 和执行验证进行局部修复，比整体重生成更稳定。

### 6.7 Spider 小规模公开 Benchmark Smoke Test

为了证明本课题不只在自建数据集上可行，当前进一步引入 Spider dev 的小规模受支持子集进行 smoke test。该实验不是完整 Spider 排行榜评测，而是开题阶段的公开 benchmark 子集迁移性验证。

| 指标 | 结果 |
| --- | --- |
| 数据集 | Spider dev 子集 |
| 数据库 | concert_singer |
| 样例数 | 20 |
| 覆盖结构 | count、select、where、order、limit、group、aggregation、simple join |
| SQL+ 有效 | 20/20 |
| SQL 可执行 | 20/20 |
| 执行结果一致 | 20/20 |

实验方式为：筛选当前 SQL+ 子集可覆盖的 Spider 查询，将 Spider gold SQL 改写为 SQL+，再由 SQL+ 转换器转回 SQL，并在 SQLite 数据库上比较执行结果。实验结果说明，当前 SQL+ 表达与转换机制在公开 benchmark 的简单和中等查询结构上具备初步迁移可行性。

需要说明的是，该结果不能等同于完整 Spider benchmark 成绩。当前 SQL+ 子集尚未覆盖复杂子查询、集合运算、复杂布尔条件、distinct、窗口函数等结构。后续需要继续扩展 SQL+ 语法，并在更多 Spider 数据库和 BIRD 子集上验证。

## 7. 预期创新点

### 7.1 面向大模型生成友好的 SQL+ 中间查询表示

设计一种线性、分步、可解释的 SQL+ 中间表示，将复杂 SQL 查询拆解为可生成、可检查、可修复的局部步骤，降低大模型直接生成标准 SQL 的难度。

### 7.2 面向 SQL+ 的多智能体查询生成与诊断框架

构建由 Schema Agent、Critic Agent、Skill Router、Repair Skill 和 Executor 组成的多智能体协作框架，将自然语言理解、schema linking、错误诊断、修复路由和执行验证拆分为多个可控阶段。

### 7.3 基于执行反馈的 SQL+ 层局部修正机制

不同于直接对最终 SQL 整体重生成，本课题将执行反馈和结果异常映射回 SQL+ 局部步骤，并通过错误类型路由调用不同 repair skill，实现更稳定、更可解释的局部修复。

## 8. 可行性分析

当前已完成 SQL+ parser、SQL+ 到 SQL 转换器、自建数据集、baseline 实验、错误诊断、四类 repair skill 和 Skill Router 端到端实验。从实验结果看：

1. SQL+ 表达与转换链路稳定，30/30 查询可执行且结果一致。
2. SQL+ 层局部修复链路可行，诊断辅助 Refiner 达到 13/13。
3. 真实非 gold 条件下，Skill Router + Repair Skills 达到 12/13，明显优于单 Refiner 的 4/13。

因此，本课题具备继续深入研究和系统实现的基础。

## 9. 后续工作计划

| 阶段 | 时间 | 内容 |
| --- | --- | --- |
| 第一阶段 | 开题后 1-2 个月 | 完善 SQL+ 语法，补充 projection repair skill |
| 第二阶段 | 第 3-4 个月 | 完善 Schema Agent、Critic Agent 和 Skill Router |
| 第三阶段 | 第 5-6 个月 | 接入 Spider/BIRD 小规模子集，构造 SQL+ 改写数据 |
| 第四阶段 | 第 7-8 个月 | 适配达梦 SQL 方言，测试 SQL+ 到达梦 SQL 的兼容性 |
| 第五阶段 | 第 9-10 个月 | 完成消融实验、论文撰写和系统整理 |

## 10. 参考文献与资料

1. SQL Has Problems. We Can Fix Them: Pipe Syntax In SQL. Google Research / VLDB. https://research.google/pubs/sql-has-problems-we-can-fix-them-pipe-syntax-in-sql/
2. GoogleSQL Pipe Query Syntax Guide. Google Cloud BigQuery Documentation. https://cloud.google.com/bigquery/docs/pipe-syntax-guide
3. MAC-SQL: A Multi-Agent Collaborative Framework for Text-to-SQL. arXiv:2312.11242. https://arxiv.org/abs/2312.11242
4. DAIL-SQL: Text-to-SQL Empowered by Large Language Models. arXiv:2308.15363. https://arxiv.org/abs/2308.15363
5. DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction. arXiv:2304.11015. https://arxiv.org/abs/2304.11015
6. Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows. arXiv:2411.07763. https://arxiv.org/abs/2411.07763
7. BIRD: A Big Bench for Large-Scale Database Grounded Text-to-SQL Evaluation. https://bird-bench.github.io/
8. SQLCritic: Correcting Text-to-SQL Generation via Clause-wise Critic. arXiv. https://arxiv.org/abs/2503.07996

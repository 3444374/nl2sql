# 研究生开题报告

## 题目

面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究

## 1. 研究背景与意义

自然语言数据库查询的目标，是让用户不用直接书写 SQL，也能完成数据检索、统计分析和辅助决策。这个方向近年来受到关注，一方面来自企业数据分析需求的增长，另一方面也来自大语言模型在自然语言理解和代码生成上的进展。对于业务人员、管理人员或普通分析人员来说，查询需求通常以自然语言表达，例如“统计上个月每个地区的销售额”或“找出消费金额最高的客户”。如果系统能够把这类需求可靠地转换成可执行查询，就能明显降低数据库使用门槛。

不过，Text-to-SQL 在真实场景中仍然不是一个已经解决的问题。大语言模型可以生成语法上看似合理的 SQL，但复杂 schema、多表 join、聚合口径、排序逻辑、字段值匹配和数据库方言差异常常导致结果错误。更关键的是，SQL 一旦生成错误，错误位置不一定容易定位。一个查询可能同时涉及 FROM、JOIN、WHERE、GROUP BY、HAVING、ORDER BY 等多个部分，最终执行失败或结果不一致时，很难直接判断应该修哪一个局部结构。

标准 SQL 的表达顺序也会增加生成和修复难度。用户理解查询时往往是从数据源开始，逐步考虑过滤、连接、分组、聚合和最终输出；而标准 SQL 的书写顺序并不完全等同于查询构造过程。GoogleSQL Pipe Syntax 的研究提出，可以用管道式表达让查询按照数据流顺序逐步展开。这类思想说明，查询表达形式本身可能影响可读性、可维护性，也可能影响大模型生成和修复的稳定性。

基于此，本课题不把目标限定为“做一个自然语言转 SQL 的 Demo”，而是研究一条更适合诊断和修复的生成路线：

```text
自然语言问题
-> SQL+ 中间表示
-> 可执行 SQL
-> 执行反馈
-> SQL+ 层局部诊断与修复
```

这里的 SQL+ 不是为了替代标准 SQL，而是作为自然语言生成与反馈修正之间的中间表示。它把复杂查询拆成线性步骤，使错误更容易映射回具体步骤；再结合多智能体的意图理解、schema linking、错误诊断、技能路由和执行验证，提升查询生成的可解释性和可修复性。

本课题的意义主要体现在三个方面。第一，从研究角度看，可以探索 SQL+ 作为 Text-to-SQL 中间表示是否有助于降低复杂 SQL 的生成和修复难度。第二，从方法角度看，可以把单轮直接生成 SQL 的过程拆成多智能体协作流程，让每个环节都有明确输入、输出和可检查结果。第三，从应用角度看，课题面向达梦 SQL+ 和国产数据库智能化需求，可为企业数据分析、自然语言数据库交互和查询错误修复提供原型基础。

## 2. 国内外研究现状

### 2.1 Text-to-SQL 方法的发展

早期 Text-to-SQL 主要依赖语义解析、模板匹配、Seq2Seq、schema linking 和语法约束解码等技术。其核心问题是把自然语言问题映射到数据库 schema，并生成满足语法和语义要求的 SQL。Spider 数据集推动了跨数据库 Text-to-SQL 研究，使模型不仅要处理单一数据库，还要面对未知 schema 和更复杂的 SQL 结构。

大语言模型出现后，Text-to-SQL 逐渐转向基于上下文学习和提示工程的方法。RESDSQL 将 schema linking 与 skeleton parsing 解耦；DIN-SQL 将任务拆解为 schema linking、问题分解、SQL 生成和自修正等阶段；一些后续工作进一步引入检索增强、执行反馈和多候选选择机制。这些方法说明，大模型生成 SQL 的效果不仅取决于模型能力，也取决于任务拆解方式、schema 信息组织方式和反馈利用方式。

但现有方法仍有不足。模型可能生成语法正确但语义错误的 SQL；schema linking 错误会导致表和字段选择错误；复杂 join、聚合、排序和隐含业务条件容易出错；执行反馈经常被用于整体重生成，而不是定位到某个局部结构进行修复。因此，仅依赖“自然语言 -> SQL”的单轮生成，很难满足复杂查询场景下的稳定性要求。

### 2.2 Benchmark 与真实场景挑战

Text-to-SQL benchmark 从 Spider 发展到 BIRD、Spider 2.0，研究重点也从单纯 SQL 生成逐渐扩展到真实企业环境。BIRD 更关注真实数据库、外部知识和执行效率；Spider 2.0 强调企业级 Text-to-SQL workflow，包括复杂数据环境、多 SQL 方言、项目代码和真实业务分析流程。

这些 benchmark 反映出一个趋势：自然语言数据库查询已经不只是单轮文本生成任务，而是需要理解 schema、业务知识、方言文档、执行反馈和数据分析流程的综合任务。对于这类任务，多阶段、多智能体和可反馈修正的系统结构具有现实必要性。

### 2.3 SQL 扩展与 SQL+ 表达

SQL 是数据库查询的事实标准，但在复杂查询中容易出现表达结构紧凑、局部关系交织和错误定位困难等问题。嵌套子查询、多表 join、聚合过滤、窗口函数和方言差异都会增加大模型生成难度。GoogleSQL Pipe Syntax 提出在不脱离 SQL 生态的基础上引入管道式表达，使查询更接近数据处理流程。

本课题中的 SQL+ 借鉴管道式表达思想，但定位更具体：它作为 Text-to-SQL 的中间查询表示，用于降低生成和修复难度。当前 SQL+ 的基本思路包括：

1. 以 FROM 作为查询起点，按照数据流逐步展开。
2. 将 JOIN、WHERE、GROUP、AGG、HAVING、SELECT、ORDER、LIMIT 拆成局部步骤。
3. 保留每一步的可解释性，便于 Critic Agent 定位错误。
4. 通过规则转换器转换为标准 SQL 或后续达梦 SQL 方言执行。

### 2.4 多智能体 Text-to-SQL 与反馈修正

多智能体 Text-to-SQL 的已有研究表明，把任务拆分给不同角色，有助于处理复杂查询。例如 MAC-SQL 将任务拆成 selector、decomposer、refiner 等角色；CHASE-SQL 采用多路径候选生成和选择；LEVER 通过执行结果学习 verifier 来筛选候选程序，为执行反馈验证提供了参考。

不过，许多方法仍主要在标准 SQL 层进行修复。标准 SQL 的结构较紧凑，一个错误可能同时影响多个子句，导致修复时需要整体重写。SQL+ 的优势在于它把查询拆成线性步骤，天然更适合“错误类型 -> 局部步骤 -> repair skill”的修复方式。本课题的研究重点也不只是让多个 Agent 串联生成 SQL，而是围绕 SQL+ 中间表示建立生成、诊断、路由、局部修复和执行验证闭环。

## 3. 研究问题与研究目标

### 3.1 研究问题

本课题主要研究以下问题：

1. 如何设计一种适合大模型生成和局部修正的 SQL+ 中间查询表示？
2. 如何构建面向 SQL+ 的多智能体自然语言数据库查询生成框架？
3. 如何将执行错误、结果异常和语义偏差映射回 SQL+ 局部步骤？
4. 如何通过 Skill Router 将不同错误类型路由到不同 repair skill？
5. SQL+、多智能体和反馈修正结合后，是否能优于直接生成 SQL 或单 Agent 修复？

### 3.2 研究目标

本课题拟设计 SQL+ 查询表达与转换机制，构建面向 SQL+ 的多智能体自然语言数据库查询生成与反馈修正框架。系统流程包括自然语言理解、schema linking、SQL+ 生成、SQL 转换、执行验证、错误诊断、Skill Router 和局部 repair skill。最终目标是在自建数据集、公开 Text-to-SQL 子集和达梦数据库场景中验证该方法的有效性，重点考察执行正确率、SQL+ 有效率、修复成功率、错误定位能力和系统可解释性。

## 4. 研究内容

### 4.1 SQL+ 查询表达与转换机制

SQL+ 的最小可行语法子集包括：

- `FROM`：指定数据源。
- `JOIN`：指定连接路径。
- `WHERE`：表达过滤条件。
- `GROUP`：表达分组维度。
- `AGG`：表达聚合输出。
- `HAVING`：表达聚合后过滤。
- `SELECT`：表达最终投影。
- `ORDER`：表达排序。
- `LIMIT`：表达 Top-K 或结果限制。

当前已经实现 SQL+ parser 和 SQL+ 到标准 SQL 的规则转换器，并在自建企业订单数据集上验证了单表查询、多表 join、聚合、排序和 Top-K 等常见结构。后续将继续扩展 projection、复杂布尔条件、子查询替代表达和达梦 SQL 方言适配。

### 4.2 面向 SQL+ 的多智能体生成框架

本课题计划构建以下模块：

| Agent / 模块 | 主要作用 | 输出 |
| --- | --- | --- |
| Intent Agent | 理解自然语言问题 | 查询目标、过滤条件、聚合需求 |
| Schema Agent | 选择相关表、字段、join 路径和候选字段值 | schema linking 结果 |
| SQL+ Generator Agent | 生成 SQL+ 查询 | SQL+ 表达 |
| Translator Agent | 将 SQL+ 转换为 SQL | 可执行 SQL |
| Critic Agent | 根据执行反馈定位错误 | 错误类型、局部步骤诊断 |
| Skill Router | 按错误类型选择修复技能 | repair skill 调用计划 |
| Repair Skill / Refiner | 局部修复 SQL+ | 修正后的 SQL+ |
| Executor | 执行和验证候选结果 | 执行结果、错误信息 |

这个框架强调“可检查的中间状态”。每个 Agent 的输出都应能被记录、比较和复现，而不是把全部任务压缩成一次生成。

### 4.3 基于执行反馈的 SQL+ 层局部修正

当前实验中将 SQL+ 生成错误初步划分为五类：

1. value-linking 错误：字段值拼写、日期边界、状态值不匹配。
2. ORDER/LIMIT 错误：缺少排序、排序字段或方向错误、Top-K 不稳定。
3. aggregation 错误：GROUP 维度、AGG 口径、COUNT 口径、别名、HAVING/ORDER 引用错误。
4. join 错误：JOIN 路径错误、冗余 JOIN、缺失 JOIN、连接方向不规范、缺少 paid 过滤。
5. projection 错误：结果列多、少或列顺序错误。

目前已经实现 value-linking、ORDER、aggregation、join 四类 repair skill。后续计划补充 projection repair skill，并进一步研究复合错误下多个 repair skill 的调用顺序。

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

评估指标包括 Execution Accuracy、Valid SQL Rate、SQL+ Valid Rate、Repair Success Rate、Average Repair Rounds、Schema Linking Accuracy、复杂查询准确率、Token Cost 和 Latency。开题阶段重点关注链路可行性和修复成功率，后续再扩大公开数据集和数据库方言适配范围。

## 5. 技术路线

本课题按照由小到大的路线推进：

1. 设计 SQL+ 最小语法子集，实现 parser 和 SQL 转换器。
2. 构建企业订单样例库，覆盖基本查询和复杂查询。
3. 设计 Direct NL2SQL 与 NL2SQL+ 两类 baseline。
4. 运行大模型 baseline，分析失败类型。
5. 构建 Critic Agent，对 SQL+ 失败样例进行结构化诊断。
6. 设计 value-linking、ORDER、aggregation、join 四类局部 repair skill。
7. 实现 Skill Router，将 Critic 输出路由到不同 repair skill。
8. 补充 projection repair skill，接入 Spider/BIRD 小规模子集，后续适配达梦 SQL 方言。

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

该实验说明，当前 SQL+ 不是停留在概念层面的表达设计，而是已经能通过 parser 和转换器形成可执行 SQL，并在自建样例库上得到一致执行结果。

### 6.3 单 Agent Baseline

| 方法 | 样例数 | SQL/SQL+ 有效 | SQL 可执行 | 执行结果一致 |
| --- | --- | --- | --- | --- |
| Direct NL2SQL | 30 | - | 30/30 | 16/30 |
| NL2SQL+ prompt v1 | 30 | 30/30 | 30/30 | 13/30 |
| NL2SQL+ prompt v2 | 30 | 30/30 | 30/30 | 17/30 |

SQL+ prompt v2 的结果略高于 Direct NL2SQL，但差距不大。这个结果也说明，仅把输出格式从 SQL 改成 SQL+ 并不足以解决问题，后续必须结合错误定位、工具调用和局部修复机制。

### 6.4 错误类型分析

SQL+ prompt v2 失败 13 条，错误分布如下：

| 错误类型 | 数量 |
| --- | --- |
| filter/value-linking | 5 |
| ORDER/LIMIT | 3 |
| aggregation planning | 2 |
| schema/join planning | 2 |
| projection mismatch | 1 |

这些失败主要是语义层面的错误，而不是 SQL+ 语法错误。这为后续基于 Critic Agent 的错误诊断和 Skill Router 修复提供了实验依据。

### 6.5 反馈修正对比实验

| 方法 | 失败样例 | SQL+ 有效 | SQL 可执行 | 修复成功 |
| --- | --- | --- | --- | --- |
| SQL+ 诊断辅助 Refiner | 13 | 13/13 | 13/13 | 13/13 |
| SQL+ 非 gold Refiner v2 | 13 | 13/13 | 12/13 | 4/13 |
| Direct SQL 非 gold Refiner | 14 | - | 14/14 | 6/14 |
| SQL+ Schema-Critic-Refiner 初版 | 13 | 13/13 | 13/13 | 3/13 |
| SQL+ Step-wise Critic-Refiner | 13 | 13/13 | 12/13 | 3/13 |
| SQL+ Skill Router + Repair Skills | 13 | 13/13 | 13/13 | 12/13 |

需要说明的是，SQL+ 诊断辅助 Refiner 使用了 gold-derived differences，只能说明“结构化反馈 -> SQL+ 局部修复 -> 执行验证”的链路可行，不能作为真实自主修复结果。更接近真实场景的是非 gold 实验。在该条件下，单 Refiner 和简单多 Agent 串联效果有限，而 Critic Agent、Skill Router、局部 repair skill 和执行验证结合后，在 13 条 SQL+ 失败样例上达到 12/13 修复成功。

### 6.6 Repair Skill 分治实验

| Repair Skill | 样例数 | 修复成功 |
| --- | --- | --- |
| value-linking repair skill | 3 | 3/3 |
| ORDER repair skill | 3 | 3/3 |
| aggregation repair skill | 3 | 3/3 |
| join repair skill | 3 | 3/3 |

分治实验说明，不同错误类型适合采用不同的局部修复策略。例如 value-linking 更依赖字段值检索和候选值验证，ORDER 更依赖排序字段和方向判断，aggregation 更依赖分组维度和聚合口径检查，join 更依赖连接路径和表关系约束。相比整体重生成，局部修复更容易控制修改范围。

### 6.7 Spider 小规模公开 Benchmark Smoke Test

为了验证 SQL+ 不只适用于自建数据集，当前进一步引入 Spider dev 的小规模受支持子集进行 smoke test。该实验不是完整 Spider benchmark 跑分，而是开题阶段的公开 benchmark 子集迁移性验证。

| 指标 | 结果 |
| --- | --- |
| 数据集 | Spider dev 子集 |
| 数据库 | concert_singer |
| 样例数 | 20 |
| 覆盖结构 | count、select、where、order、limit、group、aggregation、simple join |
| SQL+ 有效 | 20/20 |
| SQL 可执行 | 20/20 |
| 执行结果一致 | 20/20 |

实验方式为：筛选当前 SQL+ 子集可覆盖的 Spider 查询，将 Spider gold SQL 改写为 SQL+，再由 SQL+ 转换器转回 SQL，并在 SQLite 数据库上比较执行结果。结果说明，当前 SQL+ 表达与转换机制在公开 benchmark 的简单和中等查询结构上具备初步迁移可行性。

同时也需要明确，该结果不能等同于完整 Spider benchmark 成绩。当前 SQL+ 子集尚未覆盖复杂子查询、集合运算、复杂布尔条件、distinct、窗口函数等结构。后续需要继续扩展 SQL+ 语法，并在更多 Spider 数据库和 BIRD 子集上验证。

## 7. 预期创新点

### 7.1 面向大模型生成友好的 SQL+ 中间查询表示

本课题设计线性、分步、可解释的 SQL+ 中间表示，将复杂 SQL 查询拆解为可生成、可检查、可修复的局部步骤。相比直接生成标准 SQL，SQL+ 更接近查询构造过程，也更适合与执行反馈结合。

### 7.2 面向 SQL+ 的多智能体查询生成与诊断框架

本课题构建由 Schema Agent、Critic Agent、Skill Router、Repair Skill 和 Executor 组成的多智能体协作框架。各模块分别负责 schema linking、错误诊断、修复路由、局部修正和执行验证，使系统不再完全依赖单次 prompt 输出。

### 7.3 基于执行反馈的 SQL+ 层局部修正机制

本课题不直接对最终 SQL 整体重生成，而是将执行反馈和结果异常映射回 SQL+ 局部步骤，再通过错误类型路由调用不同 repair skill。该机制有助于控制修复范围，提高修复过程的可解释性。

## 8. 可行性分析

当前已经完成 SQL+ parser、SQL+ 到 SQL 转换器、自建数据集、baseline 实验、错误诊断、四类 repair skill 和 Skill Router 端到端实验。从已有结果看：

1. SQL+ 表达与转换链路稳定，30/30 查询可执行且结果一致。
2. SQL+ 层局部修复链路可行，诊断辅助 Refiner 达到 13/13。
3. 在真实非 gold 条件下，Skill Router + Repair Skills 达到 12/13，明显优于 SQL+ 单 Refiner 的 4/13。
4. Spider 小规模受支持子集的 conversion smoke test 达到 20/20，fresh e2e 生成达到 19/20，同一次 fresh 输出经 `Skill Router -> semantic repair skill` 后达到 20/20，说明当前 SQL+ 子集具备初步公开 benchmark 迁移可行性；其中 conversion smoke test 使用 gold SQL 改写得到 SQL+，不能当作端到端生成准确率。

因此，本课题已经具备继续深入研究和系统实现的基础。后续重点不是简单扩大 prompt，而是完善 projection repair skill、增强 Schema Agent 和 Critic Agent，并扩展公开数据集和达梦 SQL 方言验证。

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
3. MAC-SQL: A Multi-Agent Collaborative Framework for Text-to-SQL. COLING 2025. https://aclanthology.org/2025.coling-main.36/
4. RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL. AAAI 2023. https://ojs.aaai.org/index.php/AAAI/article/view/26535
5. DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction. NeurIPS 2023. https://proceedings.neurips.cc/paper_files/paper/2023/hash/72223cc66f63ca1aa59edaec1b3670e6-Abstract-Conference.html
6. Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows. ICLR 2025. https://openreview.net/forum?id=XmProj9cPs
7. BIRD: A Big Bench for Large-Scale Database Grounded Text-to-SQL Evaluation. https://bird-bench.github.io/
8. LEVER: Learning to Verify Language-to-Code Generation with Execution. ICML 2023. https://proceedings.mlr.press/v202/ni23b.html

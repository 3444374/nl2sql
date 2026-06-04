# 研究生开题报告

## 题目

面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究

## 1. 研究背景与意义

自然语言数据库查询想解决的问题很直接：用户不写 SQL，也能完成数据检索、统计分析和辅助决策。企业里的很多查询需求本来就是用自然语言提出的，例如“统计上个月每个地区的销售额”或“找出消费金额最高的客户”。如果系统能把这类需求稳定地转换成可执行查询，业务人员和普通分析人员就不必先掌握完整 SQL 语法才能使用数据库。

不过，Text-to-SQL 在真实场景中仍然不是一个已经解决的问题。大语言模型可以生成语法上看似合理的 SQL，但复杂 schema、多表 join、聚合口径、排序逻辑、字段值匹配和数据库方言差异常常导致结果错误。更关键的是，SQL 一旦生成错误，错误位置不一定容易定位。一个查询可能同时涉及 FROM、JOIN、WHERE、GROUP BY、HAVING、ORDER BY 等多个部分，最终执行失败或结果不一致时，很难直接判断应该修哪一个局部结构。

标准 SQL 的表达顺序也会增加生成和修复难度。用户理解查询时通常先确定数据源，再考虑过滤、连接、分组、聚合和最终输出；标准 SQL 的书写顺序并不完全等同于这个构造过程。GoogleSQL Pipe Syntax 的研究提出，可以用管道式表达让查询按照数据流顺序逐步展开。这个思路给本课题一个启发：查询表达形式本身可能影响可读性，也可能影响大模型生成和修复的稳定性。

基于这些问题，本课题不把目标限定为“做一个自然语言转 SQL 的 Demo”，而是研究一条更适合诊断和修复的生成路线：

```text
自然语言问题
-> SQL+ 中间表示
-> 可执行 SQL
-> 执行反馈
-> SQL+ 层局部诊断与修复
```

这里的 SQL+ 不替代标准 SQL，而是放在自然语言和最终 SQL 之间，作为中间查询表示。它把复杂查询拆成线性步骤，使错误更容易映射回具体步骤。多智能体部分则负责意图理解、schema linking、错误诊断、技能路由和执行验证，让修复过程不再完全依赖一次性重写。

这项工作的价值不在于再做一个 Text-to-SQL 演示系统，而在于检验一个更细的问题：当 SQL 被改写成更线性的中间表示后，大模型生成和反馈修正是否更容易控制。方法上，课题把单轮生成拆成一组可检查的中间环节；应用上，它也可以为达梦 SQL+、国产数据库智能交互和查询错误修复提供原型基础。

## 2. 国内外研究现状

### 2.1 Text-to-SQL 方法的发展

早期 Text-to-SQL 主要依赖语义解析、模板匹配、Seq2Seq、schema linking 和语法约束解码等技术。其核心问题是把自然语言问题映射到数据库 schema，并生成满足语法和语义要求的 SQL。Spider 数据集推动了跨数据库 Text-to-SQL 研究，使模型不仅要处理单一数据库，还要面对未知 schema 和更复杂的 SQL 结构。

在大模型之前，研究重点主要集中在 schema linking、结构化中间表示和约束解码。例如 RAT-SQL 通过关系感知编码建模表、列和问题之间的关系；IRNet 使用 SemQL 作为中间表示，减少直接生成复杂 SQL 的难度；NatSQL 进一步提出面向 Text-to-SQL 的通用中间表示，试图把自然语言到 SQL 的映射拆得更平滑。PICARD 则从解码阶段入手，在大语言模型生成过程中进行增量语法约束，降低无效 SQL 的比例。这些工作都说明，Text-to-SQL 的难点并不只在语言理解，也在于如何控制输出结构。

大语言模型出现后，Text-to-SQL 逐渐转向基于上下文学习、提示工程和候选选择的方法。DAIL-SQL 关注问题表示、样例选择和样例组织方式；DIN-SQL 将任务拆解为 schema linking、问题分解、SQL 生成和自修正等阶段；C3、RESDSQL 等工作分别从零样本提示、schema linking 与骨架解析解耦等角度改进生成效果。近两年的 CHESS、CHASE-SQL、XiYan-SQL 和 ReFoRCE 等系统进一步引入检索增强、多候选生成、候选排序、自修正、执行反馈和列探索。这些工作说明，大模型生成 SQL 的效果不仅取决于模型本身，也取决于 schema 信息如何组织、复杂问题如何拆解、执行反馈如何被利用。

但这些方法大多仍以标准 SQL 为最终生成和修复对象。模型可能生成语法正确但语义错误的 SQL；schema linking 错误会导致表和字段选择错误；复杂 join、聚合、排序和隐含业务条件容易出错；执行反馈经常被用于整体重生成，而不是定位到某个局部结构进行修复。所以，仅依赖“自然语言 -> SQL”的单轮生成，很难满足复杂查询场景下的稳定性要求。本课题把 SQL+ 放在自然语言和标准 SQL 之间，是为了把错误定位和局部修复从最终 SQL 层提前到更线性的中间表示层。

### 2.2 Benchmark 与真实场景挑战

Text-to-SQL benchmark 从 Spider 发展到 BIRD、Spider 2.0，研究重点也从单纯 SQL 生成逐渐扩展到真实企业环境。BIRD 更关注真实数据库、外部知识和执行效率；Spider 2.0 强调企业级 Text-to-SQL workflow，包括复杂数据环境、多 SQL 方言、项目代码和真实业务分析流程。

这些 benchmark 反映出一个趋势：自然语言数据库查询已经不只是单轮文本生成任务，而是需要理解 schema、业务知识、方言文档、执行反馈和数据分析流程的综合任务。多阶段、多智能体和可反馈修正的系统结构更接近真实工作流。不过，开题阶段不宜把目标直接设定为完整 Spider 或 BIRD 排行榜成绩。本课题先从自建可控数据集和公开小子集入手，验证 SQL+ 表达、转换和修复链路是否成立，再逐步扩大数据范围。

### 2.3 SQL 扩展与 SQL+ 表达

SQL 是数据库查询的事实标准，但在复杂查询中容易出现表达结构紧凑、局部关系交织和错误定位困难等问题。嵌套子查询、多表 join、聚合过滤、窗口函数和方言差异都会增加大模型生成难度。GoogleSQL Pipe Syntax 提出在不脱离 SQL 生态的基础上引入管道式表达，使查询更接近数据处理流程。

本课题中的 SQL+ 借鉴管道式表达思想，但定位更具体：它作为 Text-to-SQL 的中间查询表示，用于降低生成和修复难度。与主要面向人工书写体验的 SQL 扩展不同，本课题更关注 SQL+ 能否为大模型提供稳定的中间结构，使 Critic Agent 可以在步骤级别定位错误，使 Repair Skill 可以在有限范围内修改候选查询。当前 SQL+ 的基本思路包括：

1. 以 FROM 作为查询起点，按照数据流逐步展开。
2. 将 JOIN、WHERE、GROUP、AGG、HAVING、SELECT、ORDER、LIMIT 拆成局部步骤。
3. 保留每一步的可解释性，便于 Critic Agent 定位错误。
4. 通过规则转换器转换为标准 SQL 或后续达梦 SQL 方言执行。

### 2.4 多智能体 Text-to-SQL 与反馈修正

多智能体 Text-to-SQL 的已有研究表明，把任务拆分给不同角色，有助于处理复杂查询。例如 MAC-SQL 将任务拆成 selector、decomposer、refiner 等角色；CHESS 使用信息检索、schema 选择、候选生成和单元测试等专门 Agent；CHASE-SQL 采用多路径候选生成和选择；Tool-Assisted Agent 引入 retriever 和 detector 来处理执行不报错但语义不匹配的问题；SQLCritic 关注 clause-wise critic 和结构化反馈修正。

SQL-Factory 也与本课题有关。它通过 Generation Team、Expansion Team 和 Management Team 生成高质量、大规模 SQL 查询，说明 SQL 生成任务可以被拆成多个协作环节，并通过自动化流程同时控制多样性、规模和成本。它更偏向 SQL 工作负载与训练数据生成，本课题更关注自然语言查询到 SQL+ 的中间表示、执行反馈诊断和局部 repair skill。两者的共同点是都不把 SQL 生成看成单次输出，而是看成需要分工、验证和迭代的过程。

不过，许多方法仍主要在标准 SQL 层进行修复。标准 SQL 的结构较紧凑，一个错误可能同时影响多个子句，导致修复时需要整体重写。SQL+ 的优势在于它把查询拆成线性步骤，更适合“错误类型 -> 局部步骤 -> repair skill”的修复方式。本课题的研究重点也不只是让多个 Agent 串联生成 SQL，而是围绕 SQL+ 中间表示建立生成、诊断、路由、局部修复和执行验证闭环。换句话说，多智能体在这里不是形式上的多 prompt，而是为错误定位、技能选择和执行验证分工。

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

目前已经实现 value-linking、ORDER、aggregation、join、projection 五类 repair skill。projection skill 用于处理结果列多、少或列顺序错误，例如 q006 中模型多输出了 `product_id`，而用户问题只要求商品名称和价格。后续将进一步研究复合错误下多个 repair skill 的调用顺序，以及 SQL 能执行但结果语义不匹配时的诊断稳定性。

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
6. 设计 value-linking、ORDER、aggregation、join、projection 五类局部 repair skill。
7. 实现 Skill Router，将 Critic 输出路由到不同 repair skill。
8. 扩展无报错语义错诊断，接入 Spider/BIRD 小规模子集，后续适配达梦 SQL 方言。

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

该实验表明，当前 SQL+ 不是停留在概念层面的表达设计，而是已经能通过 parser 和转换器形成可执行 SQL，并在自建样例库上得到一致执行结果。

### 6.3 单 Agent Baseline

| 方法 | 样例数 | SQL/SQL+ 有效 | SQL 可执行 | 执行结果一致 |
| --- | --- | --- | --- | --- |
| Direct NL2SQL | 30 | - | 30/30 | 16/30 |
| NL2SQL+ prompt v1 | 30 | 30/30 | 30/30 | 13/30 |
| NL2SQL+ prompt v2 | 30 | 30/30 | 30/30 | 17/30 |

SQL+ prompt v2 的结果略高于 Direct NL2SQL，但差距不大。这个结果也提醒我们，仅把输出格式从 SQL 改成 SQL+ 并不足以解决问题。SQL+ 的价值需要通过错误定位、工具调用和局部修复机制体现。

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
| SQL+ Skill Router + Repair Skills v3 | 13 | 13/13 | 13/13 | 13/13 |

SQL+ 诊断辅助 Refiner 使用了 gold-derived differences，只能说明“结构化反馈 -> SQL+ 层局部修复 -> 执行验证”的链路可行，不能作为真实自主修复结果。更接近真实场景的是非 gold 实验。在该条件下，单 Refiner 和简单多 Agent 串联效果有限；Critic Agent、Skill Router、局部 repair skill 和执行验证结合后，在 13 条已知 SQL+ 失败样例上达到 13/13 修复成功。这个结果说明，错误类型路由和局部 skill 的组合比整体重生成更稳定。不过，这仍然是开题阶段的小规模验证，后续还需要扩展到更多错误类型、复合错误和公开数据集样例。

### 6.6 Repair Skill 分治实验

| Repair Skill | 样例数 | 修复成功 |
| --- | --- | --- |
| value-linking repair skill | 3 | 3/3 |
| ORDER repair skill | 3 | 3/3 |
| aggregation repair skill | 3 | 3/3 |
| join repair skill | 3 | 3/3 |
| projection repair skill | 1 | 1/1 |

分治实验说明，不同错误类型适合采用不同的局部修复策略。例如 value-linking 更依赖字段值检索和候选值验证，ORDER 更依赖排序字段和方向判断，aggregation 更依赖分组维度和聚合口径检查，join 更依赖连接路径和表关系约束，projection 更关注 SELECT 输出是否和问题要求一致。相比整体重生成，局部修复更容易控制修改范围。

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

实验方式为：筛选当前 SQL+ 子集可覆盖的 Spider 查询，将 Spider gold SQL 改写为 SQL+，再由 SQL+ 转换器转回 SQL，并在 SQLite 数据库上比较执行结果。结果显示，当前 SQL+ 表达与转换机制在公开 benchmark 的简单和中等查询结构上具备初步迁移可行性。

同时要明确，该结果不能等同于完整 Spider benchmark 成绩。当前 SQL+ 子集尚未覆盖复杂子查询、集合运算、复杂布尔条件、distinct、窗口函数等结构。后续需要继续扩展 SQL+ 语法，并在更多 Spider 数据库和 BIRD 子集上验证。开题报告中应把这一结果表述为“公开 benchmark 子集迁移可行性证据”，而不是完整 benchmark 性能。

## 7. 预期创新点

### 7.1 面向大模型生成友好的 SQL+ 中间查询表示

本课题设计线性、分步、可解释的 SQL+ 中间表示，将复杂 SQL 查询拆解为可生成、可检查、可修复的局部步骤。相比直接生成标准 SQL，SQL+ 更接近查询构造过程，也更适合与执行反馈结合。

### 7.2 面向 SQL+ 的多智能体查询生成与诊断框架

本课题构建由 Schema Agent、Critic Agent、Skill Router、Repair Skill 和 Executor 组成的多智能体协作框架。各模块分别负责 schema linking、错误诊断、修复路由、局部修正和执行验证，使系统不再完全依赖单次 prompt 输出。

### 7.3 基于执行反馈的 SQL+ 层局部修正机制

本课题不直接对最终 SQL 整体重生成，而是将执行反馈和结果异常映射回 SQL+ 局部步骤，再通过错误类型路由调用不同 repair skill。该机制有助于控制修复范围，提高修复过程的可解释性。

## 8. 可行性分析

当前已经完成 SQL+ parser、SQL+ 到 SQL 转换器、自建数据集、baseline 实验、错误诊断、五类 repair skill 和 Skill Router v3 端到端实验。从已有结果看：

1. SQL+ 表达与转换链路稳定，30/30 查询可执行且结果一致。
2. SQL+ 层局部修复链路可行，诊断辅助 Refiner 达到 13/13。
3. 在真实非 gold 条件下，Skill Router + Repair Skills v3 在 13 条已知 SQL+ 失败样例上达到 13/13，明显优于 SQL+ 单 Refiner 的 4/13。
4. Spider 小规模受支持子集达到 20/20，说明当前 SQL+ 子集具备初步公开 benchmark 迁移可行性。

这些结果为后续研究提供了基础。接下来的重点不是简单扩大 prompt，而是增强 Critic Agent 的 SELECT/projection 诊断能力，研究无报错但语义错误的场景，扩展公开数据集和达梦 SQL 方言验证。

## 9. 后续工作计划

| 阶段 | 时间 | 内容 |
| --- | --- | --- |
| 第一阶段 | 开题后 1-2 个月 | 完善 SQL+ 语法，扩展无报错语义错诊断 |
| 第二阶段 | 第 3-4 个月 | 完善 Schema Agent、Critic Agent 和 Skill Router |
| 第三阶段 | 第 5-6 个月 | 接入 Spider/BIRD 小规模子集，构造 SQL+ 改写数据 |
| 第四阶段 | 第 7-8 个月 | 适配达梦 SQL 方言，测试 SQL+ 到达梦 SQL 的兼容性 |
| 第五阶段 | 第 9-10 个月 | 完成消融实验、论文撰写和系统整理 |

## 10. 参考文献与资料

1. Zhong, V., Xiong, C., & Socher, R. Seq2SQL: Generating Structured Queries from Natural Language using Reinforcement Learning. arXiv:1709.00103. https://arxiv.org/abs/1709.00103
2. Yu, T., et al. Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task. arXiv:1809.08887. https://arxiv.org/abs/1809.08887
3. Guo, J., et al. Towards Complex Text-to-SQL in Cross-Domain Database with Intermediate Representation. ACL 2019. https://aclanthology.org/P19-1444/
4. Wang, B., et al. RAT-SQL: Relation-Aware Schema Encoding and Linking for Text-to-SQL Parsers. ACL 2020. https://aclanthology.org/2020.acl-main.677/
5. Gan, Y., et al. Natural SQL: Making SQL Easier to Infer from Natural Language Specifications. Findings of EMNLP 2021. https://aclanthology.org/2021.findings-emnlp.174/
6. Scholak, T., Schucher, N., & Bahdanau, D. PICARD: Parsing Incrementally for Constrained Auto-Regressive Decoding from Language Models. EMNLP 2021. https://aclanthology.org/2021.emnlp-main.779/
7. Li, H., et al. RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL. AAAI 2023. https://ojs.aaai.org/index.php/AAAI/article/view/26535
8. Dong, X., et al. C3: Zero-shot Text-to-SQL with ChatGPT. arXiv:2307.07306. https://arxiv.org/abs/2307.07306
9. Gao, D., et al. Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation. arXiv:2308.15363. https://arxiv.org/abs/2308.15363
10. Pourreza, M., & Rafiei, D. DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction. arXiv:2304.11015. https://arxiv.org/abs/2304.11015
11. Wang, B., et al. MAC-SQL: A Multi-Agent Collaborative Framework for Text-to-SQL. arXiv:2312.11242. https://arxiv.org/abs/2312.11242
12. Pourreza, M., et al. CHESS: Contextual Harnessing for Efficient SQL Synthesis. arXiv:2405.16755. https://arxiv.org/abs/2405.16755
13. Pourreza, M., et al. CHASE-SQL: Multi-Path Reasoning and Preference Optimized Candidate Selection in Text-to-SQL. arXiv:2410.01943. https://arxiv.org/abs/2410.01943
14. Wang, Z., Zhang, R., Nie, Z., & Kim, J. Tool-Assisted Agent on SQL Inspection and Refinement in Real-World Scenarios. arXiv:2408.16991. https://arxiv.org/abs/2408.16991
15. Li, J., Wu, T., Mao, Y., Gao, Y., Feng, Y., & Liu, H. SQL-Factory: A Multi-Agent Framework for High-Quality and Large-Scale SQL Generation. PVLDB, 19(3):292-305, 2025. https://www.vldb.org/pvldb/vol19/p292-gao.pdf
16. Chen, J., et al. SQLCritic: Correcting Text-to-SQL Generation via Clause-wise Critic. arXiv:2503.07996. https://arxiv.org/abs/2503.07996
17. Deng, M., et al. ReFoRCE: A Text-to-SQL Agent with Self-Refinement, Consensus Enforcement, and Column Exploration. arXiv:2502.00675. https://arxiv.org/abs/2502.00675
18. Liu, Y., et al. XiYan-SQL: A Novel Multi-Generator Framework For Text-to-SQL. arXiv:2507.04701. https://arxiv.org/abs/2507.04701
19. Li, J., et al. Can LLM Already Serve as A Database Interface? A Big Bench for Large-Scale Database Grounded Text-to-SQL Evaluation. arXiv:2305.03111. https://arxiv.org/abs/2305.03111
20. Lei, F., et al. Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows. arXiv:2411.07763. https://arxiv.org/abs/2411.07763
21. Google Research. SQL Has Problems. We Can Fix Them: Pipe Syntax In SQL. https://research.google/pubs/sql-has-problems-we-can-fix-them-pipe-syntax-in-sql/
22. Google Cloud. GoogleSQL Pipe Query Syntax Guide. https://cloud.google.com/bigquery/docs/pipe-syntax-guide

# 硕士生论文开题报告

## 题目

面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 学号 | （待填写） |
| 姓名 | （待填写） |
| 专业 | （待填写） |
| 指导教师 | （待填写） |
| 院（系、所） | 计算机科学与技术学院 |

## 开题要求对照说明

根据《硕士生开题报告模板0604.docx》和《关于做好2025级硕士研究生论文开题答辩工作通知.pdf》，本报告按以下栏目组织：课题背景、目的和意义，国内外研究现状，研究目标与研究内容，研究方案与可行性分析，进度安排，预期成果，主要参考文献。通知要求开题报告内容应包括文献综述、选题意义、研究内容、研究方案、预期达到的目标和课题可行性等；硕士研究生文献阅读量不少于 40 篇，其中外文文献不少于三分之一；答辩时需提供不少于 15 篇精读文献目录。本报告在参考文献部分列出 40 篇相关文献，并单独标注 15 篇拟重点精读文献。

# 课题背景、目的和意义

自然语言数据库查询要解决的问题并不复杂：用户不会写 SQL，也应该能查数据、做统计和完成一些基础分析。企业里很多查询需求本来就是用自然语言提出的，例如“统计上个月每个地区的销售额”“找出消费金额最高的客户”等。如果系统能把这类问题稳定转换成可执行查询，业务人员和普通分析人员就不必先完整掌握 SQL 语法，才能使用数据库。

不过，真实场景中的 Text-to-SQL 还远没有稳定到可以直接交付。大语言模型经常能生成一条“看起来像对的” SQL，但复杂 schema、多表 join、聚合口径、排序逻辑、字段值匹配和数据库方言差异都会让结果偏离用户意图。更麻烦的是，SQL 一旦出错，错误位置并不总是清楚。一个查询可能同时涉及 `FROM`、`JOIN`、`WHERE`、`GROUP BY`、`HAVING`、`ORDER BY` 等多个部分，最后执行失败或结果不一致时，很难直接判断该改哪一段。

标准 SQL 的书写顺序也会增加生成和修复难度。人理解查询时通常先确定数据源，再考虑过滤、连接、分组、聚合和最终输出；标准 SQL 的写法并不完全按这个构造过程展开。GoogleSQL Pipe Syntax 的研究提出，可以在 SQL 生态内引入管道式表达，让查询更接近数据流顺序。这个思路给本课题的启发是：查询表达形式本身可能会影响可读性，也可能影响大模型生成和修复时的稳定性。

基于上述问题，本课题不把目标限定为“做一个自然语言转 SQL 的工程 Demo”，而是研究一条更适合诊断和修复的生成路线：

```text
自然语言问题 -> SQL+ 中间表示 -> 可执行 SQL -> 执行反馈 -> SQL+ 层局部诊断与修复
```

这里的 SQL+ 不是替代标准 SQL，而是作为自然语言和最终 SQL 之间的中间查询表示。它将复杂查询拆成线性步骤，使错误更容易映射回具体步骤；多智能体部分则负责意图理解、schema linking、错误诊断、技能路由和执行验证，使修复过程不再完全依赖一次性整体重写。

本课题真正想验证的是一个更具体的问题：复杂查询先写成线性、分步的 SQL+ 表达后，大模型是否更容易生成、诊断和修复。若这个假设成立，SQL+ 可以作为自然语言查询和数据库方言之间的中间层；多智能体也不只是多个提示词顺序调用，而是围绕 schema 检索、错误定位、修复路由和执行验证分工。这个方向可以为达梦 SQL+ 和国产数据库智能交互提供一个可验证的原型路线。

# 国内外研究现状

## Text-to-SQL 研究：从结构化语义解析到大模型生成

Text-to-SQL 早期研究主要把任务看作语义解析问题，目标是把自然语言问题映射为形式化查询。Seq2SQL、SyntaxSQLNet、RAT-SQL 等工作分别从序列生成、SQL 结构建模和 schema linking 入手，解决自然语言词语、表、列、外键关系之间的匹配问题。Spider 数据集提出跨数据库评测后，研究重点从单库模板匹配转向跨 schema 泛化。模型不再只需要记住固定表结构，还要在未见过的数据库中理解表间关系、字段含义和复杂 SQL 结构。

这一路线说明，Text-to-SQL 的困难不只是“把一句话翻译成 SQL”。更关键的问题包括 schema linking、join 路径选择、聚合口径判断、嵌套结构生成和可执行性约束。RAT-SQL 用关系感知编码器建模 question-schema-column 之间的关系，PICARD 在解码过程中加入增量语法检查，RESDSQL 将 schema linking 和 skeleton parsing 解耦。这些方法共同表明：如果输出结构没有被有效约束，模型很容易生成语法可疑、字段错误或语义偏离的 SQL。

中间表示研究是本课题的重要基础。IRNet 提出 SemQL，将复杂 SQL 映射为更接近语义结构的树形表示，减少模型直接处理 SQL 细节的压力。NatSQL 则保留较多 SQL 外观，但去掉或简化部分 `FROM`、`JOIN ON`、`GROUP BY` 等自然语言中不容易直接对应的成分，使模型先预测较容易生成的查询表示，再转换为 SQL。这类研究已经证明，中间表示可以降低直接生成标准 SQL 的难度。但它们主要服务于生成准确率，较少讨论执行失败之后如何把错误定位到某一个中间步骤，再进行局部修复。

## 大模型 Text-to-SQL：从一次生成到候选验证和任务分解

大语言模型改变了 Text-to-SQL 的实现方式。DAIL-SQL、C3、DIN-SQL 等工作把重点放在提示设计、样例选择、问题分解和自修正上。DIN-SQL 将任务拆为 schema linking、问题分解、SQL 生成和自修正几个阶段，说明复杂查询不适合完全依赖单轮生成。CHESS、CHASE-SQL、ReFoRCE、XiYan-SQL 等较新的系统进一步引入检索、候选生成、列探索、共识约束、偏好选择和执行验证，用多路径或多模块方式提高稳定性。

从评测趋势看，Text-to-SQL 已经不再只关注 exact match。Spider 关注跨数据库泛化，BIRD 强调真实数据库、外部知识和执行效率，Spider 2.0 将任务推进到企业级工作流，涉及多 SQL 方言、代码库、数据转换和分析流程。对应地，评价指标也需要扩展。除 execution accuracy 外，还应观察 valid SQL rate、schema linking accuracy、value linking accuracy、join path accuracy、执行时间、token cost、候选数量、修复轮数和失败类型分布。对于本课题来说，这些指标比单一准确率更能反映 SQL+ 是否真正降低了生成和修复难度。

## Agentic NL2SQL：工具调用、执行反馈与多角色协作

近年来的 agentic Text-to-SQL 系统通常不再把大模型当作单一生成器，而是把查询任务拆成多个角色或工具调用过程。MAC-SQL 使用 selector、decomposer、refiner 等角色处理 schema 选择、问题分解和错误修正。CHESS 结合 schema 检索、上下文组织、候选生成和单元测试。CHASE-SQL 采用多路径候选生成与偏好优化选择。Tool-Assisted Agent、LEVER、SQLCritic 等工作则强调执行反馈、候选验证或 clause-wise 诊断。

这些研究说明，多智能体或工具增强机制的价值不在于简单增加 prompt 数量，而在于让不同模块承担可观察的子任务。例如，Schema Agent 需要给出相关表列和连接路径，Critic Agent 需要说明错误类型和证据，Repair Skill 需要产生可验证的修复候选，Executor 需要用数据库执行结果过滤错误候选。若每个模块的中间输出不可检查，多智能体很容易退化为“多个提示词串联”，并不一定提升效果。本课题后续实验也需要把 agent 的贡献拆开评估，而不是只报告完整系统的最终成功率。

现有 agentic NL2SQL 方法大多仍以标准 SQL 为主要诊断和修复对象。执行反馈常被用于候选筛选或整条 SQL 重写，但错误通常没有稳定映射到一个可修复的中间步骤。实际错误却常具有局部性，例如 value-linking 错误、聚合别名引用错误、join 路径错误、ORDER/LIMIT 遗漏、projection mismatch 等。若每次都重写整条 SQL，容易改坏原本正确的部分。因此，本课题把 SQL+ 放在 agent 修复链路的中心，试图让 Critic 的诊断、Skill Router 的路由和 Repair Skill 的补丁都围绕 SQL+ 步骤展开。

## SQL 中间表示与 SQL 语言扩展：SQL+ 的位置

SQL+ 不是从零提出的新数据库语言。它与 SemQL、NatSQL 和 GoogleSQL Pipe Syntax 都有关联，但研究目标不同。

SemQL 是面向复杂 Text-to-SQL 的树形语义表示，重点是隐藏标准 SQL 的实现细节，让模型先生成语义结构。它适合降低生成难度，但树形表示和最终 SQL 的执行错误之间不一定有直接的一步对应关系。NatSQL 更接近 SQL，通过简化连接、分组和嵌套结构来减少模型预测负担，适合作为生成中间层，但它主要讨论从自然语言到可转换查询表示的过程。GoogleSQL Pipe Syntax 是数据库系统内的 SQL 扩展，强调用线性数据流方式改善 SQL 的阅读、编写和维护。它给 SQL+ 提供了重要启发：查询表达顺序可以更接近数据处理流程，而不是完全受传统 SQL 书写顺序限制。

本课题中的 SQL+ 更强调“生成、转换、诊断、局部修复”四个目标的统一。它保留 `FROM -> JOIN -> WHERE -> GROUP -> AGG -> HAVING -> SELECT -> ORDER -> LIMIT` 这样的线性步骤，使每一步可以被 parser 检查、被 converter 转换、被 Critic 定位、被 Repair Skill 局部修改。也就是说，SQL+ 的价值不只在于让 SQL 看起来更线性，而在于为多智能体反馈修正提供一个可操作的中间层。

因此，后续研究不能只说 SQL+ “更容易读”。需要通过实验比较它与标准 SQL、SemQL-style 表示、NatSQL-style 表示和 Pipe-style 表示在以下方面的差别：表达复杂度、生成 token、转换时间、可执行率、错误定位准确率、patch 影响范围、修复轮数和最终执行准确率。只有这些指标能够支撑“为什么使用 SQL+”这一核心论证。

## 现有研究不足与本课题切入点

综合已有研究，可以归纳出四个不足。第一，中间表示研究多关注生成准确率，对执行反馈后的错误定位和局部修复关注不足。第二，多智能体 Text-to-SQL 多关注任务分解、候选生成和候选选择，较少把错误诊断结果映射到可执行的局部修复技能。第三，现有评测常以 execution accuracy 为主，对 repairability 的评价不够充分，本课题需要引入 error localization accuracy、router accuracy、patch minimality、average repair rounds、token cost、latency、IR parse time 和 IR-to-SQL conversion time 等指标。第四，公开 benchmark 与企业数据库环境之间存在差距，开题阶段应先用自建可控数据集和 Spider 小规模子集验证机制，后续再扩展到 BIRD 子集和达梦 SQL 方言适配。

基于这些不足，本课题的切入点是：将 SQL+ 作为面向生成和修复的中间表示，把多智能体机制落到 schema/value grounding、错误诊断、技能路由、局部修复和执行验证上，并用多系统对比和多维指标评估 SQL+ 是否真正提高了可生成性、可解释性和可修复性。

# 研究目标与研究内容

## 研究目标

本课题拟研究一种面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法。核心假设是：相比直接生成标准 SQL，先生成线性、分步、可转换的 SQL+ 中间表示，再结合执行反馈、错误诊断、技能路由和局部 repair skill，能够提高复杂查询的可执行性、可解释性和可修复性。

本课题不把目标限定为实现一个完整工程 Demo，而是围绕以下问题建立可验证的方法和实验体系：SQL+ 是否能降低查询表达复杂度，并为错误定位提供更清晰的步骤边界；SQL+ 与 SemQL、NatSQL、Pipe-style 表示相比，在哪些指标上更适合反馈修正；多智能体机制如何服务于 schema/value grounding、错误诊断、技能路由和执行验证，而不是简单串联多个 prompt；执行反馈能否被稳定映射回 SQL+ 局部步骤，并通过局部 patch 提高修复成功率；在自建可控数据集、Spider 小规模子集和后续 BIRD/达梦样例上，SQL+ 路线是否具有可迁移性。

## 拟解决的关键问题

第一个问题是 SQL+ 的必要性。已有 SemQL、NatSQL 和 Pipe Syntax 都说明标准 SQL 可以被重构，但本课题需要进一步证明 SQL+ 不是另一种写法，而是面向生成、转换、诊断和修复的一体化中间表示。这个问题需要通过复杂度指标、转换指标和修复指标共同回答。

第二个问题是 SQL+ 的边界。SQL+ 过于接近标准 SQL，简化效果有限；过于抽象，又会增加转换和方言适配难度。本课题需要确定一个能覆盖常见分析查询、能转换为 SQL、能映射执行错误的语法子集，并逐步扩展到更复杂结构。

第三个问题是多智能体的可验证性。Agent 的价值必须体现在可观察输出上，例如 schema 选择是否正确、Critic 是否定位到正确步骤、Router 是否选择正确 repair skill、patch 是否只修改相关步骤、Executor 是否过滤无效候选。否则多智能体只会增加成本和延迟。

第四个问题是评估方法。除 execution accuracy 外，还需要比较 valid SQL rate、SQL+ valid rate、schema linking accuracy、value linking accuracy、join path accuracy、error localization accuracy、router accuracy、repair success rate、average repair rounds、patch minimality、token cost、latency、IR parse time 和 IR-to-SQL conversion time。这样才能判断 SQL+ 的收益是否超过它引入的转换成本。

## 研究内容一：面向生成和修复的 SQL+ 中间表示设计与对比评估

本部分研究 SQL+ 的语法边界、AST 表示、转换规则和与其他中间表示的差别。技术难点在于，SQL+ 需要同时满足四个要求：足够线性，便于自然语言映射；足够完整，能够表达 join、filter、aggregation、having、order、limit 等常见分析查询；足够确定，能够转换为标准 SQL 或后续达梦 SQL；足够可诊断，能够把错误映射到具体步骤。

拟采用的方法是：以 `FROM` 为查询起点，将 `JOIN`、`WHERE`、`GROUP`、`AGG`、`HAVING`、`SELECT`、`ORDER`、`LIMIT` 组织成线性步骤；在 AST 中显式记录表别名、字段引用、聚合别名、连接条件和排序引用；对 AGG 别名、HAVING/ORDER 引用、join 方向、projection 列等易错位置设计规范化规则。转换器采用确定性规则，将 SQL+ 转换为可执行 SQL，并保留步骤到 SQL 子句的映射关系。

评估上，本部分不只检查 SQL+ 能否转换成功，还要比较不同表示的复杂度和可修复性。对比对象包括标准 SQL、SemQL-style 语义表示、NatSQL-style 简化 SQL、Pipe-style 线性表示和 SQL+。指标包括 token 长度、嵌套深度、子查询/CTE 数量、跨子句引用数量、join 路径长度、别名依赖数量、IR parse time、IR-to-SQL conversion time、转换成功率、SQL 可执行率和错误步骤可定位率。开题阶段可以先使用 simplified proxy 表示进行公平对比，后续再考虑接入公开 SemQL/NatSQL 实现。

## 研究内容二：自然语言到 SQL+ 的生成与 schema/value grounding 方法

本部分研究从自然语言问题生成 SQL+ 的方法。技术难点在于，模型不仅要生成合法语法，还要正确选择表列、连接路径、过滤值、聚合口径和排序依据。当前初步实验显示，SQL+ prompt v2 在 30 条样例上达到 17/30，略高于 Direct NL2SQL 的 16/30，但差距不大。这说明单纯更换输出格式不足以解决问题，必须引入更明确的 schema/value grounding 和候选验证。

拟采用的方法是构建可观察的生成流程。Schema Agent 负责检索相关表、字段、外键关系和值域样例；Planner Agent 将问题拆成 SQL+ 步骤草图；SQL+ Generator 生成候选 SQL+；Translator 将 SQL+ 转换为 SQL；Executor 执行候选并返回错误或结果摘要。对于多候选生成，记录每个候选的 token 消耗、生成延迟、SQL+ 合法性和执行结果，由选择策略挑选更可靠的候选。

评估上，本部分比较 Direct NL2SQL、NL2SQL+ single agent、decomposition-based NL2SQL、standard SQL multi-agent、multi-agent NL2SQL+ 等方法。指标包括 execution accuracy、valid SQL rate、SQL+ valid rate、schema linking accuracy、value linking accuracy、join path accuracy、candidate pass rate、prompt tokens、completion tokens、total latency 和不同复杂度查询上的表现。通过这些指标判断 SQL+ 是降低生成负担，还是只是把复杂度转移到转换器和后续修复阶段。

## 研究内容三：执行反馈驱动的 SQL+ 层错误诊断与局部修复

本部分研究如何把数据库执行错误、结果异常和用户意图偏差映射回 SQL+ 步骤，并通过局部 repair skill 修复。技术难点在于，很多错误并不会触发数据库报错。例如过滤值错误、聚合口径错误、排序遗漏、projection mismatch 都可能产生可执行但语义错误的 SQL。仅凭报错信息无法完成诊断，需要结合问题文本、schema、SQL+ 步骤、执行结果和候选差异。

拟采用的方法是构建 `Critic Agent -> Skill Router -> Repair Skill -> Executor` 闭环。Critic Agent 输出错误类型、可疑步骤和诊断证据；Skill Router 根据错误类型和 SQL+ 结构特征选择 value-linking、ORDER、aggregation、join、projection 等 repair skill；每个 repair skill 只修改相关步骤，生成候选 patch；Executor 执行候选 SQL 并比较结果，筛掉语法错误和执行错误。该机制避免整条 SQL 重写，尽量减少对正确部分的破坏。

评估上，本部分设置 SQL 层整体重写、SQL+ 单 Refiner、Schema-Critic-Refiner、Step-wise Critic-Refiner、SQL+ Skill Router + Repair Skills 等对照组。指标包括 repair success rate、average repair rounds、error localization accuracy、router accuracy、patch minimality、unchanged-correct-step rate、SQL executable rate、token cost 和 latency。当前 13 条已知 SQL+ 失败样例中，SQL+ non-gold single Refiner 为 4/13，Direct SQL non-gold Refiner 为 6/14，SQL+ Skill Router + Repair Skills v3 为 13/13。该结果只能说明当前小规模已知失败集上的机制可行，后续需要扩展到无报错语义错误、复合错误和公开子集。

## 研究内容四：多系统对比、消融实验与公开子集迁移评估

本部分建立完整实验体系，用于回答 SQL+ 和多智能体修复机制是否真正有效。技术难点在于公平比较。SQL+ 引入了中间表示和转换器，可能带来额外 token、转换时间和错误传播；多智能体增加了调用成本和延迟。如果只报告最终准确率，无法说明收益来自 SQL+、Agent、工具还是 repair skill。

拟采用的对比方法包括：Direct NL2SQL、NL2SQL+ single agent、SemQL-style IR generation、NatSQL-style IR generation、Pipe-style linear query generation、standard SQL multi-agent、SQL layer global repair、multi-agent NL2SQL+ without feedback、multi-agent NL2SQL+ with feedback、SQL+ Skill Router + Repair Skills。消融实验包括去掉 SQL+、去掉多智能体、去掉 Schema/value lookup、去掉 Critic Agent、去掉 Skill Router、只做 SQL 层修复、关闭执行验证、替换不同 SQL+ 语法设计等。

实验数据分三层推进。第一层是自建订单分析数据集，用于控制变量、构造错误类型和快速迭代。第二层是 Spider 小规模受支持子集，用于验证 SQL+ 表达与转换机制在公开 benchmark 上的初步迁移能力。当前已完成 `concert_singer` 数据库中 20 条受支持查询的 smoke test，SQL+ 有效、SQL 可执行和执行一致均为 20/20，但这不是完整 Spider 成绩。第三层后续扩展到 BIRD 子集和达梦 SQL 方言样例，用于检验真实 schema、外部知识和方言差异的影响。

评估报告将按“结果质量、表达复杂度、修复能力、成本效率、可解释性”五类组织。结果质量关注 execution accuracy 和 valid rate；表达复杂度关注 token 长度、嵌套深度、跨子句依赖和 join 路径长度；修复能力关注定位准确率、路由准确率、修复成功率和 patch 范围；成本效率关注 token cost、latency、IR parse time 和 conversion time；可解释性通过步骤级错误定位、人类定位错误时间或人工评分进行补充评估。

# 研究方案与可行性分析

## 研究方案

研究会按由小到大的路线推进。先定义 SQL+ 最小语法子集，实现 parser 和 SQL 转换器；再构建企业订单样例库，覆盖单表查询、多表连接、过滤、排序、聚合、分组和 Top-K。随后设计 Direct NL2SQL 与 NL2SQL+ 两类 baseline，运行大模型生成实验，并对 SQL+ 失败样例做错误类型分析。在此基础上，继续构建 Critic Agent 结构化诊断，设计 value-linking、ORDER、aggregation、join、projection 五类局部 repair skill，并通过 Skill Router 把 Critic 输出路由到不同 repair skill。后续再扩展无报错语义错诊断，接入 Spider/BIRD 小规模子集，并适配达梦 SQL 方言。

## 当前初步实验

当前实验主要用于开题阶段的可行性论证，不作为完整 benchmark 成绩。实验先在自建企业订单分析样例库上控制变量，随后补充 Spider dev 小规模受支持子集 smoke test，用来验证 SQL+ 表达与转换机制是否具备初步迁移可能。

### 实验设置

| 项目 | 当前设置 |
| --- | --- |
| 自建数据库 | 企业订单分析样例库 |
| 数据表 | customers、products、orders、order_items |
| 自然语言查询 | 30 条 |
| SQL+ 标准样例 | 30 条 |
| 错误修正样例 | 15 条规则修正样例；13 条 SQL+ prompt v2 已知失败样例 |
| 执行环境 | SQLite 内存数据库 |
| 模型 | gpt-5-mini |
| 评价方式 | 执行生成 SQL，并与标准 SQL 执行结果比较 |
| gold 使用边界 | gold SQL 只用于离线评估；非 gold 修复实验不把 gold 差异输入模型 |

### 核心结果总览

| 实验问题 | 对比对象或样例 | 关键结果 | 当前能说明什么 | 需要保留的限制 |
| --- | --- | --- | --- | --- |
| SQL+ 能否转换为 SQL | 自建 30 条 SQL+ 样例 | SQL+ 有效 30/30；SQL 可执行 30/30；执行一致 30/30 | SQL+ 不是停留在概念层，已经能形成可执行闭环 | 仍是自建小规模订单数据集 |
| 直接生成 SQL 与生成 SQL+ 哪个更好 | Direct NL2SQL、NL2SQL+ prompt v1/v2 | Direct SQL 16/30；SQL+ v1 13/30；SQL+ v2 17/30 | SQL+ v2 略高，但优势不明显，不能只靠换输出格式解决问题 | 需要引入 schema/value grounding、候选验证和反馈修正 |
| SQL+ 失败主要错在哪里 | SQL+ prompt v2 的 13 条失败样例 | value-linking 5；ORDER/LIMIT 3；aggregation 2；join/schema 2；projection 1 | 失败主要是语义错误，不是语法错误 | 后续 Critic 不能只看数据库报错，还要看结果语义 |
| SQL+ 层局部修复是否可行 | 15 条规则修正样例 | 修正后 SQL 可执行 15/15；修复成功 15/15 | 执行反馈可以映射到 SQL+ 局部步骤 | 规则样例较可控，不能代表真实模型修复难度 |
| 多智能体修复是否有必要 | SQL+ 单 Refiner、Direct SQL Refiner、Skill Router v3 | SQL+ 非 gold 单 Refiner 4/13；Direct SQL 非 gold Refiner 6/14；SQL+ Skill Router v3 13/13 | 单 prompt 修复不稳定，错误定位、路由和局部 skill 拆开后效果更好 | 13/13 来自当前已知失败集，不是大规模泛化结果 |
| 公开数据集能否初步迁移 | Spider dev `concert_singer` 受支持子集 20 条 | conversion smoke test 20/20；fresh e2e 19/20；fresh 输出经 Skill Router -> semantic repair skill 后 20/20 | SQL+ 表达/转换具备公开子集覆盖能力，端到端生成和修复链路也已在小子集跑通 | conversion smoke test 使用 gold SQL 改写，不是端到端生成分数；整体不是完整 Spider benchmark 跑分 |

### IR 表达复杂度对比

这组实验用于回答“为什么使用 SQL+，而不是直接 SQL、SemQL、NatSQL 或 Pipe-style 表示”。SemQL-style、NatSQL-style 和 Pipe-style 在这里是 controlled proxy，只用于受控比较表达形态，不代表完整复现原系统。

| 表示形式 | 平均 token | 平均步骤/子句 | 平均嵌套深度 | 平均别名依赖 | 平均跨子句引用 | 转换成功 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Standard SQL | 31.5333 | 5.9 | 0.6667 | 2.0333 | 2.3333 | 30/30 |
| SQL+ | 35.0333 | 6.1333 | 0.6667 | 0.7 | 1.0 | 30/30 |
| SemQL-style proxy | 50.5667 | 10.7333 | 3.6667 | 0.9 | 1.2 | N/A |
| NatSQL-style proxy | 31.5 | 5.4333 | 0.9667 | 1.3667 | 1.6667 | N/A |
| Pipe-style proxy | 40.8 | 6.1333 | 0.6667 | 1.3667 | 1.6667 | N/A |

这组结果说明，SQL+ 的优势不能写成“更短”。当前 SQL+ 平均 token 反而高于 Standard SQL。更准确的表述是：SQL+ 用显式步骤边界换取更低的别名依赖和跨子句引用，使错误更容易定位到具体步骤，也更适合后续局部 repair skill。SQL+ 到 SQL 的平均转换时间约 0.007 ms，当前转换开销很小。

### IR 生成成本与执行效果对比

| 方法 | 表示有效 | SQL 可执行 | 执行一致 | 平均总 token | 平均延迟 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Direct SQL | 30/30 | 30/30 | 12/30 | 599.1667 | 6.5851s |
| SQL+ | 28/30 | 28/30 | 14/30 | 813.0333 | 9.2197s |
| NatSQL-style proxy | 30/30 | 30/30 | 13/30 | 740.7667 | 6.2802s |
| SemQL-style proxy | 30/30 | 25/30 | 12/30 | 1028.9667 | 9.9684s |

从生成阶段看，SQL+ 的执行一致率为 14/30，略高于其他组，但差距不足以支持“显著更准”的结论。同时，SQL+ 平均 token 和延迟高于 Direct SQL 与 NatSQL-style proxy，说明步骤化表达存在生成成本。后续论证重点应放在修复阶段：SQL+ 是否能提高错误定位、缩小 patch 范围，并以更可控的方式完成反馈修正。

### 反馈修正与 repairability 指标

| 方法 | 初始失败样例 | SQL+ 有效 | SQL 可执行 | 修复成功 | 说明 |
| --- | ---: | ---: | ---: | ---: | --- |
| SQL+ 诊断辅助 Refiner | 13 | 13/13 | 13/13 | 13/13 | 使用 gold-derived differences，只验证链路可行 |
| SQL+ 非 gold Refiner v2 | 13 | 13/13 | 12/13 | 4/13 | 只使用执行反馈和粗粒度诊断 |
| Direct SQL 非 gold Refiner | 14 | - | 14/14 | 6/14 | 直接修标准 SQL |
| SQL+ Skill Router + Repair Skills v3 | 13 | 13/13 | 13/13 | 13/13 | Critic 路由到五类局部 repair skill |

进一步计算 repairability 指标后，结果如下。

| 方法 | 样例数 | 修复成功 | 定位准确率 | 严格最小 patch 率 | 平均 patch minimality | 平均修复轮数 | 平均 repair token |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct SQL Refiner | 14 | 6/14 | 0.8571 | 0.8571 | 0.8571 | 1 | 1609.3571 |
| SQL+ Critic Router Skills | 13 | 13/13 | 0.7692 | 0.9231 | 0.9744 | 2.2308 | 3813.9231 |
| Direct SQL Refiner overlap | 9 | 4/9 | 0.8889 | 0.8889 | 0.8889 | 1 | 1583.2222 |
| SQL+ Critic Router Skills overlap | 9 | 9/9 | 0.7778 | 0.8889 | 0.9630 | 2.3333 | 4001.7778 |

该结果的解释需要谨慎。SQL+ 路线当前的收益主要体现在修复成功率和局部 patch 可控性上；代价是 Critic 与多步骤修复带来更高 token 消耗和更多修复轮数。旧实验输出没有完整记录 API latency，后续需要用带 `latency_seconds` 字段的新脚本重新跑端到端修复延迟。

### Repair Skill 分治结果

| Repair skill | 样例数 | 修复成功 | 覆盖的典型问题 |
| --- | ---: | ---: | --- |
| value-linking | 3 | 3/3 | 候选值替换、日期边界归一化、值过滤错误 |
| ORDER | 3 | 3/3 | 排序字段错误、升降序错误、LIMIT/Top-K 约束 |
| aggregation | 3 | 3/3 | COUNT 口径、GROUP 维度、AGG 别名、ORDER/HAVING 引用 |
| join | 3 | 3/3 | JOIN 方向、冗余 JOIN、缺失 JOIN、paid 过滤遗漏 |
| projection | 1 | 1/1 | 结果列多、列少或列顺序错误 |

这组结果支持后续多智能体设计：系统不应只把多个 prompt 串起来，而应让 Critic Agent 给出错误类型和可疑步骤，由 Skill Router 选择局部 repair skill，再由 Executor 执行候选 patch 并筛选结果。

### 当前初步结论

当前实验可以支撑三个开题判断。第一，SQL+ 作为中间表示具备可执行和可转换基础，已在 30 条自建样例和 20 条 Spider 受支持子集上跑通。第二，SQL+ 并不天然带来更低生成成本，甚至会增加 token 和延迟，因此不能把研究动机写成“SQL+ 更短”。第三，SQL+ 的更合理价值在于为错误定位、Skill Router 和局部修复提供步骤化载体；这一点已经在当前已知失败集和 repair skill 分治实验中得到初步验证，但还需要更大规模、更复杂错误和完整 latency 记录继续检验。


## 可行性分析

从技术可行性看，当前已经完成 SQL+ parser、SQL+ 到 SQL 转换器、自建数据集、baseline 实验、错误诊断、五类 repair skill 和 Skill Router v3 端到端实验。SQL+ 表达与转换链路稳定，30/30 查询可执行且结果一致。SQL+ 层局部修复链路可行，诊断辅助 Refiner 达到 13/13。真实非 gold 条件下，Skill Router + Repair Skills v3 在 13 条已知 SQL+ 失败样例上达到 13/13，高于 SQL+ 单 Refiner 的 4/13。Spider 小规模受支持子集上，conversion smoke test 达到 20/20，fresh e2e 生成达到 19/20，同一次 fresh 输出经 `Skill Router -> semantic repair skill` 后达到 20/20，说明当前 SQL+ 子集具备初步公开 benchmark 迁移可行性。

从数据和实验条件看，当前已有自建可控数据集、公开 Spider 子集适配脚本和完整实验记录。后续可继续扩展 Spider/BIRD 子集，逐步增加复杂 SQL 结构。从工程实现看，当前脚本、报告、数据和 project skills 已在 GitHub 中留痕，具备跨电脑复现基础。从应用场景看，达梦 SQL+ 方言适配可作为后续扩展目标，先通过标准 SQL/SQLite 验证核心机制，再迁移到达梦数据库场景。

当前不足也需要明确。自建数据集规模还比较小，主要用于开题阶段可行性验证；Spider conversion smoke test 使用 gold SQL 改写得到 SQL+，只能说明表达与转换覆盖性，不能当作端到端生成准确率；Spider fresh e2e 结果也只是 `concert_singer` 20 条小子集，不是完整 benchmark 跑分。SQL+ 语法子集还没有覆盖复杂子查询、集合运算、窗口函数、复杂布尔条件等结构。非 gold 反馈修正目前仍依赖 Critic 的错误类型识别，后续需要增强无报错语义错的诊断能力。达梦 SQL 方言适配也还没有完成。

# 已有工作局限

当前实验结果主要用于开题阶段的可行性论证，不能直接解释为完整系统性能。自建订单数据集规模较小，查询类型仍以常见分析查询为主。Spider 实验只覆盖 `concert_singer` 数据库中当前 SQL+ 子集支持的 20 条查询，不是完整 Spider benchmark 跑分。Skill Router v3 的 13/13 结果来自已知 SQL+ 失败样例，后续还需要在更大样本、更复杂复合错误和无报错语义错误上验证。当前系统主要使用 SQLite 验证标准 SQL 执行链路，达梦 SQL 方言适配尚未完成。这些限制不会否定现阶段结果，但也说明后续研究不能停留在小样例修复实验上。

# 进度安排

| 阶段 | 时间 | 主要工作 |
| --- | --- | --- |
| 第一阶段 | 开题后 1-2 个月 | 完善 SQL+ 语法子集，扩展无报错语义错诊断，补充更多 projection/SELECT 诊断样例 |
| 第二阶段 | 第 3-4 个月 | 完善 Schema Agent、Critic Agent 和 Skill Router，加入 schema/value lookup、SQL+ parser、SQL executor 等工具能力 |
| 第三阶段 | 第 5-6 个月 | 接入 Spider/BIRD 小规模子集，构造 SQL+ 改写数据，扩展多数据库、多难度实验 |
| 第四阶段 | 第 7-8 个月 | 适配达梦 SQL 方言，测试 SQL+ 到达梦 SQL 的兼容性，补充方言函数和语法转换规则 |
| 第五阶段 | 第 9-10 个月 | 完成消融实验、结果分析、论文初稿撰写和原型系统整理 |
| 第六阶段 | 第 11-12 个月 | 根据导师和中期反馈修改系统与论文，完成论文定稿、答辩材料和代码归档 |

# 预期成果

本课题预期形成以下成果：一种面向大模型生成友好的 SQL+ 中间查询表示，包含最小语法子集、转换规则以及与标准 SQL/达梦 SQL 的关系；一套面向 SQL+ 的多智能体自然语言数据库查询生成与反馈修正框架，包含 Schema Agent、Critic Agent、Skill Router、Repair Skill 和 Executor；一组基于执行反馈的 SQL+ 层局部修复方法，覆盖 value-linking、ORDER、aggregation、join、projection 等典型错误类型。在此基础上，完成原型系统和实验评估，并形成论文、实验记录、开题答辩材料和可复现实验脚本。

预期技术指标包括：SQL+ 转标准 SQL 的可执行率保持较高水平；在自建数据集上完成 Direct NL2SQL、NL2SQL+、多智能体 NL2SQL+ 和反馈修正方法对比；在典型错误类型上验证局部 repair skill 的修复能力；在公开 benchmark 子集上完成 SQL+ 表达与转换迁移性验证；在达梦数据库场景下完成核心查询类型的方言适配测试。

# 预期创新点

本课题的预期创新主要体现在三个方面。

一是设计面向大模型生成与修复的 SQL+ 中间查询表示。与直接生成标准 SQL 不同，SQL+ 将查询拆成线性步骤，使数据源、连接、过滤、聚合、排序和投影等操作更容易被定位和修改。

二是构建面向 SQL+ 的多智能体查询生成与诊断框架。Schema Agent、Critic Agent、Skill Router、Repair Skill 和 Executor 分别处理 schema linking、错误诊断、修复路由、局部修正和执行验证，避免把所有问题压缩到单个 prompt 中。

三是研究基于执行反馈的 SQL+ 层局部修正机制。系统不直接重写最终 SQL，而是把执行错误、结果异常和语义偏差映射回 SQL+ 局部步骤，再调用对应 repair skill 生成候选修复。这样可以控制修复范围，也能给出更清楚的修复解释。

# 精读文献清单

通知要求答辩时提供不少于 15 篇精读文献目录。拟重点精读文献如下：

| 序号 | 文献 | 重点关注内容 |
| --- | --- | --- |
| 1 | Yu 等，Spider | 跨数据库 Text-to-SQL benchmark 与复杂 SQL 分类 |
| 2 | Guo 等，IRNet/SemQL | 中间表示降低 SQL 生成难度 |
| 3 | Wang 等，RAT-SQL | schema linking 与关系感知编码 |
| 4 | Gan 等，NatSQL | 面向 Text-to-SQL 的 SQL 中间表示 |
| 5 | Scholak 等，PICARD | 语法约束解码 |
| 6 | Li 等，RESDSQL | schema linking 与 skeleton parsing 解耦 |
| 7 | Pourreza 等，DIN-SQL | 分解式生成与自修正 |
| 8 | Wang 等，MAC-SQL | 多智能体 Text-to-SQL 框架 |
| 9 | Pourreza 等，CHESS | 检索、schema 选择与执行验证 |
| 10 | Pourreza 等，CHASE-SQL | 多路径候选生成与选择 |
| 11 | Shute 等，Pipe Syntax in SQL | SQL 管道式扩展与表达顺序问题 |
| 12 | Li 等，SQL-Factory | 多智能体 SQL 生成流程 |
| 13 | Ni 等，LEVER | 执行反馈验证与候选筛选 |
| 14 | Lei 等，Spider 2.0 | 企业级 Text-to-SQL workflow |
| 15 | Li 等，BIRD | 真实数据库、外部知识与执行效率 |

# 主要参考文献

[1] Zhong V, Xiong C, Socher R. Seq2SQL: Generating Structured Queries from Natural Language using Reinforcement Learning. arXiv:1709.00103, 2017

[2] Yu T, Zhang R, Yang K, et al. Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task. EMNLP, 2018

[3] Guo J, Zhan Z, Gao Y, et al. Towards Complex Text-to-SQL in Cross-Domain Database with Intermediate Representation. ACL, 2019

[4] Wang B, Shin R, Liu X, et al. RAT-SQL: Relation-Aware Schema Encoding and Linking for Text-to-SQL Parsers. ACL, 2020

[5] Gan Y, Chen X, Purver M. Natural SQL: Making SQL Easier to Infer from Natural Language Specifications. Findings of EMNLP, 2021

[6] Scholak T, Schucher N, Bahdanau D. PICARD: Parsing Incrementally for Constrained Auto-Regressive Decoding from Language Models. EMNLP, 2021

[7] Li H, Zhang J, Li C, et al. RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL. AAAI, 2023

[8] Dong X, Zhang C, Ge Y, et al. C3: Zero-shot Text-to-SQL with ChatGPT. arXiv:2307.07306, 2023

[9] Gao D, Wang H, Li Y, et al. Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation. Proceedings of the VLDB Endowment, 2024

[10] Pourreza M, Rafiei D. DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction. NeurIPS, 2023

[11] Wang B, Ren C, Yang J, et al. MAC-SQL: A Multi-Agent Collaborative Framework for Text-to-SQL. COLING, 2025

[12] Pourreza M, Rafiei D. CHESS: Contextual Harnessing for Efficient SQL Synthesis. arXiv:2405.16755, 2024

[13] Pourreza M, Rafiei D, et al. CHASE-SQL: Multi-Path Reasoning and Preference Optimized Candidate Selection in Text-to-SQL. arXiv:2410.01943, 2024

[14] Wang Z, Zhang R, Nie Z, Kim J. Tool-Assisted Agent on SQL Inspection and Refinement in Real-World Scenarios. arXiv:2408.16991, 2024

[15] Li J, Wu T, Mao Y, Gao Y, Feng Y, Liu H. SQL-Factory: A Multi-Agent Framework for High-Quality and Large-Scale SQL Generation. Proceedings of the VLDB Endowment, 2025

[16] Ni A, Iyer S, Radev D, et al. LEVER: Learning to Verify Language-to-Code Generation with Execution. ICML, 2023

[17] Deng M, et al. ReFoRCE: A Text-to-SQL Agent with Self-Refinement, Consensus Enforcement, and Column Exploration. arXiv:2502.00675, 2025

[18] Liu Y, et al. XiYan-SQL: A Novel Multi-Generator Framework For Text-to-SQL. arXiv:2507.04701, 2025

[19] Li J, et al. Can LLM Already Serve as A Database Interface- A Big Bench for Large-Scale Database Grounded Text-to-SQL Evaluation. NeurIPS Datasets and Benchmarks Track, 2023

[20] Lei F, et al. Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows. ICLR, 2025

[21] Shute J, et al. SQL Has Problems. We Can Fix Them: Pipe Syntax In SQL. Proceedings of the VLDB Endowment, 2024

[22] Google Cloud. GoogleSQL Pipe Query Syntax Guide. BigQuery Documentation, 2024

[23] Google Cloud. Pipe Query Syntax Reference. BigQuery Documentation, 2024

[24] Google Cloud. Simplify your SQL with pipe syntax in BigQuery and Cloud Logging. Google Cloud Blog, 2024

[25] Li J, et al. BIRD: A Big Bench for Large-Scale Database Grounded Text-to-SQL Evaluation. NeurIPS Datasets and Benchmarks Track, 2023

[26] Deng X, Sun H, Lees A, et al. TURL: Table Understanding through Representation Learning. Proceedings of the VLDB Endowment, 2020

[27] Hwang W, Yim J, Park S, Seo M. A Comprehensive Exploration on WikiSQL with Table-Aware Word Contextualization. arXiv:1902.01069, 2019

[28] Herzig J, Nowak P K, Muller T, Piccinno F, Eisenschlos J. TaPas: Weakly Supervised Table Parsing via Pre-training. ACL, 2020

[29] Yu T, Yasunaga M, Yang K, et al. SyntaxSQLNet: Syntax Tree Networks for Complex and Cross-Domain Text-to-SQL Task. EMNLP, 2018

[30] Bogin B, Berant J, Gardner M. Representing Schema Structure with Graph Neural Networks for Text-to-SQL Parsing. ACL, 2019

[31] Rubin O, Herzig J, Berant J. Learning To Retrieve Prompts for In-Context Learning. NAACL, 2022

[32] Rajkumar N, Li R, Bahdanau D. Evaluating the Text-to-SQL Capabilities of Large Language Models. arXiv:2204.00498, 2022

[33] Nan L, et al. Enhancing Few-shot Text-to-SQL Capabilities of Large Language Models: A Study on Prompt Design Strategies. arXiv:2305.12586, 2023

[34] Sun R, et al. SQL-PaLM: Improved Large Language Model Adaptation for Text-to-SQL. arXiv, 2023

[35] Liu A, Hu X, Wen L, Yu P S. A Comprehensive Evaluation of ChatGPT's Zero-shot Text-to-SQL Capability. arXiv:2303.13547, 2023

[36] Arora S, et al. Ask Me Anything: A Simple Strategy for Prompting Language Models. ICLR, 2023

[37] Yao S, Zhao J, Yu D, et al. ReAct: Synergizing Reasoning and Acting in Language Models. ICLR, 2023

[38] Schick T, Dwivedi-Yu J, Dessì R, et al. Toolformer: Language Models Can Teach Themselves to Use Tools. NeurIPS, 2023

[39] Madaan A, Tandon N, Gupta P, et al. Self-Refine: Iterative Refinement with Self-Feedback. NeurIPS, 2023

[40] Welleck S, et al. Generating Sequences by Learning to Self-Correct. ICLR, 2023

# 签字页

| 项目 | 签字 |
| --- | --- |
| 研究生签字 |  |
| 指导教师签字 |  |
| 院（系、所）领导签字 |  |
| 日期 | 年    月    日 |

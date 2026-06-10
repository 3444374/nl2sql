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

## Text-to-SQL 方法发展与评测重点变化

Text-to-SQL 早期主要依赖语义解析、序列到序列生成、schema linking 和语法约束解码。Spider 提出跨数据库评测后，研究重点从单库模板匹配转向跨 schema 泛化，模型必须同时处理未知表结构、复杂 SQL 组合和自然语言表达差异。RAT-SQL 通过关系感知编码建模问题、表和列之间的关系；PICARD 在解码阶段做增量语法检查，减少无效 SQL；这类工作说明，Text-to-SQL 的关键问题并不只是语言理解，还包括 schema 组织、输出结构控制和可执行性约束。

中间表示路线是本课题的重要先导。IRNet 提出 SemQL，把自然语言意图和 SQL 实现细节分开，先生成语义结构，再根据 schema 推断 SQL。NatSQL 则进一步减少 `FROM`、`JOIN ON`、`GROUP BY` 等自然语言中不容易直接对应的 SQL 细节，使模型更容易生成可转换的查询表示。这两类工作都表明，标准 SQL 不是唯一的生成目标，适当的中间表示可以降低模型需要一次性预测的结构复杂度。

大语言模型出现后，研究路线从模型结构设计扩展到提示工程、检索增强、多候选生成、执行反馈和候选选择。RESDSQL 将 schema linking 与 skeleton parsing 解耦；DIN-SQL 把任务拆成 schema linking、问题分解、SQL 生成和自修正；CHESS、CHASE-SQL、ReFoRCE、XiYan-SQL 等系统进一步引入检索、列探索、候选排序、共识约束和自修正机制。评测关注点也从 exact match 扩展到 execution accuracy、valid SQL rate、执行效率、交互式修正和企业 workflow 适配。BIRD 强调真实数据库、外部知识和执行效率；Spider 2.0 则把问题推进到多 SQL 方言、项目代码、数据转换和企业分析流程。

这些研究给本课题提供了两点启发。第一，直接生成标准 SQL 在复杂查询中容易受到 SQL 结构细节拖累。第二，单一准确率不足以评价一个自然语言数据库查询系统，后续需要同时考察可执行率、执行一致性、schema linking、修复成功率、修复轮数、成本、延迟和复杂查询分层表现。

## 查询中间表示与 SQL 扩展研究

IRNet/SemQL、NatSQL 和 GoogleSQL Pipe Syntax 是理解 SQL+ 定位的三类近邻工作。SemQL 是树状语义表示，主要目标是隐藏 SQL 实现细节并提升复杂 SQL 生成效果。NatSQL 更接近 SQL 语法，但通过简化集合操作、子查询和连接细节来降低预测难度。GoogleSQL Pipe Syntax 则是数据库语言扩展，它把查询写成自上而下的数据流式 operator 序列，缓解传统 SQL 中书写顺序、作用域和嵌套结构带来的阅读与维护困难。

本课题的 SQL+ 与上述工作有继承关系，但目标不同。SQL+ 借鉴中间表示和线性数据流思想，但不只是为了让模型更容易“生成一条 SQL”。它需要同时服务四个目标：自然语言生成、确定性 SQL 转换、执行反馈定位和局部修复。为此，SQL+ 保留 `FROM -> JOIN -> WHERE -> GROUP -> AGG -> HAVING -> SELECT -> ORDER -> LIMIT` 这样的步骤结构，使错误可以映射到具体操作，而不是只得到一条整体 SQL 的失败信息。

因此，SQL+ 的研究难点不是简单设计一套新语法。它需要在表达能力、简化程度、可转换性和可修复性之间取平衡。语法过于接近 SQL，就难以体现简化和局部诊断价值；语法过于抽象，又会增加转换器和方言适配难度。后续实验也不能只证明 SQL+ 能转换成 SQL，还要评估它是否降低了表达复杂度，是否能支持错误定位和 repair skill 的局部修改。

## 多智能体、执行反馈与候选验证研究

多智能体 Text-to-SQL 研究已经证明，复杂查询生成适合拆解为多个子问题。MAC-SQL 使用 selector、decomposer、refiner 等角色处理 schema 选择、问题分解和错误修正。CHESS 结合信息检索、schema 选择、候选生成和单元测试，强调系统化上下文组织。CHASE-SQL 采用多路径候选生成和偏好优化选择，说明复杂查询往往需要候选比较而不是单次生成。LEVER 通过执行结果学习 verifier，为 language-to-code 候选筛选提供了执行反馈视角。SQL-Factory 从多智能体角度生成大规模高质量 SQL，说明 SQL 生成任务可以通过协作流程控制规模、多样性和成本。

不过，现有多智能体方法多数仍以标准 SQL 为最终诊断对象。执行反馈常被用来筛选候选或触发整条 SQL 重写，而不是把错误定位到某个中间步骤。实际错误还包括能执行但结果语义不一致的情况，例如值链接错误、聚合口径错误、排序遗漏、连接路径冗余和投影列不符合用户意图。数据库报错信息通常较粗，无法直接告诉系统该改 `WHERE`、`JOIN`、`AGG` 还是 `ORDER`。

本课题把 SQL+ 放在多智能体反馈链路的中心位置。Critic Agent 不只判断 SQL 对错，而是输出错误类型、疑似步骤和修复依据；Skill Router 根据错误类型调用 value-linking、ORDER、aggregation、join、projection 等局部 repair skill；Executor 再用执行结果验证候选 patch。这条路线的研究重点不在于堆叠更多 Agent，而在于让每个 Agent 的输入输出可检查，并通过局部修复减少无关结构被改坏的风险。

## 现有研究不足与本课题切入点

综合现有工作，当前仍有四个不足。第一，很多方法已经承认 SQL 结构复杂，但中间表示多面向生成准确率，较少面向执行反馈后的错误定位和局部修复。第二，多智能体框架常强调任务分解和候选选择，但对于“错误来自哪一步、应该调用哪类修复策略”讨论不够充分。第三，现有评测容易集中在 execution accuracy，缺少对 repair success rate、average repair rounds、error localization accuracy、patch minimality、token cost 和 latency 的系统比较。第四，公开 benchmark 与企业数据库之间仍有差距，方言差异、schema 质量和业务语义会影响实际可用性。

本课题的切入点是：把 SQL+ 作为面向生成和修复的中间表示，把多智能体机制落到错误诊断、技能路由、局部修复和执行验证上，并通过多 baseline、消融实验和复杂度分层评估来检验 SQL+ 是否真正带来收益。开题阶段已有实验只证明初步可行性，后续研究需要扩展到更大的公开子集、更多错误类型和更接近达梦 SQL+ 场景的方言适配。

# 研究目标与研究内容

## 研究目标

本课题拟研究一种面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法。核心假设是：当复杂查询先表示为线性、分步、可转换的 SQL+，再结合执行反馈、错误诊断、技能路由和局部 repair skill，系统在复杂查询上的可执行性、可解释性和可修复性会优于直接生成标准 SQL 的路线。

研究目标包括四个方面。第一，设计面向生成和修复的 SQL+ 中间表示，并证明它能够覆盖常见分析查询且可稳定转换为 SQL。第二，研究自然语言到 SQL+ 的生成方法，重点处理 schema linking、join 路径、值链接和聚合意图等难点。第三，研究执行反馈到 SQL+ 局部步骤的错误诊断和修复机制，减少整条 SQL 重写带来的不稳定性。第四，建立多系统对比和消融实验体系，评价 SQL+、多智能体、工具调用、Skill Router 和 repair skill 各自的贡献。

## 拟解决的关键问题

1. SQL+ 为什么有必要。已有 SemQL、NatSQL 和 Pipe Syntax 说明 SQL 结构可以被重写或线性化，但本课题需要进一步证明 SQL+ 不只是“另一种写法”，而是能服务生成、诊断和修复的中间层。
2. SQL+ 如何保持可转换和可修复。SQL+ 必须足够简单，便于模型生成；也必须足够完整，能表达 join、聚合、having、order、limit 等常见结构，并能转换为标准 SQL 或后续达梦 SQL 方言。
3. 多智能体如何避免变成工程堆叠。Agent 的价值应通过可观察的中间输出体现，例如 schema 选择是否正确、Critic 定位是否准确、Router 是否选对 repair skill、patch 是否只修改相关步骤。
4. 如何评价方法是否有效。除 execution accuracy 外，还要比较 SQL+ valid rate、valid SQL rate、repair success rate、average repair rounds、error localization accuracy、schema linking accuracy、complex query accuracy、token cost、latency 和人工可解释性。

## 研究内容一：面向生成和修复的 SQL+ 中间表示设计

本部分研究 SQL+ 的语法边界、表达能力和转换机制。技术难点在于，SQL+ 不能只是把标准 SQL 换一种排列方式。它需要减少自然语言难以直接预测的结构细节，同时保留足够的信息，使转换器能够生成可执行 SQL，并使 Critic Agent 能把错误定位到具体步骤。

拟采用的方法是：以 `FROM` 为查询起点，将 `JOIN`、`WHERE`、`GROUP`、`AGG`、`HAVING`、`SELECT`、`ORDER`、`LIMIT` 组织成线性步骤；在 AST 中显式记录字段、别名、聚合口径、排序引用和连接条件；对 AGG 别名、HAVING/ORDER 引用、join 方向和投影列等容易出错的位置设计规范化规则；后续增加达梦 SQL 方言适配层。

评估方式包括：SQL+ 语法通过率、SQL 转换可执行率、与标准 SQL 的执行一致率、查询结构覆盖率、转换失败类型分布，以及表达复杂度指标。表达复杂度拟从子查询/CTE 数量、嵌套深度、跨子句引用数量、join 路径长度、别名依赖数量和 SQL+ 步骤数等角度统计，用来解释 SQL+ 是否真的降低了生成和修复难度。

## 研究内容二：自然语言到 SQL+ 的生成与 schema/value grounding 方法

本部分研究自然语言问题如何稳定生成 SQL+。技术难点主要来自 schema linking、value linking、join path planning 和 aggregation planning。真实问题往往不会显式给出表名、字段名、主外键路径和聚合口径，模型容易生成字段错、连接错、过滤值错或聚合维度错的 SQL+。

拟采用的方法是：构建 schema 与字段值检索工具，为 Schema Agent 提供表、列、外键、候选值和样例数据；使用 Planner Agent 先形成查询步骤草图，再由 SQL+ Generator 生成 SQL+；对复杂查询引入候选生成和执行验证，让系统比较多个 SQL+ 候选，而不是依赖一次输出。对比方法包括 Direct NL2SQL、NL2SQL+ 单 Agent、分解式 NL2SQL、多智能体标准 SQL、多智能体 SQL+ 和 SQL+ 工具增强生成。

评估方式包括：execution accuracy、valid SQL rate、SQL+ valid rate、schema linking accuracy、value linking accuracy、join path accuracy、aggregation accuracy、complex query accuracy、token cost 和 latency。实验会按 simple、medium、hard 查询分层，单独观察多表 join、聚合、having、top-k、时间范围和隐含业务条件等场景。

## 研究内容三：执行反馈驱动的 SQL+ 层错误诊断与局部修复

本部分研究如何从数据库执行反馈和结果异常中定位错误，并在 SQL+ 层做局部修复。难点在于，数据库报错信息常常只说明“字段不存在”或“类型不匹配”，不能直接说明自然语言语义哪里偏了；更困难的是 SQL 能执行但结果错误的情况，例如过滤值不匹配、排序方向错、缺少 paid 条件、COUNT 口径不对或投影列多余。

拟采用的方法是：由 Critic Agent 输出结构化诊断，包括错误类型、疑似 SQL+ 步骤、证据和修复建议；由 Skill Router 将诊断路由到 value-linking、ORDER、aggregation、join、projection 等 repair skill；repair skill 生成有限候选 patch，并由 Executor 执行验证。修复优先在 SQL+ 层进行，只在必要时对最终 SQL 做辅助检查。gold-derived differences 只用于离线可行性验证，不作为真实自主修复指标。

评估方式包括：repair success rate、average repair rounds、error localization accuracy、router accuracy、patch minimality、post-repair valid SQL rate、post-repair execution accuracy，以及 SQL+ 层修复与 SQL 层整体重写的对比。当前小规模结果显示，SQL+ 非 gold 单 Refiner 为 4/13，Direct SQL 非 gold Refiner 为 6/14，而 SQL+ Skill Router + Repair Skills v3 在当前 13 条已知失败样例上达到 13/13。该结果只能说明小样例闭环可行，后续需要扩展到更多无报错语义错误和复合错误。

## 研究内容四：多系统对比、消融实验与公开子集迁移评估

本部分重点解决“如何证明 SQL+ 和多智能体机制确实有贡献”的问题。技术难点在于，LLM 本身能力、prompt 设计、schema 信息、执行反馈和 repair skill 都可能影响结果。如果只展示一个完整系统，很难说明改进来自 SQL+，还是来自模型或提示词。

拟设置多组对比方法：Direct NL2SQL、NL2SQL+ 单 Agent、DAIL-SQL 风格 few-shot baseline、DIN-SQL 风格分解 baseline、MAC-SQL 风格标准 SQL 多智能体、Multi-agent NL2SQL+、Multi-agent NL2SQL+ + Feedback、SQL 层整体修复 baseline，以及 SQL+ Skill Router + Repair Skills。消融实验包括去掉 SQL+、去掉多智能体、去掉 Schema/value lookup、去掉 Critic Agent、去掉 Skill Router、只做 SQL 层修复、只做单一 repair skill、关闭执行验证等。

评估数据分三层推进。第一层是自建企业订单分析样例，用于控制变量和错误类型分析。第二层是 Spider 小规模受支持子集，用于验证 SQL+ 表达和转换机制在公开 benchmark 上的初步迁移能力。当前 Spider smoke test 只覆盖 `concert_singer` 数据库中的 20 条受支持查询，结果为 20/20，不能表述为完整 Spider 成绩。第三层后续扩展到 BIRD 子集和达梦 SQL 方言样例，用来检验真实 schema、外部知识和方言差异带来的影响。

# 研究方案与可行性分析

## 研究方案

研究会按由小到大的路线推进。先定义 SQL+ 最小语法子集，实现 parser 和 SQL 转换器；再构建企业订单样例库，覆盖单表查询、多表连接、过滤、排序、聚合、分组和 Top-K。随后设计 Direct NL2SQL 与 NL2SQL+ 两类 baseline，运行大模型生成实验，并对 SQL+ 失败样例做错误类型分析。在此基础上，继续构建 Critic Agent 结构化诊断，设计 value-linking、ORDER、aggregation、join、projection 五类局部 repair skill，并通过 Skill Router 把 Critic 输出路由到不同 repair skill。后续再扩展无报错语义错诊断，接入 Spider/BIRD 小规模子集，并适配达梦 SQL 方言。

## 当前初步实验

当前使用自建企业订单分析样例库，包括 customers、products、orders、order_items 四张表，构造 30 条自然语言查询、30 条 SQL+ 标准样例和 15 条错误修正样例，执行环境为 SQLite 内存数据库，模型使用 gpt-5-mini，评估方式为执行生成 SQL 并与标准 SQL 执行结果比较。

SQL+ 转换实验结果如下：SQL+ 样例数 30 条，SQL+ 语法通过 30/30，转换 SQL 可执行 30/30，与标准 SQL 执行结果一致 30/30。这个结果至少说明，当前 SQL+ 不是只停留在概念层面的表达设计。它已经能通过 parser 和转换器形成可执行 SQL，并在自建样例库上得到一致执行结果。

单 Agent baseline 结果如下：Direct NL2SQL 在 30 条样例上执行结果一致 16/30；NL2SQL+ prompt v1 为 13/30；NL2SQL+ prompt v2 为 17/30。SQL+ prompt v2 略高于 Direct NL2SQL，但差距不大。这个结果也提醒我们，仅把输出格式从 SQL 改成 SQL+ 并不足以解决问题。SQL+ 的价值需要通过错误定位、工具调用和局部修复机制体现出来。

SQL+ prompt v2 的 13 条失败样例主要是语义错误，而不是语法错误。错误分布为 filter/value-linking 5 条、ORDER/LIMIT 3 条、aggregation planning 2 条、schema/join planning 2 条、projection mismatch 1 条。这为后续 Critic Agent 错误诊断和 Skill Router 修复提供了实验依据。

反馈修正对比实验结果如下：SQL+ 诊断辅助 Refiner 在 13 条失败样例上达到 13/13，但该实验使用 gold-derived differences，只能说明“结构化反馈 -> SQL+ 层局部修复 -> 执行验证”的链路可行，不能作为真实自主修复结果。更接近真实场景的非 gold 实验中，SQL+ 单 Refiner v2 为 4/13，Direct SQL 单 Refiner 为 6/14，Schema-Critic-Refiner 初版为 3/13，Step-wise Critic-Refiner 为 3/13。进一步引入 Critic Agent、Skill Router、五类局部 repair skill 和执行验证后，Skill Router v3 在 13 条 SQL+ 失败样例上达到 SQL+ 有效 13/13、SQL 可执行 13/13、修复成功 13/13。

Repair Skill 分治实验结果如下：value-linking repair skill 3/3，ORDER repair skill 3/3，aggregation repair skill 3/3，join repair skill 3/3，projection repair skill 1/1。这个结果比较符合预期：不同错误类型需要不同的局部修复策略。整体重生成虽然简单，但容易改动无关部分；局部修复的范围更小，也更容易解释。

为验证公开 benchmark 子集迁移性，当前还完成了 Spider dev 的小规模受支持子集 smoke test。实验选择 `concert_singer` 数据库中当前 SQL+ 子集可覆盖的 20 条查询，覆盖 count、select、where、order、limit、group、aggregation 和 simple join。结果为 SQL+ 有效 20/20，SQL 可执行 20/20，执行结果一致 20/20。该结果只能作为公开 benchmark 子集迁移可行性证据，不能等同于完整 Spider benchmark 成绩。

## 可行性分析

从技术可行性看，当前已经完成 SQL+ parser、SQL+ 到 SQL 转换器、自建数据集、baseline 实验、错误诊断、五类 repair skill 和 Skill Router v3 端到端实验。SQL+ 表达与转换链路稳定，30/30 查询可执行且结果一致。SQL+ 层局部修复链路可行，诊断辅助 Refiner 达到 13/13。真实非 gold 条件下，Skill Router + Repair Skills v3 在 13 条已知 SQL+ 失败样例上达到 13/13，高于 SQL+ 单 Refiner 的 4/13。Spider 小规模受支持子集达到 20/20，说明当前 SQL+ 子集具备初步公开 benchmark 迁移可行性。

从数据和实验条件看，当前已有自建可控数据集、公开 Spider 子集适配脚本和完整实验记录。后续可继续扩展 Spider/BIRD 子集，逐步增加复杂 SQL 结构。从工程实现看，当前脚本、报告、数据和 project skills 已在 GitHub 中留痕，具备跨电脑复现基础。从应用场景看，达梦 SQL+ 方言适配可作为后续扩展目标，先通过标准 SQL/SQLite 验证核心机制，再迁移到达梦数据库场景。

当前不足也需要明确。自建数据集规模还比较小，主要用于开题阶段可行性验证；Spider smoke test 只是受支持子集验证，不是完整 benchmark 跑分；SQL+ 语法子集还没有覆盖复杂子查询、集合运算、窗口函数、复杂布尔条件等结构。非 gold 反馈修正目前仍依赖 Critic 的错误类型识别，后续需要增强无报错语义错的诊断能力。达梦 SQL 方言适配也还没有完成。

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

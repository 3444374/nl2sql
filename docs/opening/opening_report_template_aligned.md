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

自然语言数据库查询的目标，是让用户不必直接掌握 SQL，也能够通过自然语言完成数据检索、统计分析和辅助决策。随着企业数据规模扩大和大语言模型能力提升，Text-to-SQL 已成为数据库智能交互的研究方向。业务人员、管理人员和普通分析人员往往以自然语言表达需求，例如“统计上个月每个地区的销售额”“找出消费金额最高的客户”等。如果系统能够将这类需求稳定转换为可执行查询，就能降低数据库使用门槛，提高企业数据分析效率。

然而，真实场景中的 Text-to-SQL 仍然有不少困难。大语言模型可以生成语法上看似合理的 SQL，但复杂 schema、多表 join、聚合口径、排序逻辑、字段值匹配和数据库方言差异常常导致结果错误。更具体地说，SQL 一旦生成错误，错误位置并不总是容易定位。一个查询可能同时涉及 `FROM`、`JOIN`、`WHERE`、`GROUP BY`、`HAVING`、`ORDER BY` 等多个部分，最终执行失败或结果不一致时，很难直接判断应修正哪一个局部结构。

标准 SQL 的表达顺序也会增加生成和修复难度。用户理解查询时通常先确定数据源，再逐步考虑过滤、连接、分组、聚合和最终输出；而标准 SQL 的书写顺序并不完全等同于查询构造过程。GoogleSQL Pipe Syntax 的研究提出，可以在 SQL 生态内引入管道式表达，使查询按照数据流顺序逐步展开。这说明查询表达形式本身会影响可读性、可维护性，也可能影响大模型生成和反馈修正的稳定性。

基于上述问题，本课题不把目标限定为“做一个自然语言转 SQL 的工程 Demo”，而是研究一条更适合诊断和修复的生成路线：

```text
自然语言问题 -> SQL+ 中间表示 -> 可执行 SQL -> 执行反馈 -> SQL+ 层局部诊断与修复
```

这里的 SQL+ 不是替代标准 SQL，而是作为自然语言和最终 SQL 之间的中间查询表示。它将复杂查询拆成线性步骤，使错误更容易映射回具体步骤；多智能体部分则负责意图理解、schema linking、错误诊断、技能路由和执行验证，使修复过程不再完全依赖一次性整体重写。

本课题的意义不在于再实现一个自然语言转 SQL 的演示系统，而在于检验一个更具体的问题：当复杂查询先被写成线性、分步的 SQL+ 表达后，大模型的生成、诊断和修复是否更容易被控制。若这一假设成立，SQL+ 可以成为自然语言查询和数据库方言之间的中间层；多智能体也不再只是多个提示词的串联，而是围绕 schema 检索、错误定位、修复路由和执行验证进行分工。这一思路对达梦 SQL+、国产数据库智能交互和企业数据分析场景都有一定应用价值。

# 国内外研究现状

## Text-to-SQL 方法发展

早期 Text-to-SQL 主要依赖语义解析、模板匹配、Seq2Seq、schema linking 和语法约束解码等技术。其核心问题是把自然语言问题映射到数据库 schema，并生成满足语法和语义要求的 SQL。Spider 数据集推动了跨数据库 Text-to-SQL 研究，使模型不仅要处理单一数据库，还要面对未知 schema 和复杂 SQL 结构。

在大模型之前，研究重点主要集中在 schema linking、结构化中间表示和约束解码。例如 RAT-SQL 通过关系感知编码建模表、列和问题之间的关系；IRNet 使用 SemQL 作为中间表示，减少直接生成复杂 SQL 的难度；NatSQL 进一步提出面向 Text-to-SQL 的通用中间表示；PICARD 则在解码阶段进行增量语法约束，降低无效 SQL 的比例。这些工作说明，Text-to-SQL 的难点不仅在语言理解，也在于如何控制输出结构。

大语言模型出现后，Text-to-SQL 逐渐转向基于上下文学习、提示工程和候选选择的方法。DAIL-SQL 关注问题表示、样例选择和样例组织方式；DIN-SQL 将任务拆解为 schema linking、问题分解、SQL 生成和自修正等阶段；C3、RESDSQL、CHESS、CHASE-SQL、XiYan-SQL 和 ReFoRCE 等系统进一步引入检索增强、多候选生成、候选排序、自修正、执行反馈和列探索机制。这些工作说明，模型能力只是 Text-to-SQL 的一部分。schema 信息的组织方式、复杂问题的拆解方法，以及执行反馈能否被正确利用，都会影响最终 SQL 的质量。

但是，现有方法多数仍以标准 SQL 为最终生成和修复对象。模型可能生成语法正确但语义错误的 SQL；schema linking 错误会导致表和字段选择错误；复杂 join、聚合、排序和隐含业务条件容易出错；执行反馈经常被用于整体重生成，而不是定位到某个局部结构进行修复。因此，仅依赖“自然语言 -> SQL”的单轮生成，很难满足复杂查询场景下的稳定性要求。

## Benchmark 与真实场景挑战

Text-to-SQL benchmark 从 Spider 发展到 BIRD、Spider 2.0，研究重点也从单纯 SQL 生成逐渐扩展到真实企业环境。BIRD 更关注真实数据库、外部知识和执行效率；Spider 2.0 强调企业级 Text-to-SQL workflow，包括复杂数据环境、多 SQL 方言、项目代码和真实业务分析流程。

这些 benchmark 说明，自然语言数据库查询已经不是单轮文本生成任务。系统需要理解 schema、业务知识、方言文档、执行反馈和数据分析流程。对本课题而言，更稳妥的路线是先验证 SQL+ 表达、转换和修复链路是否成立，再逐步扩大到更多数据库和更多 SQL 结构。因此，本文把 Spider smoke test 定位为公开数据集子集迁移验证，而不是完整排行榜评测。

## SQL 扩展与 SQL+ 表达

SQL 是数据库查询的事实标准，但在复杂查询中容易出现表达结构紧凑、局部关系交织和错误定位困难等问题。嵌套子查询、多表 join、聚合过滤、窗口函数和方言差异都会增加大模型生成难度。GoogleSQL Pipe Syntax 提出在不脱离 SQL 生态的基础上引入管道式表达，使查询更接近数据处理流程。

本课题中的 SQL+ 借鉴管道式表达思想，但定位更加具体：它作为 Text-to-SQL 的中间查询表示，用于降低生成和修复难度。与主要面向人工书写体验的 SQL 扩展不同，本课题更关注 SQL+ 能否为大模型提供稳定的中间结构，使 Critic Agent 可以在步骤级别定位错误，使 Repair Skill 可以在有限范围内修改候选查询。当前 SQL+ 的基本设计包括：以 `FROM` 作为查询起点，按照数据流逐步展开；将 `JOIN`、`WHERE`、`GROUP`、`AGG`、`HAVING`、`SELECT`、`ORDER`、`LIMIT` 拆成局部步骤；保留每一步的可解释性；通过规则转换器转换为标准 SQL 或后续达梦 SQL 方言执行。

## 多智能体 Text-to-SQL 与反馈修正

已有多智能体 Text-to-SQL 研究表明，把任务拆分给不同角色有助于处理复杂查询。例如 MAC-SQL 将任务拆成 selector、decomposer、refiner 等角色；CHESS 使用信息检索、schema 选择、候选生成和单元测试等专门 Agent；CHASE-SQL 采用多路径候选生成和选择机制；Tool-Assisted Agent 引入 retriever 和 detector 来处理执行不报错但语义不匹配的问题；SQLCritic 关注 clause-wise critic 和结构化反馈修正。

SQL-Factory 也与本课题有关。它通过 Generation Team、Expansion Team 和 Management Team 生成高质量、大规模 SQL 查询，说明 SQL 生成任务可以拆成多个协作环节，并通过自动化流程同时控制多样性、规模和成本。它更偏向 SQL 工作负载与训练数据生成，本课题更关注自然语言查询到 SQL+ 的中间表示、执行反馈诊断和局部 repair skill。

总体来看，现有多智能体方法多数仍在标准 SQL 层修复。标准 SQL 的结构比较紧凑，一个错误可能同时影响多个子句，修复时往往只能整体重写。SQL+ 把查询拆成线性步骤，更适合按照“错误类型 -> 局部步骤 -> repair skill”的方式处理。本课题关注的不是形式上的多 Agent 串联，而是让不同 Agent 围绕 SQL+ 中间表示承担可检查的职责。

## 当前研究存在的问题

综合现有研究，当前仍存在以下问题：第一，复杂 SQL 的结构对大模型生成不友好，标准 SQL 层错误定位和局部修复困难。第二，现有 Text-to-SQL 方法常把执行反馈用于整体重生成，缺少面向中间表示的局部修复机制。第三，多智能体方法如果只是多个 prompt 串联，并不一定提升效果，关键在于角色拆分、工具调用、错误类型路由和执行验证。第四，SQL 方言和企业场景增加了真实应用难度，需要一种既能保持 SQL 生态兼容，又能服务生成和修复的中间表达。

# 研究目标与研究内容

## 研究目标

本课题拟设计 SQL+ 查询表达与转换机制，构建面向 SQL+ 的多智能体自然语言数据库查询生成与反馈修正框架。系统流程包括自然语言理解、schema linking、SQL+ 生成、SQL 转换、执行验证、错误诊断、Skill Router 和局部 repair skill。最终目标是在自建数据集、公开 Text-to-SQL 子集和达梦数据库场景中验证该方法的有效性，重点考察执行正确率、SQL+ 有效率、修复成功率、错误定位能力和系统可解释性。

## 研究内容一：SQL+ 查询表达与转换机制

研究 SQL+ 的最小可行语法子集，包括 `FROM`、`JOIN`、`WHERE`、`GROUP`、`AGG`、`HAVING`、`SELECT`、`ORDER`、`LIMIT` 等操作。当前已实现 SQL+ parser 和 SQL+ 到标准 SQL 的规则转换器，并在自建企业订单数据集上验证了单表查询、多表 join、聚合、排序和 Top-K 等常见结构。后续将继续扩展 projection、复杂布尔条件、子查询替代表达和达梦 SQL 方言适配。

## 研究内容二：面向 SQL+ 的多智能体生成框架

计划构建以下模块：Intent Agent 负责理解自然语言问题；Schema Agent 负责选择相关表、字段、join 路径和候选字段值；SQL+ Generator Agent 负责生成 SQL+ 查询；Translator Agent 负责将 SQL+ 转换为 SQL；Critic Agent 负责根据执行反馈定位错误；Skill Router 负责按错误类型选择修复技能；Repair Skill / Refiner 负责局部修复 SQL+；Executor 负责执行和验证候选结果。该框架要求每个 Agent 都产生可记录的中间结果，便于比较不同方法、追踪错误来源，也便于后续复现实验。

## 研究内容三：基于执行反馈的 SQL+ 层局部修正

当前实验中将 SQL+ 生成错误初步划分为五类：value-linking 错误、ORDER/LIMIT 错误、aggregation 错误、join 错误和 projection 错误。当前已实现 value-linking、ORDER、aggregation、join、projection 五类 repair skill。后续将进一步研究复合错误下多个 repair skill 的调用顺序，以及 SQL 能执行但结果语义不匹配时的诊断稳定性。

## 研究内容四：原型系统与实验评估

系统流程如下：自然语言问题首先生成 SQL+；SQL+ 转换为 SQL 后执行；执行反馈和结果预览进入 Critic Agent；Critic 输出错误类型和局部步骤诊断；Skill Router 选择合适的 repair skill；repair skill 生成候选 patch；Executor 执行验证，最终输出 SQL+、SQL、查询结果和修复解释。评估指标包括 Execution Accuracy、Valid SQL Rate、SQL+ Valid Rate、Repair Success Rate、Average Repair Rounds、Schema Linking Accuracy、复杂查询准确率、Token Cost 和 Latency。

# 研究方案与可行性分析

## 研究方案

本课题按由小到大的路线推进。第一步，设计 SQL+ 最小语法子集，实现 parser 和 SQL 转换器。第二步，构建企业订单样例库，覆盖单表查询、多表连接、过滤、排序、聚合、分组和 Top-K。第三步，设计 Direct NL2SQL 与 NL2SQL+ 两类 baseline，并运行大模型生成实验。第四步，对 SQL+ 失败样例进行错误类型分析，构建 Critic Agent 结构化诊断。第五步，设计 value-linking、ORDER、aggregation、join、projection 五类局部 repair skill。第六步，实现 Skill Router，将 Critic 输出路由到不同 repair skill。第七步，扩展无报错语义错诊断，接入 Spider/BIRD 小规模子集，后续适配达梦 SQL 方言。

## 当前初步实验

当前使用自建企业订单分析样例库，包括 customers、products、orders、order_items 四张表，构造 30 条自然语言查询、30 条 SQL+ 标准样例和 15 条错误修正样例，执行环境为 SQLite 内存数据库，模型使用 gpt-5-mini，评估方式为执行生成 SQL 并与标准 SQL 执行结果比较。

SQL+ 转换实验结果如下：SQL+ 样例数 30 条，SQL+ 语法通过 30/30，转换 SQL 可执行 30/30，与标准 SQL 执行结果一致 30/30。该实验说明，当前 SQL+ 不是停留在概念层面的表达设计，而是已经能够通过 parser 和转换器形成可执行 SQL，并在自建样例库上得到一致执行结果。

单 Agent baseline 结果如下：Direct NL2SQL 在 30 条样例上执行结果一致 16/30；NL2SQL+ prompt v1 为 13/30；NL2SQL+ prompt v2 为 17/30。SQL+ prompt v2 略高于 Direct NL2SQL，但差距不大。这说明仅把输出格式从 SQL 改成 SQL+ 并不足以解决问题，SQL+ 的价值需要通过错误定位、工具调用和局部修复机制体现。

SQL+ prompt v2 的 13 条失败样例主要是语义错误，而不是语法错误。错误分布为 filter/value-linking 5 条、ORDER/LIMIT 3 条、aggregation planning 2 条、schema/join planning 2 条、projection mismatch 1 条。这为后续 Critic Agent 错误诊断和 Skill Router 修复提供了实验依据。

反馈修正对比实验结果如下：SQL+ 诊断辅助 Refiner 在 13 条失败样例上达到 13/13，但该实验使用 gold-derived differences，只能说明“结构化反馈 -> SQL+ 层局部修复 -> 执行验证”的链路可行，不能作为真实自主修复结果。更接近真实场景的非 gold 实验中，SQL+ 单 Refiner v2 为 4/13，Direct SQL 单 Refiner 为 6/14，Schema-Critic-Refiner 初版为 3/13，Step-wise Critic-Refiner 为 3/13。进一步引入 Critic Agent、Skill Router、五类局部 repair skill 和执行验证后，Skill Router v3 在 13 条 SQL+ 失败样例上达到 SQL+ 有效 13/13、SQL 可执行 13/13、修复成功 13/13。

Repair Skill 分治实验结果如下：value-linking repair skill 3/3，ORDER repair skill 3/3，aggregation repair skill 3/3，join repair skill 3/3，projection repair skill 1/1。该结果说明，不同错误类型需要不同的局部修复策略。整体重生成虽然简单，但容易改动无关部分；局部修复的范围更小，也更容易解释。

为验证公开 benchmark 子集迁移性，当前还完成了 Spider dev 的小规模受支持子集 smoke test。实验选择 `concert_singer` 数据库中当前 SQL+ 子集可覆盖的 20 条查询，覆盖 count、select、where、order、limit、group、aggregation 和 simple join。结果为 SQL+ 有效 20/20，SQL 可执行 20/20，执行结果一致 20/20。该结果只能作为公开 benchmark 子集迁移可行性证据，不能等同于完整 Spider benchmark 成绩。

## 可行性分析

从技术可行性看，当前已经完成 SQL+ parser、SQL+ 到 SQL 转换器、自建数据集、baseline 实验、错误诊断、五类 repair skill 和 Skill Router v3 端到端实验。SQL+ 表达与转换链路稳定，30/30 查询可执行且结果一致。SQL+ 层局部修复链路可行，诊断辅助 Refiner 达到 13/13。真实非 gold 条件下，Skill Router + Repair Skills v3 在 13 条已知 SQL+ 失败样例上达到 13/13，高于 SQL+ 单 Refiner 的 4/13。Spider 小规模受支持子集达到 20/20，说明当前 SQL+ 子集具备初步公开 benchmark 迁移可行性。

从数据和实验条件看，当前已有自建可控数据集、公开 Spider 子集适配脚本和完整实验记录。后续可继续扩展 Spider/BIRD 子集，逐步增加复杂 SQL 结构。从工程实现看，当前脚本、报告、数据和 project skills 已在 GitHub 中留痕，具备跨电脑复现基础。从应用场景看，达梦 SQL+ 方言适配可作为后续扩展目标，先通过标准 SQL/SQLite 验证核心机制，再迁移到达梦数据库场景。

当前不足也需要明确。第一，当前自建数据集规模较小，主要用于开题阶段可行性验证。第二，Spider smoke test 是受支持子集验证，不是完整 benchmark 跑分。第三，SQL+ 语法子集尚未覆盖复杂子查询、集合运算、窗口函数、复杂布尔条件等结构。第四，非 gold 反馈修正仍依赖 Critic 错误类型识别，后续需要增强无报错语义错诊断能力。第五，达梦 SQL 方言适配尚未完成。

# 已有工作局限

当前实验结果主要用于开题阶段的可行性论证，不能直接解释为完整系统性能。第一，自建订单数据集规模较小，查询类型仍以常见分析查询为主。第二，Spider 实验只覆盖 `concert_singer` 数据库中当前 SQL+ 子集支持的 20 条查询，不是完整 Spider benchmark 跑分。第三，Skill Router v3 的 13/13 结果来自已知 SQL+ 失败样例，后续还需要在更大样本、更复杂复合错误和无报错语义错误上验证。第四，当前系统主要使用 SQLite 验证标准 SQL 执行链路，达梦 SQL 方言适配尚未完成。上述限制不会否定现阶段结果，但决定了后续研究不能停留在小样例修复实验上。

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

本课题预期形成以下成果：第一，提出一种面向大模型生成友好的 SQL+ 中间查询表示，明确其最小语法子集、转换规则和与标准 SQL/达梦 SQL 的关系。第二，构建面向 SQL+ 的多智能体自然语言数据库查询生成与反馈修正框架，包括 Schema Agent、Critic Agent、Skill Router、Repair Skill 和 Executor。第三，形成基于执行反馈的 SQL+ 层局部修复机制，覆盖 value-linking、ORDER、aggregation、join、projection 等典型错误类型。第四，完成原型系统和实验评估，在自建数据集、Spider/BIRD 子集和达梦数据库场景中验证方法有效性。第五，形成完整论文、实验记录、开题答辩材料和可复现实验脚本。

预期技术指标包括：SQL+ 转标准 SQL 的可执行率保持较高水平；在自建数据集上完成 Direct NL2SQL、NL2SQL+、多智能体 NL2SQL+ 和反馈修正方法对比；在典型错误类型上验证局部 repair skill 的修复能力；在公开 benchmark 子集上完成 SQL+ 表达与转换迁移性验证；在达梦数据库场景下完成核心查询类型的方言适配测试。

# 预期创新点

本课题的预期创新主要有三点。

第一，设计面向大模型生成与修复的 SQL+ 中间查询表示。与直接生成标准 SQL 不同，SQL+ 将查询拆成线性步骤，使数据源、连接、过滤、聚合、排序和投影等操作更容易被定位和修改。

第二，构建面向 SQL+ 的多智能体查询生成与诊断框架。Schema Agent、Critic Agent、Skill Router、Repair Skill 和 Executor 分别处理 schema linking、错误诊断、修复路由、局部修正和执行验证，避免把所有问题压缩到单个 prompt 中。

第三，研究基于执行反馈的 SQL+ 层局部修正机制。系统不直接重写最终 SQL，而是把执行错误、结果异常和语义偏差映射回 SQL+ 局部步骤，再调用对应 repair skill 生成候选修复。这样可以控制修复范围，也能给出更清楚的修复解释。

# 精读文献清单

通知要求答辩时提供不少于 15 篇精读文献目录。拟重点精读文献如下：

| 序号 | 文献 | 重点关注内容 |
| --- | --- | --- |
| 1 | Yu 等，Spider | 跨数据库 Text-to-SQL benchmark 与复杂 SQL 分类 |
| 2 | Guo 等，IRNet/SemQL | 中间表示降低 SQL 生成难度 |
| 3 | Wang 等，RAT-SQL | schema linking 与关系感知编码 |
| 4 | Gan 等，NatSQL | 面向 Text-to-SQL 的 SQL 中间表示 |
| 5 | Scholak 等，PICARD | 语法约束解码 |
| 6 | Gao 等，DAIL-SQL | LLM Text-to-SQL prompt 设计 |
| 7 | Pourreza 等，DIN-SQL | 分解式生成与自修正 |
| 8 | Wang 等，MAC-SQL | 多智能体 Text-to-SQL 框架 |
| 9 | Pourreza 等，CHESS | 检索、schema 选择与执行验证 |
| 10 | Pourreza 等，CHASE-SQL | 多路径候选生成与选择 |
| 11 | Shute 等，Pipe Syntax in SQL | SQL 管道式扩展与表达顺序问题 |
| 12 | Li 等，SQL-Factory | 多智能体 SQL 生成流程 |
| 13 | Chen 等，SQLCritic | clause-wise critic 与反馈修正 |
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

[9] Gao D, Wang H, Li Y, et al. Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation. arXiv:2308.15363, 2023

[10] Pourreza M, Rafiei D. DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction. arXiv:2304.11015, 2023

[11] Wang B, Ren C, Yang J, et al. MAC-SQL: A Multi-Agent Collaborative Framework for Text-to-SQL. arXiv:2312.11242, 2023

[12] Pourreza M, Rafiei D. CHESS: Contextual Harnessing for Efficient SQL Synthesis. arXiv:2405.16755, 2024

[13] Pourreza M, Rafiei D, et al. CHASE-SQL: Multi-Path Reasoning and Preference Optimized Candidate Selection in Text-to-SQL. arXiv:2410.01943, 2024

[14] Wang Z, Zhang R, Nie Z, Kim J. Tool-Assisted Agent on SQL Inspection and Refinement in Real-World Scenarios. arXiv:2408.16991, 2024

[15] Li J, Wu T, Mao Y, Gao Y, Feng Y, Liu H. SQL-Factory: A Multi-Agent Framework for High-Quality and Large-Scale SQL Generation. Proceedings of the VLDB Endowment, 2025

[16] Chen J, et al. SQLCritic: Correcting Text-to-SQL Generation via Clause-wise Critic. arXiv:2503.07996, 2025

[17] Deng M, et al. ReFoRCE: A Text-to-SQL Agent with Self-Refinement, Consensus Enforcement, and Column Exploration. arXiv:2502.00675, 2025

[18] Liu Y, et al. XiYan-SQL: A Novel Multi-Generator Framework For Text-to-SQL. arXiv:2507.04701, 2025

[19] Li J, et al. Can LLM Already Serve as A Database Interface? A Big Bench for Large-Scale Database Grounded Text-to-SQL Evaluation. arXiv:2305.03111, 2023

[20] Lei F, et al. Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows. arXiv:2411.07763, 2024

[21] Shute J, et al. SQL Has Problems. We Can Fix Them: Pipe Syntax In SQL. Proceedings of the VLDB Endowment, 2024

[22] Google Cloud. GoogleSQL Pipe Query Syntax Guide. BigQuery Documentation, 2024

[23] Google Cloud. Pipe Query Syntax Reference. BigQuery Documentation, 2024

[24] Google Cloud. Simplify your SQL with pipe syntax in BigQuery and Cloud Logging. Google Cloud Blog, 2024

[25] Li J, et al. BIRD: A Big Bench for Large-Scale Database Grounded Text-to-SQL Evaluation. arXiv:2305.03111, 2023

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

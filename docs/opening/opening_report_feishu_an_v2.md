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

本报告按照硕士研究生论文开题报告模板组织，主要包括课题背景、研究意义、国内外研究现状、研究目标与研究内容、研究方案与技术路线、实验设计与初步结果、可行性分析、进度安排、预期成果和参考文献等内容。根据开题答辩要求，后续将继续补充不少于 40 篇相关文献阅读记录，并单独整理不少于 15 篇精读文献目录。当前版本重点根据已有 PPT、实验大纲和项目实验结果，对研究现状、研究内容和实验设计进行研究化表述，避免把研究内容写成单纯工程步骤。

---

# 一、课题背景、目的和意义

自然语言数据库查询希望让用户用自然语言完成数据检索、统计分析和辅助决策。企业中的查询需求往往以业务语言提出，例如“统计上个月每个地区的销售额”“找出消费金额最高的客户”“查询已支付订单中金额最高的 10 个订单”。如果系统能够稳定地将这类问题转换为可执行查询，业务人员和数据分析人员就不必先掌握完整 SQL 语法，才能使用数据库完成分析工作。

近几年，大语言模型推动了 Text-to-SQL 的快速发展，但真实场景中的自然语言数据库查询仍然存在明显困难。模型可能生成语法上可执行、表面上合理的 SQL，但在复杂 schema、多表 join、聚合口径、排序逻辑、字段值匹配、隐含业务条件和数据库方言差异上出现偏差。更关键的是，SQL 一旦出错，错误位置并不总是清楚。一个查询可能同时涉及 FROM、JOIN、WHERE、GROUP BY、HAVING、SELECT、ORDER BY 等多个部分，最终执行失败或结果不一致时，很难直接判断应该修复哪一个局部结构。

标准 SQL 的表达顺序也会增加生成和修复难度。用户理解查询时通常先确定数据源，再逐步考虑连接、过滤、分组、聚合、投影和排序；而标准 SQL 的书写顺序并不完全等同于这个查询构造过程。GoogleSQL Pipe Syntax 的研究提出，可以在 SQL 生态内引入管道式表达，使查询按照数据流顺序逐步展开。该思路说明，查询表达形式本身可能影响可读性、可维护性，也可能影响大模型生成和反馈修正的稳定性。

基于上述问题，本课题不将目标限定为“自然语言直接生成 SQL”的工程演示，而是研究一条更适合诊断和修复的生成路线：

```text
自然语言问题 -> SQL+ 中间表示 -> 可执行 SQL -> 执行反馈 -> SQL+ 层局部诊断与修复
```

其中，SQL+ 不是替代标准 SQL 的新数据库语言，而是放在自然语言和最终 SQL 之间的中间查询表示。它把复杂查询拆成线性、分步、可转换、可检查的结构，使错误更容易映射到具体步骤。多智能体部分则承担意图理解、schema linking、错误诊断、技能路由、局部修复和执行验证等任务，使系统不再完全依赖单次整体重写。

本课题的研究意义体现在三个方面。第一，从数据库交互角度看，SQL+ 与多智能体反馈修正可以降低非专业用户使用数据库的门槛。第二，从 Text-to-SQL 方法角度看，本课题将中间表示从“生成辅助”扩展到“诊断和修复辅助”，有助于研究可解释、可修复的自然语言数据库查询生成机制。第三，从国产数据库智能化角度看，SQL+ 可作为标准 SQL 与达梦 SQL 方言之间的中间层，为后续达梦数据库自然语言查询和 SQL 方言适配提供可验证的原型基础。

---

# 二、国内外研究现状

## 2.1 Text-to-SQL：从语义解析到大模型生成

早期 Text-to-SQL 主要把任务看作语义解析问题，目标是将自然语言问题映射为形式化 SQL 查询。Seq2SQL、SyntaxSQLNet、RAT-SQL 等工作分别从序列生成、SQL 结构建模和 schema linking 入手，解决自然语言词语、表、列和外键关系之间的匹配问题。Spider 数据集提出跨数据库评测后，研究重点从单库模板匹配转向跨 schema 泛化。模型不仅要理解问题文本，还要在未见过的数据库中识别相关表列、连接路径和复杂 SQL 结构。

在大模型出现之前，研究重点集中在 schema linking、结构化表示和约束解码。RAT-SQL 通过关系感知编码建模问题、表和列之间的关系；IRNet 使用 SemQL 作为中间表示，减少模型直接生成复杂 SQL 的压力；NatSQL 保留较多 SQL 外观，但简化 FROM、JOIN、GROUP BY 等难以从自然语言直接预测的部分；PICARD 在解码过程中进行增量语法约束，以减少无效 SQL。这些工作共同说明，Text-to-SQL 的困难不仅在语言理解，也在于输出结构控制。

大语言模型出现后，Text-to-SQL 逐渐转向基于上下文学习、提示工程、检索增强和候选选择的方法。DAIL-SQL 研究问题表示、样例选择和样例组织；DIN-SQL 将任务拆解为 schema linking、问题分解、SQL 生成和自修正；CHESS、CHASE-SQL、ReFoRCE、XiYan-SQL 等系统进一步引入 schema 检索、多候选生成、候选排序、自修正、执行反馈和列探索。这些工作表明，大模型生成 SQL 的效果不仅取决于模型能力，也取决于 schema 信息如何组织、复杂问题如何拆解、候选如何验证。

现有方法仍然存在不足。多数工作以标准 SQL 作为最终生成和修复对象，模型生成语法正确但语义错误的 SQL 时，执行反馈往往只用于整体重生成，而不是定位到某个局部结构进行修复。对于 value-linking 错误、聚合口径错误、join 路径错误、ORDER/LIMIT 遗漏和 projection mismatch 等局部错误，整体重写容易改坏原本正确的部分。本课题引入 SQL+ 中间表示，正是为了将错误定位和局部修复从最终 SQL 层提前到更线性的中间表示层。

## 2.2 Benchmark：从标准评测到真实工作流

Text-to-SQL benchmark 的发展体现了任务复杂度的提升。Spider 关注跨数据库泛化，要求模型在未见过的 schema 上生成复杂 SQL。BIRD 更强调真实数据库、外部知识和执行效率。Spider 2.0 将任务进一步推进到企业级 Text-to-SQL workflow，涉及复杂数据环境、多 SQL 方言、项目代码、数据转换和真实业务分析流程。

这些 benchmark 表明，自然语言数据库查询已经不只是单轮文本生成任务，而是需要理解 schema、业务知识、方言文档、执行反馈和数据分析流程的综合任务。相应地，评价指标也不应只停留在 exact match 或 execution accuracy。对真实系统而言，还需要关注 valid SQL rate、schema linking accuracy、value linking accuracy、join path accuracy、执行时间、token cost、修复轮数、错误定位准确率和失败类型分布。

本课题的实验设计也遵循这一趋势。开题阶段不直接追求完整 Spider 或 BIRD 排行榜成绩，而是先在自建可控数据集和 Spider 小规模子集上验证 SQL+ 表达、转换、端到端生成和局部修复链路是否成立，再逐步扩展到更多数据库、更多 SQL 结构和达梦 SQL 方言适配。

## 2.3 中间表示与 SQL 语言扩展

中间表示是缓解 Text-to-SQL 复杂度的重要方向。SemQL 通过树形语义结构隐藏部分 SQL 实现细节，使模型先生成较抽象的查询结构。NatSQL 通过保留 SQL 外观并简化连接、分组和嵌套结构，降低模型预测负担。这类方法已经证明，中间表示可以降低直接生成标准 SQL 的难度。

不过，SemQL 和 NatSQL 主要服务于初次生成，其设计目标并不完全覆盖执行失败后的步骤级错误定位和局部修复。SemQL 的树形结构与最终 SQL 执行错误之间不一定存在稳定的一步对应关系；NatSQL 更接近 SQL，但仍主要关注从自然语言到可转换查询表示的生成过程。相比之下，本课题的 SQL+ 更强调“生成、转换、诊断、局部修复”四个目标的统一。

GoogleSQL Pipe Syntax 与 SQL+ 也有联系。Pipe Syntax 是 SQL 生态内的扩展，目标是让查询按照数据流方式线性展开，提升 SQL 的阅读、编写和维护体验。本课题借鉴其线性化思想，但研究对象不是人工 SQL 书写体验，而是大模型生成和反馈修正。SQL+ 将 FROM、JOIN、WHERE、GROUP、AGG、HAVING、SELECT、ORDER、LIMIT 等操作拆成步骤，使每一步都可以被 parser 检查、被 converter 转换、被 Critic 定位、被 Repair Skill 修改。

因此，SQL+ 的价值不能简单概括为“更短”或“更像自然语言”。当前初步实验也显示，SQL+ 的平均 token 数并不低于标准 SQL。更准确的表述是：SQL+ 用显式步骤边界换取更低的跨子句耦合和别名依赖，从而为错误定位、技能路由和局部修复提供结构化载体。

## 2.4 多智能体 Text-to-SQL 与反馈修正

近年来，agentic Text-to-SQL 系统开始将自然语言查询任务拆解为多个角色或工具调用过程。MAC-SQL 使用 selector、decomposer、refiner 等角色处理 schema 选择、问题分解和错误修正。CHESS 结合 schema 检索、上下文组织、候选生成和单元测试。CHASE-SQL 采用多路径候选生成和偏好优化选择。Tool-Assisted Agent、LEVER、SQLCritic 等工作强调执行反馈、候选验证或 clause-wise 诊断。SQL-Factory 则从多智能体数据生成角度说明，SQL 生成任务可以被拆成多个协作环节，通过自动化流程控制质量、规模和成本。

这些研究说明，多智能体的价值不在于简单增加 prompt 数量，而在于让不同模块承担可观察、可评估的子任务。例如 Schema Agent 需要给出相关表列和连接路径，Critic Agent 需要说明错误类型和诊断证据，Skill Router 需要选择合适的修复技能，Repair Skill 需要产生局部候选 patch，Executor 需要用数据库执行结果验证候选。若每个模块的输出不可检查，多智能体容易退化为多个提示词串联，并不一定提升效果。

现有多智能体方法大多仍在标准 SQL 层诊断和修复。执行反馈常被用于筛选候选或整条 SQL 重写，而不是映射到一个稳定的中间步骤。本课题的切入点是把 SQL+ 放在多智能体修复链路中心，使 Critic 的诊断、Router 的路由、Repair Skill 的 patch 和 Executor 的验证都围绕 SQL+ 步骤展开。

## 2.5 现有研究不足与本课题切入点

综合已有研究，可以归纳出四个不足。第一，中间表示研究多关注初次生成准确率，对执行反馈后的错误定位和局部修复关注不足。第二，多智能体 Text-to-SQL 多关注任务分解、候选生成和候选选择，较少将错误诊断结果映射到可执行的局部修复技能。第三，现有评测常以 execution accuracy 为主，对 repairability 的评价不够充分。第四，公开 benchmark 与企业数据库环境之间存在差距，方法需要在可控数据集、公开子集和具体数据库方言之间逐步验证。

本课题据此选择以下切入点：将 SQL+ 作为面向生成和修复的中间表示，把多智能体机制落到 schema/value grounding、错误诊断、技能路由、局部修复和执行验证上，并使用多系统对比和多维指标评估 SQL+ 是否真正提高了可生成性、可解释性和可修复性。

---

# 三、研究目标与拟解决的关键问题

## 3.1 研究目标

本课题拟研究一种面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法。核心假设是：相比直接生成标准 SQL，先生成线性、分步、可转换的 SQL+ 中间表示，再结合执行反馈、错误诊断、技能路由和局部 repair skill，能够提高复杂查询的可执行性、可解释性和可修复性。

本课题的具体目标包括：

1. 设计 SQL+ 最小语法子集和 AST 表示，实现 SQL+ 到标准 SQL 的确定性转换，并为后续达梦 SQL 方言适配保留接口。
2. 构建自然语言到 SQL+ 的生成流程，研究 schema linking、value linking、join path selection 和查询步骤规划对 SQL+ 生成的影响。
3. 构建 `Critic Agent -> Skill Router -> Repair Skill -> Executor` 的反馈修正闭环，将执行反馈和结果异常映射到 SQL+ 局部步骤。
4. 建立多维实验评估体系，比较 Direct SQL、SQL+、SemQL-style proxy、NatSQL-style proxy、Pipe-style proxy、SQL 层整体修复和 SQL+ 层局部修复等方法。
5. 在自建数据集、Spider 小规模子集和后续达梦 SQL 场景中验证方法的可行性和边界。

## 3.2 拟解决的关键问题

第一个问题是 SQL+ 的必要性。已有 SemQL、NatSQL 和 Pipe Syntax 都说明标准 SQL 可以被重构，但本课题需要进一步证明 SQL+ 不是另一种写法，而是面向生成、转换、诊断和修复的一体化中间表示。这个问题需要通过表达复杂度、转换成功率、错误定位和修复指标共同回答。

第二个问题是 SQL+ 的语法边界。SQL+ 过于接近标准 SQL，简化效果有限；过于抽象，又会增加转换和方言适配难度。因此需要确定一个既能覆盖常见分析查询，又能转换为 SQL，还能映射执行错误的语法子集。

第三个问题是多智能体的可验证性。Agent 的价值必须体现在可观察输出上，例如 schema 选择是否正确，Critic 是否定位到正确步骤，Router 是否选择正确 repair skill，patch 是否只修改相关步骤，Executor 是否过滤无效候选。否则多智能体只会增加 token 成本和延迟。

第四个问题是评价方法。除 execution accuracy 外，还需要比较 SQL+ valid rate、valid SQL rate、schema linking accuracy、value linking accuracy、join path accuracy、error localization accuracy、router accuracy、repair success rate、average repair rounds、patch minimality、token cost、latency、IR parse time 和 IR-to-SQL conversion time。这样才能判断 SQL+ 的修复收益是否足以抵消它引入的额外生成和转换成本。

---

# 四、研究内容

## 4.1 面向生成和修复的 SQL+ 中间表示设计

本部分研究 SQL+ 的语法边界、AST 表示、转换规则和与其他中间表示的差别。技术难点在于，SQL+ 需要同时满足四个要求：足够线性，便于自然语言映射；足够完整，能够表达 join、filter、aggregation、having、order、limit 等常见分析查询；足够确定，能够转换为标准 SQL 或后续达梦 SQL；足够可诊断，能够把错误映射到具体步骤。

拟采用的方法是：以 FROM 为查询起点，将 JOIN、WHERE、GROUP、AGG、HAVING、SELECT、ORDER、LIMIT 组织成线性步骤；在 AST 中显式记录表别名、字段引用、聚合别名、连接条件和排序引用；对 AGG 别名、HAVING/ORDER 引用、join 方向、projection 列等易错位置设计规范化规则。转换器采用确定性规则，将 SQL+ 转换为可执行 SQL，并保留步骤到 SQL 子句的映射关系。

评估上，本部分不只检查 SQL+ 能否转换成功，还要比较不同表示的复杂度和可修复性。对比对象包括标准 SQL、SemQL-style proxy、NatSQL-style proxy、Pipe-style proxy 和 SQL+。指标包括 token 长度、步骤/子句数、嵌套深度、跨子句引用数量、别名依赖数量、IR parse time、IR-to-SQL conversion time、转换成功率、SQL 可执行率和错误步骤可定位率。

## 4.2 自然语言到 SQL+ 的生成与 grounding 方法

本部分研究从自然语言问题生成 SQL+ 的方法。技术难点在于，模型不仅要生成合法语法，还要正确选择表列、连接路径、过滤值、聚合口径和排序依据。当前初步实验显示，SQL+ prompt v2 在 30 条样例上达到 17/30，略高于 Direct NL2SQL 的 16/30，但差距不大。这说明单纯更换输出格式不足以解决问题，必须引入更明确的 schema/value grounding 和候选验证。

拟采用的方法是构建可观察的生成流程。Schema Agent 负责检索相关表、字段、外键关系和值域样例；Planner Agent 将问题拆成 SQL+ 步骤草图；SQL+ Generator 生成候选 SQL+；Translator 将 SQL+ 转换为 SQL；Executor 执行候选并返回错误或结果摘要。对于多候选生成，记录每个候选的 token 消耗、生成延迟、SQL+ 合法性和执行结果，由选择策略挑选更可靠的候选。

评估上，本部分比较 Direct NL2SQL、NL2SQL+ single agent、decomposition-based NL2SQL、standard SQL multi-agent、multi-agent NL2SQL+ 等方法。指标包括 execution accuracy、valid SQL rate、SQL+ valid rate、schema linking accuracy、value linking accuracy、join path accuracy、candidate pass rate、prompt tokens、completion tokens、total latency 和不同复杂度查询上的表现。

## 4.3 执行反馈驱动的 SQL+ 层错误诊断与局部修复

本部分研究如何把数据库执行错误、结果异常和用户意图偏差映射回 SQL+ 步骤，并通过局部 repair skill 修复。技术难点在于，很多错误并不会触发数据库报错。例如过滤值错误、聚合口径错误、排序遗漏、projection mismatch 都可能产生可执行但语义错误的 SQL。仅凭报错信息无法完成诊断，需要结合问题文本、schema、SQL+ 步骤、执行结果和候选差异。

拟采用的方法是构建 `Critic Agent -> Skill Router -> Repair Skill -> Executor` 闭环。Critic Agent 输出错误类型、可疑步骤和诊断证据；Skill Router 根据错误类型和 SQL+ 结构特征选择 value-linking、ORDER、aggregation、join、projection 等 repair skill；每个 repair skill 只修改相关步骤，生成候选 patch；Executor 执行候选 SQL 并比较结果，筛掉语法错误和执行错误。该机制避免整条 SQL 重写，尽量减少对正确部分的破坏。

评估上，本部分设置 SQL 层整体重写、SQL+ 单 Refiner、Schema-Critic-Refiner、Step-wise Critic-Refiner、SQL+ Skill Router + Repair Skills 等对照组。指标包括 repair success rate、average repair rounds、error localization accuracy、router accuracy、patch minimality、unchanged-correct-step rate、SQL executable rate、token cost 和 latency。

## 4.4 面向公开数据集与达梦场景的实验评估体系

本部分研究如何把自建可控实验扩展到公开数据集和达梦数据库场景。技术难点在于，公开 benchmark 的 SQL 结构和 schema 多样性更强，而达梦 SQL 方言又可能带来函数、分页、日期类型和语法兼容问题。若只在自建小数据集上验证，难以说明方法具有迁移潜力；若直接追求完整 benchmark，又容易把开题阶段的工作变成大规模工程复现。

拟采用逐步扩展策略。第一阶段使用自建订单分析数据集验证 SQL+ 表达、转换、生成和修复链路。第二阶段使用 Spider 小规模受支持子集验证公开 benchmark 迁移可行性，并明确区分 gold-derived conversion smoke test 与 fresh end-to-end generation。第三阶段扩展到更多 Spider 数据库和 BIRD 子集，观察 schema linking、join path 和复杂 SQL 结构的泛化情况。第四阶段适配达梦 SQL 方言，重点检查日期函数、分页语法、类型转换和方言函数差异。

评估上，本部分将建立分层实验：动机测试回答为什么需要 SQL+ 和多智能体；可行性测试验证 SQL+ parser、translator、executor 和 repair skill 是否可运行；对比实验比较不同中间表示和修复策略；消融实验分析去掉 Critic、Router、Repair Skill 或 Executor 后性能如何变化；迁移实验评估 Spider/BIRD/达梦场景下的泛化能力。

---

# 五、技术路线

本课题的技术路线如下：

```text
用户自然语言问题
        ↓
Schema / Value Grounding
        ↓
SQL+ 查询步骤规划与生成
        ↓
SQL+ Parser / Translator
        ↓
标准 SQL / 达梦 SQL
        ↓
Executor 执行与结果反馈
        ↓
Critic Agent 错误诊断
        ↓
Skill Router 选择修复技能
        ↓
Repair Skill 生成局部 patch
        ↓
重新转换与执行验证
        ↓
最终 SQL / 查询结果 / 修复解释
```

该路线分为三个阶段推进。第一阶段，完成 SQL+ 语法子集、parser、AST 和 SQL 转换器，验证 SQL+ 能否稳定转换为可执行 SQL。第二阶段，构建自然语言到 SQL+ 的生成流程，并比较 Direct SQL、SQL+、NatSQL-style proxy、SemQL-style proxy 等表示的生成成本和执行效果。第三阶段，引入 Critic Agent、Skill Router 和多类 Repair Skill，研究 SQL+ 层局部修复相对 SQL 整体重写的收益，并扩展到公开数据集和达梦 SQL 方言。

---

# 六、实验设计与初步结果

## 6.1 实验总体设置

开题阶段实验的目标不是追求完整 benchmark 跑分，而是验证研究方向是否具有可行性。当前主要使用自建企业订单分析样例库，包含 customers、products、orders、order_items 四张表，覆盖单表查询、多表连接、过滤、排序、聚合、分组、Top-K 和部分复杂统计查询。模型实验主要使用 gpt-5-mini，执行环境为 SQLite 内存数据库。gold SQL 只用于离线评估，不进入非 gold 反馈修正模型输入。

| 项目 | 内容 |
| --- | --- |
| 自建数据库 | 企业订单分析样例库 |
| 表数量 | 4 张表：customers、products、orders、order_items |
| 自然语言查询样例 | 30 条 |
| SQL+ 标准样例 | 30 条 |
| 规则修正样例 | 15 条 |
| 已知 SQL+ 失败样例 | 13 条 |
| 执行环境 | SQLite 内存数据库 |
| 模型 | gpt-5-mini |
| 评估方式 | 执行生成 SQL，并与 gold SQL 执行结果比较 |

## 6.2 SQL+ 表达与转换可行性

该实验验证 SQL+ 作为中间表示是否可解析、可转换、可执行。实验流程为：人工构造 SQL+ 标准样例，使用 SQL+ parser 解析为 AST，再由转换器生成标准 SQL，最后在 SQLite 上执行并与 gold SQL 执行结果比较。

| 指标 | 结果 |
| --- | ---: |
| SQL+ 样例数 | 30 |
| SQL+ 语法通过 | 30/30 |
| 转换 SQL 可执行 | 30/30 |
| 与 gold SQL 执行结果一致 | 30/30 |

初步结论：SQL+ 已经形成“表达 -> 解析 -> 转换 -> 执行 -> 结果比较”的最小闭环，说明它不是停留在概念层面的表达设计，而是具备原型验证基础。

## 6.3 初次生成对比：Direct SQL 与 NL2SQL+

该实验比较自然语言直接生成 SQL 与自然语言生成 SQL+ 后再转换为 SQL 的效果。实验使用同一批 30 条问题、同一 schema 和相同评估脚本。

| 方法 | 样例数 | SQL/SQL+ 有效 | SQL 可执行 | 执行结果一致 |
| --- | ---: | ---: | ---: | ---: |
| Direct NL2SQL | 30 | - | 30/30 | 16/30 |
| NL2SQL+ prompt v1 | 30 | 30/30 | 30/30 | 13/30 |
| NL2SQL+ prompt v2 | 30 | 30/30 | 30/30 | 17/30 |

初步结论：SQL+ prompt v2 略高于 Direct NL2SQL，但差距很小，不能据此宣称 SQL+ 在初次生成阶段显著更准。这个结果反而说明，SQL+ 的主要价值不应写成“让初次生成更短、更准”，而应放在步骤边界、错误定位和局部修复上。

## 6.4 中间表示复杂度对比

该实验用于回答“为什么使用 SQL+，而不是直接 SQL、SemQL、NatSQL 或 Pipe-style 表示”。实验在同一批 30 条自建订单分析样例上，构造 Standard SQL、SQL+、SemQL-style proxy、NatSQL-style proxy 和 Pipe-style proxy，并统计 token、步骤/子句数、嵌套深度、别名依赖和跨子句引用。

这里的 SemQL-style、NatSQL-style 和 Pipe-style 是 controlled proxy，只用于受控比较表达形态，不代表完整复现原系统或 GoogleSQL Pipe Syntax。

| 表示形式 | 平均 token | 平均步骤/子句 | 平均嵌套深度 | 平均别名依赖 | 平均跨子句引用 | 转换成功 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Standard SQL | 31.5333 | 5.9000 | 0.6667 | 2.0333 | 2.3333 | 30/30 |
| SQL+ | 35.0333 | 6.1333 | 0.6667 | 0.7000 | 1.0000 | 30/30 |
| SemQL-style proxy | 50.5667 | 10.7333 | 3.6667 | 0.9000 | 1.2000 | N/A |
| NatSQL-style proxy | 31.5000 | 5.4333 | 0.9667 | 1.3667 | 1.6667 | N/A |
| Pipe-style proxy | 40.8000 | 6.1333 | 0.6667 | 1.3667 | 1.6667 | N/A |

初步结论：SQL+ 并不比标准 SQL 更短，平均 token 反而更高。因此，SQL+ 的价值不能用“长度压缩”解释。更合适的结论是：SQL+ 用显式步骤边界降低别名依赖和跨子句引用，使错误更容易落到具体步骤上，也更适合后续局部 repair skill。

## 6.5 中间表示生成成本与执行效果

为了进一步比较不同表示的生成代价，本实验使用同一模型、同一批 30 条样例和同一评价脚本，比较 Direct SQL、SQL+、NatSQL-style proxy 和 SemQL-style proxy 的表示有效率、SQL 可执行率、执行一致率、总 token 和平均延迟。

| 方法 | 表示有效 | SQL 可执行 | 执行一致 | 平均总 token | 平均延迟 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Direct SQL | 30/30 | 30/30 | 12/30 | 599.1667 | 6.5851s |
| SQL+ | 28/30 | 28/30 | 14/30 | 813.0333 | 9.2197s |
| NatSQL-style proxy | 30/30 | 30/30 | 13/30 | 740.7667 | 6.2802s |
| SemQL-style proxy | 30/30 | 25/30 | 12/30 | 1028.9667 | 9.9684s |

初步结论：SQL+ 的 execution match 为 14/30，略高于其他组，但差距不足以支持显著更准的结论。同时，SQL+ 的 token 和 latency 高于 Direct SQL 与 NatSQL-style proxy，说明步骤化表达会带来生成成本。因此，后续需要重点验证 SQL+ 在修复阶段的收益能否抵消生成阶段的额外开销。

## 6.6 反馈修正对比实验

该实验比较 SQL 层整体修复、SQL+ 单 Refiner、简单 Critic-Refiner 和 SQL+ Skill Router + Repair Skills。这里的“修复成功”指修复后的 SQL 可以执行，并且执行结果与 gold SQL 一致。

| 方法 | 初始失败样例 | SQL+ 有效 | SQL 可执行 | 修复成功 | 说明 |
| --- | ---: | ---: | ---: | ---: | --- |
| SQL+ 诊断辅助 Refiner | 13 | 13/13 | 13/13 | 13/13 | 使用 gold-derived differences，只验证链路可行 |
| SQL+ 非 gold Refiner v2 | 13 | 13/13 | 12/13 | 4/13 | 只使用执行反馈和粗粒度诊断 |
| Direct SQL 非 gold Refiner | 14 | - | 14/14 | 6/14 | 直接修标准 SQL |
| Schema-Critic-Refiner | 13 | 13/13 | 13/13 | 3/13 | 诊断未充分转化为修复动作 |
| Step-wise Critic-Refiner | 13 | 13/13 | 12/13 | 3/13 | 步骤级诊断更细，但 patch 范围仍不稳定 |
| SQL+ Skill Router + Repair Skills v3 | 13 | 13/13 | 13/13 | 13/13 | Critic 路由到五类局部 repair skill |

初步结论：诊断辅助 Refiner 的 13/13 只能说明结构化反馈链路可行，不能作为真实自主修复结果。非 gold 条件下，单 Refiner 和简单 Critic 串联效果有限。引入 Skill Router 和局部 Repair Skill 后，当前已知失败集上的修复成功率提升明显，说明“错误定位 -> 技能路由 -> 局部 patch -> 执行验证”的机制比整体重写更可控。但该结果仍是 13 条 known-failure set 上的小规模验证，不能表述为完整 benchmark 结果。

## 6.7 Repairability 指标补充

为了避免只看修复成功率，本课题进一步统计错误定位、patch minimality、修复轮数和 token 成本。

| 方法 | 样例数 | 修复成功 | 定位准确率 | 严格最小 patch 率 | 平均 patch minimality | 平均修复轮数 | 平均 repair token |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct SQL Refiner | 14 | 6/14 | 0.8571 | 0.8571 | 0.8571 | 1.0000 | 1609.3571 |
| SQL+ Critic Router Skills | 13 | 13/13 | 0.7692 | 0.9231 | 0.9744 | 2.2308 | 3813.9231 |
| Direct SQL Refiner overlap | 9 | 4/9 | 0.8889 | 0.8889 | 0.8889 | 1.0000 | 1583.2222 |
| SQL+ Critic Router Skills overlap | 9 | 9/9 | 0.7778 | 0.8889 | 0.9630 | 2.3333 | 4001.7778 |

初步结论：SQL+ 路线的收益主要体现在修复成功率和局部 patch 可控性上，代价是更高的 repair token 和更多修复轮数。旧 Direct SQL Refiner 与 SQL+ Critic 运行没有完整记录 API latency，因此当前不能直接比较完整端到端修复延迟。后续需要用统一脚本重新记录 latency、token 和 repair rounds，验证 SQL+ 的修复收益是否足以抵消额外成本。

## 6.8 Repair Skill 分治实验

| Repair Skill | 样例数 | 修复成功 | 典型问题 |
| --- | ---: | ---: | --- |
| value-linking | 3 | 3/3 | 候选值替换、日期边界、状态值过滤 |
| ORDER | 3 | 3/3 | 排序字段、排序方向、Top-K 约束 |
| aggregation | 3 | 3/3 | COUNT 口径、GROUP 维度、AGG 别名、ORDER/HAVING 引用 |
| join | 3 | 3/3 | JOIN 方向、冗余 JOIN、缺失 JOIN、过滤条件遗漏 |
| projection | 1 | 1/1 | 输出列多、列少或列顺序错误 |

初步结论：不同错误类型适合不同的局部修复策略。value-linking 更依赖字段值检索和候选值验证，ORDER 更依赖排序字段和方向判断，aggregation 更依赖分组维度和聚合口径检查，join 更依赖连接路径和表关系约束，projection 更关注 SELECT 输出是否与问题要求一致。这支持将修复能力沉淀为可路由的 repair skill，而不是让单个 Refiner 处理所有错误。

## 6.9 Spider 小规模公开子集实验

为验证 SQL+ 不只适用于自建数据集，当前引入 Spider dev 的 `concert_singer` 数据库进行小规模测试。该实验分为两类，必须明确边界。

第一类是 conversion smoke test。它从 Spider gold SQL 出发，人工改写为 SQL+，再由 SQL+ 转换回 SQL，并比较执行结果。该实验只验证 SQL+ 表达和转换器对公开 benchmark 一部分查询结构的覆盖性，不是端到端生成准确率。

第二类是 fresh end-to-end generation。它只输入自然语言问题和 schema，由 SQL+ Generator 生成 SQL+，再经 parser、Translator 和 Executor 执行。后续的 `Skill Router -> semantic repair skill` 使用问题词义、schema 字段、SQL+ 结构、parser 反馈和执行反馈进行局部修复，gold SQL 只用于最终离线 execution-match 评价。

| 实验 | 样例数 | SQL+ 有效 | SQL 可执行 | 执行一致 | 说明 |
| --- | ---: | ---: | ---: | ---: | --- |
| Spider SQL+ conversion smoke test | 20 | 20/20 | 20/20 | 20/20 | gold SQL -> SQL+ -> SQL，只验证转换覆盖性 |
| Spider SQL+ e2e v2 | 20 | 19/20 | 17/20 | 13/20 | 早期 SQL+ prompt 与 Refiner 流程 |
| Spider SQL+ e2e v3 fresh | 20 | 19/20 | 19/20 | 19/20 | question + schema -> SQL+，未使用 post-hoc repair |
| Spider SQL+ e2e v3 + semantic repair | 20 | 20/20 | 20/20 | 20/20 | 同一次 fresh 输出经 Router 调用 semantic repair skill 后重评估 |

初步结论：Spider 小子集结果说明当前 SQL+ 表达和转换器可以覆盖公开 benchmark 中一部分简单和中等查询结构，fresh e2e 结果说明 SQL+ 生成链路已经跑通，semantic repair skill 说明问题词义、schema 字段、SQL+ 步骤结构和执行反馈可以共同支持局部修复。但以上结果都不是完整 Spider benchmark 成绩，也不是多数据库泛化结论。当前本地只具备 `concert_singer` 数据库，后续需要补齐更多 Spider 数据库后再做多库验证。

---

# 七、可行性分析

从技术实现看，当前已经完成 SQL+ parser、SQL+ 到 SQL 转换器、自建数据集、baseline 实验、错误诊断、五类 repair skill 和 Skill Router v3 端到端实验。SQL+ 表达与转换链路在 30 条自建样例上达到 30/30 执行一致；Spider conversion smoke test 在 20 条受支持子集上达到 20/20；fresh e2e 生成在同一 Spider 子集上达到 19/20，经 semantic repair 后达到 20/20。这说明课题的基本链路具备可运行基础。

从实验条件看，项目已经形成可复现实验脚本、实验日志、PPT、开题报告和项目级 skill。自建数据集可以用于机制验证，Spider 子集可以用于公开 benchmark 迁移性验证，后续可逐步补充 BIRD 子集和达梦 SQL 方言样例。

同时，当前不足也需要明确。第一，自建数据集规模较小，主要用于开题阶段可行性验证。第二，Spider 结果仅覆盖 `concert_singer` 20 条小子集，不能表述为完整 benchmark 分数。第三，SQL+ 语法子集尚未覆盖复杂子查询、集合运算、窗口函数和复杂布尔条件。第四，SQL+ 修复路线的 token 成本和修复轮数较高，后续需要补齐统一 latency 记录。第五，达梦 SQL 方言适配尚未完成，需要在日期函数、分页语法、类型转换和方言函数上继续扩展。

因此，当前结果足以支撑开题阶段的可行性论证，但还不能作为最终系统性能结论。后续研究应重点扩大样例规模、增强 schema/value grounding、补齐多库 Spider/BIRD 验证，并完成达梦 SQL 方言适配。

---

# 八、预期创新点

## 8.1 面向生成与修复统一设计的 SQL+ 中间表示

不同于只用于初次生成的中间表示，本课题将 SQL+ 设计为同时服务于生成、转换、诊断和局部修复的中间查询表示。SQL+ 通过线性步骤降低跨子句耦合，使错误能够更清楚地映射到 FROM、JOIN、WHERE、AGG、SELECT、ORDER 等局部步骤。

## 8.2 面向 SQL+ 的多智能体反馈修正框架

本课题构建由 Schema Agent、SQL+ Generator、Translator、Executor、Critic Agent、Skill Router 和 Repair Skill 组成的多智能体框架。其重点不是增加 Agent 数量，而是让每个 Agent 产生可检查的中间结果，并通过执行反馈形成闭环。

## 8.3 基于 Skill Router 的 SQL+ 层局部 repair skill 机制

本课题将错误修复拆分为 value-linking、ORDER、aggregation、join、projection 等局部 skill。Critic Agent 负责定位错误类型和可疑步骤，Skill Router 负责选择修复技能，Repair Skill 只修改相关 SQL+ 步骤，Executor 负责验证候选 patch。该机制有助于控制修复范围，提高修复过程的可解释性和可复现性。

## 8.4 面向 repairability 的多维评估体系

本课题不只关注 execution accuracy，还引入 error localization accuracy、router accuracy、patch minimality、average repair rounds、token cost、latency、IR parse time 和 IR-to-SQL conversion time 等指标。通过这些指标，可以更具体地判断 SQL+ 是否真正提升了错误定位和局部修复能力。

---

# 九、后续实验计划与进度安排

## 9.1 后续实验计划

| 实验组 | 目的 | 主要指标 |
| --- | --- | --- |
| Direct SQL / NL2SQL+ 对比 | 比较直接生成和 SQL+ 生成 | execution accuracy、valid rate、token、latency |
| SemQL/NatSQL/Pipe-style proxy 对比 | 比较中间表示形态 | token、嵌套深度、别名依赖、跨子句引用、转换成本 |
| SQL 层整体修复 / SQL+ 局部修复 | 比较修复策略 | repair success、repair rounds、patch minimality、token cost |
| 消融实验 | 验证 Critic、Router、Skill、Executor 的贡献 | 模块移除后的性能下降、失败类型变化 |
| Spider/BIRD/达梦子集 | 验证迁移和方言适配 | exec match、方言错误、schema linking、泛化失败类型 |

## 9.2 进度安排

| 阶段 | 时间 | 主要工作 |
| --- | --- | --- |
| 第一阶段 | 开题后 1-2 个月 | 完善 SQL+ 语法子集，扩展无报错语义错误诊断，补充 projection/SELECT 样例 |
| 第二阶段 | 第 3-4 个月 | 完善 Schema Agent、Critic Agent 和 Skill Router，加入 schema/value lookup、SQL+ parser、SQL executor 等工具能力 |
| 第三阶段 | 第 5-6 个月 | 接入更多 Spider/BIRD 小规模子集，构造 SQL+ 改写数据，扩展多数据库、多难度实验 |
| 第四阶段 | 第 7-8 个月 | 适配达梦 SQL 方言，测试日期函数、分页语法、类型转换和方言函数规则 |
| 第五阶段 | 第 9-10 个月 | 完成消融实验、结果分析、论文初稿和原型系统整理 |
| 第六阶段 | 第 11-12 个月 | 根据导师和中期反馈修改系统与论文，完成论文定稿、答辩材料和代码归档 |

---

# 十、预期成果

本课题预期形成以下成果：

1. 一种面向大模型生成与局部修复的 SQL+ 中间查询表示，包括语法子集、AST、转换规则和与标准 SQL/达梦 SQL 的关系说明。
2. 一套面向 SQL+ 的多智能体自然语言数据库查询生成与反馈修正框架，包括 Schema Agent、Critic Agent、Skill Router、Repair Skill 和 Executor。
3. 一组基于执行反馈的 SQL+ 层局部修复方法，覆盖 value-linking、ORDER、aggregation、join、projection 等典型错误类型。
4. 一套多维实验评估体系，覆盖 execution accuracy、valid rate、repair success、error localization、patch minimality、token cost 和 latency 等指标。
5. 一个可复现实验原型，包括自建数据集、Spider 小子集实验、实验日志、开题材料和后续达梦 SQL 方言适配脚本。

---

# 十一、精读文献清单

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

---

# 十二、主要参考文献

[1] Zhong V, Xiong C, Socher R. Seq2SQL: Generating Structured Queries from Natural Language using Reinforcement Learning. arXiv:1709.00103, 2017.

[2] Yu T, Zhang R, Yang K, et al. Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task. EMNLP, 2018.

[3] Guo J, Zhan Z, Gao Y, et al. Towards Complex Text-to-SQL in Cross-Domain Database with Intermediate Representation. ACL, 2019.

[4] Wang B, Shin R, Liu X, et al. RAT-SQL: Relation-Aware Schema Encoding and Linking for Text-to-SQL Parsers. ACL, 2020.

[5] Gan Y, Chen X, Purver M. Natural SQL: Making SQL Easier to Infer from Natural Language Specifications. Findings of EMNLP, 2021.

[6] Scholak T, Schucher N, Bahdanau D. PICARD: Parsing Incrementally for Constrained Auto-Regressive Decoding from Language Models. EMNLP, 2021.

[7] Li H, Zhang J, Li C, et al. RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL. AAAI, 2023.

[8] Dong X, Zhang C, Ge Y, et al. C3: Zero-shot Text-to-SQL with ChatGPT. arXiv:2307.07306, 2023.

[9] Gao D, Wang H, Li Y, et al. Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation. Proceedings of the VLDB Endowment, 2024.

[10] Pourreza M, Rafiei D. DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction. NeurIPS, 2023.

[11] Wang B, Ren C, Yang J, et al. MAC-SQL: A Multi-Agent Collaborative Framework for Text-to-SQL. COLING, 2025.

[12] Pourreza M, Rafiei D. CHESS: Contextual Harnessing for Efficient SQL Synthesis. arXiv:2405.16755, 2024.

[13] Pourreza M, Rafiei D, et al. CHASE-SQL: Multi-Path Reasoning and Preference Optimized Candidate Selection in Text-to-SQL. arXiv:2410.01943, 2024.

[14] Wang Z, Zhang R, Nie Z, Kim J. Tool-Assisted Agent on SQL Inspection and Refinement in Real-World Scenarios. arXiv:2408.16991, 2024.

[15] Li J, Wu T, Mao Y, Gao Y, Feng Y, Liu H. SQL-Factory: A Multi-Agent Framework for High-Quality and Large-Scale SQL Generation. Proceedings of the VLDB Endowment, 2025.

[16] Ni A, Iyer S, Radev D, et al. LEVER: Learning to Verify Language-to-Code Generation with Execution. ICML, 2023.

[17] Deng M, et al. ReFoRCE: A Text-to-SQL Agent with Self-Refinement, Consensus Enforcement, and Column Exploration. arXiv:2502.00675, 2025.

[18] Liu Y, et al. XiYan-SQL: A Novel Multi-Generator Framework For Text-to-SQL. arXiv:2507.04701, 2025.

[19] Li J, et al. Can LLM Already Serve as A Database Interface? A Big Bench for Large-Scale Database Grounded Text-to-SQL Evaluation. NeurIPS Datasets and Benchmarks Track, 2023.

[20] Lei F, et al. Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows. ICLR, 2025.

[21] Shute J, et al. SQL Has Problems. We Can Fix Them: Pipe Syntax In SQL. Proceedings of the VLDB Endowment, 2024.

[22] Google Cloud. GoogleSQL Pipe Query Syntax Guide. BigQuery Documentation, 2024.

[23] Google Cloud. Pipe Query Syntax Reference. BigQuery Documentation, 2024.

[24] Google Cloud. Simplify your SQL with pipe syntax in BigQuery and Cloud Logging. Google Cloud Blog, 2024.

[25] Li J, et al. BIRD: A Big Bench for Large-Scale Database Grounded Text-to-SQL Evaluation. NeurIPS Datasets and Benchmarks Track, 2023.

[26] Deng X, Sun H, Lees A, et al. TURL: Table Understanding through Representation Learning. Proceedings of the VLDB Endowment, 2020.

[27] Hwang W, Yim J, Park S, Seo M. A Comprehensive Exploration on WikiSQL with Table-Aware Word Contextualization. arXiv:1902.01069, 2019.

[28] Herzig J, Nowak P K, Muller T, Piccinno F, Eisenschlos J. TaPas: Weakly Supervised Table Parsing via Pre-training. ACL, 2020.

[29] Yu T, Yasunaga M, Yang K, et al. SyntaxSQLNet: Syntax Tree Networks for Complex and Cross-Domain Text-to-SQL Task. EMNLP, 2018.

[30] Bogin B, Berant J, Gardner M. Representing Schema Structure with Graph Neural Networks for Text-to-SQL Parsing. ACL, 2019.

[31] Rubin O, Herzig J, Berant J. Learning To Retrieve Prompts for In-Context Learning. NAACL, 2022.

[32] Rajkumar N, Li R, Bahdanau D. Evaluating the Text-to-SQL Capabilities of Large Language Models. arXiv:2204.00498, 2022.

[33] Nan L, et al. Enhancing Few-shot Text-to-SQL Capabilities of Large Language Models: A Study on Prompt Design Strategies. arXiv:2305.12586, 2023.

[34] Sun R, et al. SQL-PaLM: Improved Large Language Model Adaptation for Text-to-SQL. arXiv, 2023.

[35] Liu A, Hu X, Wen L, Yu P S. A Comprehensive Evaluation of ChatGPT's Zero-shot Text-to-SQL Capability. arXiv:2303.13547, 2023.

[36] Arora S, et al. Ask Me Anything: A Simple Strategy for Prompting Language Models. ICLR, 2023.

[37] Yao S, Zhao J, Yu D, et al. ReAct: Synergizing Reasoning and Acting in Language Models. ICLR, 2023.

[38] Schick T, Dwivedi-Yu J, Dessì R, et al. Toolformer: Language Models Can Teach Themselves to Use Tools. NeurIPS, 2023.

[39] Madaan A, Tandon N, Gupta P, et al. Self-Refine: Iterative Refinement with Self-Feedback. NeurIPS, 2023.

[40] Welleck S, et al. Generating Sequences by Learning to Self-Correct. ICLR, 2023.

---

# 签字页

| 项目 | 签字 |
| --- | --- |
| 研究生签字 |  |
| 指导教师签字 |  |
| 院（系、所）领导签字 |  |
| 日期 | 年   月   日 |

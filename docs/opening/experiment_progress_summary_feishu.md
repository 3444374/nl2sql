# 开题实验进展小结

课题名称：面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究

这份小结只整理已经完成的实验。这里的结果用于开题阶段说明技术路线是否走得通，不把小规模实验说成完整公开 benchmark 成绩。SemQL-style、NatSQL-style 和 Pipe-style 结果目前都是 controlled proxy，用于比较表达形态和生成成本，不代表复现原系统。

## 一、实验总览

| 序号 | 实验 | 要回答的问题 | 主要结果 | 当前结论 |
| --- | --- | --- | --- | --- |
| 1 | SQL+ 表达与转换实验 | SQL+ 能不能稳定转成可执行 SQL | 30/30 执行一致 | SQL+ 具备作为中间表示的基础 |
| 2 | IR 表达复杂度对比实验 | SQL+ 和 Standard SQL、SemQL-style、NatSQL-style 有什么区别 | SQL+ token 不更短，但 alias dependency 和 cross-clause reference 更低 | SQL+ 的价值不在压缩长度，而在步骤化和可修复性 |
| 3 | IR 生成成本与执行效果实验 | SQL+ 初次生成是否更准、更省 | SQL+ 14/30，Direct SQL 12/30；SQL+ token 和 latency 更高 | 初次生成优势有限，修复收益需要单独验证 |
| 4 | SQL+ 规则修正实验 | SQL+ 局部步骤是否便于修复 | 15/15 修复成功 | 分步表达方便定位错误 |
| 5 | 单 Agent baseline | 直接生成 SQL 和生成 SQL+ 哪个更好 | Direct 16/30，SQL+ v2 17/30 | 只改输出格式提升有限 |
| 6 | SQL+ 失败类型分析 | SQL+ 初始生成主要错在哪里 | 13 条失败分为 5 类 | 主要是语义错，不是语法错 |
| 7 | 反馈修正对比实验 | 单 Refiner 和局部 skill 哪个更稳 | SQL+ 单 Refiner 4/13，Router v3 13/13 | 单 prompt 不够，路由和局部 skill 更有效 |
| 8 | Repair skill 分治实验 | 不同错误能否分开修 | value、ORDER、aggregation、join 均 3/3，projection 1/1 | 错误类型分治有实验支撑 |
| 9 | Skill Router v3 端到端实验 | Critic、Router、Skill、Executor 能否闭环 | 13 条已知失败样例修复 13 条 | 当前闭环跑通，但还需扩样例 |
| 10 | Repairability 指标对比实验 | SQL+ 的修复收益能否抵消生成阶段额外开销 | SQL+ Router 13/13，Direct SQL Refiner 6/14；SQL+ patch minimality 更高但 token 成本更高 | SQL+ 价值主要体现在修复成功率和局部 patch 可控性 |
| 11 | Spider 小规模公开子集实验 | SQL+ 表达/转换和端到端生成修复能否迁移到公开子集 | conversion smoke test 20/20；fresh e2e 19/20；semantic repair 后 20/20 | 具备公开子集迁移可行性，但需区分 gold conversion 与 fresh e2e |

## 二、SQL+ 表达与转换实验

| 项目 | 内容 |
| --- | --- |
| 实验目的 | 验证 SQL+ 是否能被 parser 解析，并稳定转换为标准 SQL 执行 |
| 数据来源 | 自建企业订单分析样例库 |
| 数据规模 | 30 条 SQL+ 标准样例 |
| 覆盖结构 | 单表查询、多表 join、WHERE、GROUP、AGG、HAVING、SELECT、ORDER、LIMIT |
| 评估方式 | 将 SQL+ 转换为 SQL，在 SQLite 中执行，再与人工标准 SQL 的执行结果比较 |
| SQL+ 语法通过 | 30/30 |
| 转换 SQL 可执行 | 30/30 |
| 执行结果一致 | 30/30 |

结果解读：

这个实验先验证最底层链路。SQL+ 如果不能确定性转换为 SQL，后面的生成、诊断和修复都没有意义。30 条样例全部通过，说明当前 SQL+ 子集已经能覆盖开题阶段常见查询结构。

对课题的意义：

SQL+ 在这里不是一个只写在报告里的表达设想。它已经有 parser 和 converter，可以落到可执行 SQL 上。这个结果支撑了课题的第一层假设：SQL+ 可以作为自然语言到 SQL 之间的中间表示。

## 三、IR 表达复杂度对比实验

| 项目 | 内容 |
| --- | --- |
| 实验目的 | 比较 SQL+ 与 Standard SQL、SemQL-style、NatSQL-style、Pipe-style 在表达复杂度上的差异 |
| 数据规模 | 30 条自建订单分析样例 |
| 对比对象 | Standard SQL、SQL+、SemQL-style proxy、NatSQL-style proxy、Pipe-style proxy |
| 评价指标 | token 数、步骤/子句数、嵌套深度、别名依赖、跨子句引用、转换成功率、转换时间 |
| 说明 | SemQL-style、NatSQL-style 和 Pipe-style 是开题阶段 proxy，不代表复现原系统 |

| 表示形式 | 平均 token | 平均步骤/子句 | 平均嵌套深度 | 平均 alias dependency | 平均 cross-clause reference | 转换成功 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Standard SQL | 31.5333 | 5.9 | 0.6667 | 2.0333 | 2.3333 | 30/30 |
| SQL+ | 35.0333 | 6.1333 | 0.6667 | 0.7 | 1.0 | 30/30 |
| SemQL-style proxy | 50.5667 | 10.7333 | 3.6667 | 0.9 | 1.2 | N/A |
| NatSQL-style proxy | 31.5 | 5.4333 | 0.9667 | 1.3667 | 1.6667 | N/A |
| Pipe-style proxy | 40.8 | 6.1333 | 0.6667 | 1.3667 | 1.6667 | N/A |

| SQL+ 转换指标 | 结果 |
| --- | ---: |
| SQL+ 到 SQL 转换成功 | 30/30 |
| 平均转换时间 | 0.0072 ms |

结果解读：

这个实验没有证明 SQL+ 更短。相反，SQL+ 的平均 token 数是 35.0333，高于 Standard SQL 的 31.5333。原因是 SQL+ 把查询步骤显式写出来，表达长度会增加。它的优势体现在别名依赖和跨子句引用更少：Standard SQL 的 alias dependency 为 2.0333，SQL+ 为 0.7；Standard SQL 的 cross-clause reference 为 2.3333，SQL+ 为 1.0。

对课题的意义：

这组结果把“为什么要 SQL+”说得更准确。SQL+ 不是为了简单压缩 SQL，也不是复刻 SemQL、NatSQL 或 GoogleSQL Pipe Syntax。它更像一个服务于 NL2SQL 修复闭环的步骤化中间层。步骤边界清楚后，后续 Critic Agent 可以定位错误步骤，Repair Skill 也可以只改局部 patch。

## 四、IR 生成成本与执行效果实验

| 项目 | 内容 |
| --- | --- |
| 实验目的 | 比较 Direct SQL、SQL+、NatSQL-style proxy、SemQL-style proxy 的生成成本和执行效果 |
| 数据规模 | 30 条自建订单分析样例 |
| 模型 | gpt-5-mini |
| 评价指标 | 表示有效率、SQL 可执行率、执行一致率、输入 token、输出 token、总 token、latency |
| 说明 | NatSQL-style 和 SemQL-style 为受控 proxy，不代表完整复现对应系统 |

| 方法 | 表示有效 | SQL 可执行 | 执行一致 | 平均输入 token | 平均输出 token | 平均总 token | 平均延迟 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct SQL | 30/30 | 30/30 | 12/30 | 287.6 | 311.5667 | 599.1667 | 6.5851s |
| SQL+ | 28/30 | 28/30 | 14/30 | 319.1333 | 493.9 | 813.0333 | 9.2197s |
| NatSQL-style proxy | 30/30 | 30/30 | 13/30 | 319.1333 | 421.6333 | 740.7667 | 6.2802s |
| SemQL-style proxy | 30/30 | 25/30 | 12/30 | 343.1333 | 685.8333 | 1028.9667 | 9.9684s |

结果解读：

SQL+ 的执行一致率为 14/30，略高于 Direct SQL 的 12/30 和 NatSQL-style proxy 的 13/30，但差距不大，不能表述成显著优势。同时，SQL+ 的平均总 token 和平均延迟都高于 Direct SQL 与 NatSQL-style proxy。这说明步骤化表达带来额外生成成本。

对课题的意义：

这个实验限制了开题报告的表述边界。SQL+ 的论证重点不应写成“初次生成一定更短、更快、更准”，而应写成：SQL+ 是否能在错误定位、局部 patch、修复成功率和可解释性上补偿生成阶段的额外成本。后面的 repairability 实验正是围绕这个问题展开的。

## 五、SQL+ 规则修正实验

| 项目 | 内容 |
| --- | --- |
| 实验目的 | 验证 SQL+ 分步表达是否便于把错误定位到局部步骤 |
| 数据规模 | 15 条构造错误 SQL+ 样例 |
| 错误来源 | 人工构造字段错误、过滤条件错误、连接错误等 |
| 修复方式 | 基于规则的局部修正 |
| 初始失败样例 | 15/15 |
| 修正后 SQL 可执行 | 15/15 |
| 修复成功 | 15/15 |

结果解读：

这组实验不考察大模型能力，重点看 SQL+ 的表达形式有没有帮助。结果显示，错误可以被映射到具体 SQL+ 步骤，再做局部修改。字段错误可以落到 SELECT 或 AGG，过滤值错误可以落到 WHERE，连接错误可以落到 JOIN。

对课题的意义：

规则修正实验给后面的 Agent 修复提供了一个基准判断：如果错误能够定位到 SQL+ 的局部步骤，那么局部修复是可行的。后续 Critic Agent 和 Repair Skill 做的事情，本质上就是把这种定位和修复过程自动化。

## 六、单 Agent baseline 实验

| 方法 | 样例数 | SQL/SQL+ 有效 | SQL 可执行 | 执行结果一致 | 说明 |
| --- | ---: | ---: | ---: | ---: | --- |
| Direct NL2SQL | 30 | N/A | 30/30 | 16/30 | 自然语言直接生成标准 SQL |
| NL2SQL+ prompt v1 | 30 | 30/30 | 30/30 | 13/30 | 自然语言生成 SQL+，再转换为 SQL |
| NL2SQL+ prompt v2 | 30 | 30/30 | 30/30 | 17/30 | 修正 AGG、ORDER、HAVING 和别名约束 |

结果解读：

SQL+ prompt v2 比 Direct NL2SQL 多对 1 条，说明 SQL+ 中间表示有一定潜力。但这个差距并不大。换句话说，只让模型把输出写成 SQL+，还不能从根本上解决语义错误。

对课题的意义：

这个结果反而把研究重点指清楚了。SQL+ 的价值不应只放在“一次生成”上，而应放在后面的诊断和修复上。生成阶段仍会犯值链接、排序、聚合和 join 错误，SQL+ 的优势要通过错误定位和局部修复体现出来。

## 七、SQL+ 失败类型分析

| 错误类型 | 数量 | 典型问题 | 后续对应处理 |
| --- | ---: | --- | --- |
| filter/value-linking | 5 | 状态值、日期边界、候选字段值不匹配 | value lookup tool 和 value-linking repair skill |
| ORDER/LIMIT | 3 | 缺少排序、排序字段错、方向错 | ORDER repair skill |
| aggregation planning | 2 | GROUP 维度、COUNT 口径、聚合别名问题 | aggregation repair skill |
| schema/join planning | 2 | 连接路径错误、缺 JOIN、冗余 JOIN | join repair skill |
| projection mismatch | 1 | 结果列多、少或列顺序不符合问题 | projection repair skill |
| 合计 | 13 | SQL+ prompt v2 的全部失败样例 | 作为 Router v3 的已知失败集 |

结果解读：

这 13 条失败样例大多不是 SQL+ 语法错。很多候选 SQL+ 能转成 SQL，也能执行，但结果和标准答案不一致。真正的问题在语义层面：该筛哪个值、该按哪个字段排序、该按什么口径聚合、该输出哪些列。

对课题的意义：

这个分析直接决定了后续 repair skill 的设计。系统不能只看“SQL 是否能运行”，还要判断“运行结果是否符合问题”。Critic Agent 也不能只读数据库报错，还要结合 schema、SQL+ 步骤和结果预览来判断错误类型。

## 八、反馈修正对比实验

| 方法 | 初始失败样例 | SQL+ 有效 | SQL 可执行 | 修复成功 | 输入信息 | 结果性质 |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| SQL+ 诊断辅助 Refiner | 13 | 13/13 | 13/13 | 13/13 | 使用 gold-derived differences | 链路可行性验证，不算真实自主修复 |
| SQL+ 非 gold Refiner v2 | 13 | 13/13 | 12/13 | 4/13 | 执行反馈、schema、结果预览、粗粒度错误类型 | 更接近真实修复场景 |
| Direct SQL 非 gold Refiner | 14 | N/A | 14/14 | 6/14 | 直接修标准 SQL | SQL 层对照组 |
| SQL+ Schema-Critic-Refiner 初版 | 13 | 13/13 | 13/13 | 3/13 | Schema 和 Critic 串联 | 简单串联没有带来提升 |
| SQL+ Step-wise Critic-Refiner | 13 | 13/13 | 12/13 | 3/13 | 逐步骤诊断 | 诊断更细，但修复仍不稳 |
| SQL+ Skill Router + Repair Skills v3 | 13 | 13/13 | 13/13 | 13/13 | Critic 路由到五类局部 repair skill | 当前已知失败集上效果最好 |

结果解读：

诊断辅助 Refiner 的 13/13 说明，如果知道错在哪里，SQL+ 层确实能修。但这个实验用了 gold-derived differences，不能当成真实系统能力。非 gold 条件下，SQL+ 单 Refiner 只有 4/13，Direct SQL Refiner 为 6/14，说明单个 Refiner prompt 不够稳定。后来加入 Skill Router v3 后，同一批 SQL+ 失败样例修复到 13/13。

对课题的意义：

这组实验是目前最能说明路线选择的证据。多智能体不是简单把几个 prompt 串起来，而是要有明确分工：Critic 负责诊断，Router 负责选择 skill，Repair Skill 负责局部修改，Executor 负责验证候选结果。

## 九、Repair skill 分治实验

| Repair Skill | 样例数 | SQL+ 有效 | SQL 可执行 | 修复成功 | 主要处理的问题 |
| --- | ---: | ---: | ---: | ---: | --- |
| value-linking repair skill | 3 | 3/3 | 3/3 | 3/3 | 状态值、日期边界、候选值替换 |
| ORDER repair skill | 3 | 3/3 | 3/3 | 3/3 | 排序字段、排序方向、Top-K 稳定性 |
| aggregation repair skill | 3 | 3/3 | 3/3 | 3/3 | GROUP 维度、COUNT 口径、聚合别名和 ORDER 引用 |
| join repair skill | 3 | 3/3 | 3/3 | 3/3 | JOIN 路径、冗余 JOIN、缺失 JOIN、paid 过滤 |
| projection repair skill | 1 | 1/1 | 1/1 | 1/1 | 结果列多、少或列顺序错误 |

结果解读：

五类 repair skill 都在当前小样例上跑通。projection repair skill 的 q006 比较典型：问题要求“价格最高的两个商品”，模型多输出了 `product_id`，skill 删除了问题没有要求的投影列，保留 `product_name` 和 `price`。

对课题的意义：

分治实验说明不同错误类型适合不同修复方式。值链接要查候选字段值，join 要看表关系，aggregation 要检查分组和聚合口径，projection 要对照问题中的输出需求。把这些逻辑拆成 skill，修复范围更小，也更容易解释。

## 十、Skill Router v3 端到端实验

| 指标 | 结果 |
| --- | ---: |
| 测试样例 | 当前 13 条 SQL+ 已知失败样例 |
| 参与模块 | Critic Agent、Skill Router、value/order/aggregation/join/projection repair skill、Executor |
| SQL+ 有效 | 13/13 |
| SQL 可执行 | 13/13 |
| 修复成功 | 13/13 |

| 路由路径 | 样例数 | 修复成功 |
| --- | ---: | ---: |
| order | 3 | 3/3 |
| order -> aggregation | 2 | 2/2 |
| value -> order | 2 | 2/2 |
| order -> projection | 1 | 1/1 |
| join -> aggregation -> projection | 1 | 1/1 |
| value -> aggregation -> join -> order | 1 | 1/1 |
| value -> join -> aggregation -> order -> projection | 1 | 1/1 |
| value -> join -> projection | 1 | 1/1 |
| value | 1 | 1/1 |

结果解读：

Router v3 并非只做单步路由。有些样例只需要 ORDER skill，有些样例需要多个 skill 连续处理。例如 q006 走 order -> projection，q013 走 value -> join -> aggregation -> order -> projection。这说明复合错误在当前样例里已经出现，Router 需要处理 skill 顺序问题。

对课题的意义：

这组实验把前面的分治修复串成了完整闭环。它支撑了当前路线：Natural language -> SQL+ -> SQL -> Execution feedback -> Critic Agent -> Skill Router -> Repair Skill -> Executor。不过边界要讲清楚：13/13 是当前已知失败集上的结果，不是大规模 benchmark 结果。下一步要扩展无报错语义错和更多公开数据集样例。

## 十一、Repairability 指标对比实验

| 项目 | 内容 |
| --- | --- |
| 实验目的 | 比较 SQL+ 修复路线和 Direct SQL 修复路线在错误定位、patch 范围、修复轮数、token 成本和 latency 记录上的差异 |
| SQL+ 路线 | Critic Agent -> Skill Router -> Repair Skills -> Executor |
| Direct SQL 路线 | Direct SQL 非 gold Refiner |
| SQL+ 样例 | 当前 13 条 SQL+ 已知失败样例 |
| Direct SQL 样例 | 当前 14 条 Direct SQL 失败样例 |
| 重叠样例 | 9 条共同问题编号样例 |

| 方法 | 样例数 | 修复成功 | 定位准确率 | 严格最小 patch 率 | 平均 patch minimality | 平均修复轮数 | 平均 repair token |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct SQL Refiner | 14 | 6/14 | 0.8571 | 0.8571 | 0.8571 | 1 | 1609.3571 |
| SQL+ Critic Router Skills | 13 | 13/13 | 0.7692 | 0.9231 | 0.9744 | 2.2308 | 3813.9231 |
| Direct SQL Refiner overlap | 9 | 4/9 | 0.8889 | 0.8889 | 0.8889 | 1 | 1583.2222 |
| SQL+ Critic Router Skills overlap | 9 | 9/9 | 0.7778 | 0.8889 | 0.9630 | 2.3333 | 4001.7778 |

结果解读：

这组实验补充回答了“SQL+ 是否值得引入”的问题。SQL+ 路线在当前已知失败集上的修复成功率明显更高，重叠样例中 SQL+ 为 9/9，Direct SQL Refiner 为 4/9。SQL+ 的平均 patch minimality 也更高，说明修复更集中在局部步骤上。不过，SQL+ 并不是低成本路线。它需要 Critic Agent 输出结构化诊断，平均 repair token 高于 Direct SQL 单 Refiner，平均修复轮数也更多。

对课题的意义：

当前结果更适合支撑一个谨慎判断：SQL+ 的价值主要体现在修复成功率、局部 patch 可控性和解释性上，而不是 token 或延迟天然更低。由于历史 Direct SQL 和 SQL+ Critic 输出没有记录完整 API latency，现阶段还不能断言 SQL+ 的修复收益已经完全抵消生成阶段的额外开销。后续需要用带 `latency_seconds` 字段的新模型运行，继续比较端到端 repair latency 和综合成本。

## 十二、Spider 小规模公开子集实验

| 项目 | 内容 |
| --- | --- |
| 实验目的 | 验证 SQL+ 表达/转换、端到端生成和 semantic repair 是否能迁移到公开 Text-to-SQL 数据集子集 |
| 数据集 | Spider dev 子集 |
| 数据库 | concert_singer |
| 样例数 | 20 |
| 覆盖结构 | count、select、where、order、limit、group、aggregation、simple join |
| conversion smoke test | SQL+ 有效 20/20；SQL 可执行 20/20；执行一致 20/20 |
| fresh e2e generation | SQL+ 有效 19/20；SQL 可执行 19/20；执行一致 19/20 |
| fresh e2e + semantic repair | SQL+ 有效 20/20；SQL 可执行 20/20；执行一致 20/20 |

结果解读：

实验从 Spider dev 的 concert_singer 数据库中筛出当前 SQL+ 子集能覆盖的 20 条查询。这里需要区分两类结果：conversion smoke test 是先把 Spider gold SQL 改写为 SQL+，再转换回 SQL 并比较执行结果；fresh e2e generation 则是从自然语言问题和 schema 直接生成 SQL+。因此 conversion smoke test 的 20/20 不能写成端到端生成准确率。

对课题的意义：

这个结果说明 SQL+ 不是只适用于自建订单库，在公开 benchmark 的一小部分受支持结构上也能跑通。fresh e2e 结果说明端到端生成链路已经在小子集跑通，semantic repair skill 能修复当前小子集剩余问题。但它不是完整 Spider benchmark 成绩。当前 SQL+ 还没覆盖复杂子查询、集合运算、复杂布尔条件、窗口函数等结构，后续需要逐步扩大覆盖范围。

## 十三、当前综合判断

| 判断 | 依据 | 后续动作 |
| --- | --- | --- |
| SQL+ 中间表示可行 | 30 条 SQL+ 样例全部转换并执行一致 | 扩展 SQL+ 语法，覆盖更多复杂结构 |
| SQL+ 不是天然低成本表示 | SQL+ 平均 token 和 latency 高于 Direct SQL | 不把优势写成“更短更快”，改写成“更可定位、更可修复” |
| 初次生成提升有限 | Direct 16/30，SQL+ prompt v2 17/30；IR 生成成本实验中 SQL+ 14/30，Direct SQL 12/30 | 生成阶段继续优化，但不作为唯一论证重点 |
| 真实反馈修正有难度 | SQL+ 单 Refiner 4/13，Direct SQL Refiner 6/14 | 强化 Critic 诊断和工具调用 |
| 错误类型分治有效 | 五类 repair skill 小样例均修复成功 | 扩展更多错误类型和复合错误样例 |
| Router 闭环值得继续做 | Skill Router v3 在当前已知失败集达到 13/13 | 扩展无报错语义错、公开子集和消融实验 |
| SQL+ 修复收益主要体现在可修复性 | SQL+ patch minimality 为 0.9744，高于 Direct SQL Refiner 的 0.8571，但 repair token 更高 | 继续记录完整 API latency，评估修复收益能否抵消生成和诊断成本 |
| 公开数据集迁移有初步证据 | Spider `concert_singer` conversion 20/20；fresh e2e 19/20；semantic repair 后 20/20 | 扩展到更多数据库、多难度和 BIRD 子集 |

当前最稳的结论是：SQL+ 自身可以稳定转换，单次生成只能带来有限提升，真正拉开差距的是反馈修正阶段。后续工作不应只写更长的 prompt，而要把 Critic、Router、Repair Skill 和 Executor 做稳，再扩大样例和数据集范围。

## 十四、下一步实验计划

| 优先级 | 实验 | 目的 |
| --- | --- | --- |
| 1 | 重新运行带 `latency_seconds` 的 Critic/Refiner 实验 | 补齐端到端 repair latency |
| 2 | 扩展无报错语义错误样例 | 检验 Critic 是否能发现“能执行但语义错”的查询 |
| 3 | 扩展 Spider 多数据库子集 | 验证 SQL+ 转换和修复是否能跨 schema 迁移 |
| 4 | 做 Skill Router 消融实验 | 分别去掉 Critic、Router、单类 repair skill，观察修复率变化 |
| 5 | 设计 SQL+ 与 SemQL/NatSQL 的更严格对比 | 继续说明 SQL+ 与既有中间表示的区别 |

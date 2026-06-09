# 开题实验进展小结

课题名称：面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究

这份小结只整理已经完成的实验。这里的结果用于开题阶段说明技术路线是否走得通，不把小规模实验说成完整公开 benchmark 成绩。

## 一、实验总览

| 序号 | 实验 | 要回答的问题 | 主要结果 | 当前结论 |
| --- | --- | --- | --- | --- |
| 1 | SQL+ 表达与转换实验 | SQL+ 能不能稳定转成可执行 SQL | 30/30 执行一致 | SQL+ 具备作为中间表示的基础 |
| 2 | SQL+ 规则修正实验 | SQL+ 局部步骤是否便于修复 | 15/15 修复成功 | 分步表达方便定位错误 |
| 3 | 单 Agent baseline | 直接生成 SQL 和生成 SQL+ 哪个更好 | Direct 16/30，SQL+ v2 17/30 | 只改输出格式提升有限 |
| 4 | SQL+ 失败类型分析 | SQL+ 初始生成主要错在哪里 | 13 条失败分为 5 类 | 主要是语义错，不是语法错 |
| 5 | 反馈修正对比实验 | 单 Refiner 和局部 skill 哪个更稳 | SQL+ 单 Refiner 4/13，Router v3 13/13 | 单 prompt 不够，路由和局部 skill 更有效 |
| 6 | Repair skill 分治实验 | 不同错误能否分开修 | value、ORDER、aggregation、join 均 3/3，projection 1/1 | 错误类型分治有实验支撑 |
| 7 | Skill Router v3 端到端实验 | Critic、Router、Skill、Executor 能否闭环 | 13 条已知失败样例修复 13 条 | 当前闭环跑通，但还需扩样例 |
| 8 | Spider 小规模 smoke test | SQL+ 能否迁移到公开数据集子集 | 20/20 执行一致 | 具备公开子集迁移可行性 |

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

这个实验先验证最底层链路。SQL+ 如果不能稳定转换为 SQL，后面的生成、诊断和修复都没有意义。30 条样例全部通过，说明当前 SQL+ 子集已经能覆盖开题阶段常见查询结构。

对课题的意义：

SQL+ 在这里不是一个只写在报告里的表达设想。它已经有 parser 和 converter，可以落到可执行 SQL 上。这个结果支撑了课题的第一层假设：SQL+ 可以作为自然语言到 SQL 之间的中间表示。

## 三、SQL+ 规则修正实验

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

这组实验不考察大模型能力，重点看 SQL+ 的表达形式有没有帮助。结果显示，错误可以被映射到具体 SQL+ 步骤，再做局部修改。比如字段错误可以落到 SELECT 或 AGG，过滤值错误可以落到 WHERE，连接错误可以落到 JOIN。

对课题的意义：

规则修正实验给后面的 Agent 修复提供了一个基准判断：如果错误能够定位到 SQL+ 的局部步骤，那么局部修复是可行的。后续 Critic Agent 和 Repair Skill 做的事情，本质上就是把这种定位和修复过程自动化。

## 四、单 Agent baseline 实验

| 方法 | 样例数 | SQL/SQL+ 有效 | SQL 可执行 | 执行结果一致 | 说明 |
| --- | --- | --- | --- | --- | --- |
| Direct NL2SQL | 30 | 不适用 | 30/30 | 16/30 | 自然语言直接生成标准 SQL |
| NL2SQL+ prompt v1 | 30 | 30/30 | 30/30 | 13/30 | 自然语言生成 SQL+，再转换为 SQL |
| NL2SQL+ prompt v2 | 30 | 30/30 | 30/30 | 17/30 | 修正了 AGG、ORDER、HAVING 和别名约束 |

结果解读：

SQL+ prompt v2 比 Direct NL2SQL 多对 1 条，说明 SQL+ 中间表示有一定潜力。但这个差距并不大。换句话说，只让模型把输出写成 SQL+，还不能从根本上解决语义错误。

对课题的意义：

这个结果反而把研究重点指清楚了。SQL+ 的价值不应该只放在“一次生成”上，而应该放在后面的诊断和修复上。生成阶段仍会犯值链接、排序、聚合和 join 错误，SQL+ 的优势要通过错误定位和局部修复体现出来。

## 五、SQL+ 失败类型分析

| 错误类型 | 数量 | 典型问题 | 后续对应处理 |
| --- | --- | --- | --- |
| filter/value-linking | 5 | 状态值、日期边界、候选字段值不匹配 | value lookup tool 和 value-linking repair skill |
| ORDER/LIMIT | 3 | 缺少排序、排序字段错、方向错 | ORDER repair skill |
| aggregation planning | 2 | GROUP 维度、COUNT 口径、聚合别名问题 | aggregation repair skill |
| schema/join planning | 2 | 连接路径错误、缺 JOIN、冗余 JOIN | join repair skill |
| projection mismatch | 1 | 结果列多、少或列顺序不符合问题 | projection repair skill |
| 合计 | 13 | SQL+ prompt v2 的全部失败样例 | 作为 Router v3 的已知失败集 |

结果解读：

这 13 条失败样例大多不是 SQL+ 语法错。很多候选 SQL+ 能转成 SQL，也能执行，但结果和标准答案不一致。真正的问题在语义层面：该筛哪个值、该按哪个字段排序、该按什么口径聚合、该输出哪些列。

对课题的意义：

这个分析直接决定了后续 repair skill 的设计。它说明系统不能只看“SQL 是否能运行”，还要判断“运行结果是否符合问题”。Critic Agent 也不能只读数据库报错，还要结合 schema、SQL+ 步骤和结果预览来判断错误类型。

## 六、反馈修正对比实验

| 方法 | 初始失败样例 | SQL+ 有效 | SQL 可执行 | 修复成功 | 输入信息 | 结果性质 |
| --- | --- | --- | --- | --- | --- | --- |
| SQL+ 诊断辅助 Refiner | 13 | 13/13 | 13/13 | 13/13 | 使用 gold-derived differences | 链路可行性验证，不算真实自主修复 |
| SQL+ 非 gold Refiner v2 | 13 | 13/13 | 12/13 | 4/13 | 执行反馈、schema、预览结果、粗粒度错误类型 | 更接近真实修复场景 |
| Direct SQL 非 gold Refiner | 14 | 不适用 | 14/14 | 6/14 | 直接修标准 SQL | SQL 层对照组 |
| SQL+ Schema-Critic-Refiner 初版 | 13 | 13/13 | 13/13 | 3/13 | Schema 和 Critic 串联 | 简单串联没有带来提升 |
| SQL+ Step-wise Critic-Refiner | 13 | 13/13 | 12/13 | 3/13 | 逐步骤诊断 | 诊断更细，但修复仍不稳 |
| SQL+ Skill Router + Repair Skills v3 | 13 | 13/13 | 13/13 | 13/13 | Critic 路由到五类局部 repair skill | 当前已知失败集上效果最好 |

结果解读：

诊断辅助 Refiner 的 13/13 说明，如果知道错在哪里，SQL+ 层确实能修。但这个实验用了 gold-derived differences，不能拿来当真实系统能力。非 gold 条件下，SQL+ 单 Refiner 只有 4/13，Direct SQL Refiner 为 6/14，说明单个 Refiner prompt 不够稳。后来加入 Skill Router v3 后，同一批 SQL+ 失败样例修复到 13/13。

对课题的意义：

这组实验是目前最能说明路线选择的证据。它说明多智能体不是简单地把几个 prompt 串起来，而是要有明确分工：Critic 负责诊断，Router 负责选择 skill，Repair Skill 负责局部修改，Executor 负责验证候选结果。

## 七、Repair skill 分治实验

| Repair Skill | 样例数 | SQL+ 有效 | SQL 可执行 | 修复成功 | 主要处理的问题 |
| --- | --- | --- | --- | --- | --- |
| value-linking repair skill | 3 | 3/3 | 3/3 | 3/3 | 状态值拼写、日期边界、候选值替换 |
| ORDER repair skill | 3 | 3/3 | 3/3 | 3/3 | 排序字段、排序方向、Top-K 稳定性 |
| aggregation repair skill | 3 | 3/3 | 3/3 | 3/3 | GROUP 维度、COUNT 口径、聚合别名和 ORDER 引用 |
| join repair skill | 3 | 3/3 | 3/3 | 3/3 | JOIN 路径、冗余 JOIN、缺失 JOIN、paid 过滤 |
| projection repair skill | 1 | 1/1 | 1/1 | 1/1 | 结果列多、少或列顺序错误 |

结果解读：

五类 repair skill 都在当前小样例上跑通。projection repair skill 的 q006 比较典型：问题要求“价格最高的两个商品”，模型多输出了 `product_id`，skill 删除了问题没有要求的投影列，保留 `product_name` 和 `price`。

对课题的意义：

分治实验说明不同错误类型适合不同修复方式。值链接要查候选字段值，join 要看表关系，aggregation 要检查分组和聚合口径，projection 要对照问题中的输出需求。把这些逻辑拆成 skill，修复范围更小，也更容易解释。

## 八、Skill Router v3 端到端实验

| 指标 | 结果 |
| --- | --- |
| 测试样例 | 当前 13 条 SQL+ 已知失败样例 |
| 参与模块 | Critic Agent、Skill Router、value/order/aggregation/join/projection repair skill、Executor |
| SQL+ 有效 | 13/13 |
| SQL 可执行 | 13/13 |
| 修复成功 | 13/13 |

| 路由路径 | 样例数 | 修复成功 |
| --- | --- | --- |
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

Router v3 并非只做单步路由。有些样例只需要 ORDER skill，有些样例需要多个 skill 连续处理。例如 q006 走了 order -> projection，q013 走了 value -> join -> aggregation -> order -> projection。这个结果说明，复合错误在当前样例里已经出现，Router 需要处理 skill 的顺序问题。

对课题的意义：

这组实验把前面的分治修复串成了完整闭环。它支撑了当前路线：Natural language -> SQL+ -> SQL -> Execution feedback -> Critic Agent -> Skill Router -> Repair Skill -> Executor。不过边界要讲清楚：13/13 是当前已知失败集上的结果，不是大规模 benchmark 结果。下一步要扩展无报错语义错和更多公开数据集样例。

## 九、Spider 小规模 smoke test

| 项目 | 内容 |
| --- | --- |
| 实验目的 | 验证 SQL+ 表达与转换机制是否能迁移到公开 Text-to-SQL 数据集子集 |
| 数据集 | Spider dev 子集 |
| 数据库 | concert_singer |
| 样例数 | 20 |
| 覆盖结构 | count、select、where、order、limit、group、aggregation、simple join |
| SQL+ 有效 | 20/20 |
| SQL 可执行 | 20/20 |
| 执行结果一致 | 20/20 |

结果解读：

实验从 Spider dev 的 concert_singer 数据库中筛出当前 SQL+ 子集能覆盖的 20 条查询。SQL+ 转换后的 SQL 全部可执行，执行结果也和 Spider gold SQL 一致。

对课题的意义：

这个结果说明 SQL+ 不是只适用于自建订单库，在公开 benchmark 的一小部分受支持结构上也能跑通。但它不是完整 Spider benchmark 成绩。当前 SQL+ 还没覆盖复杂子查询、集合运算、复杂布尔条件、窗口函数等结构，后续需要逐步扩大覆盖范围。

## 十、当前综合判断

| 判断 | 依据 | 后续动作 |
| --- | --- | --- |
| SQL+ 中间表示可行 | 30 条 SQL+ 样例全部转换并执行一致 | 扩展 SQL+ 语法，覆盖更多复杂结构 |
| 单次生成提升有限 | Direct 16/30，SQL+ prompt v2 17/30 | 不把研究重点放在继续堆 prompt |
| 真实反馈修正有难度 | SQL+ 单 Refiner 4/13，Direct SQL Refiner 6/14 | 强化 Critic 诊断和工具调用 |
| 错误类型分治有效 | 五类 repair skill 小样例均修复成功 | 扩展更多错误类型和复合错误样例 |
| Router 闭环值得继续做 | Skill Router v3 在当前已知失败集达到 13/13 | 扩展无报错语义错、公开子集和消融实验 |
| 公开数据集迁移有初步证据 | Spider `concert_singer` 受支持子集 20/20 | 扩展到更多数据库、多难度和 BIRD 子集 |

当前最稳的结论是：SQL+ 自身可以稳定转换，单次生成只能带来有限提升，真正拉开差距的是反馈修正阶段。后续工作不应只写更长的 prompt，而要把 Critic、Router、Repair Skill 和 Executor 做稳，再扩大样例和数据集范围。

【汇报讲稿】
实验二是 IR 表达复杂度对比，目的是回答“为什么使用 SQL+”。这组实验不直接比较模型能力，而是把同一批 30 条自建订单分析查询，分别表示成 Standard SQL、SQL+、SemQL-style proxy、NatSQL-style proxy 和 Pipe-style proxy，然后统计这些表示本身的结构复杂度。这里的 proxy 只是受控代理表示，用来比较表达形态，不代表完整复现 SemQL、NatSQL 或 GoogleSQL Pipe Syntax。

具体计算方式是：每条样例都包含自然语言问题、gold SQL 和 gold SQL+。Standard SQL 直接取 gold SQL；SQL+ 直接取 gold SQL+；SemQL-style proxy 是根据 SQL+ AST 构造类似语义树的括号表达；NatSQL-style proxy 是把查询改写成更接近自然语言顺序的 SQL-like 表达；Pipe-style proxy 是把 SQL+ 步骤改写成管道式 `|>` 表达。之后对每种表示逐条计算 token 数、步骤或子句数、嵌套深度、别名依赖和跨子句引用，再对 30 条样例取平均值。

这些指标的含义分别是：token 数近似表示输入输出文本长度和模型生成成本；步骤或子句数表示查询被拆成多少个可观察单元；嵌套深度表示括号、子查询或树形结构的层级复杂度；别名依赖表示 `AS` 产生的别名在后续 SELECT、HAVING、ORDER 等区域被再次引用的次数；跨子句引用表示一个查询决策是否需要跨越多个区域才能理解。选择这些指标，是因为本课题关注的不是“哪种表示最短”，而是“哪种表示更适合定位错误和局部修复”。

结果显示，SQL+ 的平均 token 为 35.0333，高于 Standard SQL 的 31.5333，因此不能说 SQL+ 更短。但 SQL+ 的别名依赖为 0.7，跨子句引用为 1.0，低于 Standard SQL 的 2.0333 和 2.3333。这说明 SQL+ 不是靠压缩长度取得优势，而是通过线性步骤边界减少跨区域耦合，使后续 Critic Agent 定位错误、Skill Router 选择修复技能、Repair Skill 做局部 patch 时更容易落到具体步骤上。

【答辩备注】
如果老师问“这些数是怎么来的”，回答口径是：它们不是人工主观打分，而是由脚本对同一批查询的五种文本表示做规则统计得到。token 是正则切分后的 token 个数；步骤或子句数对 Standard SQL 统计 SELECT、FROM、JOIN、WHERE、GROUP BY、HAVING、ORDER BY、LIMIT 等关键子句，对 SQL+ 和 Pipe-style 统计非空步骤行，对 SemQL-style 统计括号节点；嵌套深度统计括号最大深度；别名依赖统计 `AS alias` 在后续区域再次出现的次数；跨子句引用在别名依赖基础上补充统计排序等区域对前面表达的引用。

这些指标的意义是服务研究假设：Text-to-SQL 的困难不只来自 SQL 长度，还来自查询结构之间的耦合。token 数反映生成成本；步骤或子句数反映可定位粒度；嵌套深度反映结构展开难度；别名依赖和跨子句引用反映局部修改时是否容易牵一发动全身。SQL+ 的关键优势不是“平均 token 更低”，而是“依赖关系更少、步骤边界更清楚”，这正好支撑本课题把错误反馈映射到 SQL+ 步骤并进行局部修复的设计。

需要主动说明边界：SemQL-style、NatSQL-style 和 Pipe-style 是 controlled proxy，只用于开题阶段观察表达形态差异，不能等同于完整复现原论文系统。后续如果时间允许，可以接入原系统代码或更大公开数据子集做更严格对比。

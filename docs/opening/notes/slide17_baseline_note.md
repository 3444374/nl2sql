【汇报讲稿】
实验四比较 Direct SQL 和 NL2SQL+ baseline。样例仍然是 30 条自建订单查询。Direct SQL 方法让模型直接从自然语言问题生成 SQL；NL2SQL+ 方法让模型先生成 SQL+，再通过转换器转换成 SQL。两种方法使用相同数据库 schema 和同一批问题，最终都在同一个 SQLite 数据库上执行，并与 gold SQL 的执行结果比较。

评价指标主要有两个：SQL 可执行率和执行一致率。SQL 可执行率看模型输出或转换后的 SQL 能不能在数据库中运行；执行一致率看运行结果是否与 gold SQL 一致。这里不用字符串完全匹配，因为 SQL 写法可能不同，但只要在同一数据库上的执行结果一致，就认为语义上等价。

当前 Direct NL2SQL 是 16/30，NL2SQL+ prompt v2 是 17/30，提升很小。这说明只把输出格式换成 SQL+，并不能自动解决 Text-to-SQL 的主要问题。SQL+ 的价值需要和 schema linking、Critic Agent、Skill Router、Repair Skill、Executor 反馈结合起来验证。

【答辩备注】
这页要主动说明负面结果的价值：如果 SQL+ 单独 prompt 就大幅提升，课题会变成 prompt engineering；现在结果显示单独换表示收益有限，反而说明后续多智能体反馈修复机制是必要的。

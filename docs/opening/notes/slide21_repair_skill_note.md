【汇报讲稿】
实验七展示 repair skill 的分治结果。当前把失败类型拆成 value-linking、ORDER、aggregation、join 和 projection 五类。每类 skill 都对应 SQL+ 中的一个或几个局部步骤。例如 value-linking 主要修 WHERE 条件值和 paid 过滤；ORDER 修排序字段、排序方向和 LIMIT；aggregation 修 AGG 别名、聚合口径、HAVING/ORDER 引用；join 修连接路径、冗余 join 和连接方向；projection 修 SELECT 输出列。

实验方法是：从 SQL+ 已知失败集中按错误类型切分样例，对每类 skill 分别运行局部 patch，再通过 SQL+ parser、SQL converter 和 SQLite executor 验证结果。表中的 3/3、1/1 等数字表示在该类当前小样例中，修复后执行结果与 gold SQL 一致的数量。

【答辩备注】
这页要说明分治实验的意义：它不是证明样本规模已经足够，而是验证“错误类型 -> SQL+ 步骤 -> repair skill -> 执行验证”这条路线可行。后续要扩大每类错误样例，加入复合错误和无报错语义错误。

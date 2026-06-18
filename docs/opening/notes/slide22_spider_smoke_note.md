【汇报讲稿】
实验八是 Spider 小规模公开子集实验，需要区分 conversion smoke test 和 fresh end-to-end generation。conversion smoke test 用 Spider gold SQL 改写得到 SQL+，再由 SQL+ 转回 SQL，验证 SQL+ 表达与转换机制能否覆盖公开 Text-to-SQL 数据集的一部分结构；它不是端到端生成准确率。fresh e2e 则从问题和 schema 直接生成 SQL+，当前 `concert_singer` 20 条小子集上为 19/20，同一次 fresh 输出经 `Skill Router -> semantic repair skill` 后为 20/20。这些样例不是完整 Spider，而是用于开题阶段检查迁移可行性。

实验方法是：先把这些 Spider gold SQL 改写或映射成 SQL+，再用 SQL+ 转换器生成 SQL，然后在 Spider 提供的 SQLite 数据库上执行。最后把生成 SQL 的执行结果和 Spider gold SQL 的执行结果比较。指标包括 SQL+ valid、SQL executable 和 execution match。当前结果是 20/20 SQL+ 可解析，20/20 SQL 可执行，20/20 与 gold SQL 执行一致。

【答辩备注】
这页一定要主动说明边界：这不是完整 Spider benchmark 分数，只是 `concert_singer` 数据库中受当前 SQL+ 子集支持的 20 条样例 smoke test。它的作用是证明 SQL+ 表达和转换器不只适用于自建订单数据，在公开数据集的小规模子集上也能跑通。后续需要扩展到更多数据库、更多难度和更多 SQL 结构。

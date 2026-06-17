【汇报讲稿】
实验五进入反馈修复。样例来自已知失败集：SQL+ prompt v2 在 30 条自建样例中失败的 13 条，以及 Direct SQL 失败的 14 条。失败类型包括 value-linking、ORDER、aggregation、join 和 projection 等。这里的目标不是重新跑完整 benchmark，而是观察“同样已经出错的查询，哪种修复方式更容易恢复到正确结果”。

实验方法是：对失败样例分别使用几种修复方案。单 Refiner 方案让模型直接根据错误信息修改 SQL 或 SQL+；Schema-Critic-Refiner 和 Step-wise Critic-Refiner 尝试把诊断与修复拆开；Skill Router + Repair Skills v3 则先由 Critic 给出错误类型和可疑 SQL+ 步骤，再由 Router 选择对应 repair skill，最后生成局部 patch 并重新执行验证。

repair success 的计算方式是：修复后的 SQL 或 SQL+ 转换 SQL 能在 SQLite 中执行，并且执行结果与 gold SQL 一致。error localization 用来观察错误是否定位到正确步骤；patch minimality 用来观察修复是否只改必要步骤，而不是整条查询大范围重写。当前 SQL+ Skill Router + Repair Skills v3 在这组已知失败集上达到 13/13，但这个结果只限当前 13 条失败样例。

【答辩备注】
这页必须说清楚边界：13/13 不是大规模泛化结果，也不是完整自主诊断系统已经成熟。它说明在当前已知失败类型上，按错误类型路由到专门 repair skill，比单纯让模型整体重写更稳定。后续要扩大失败样例、加入未知错误和无 gold 语义错误。

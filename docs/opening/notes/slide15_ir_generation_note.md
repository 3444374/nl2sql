【汇报讲稿】
这一页比较不同表示在模型生成阶段的成本和执行效果。这里仍然使用同一批 30 条自建订单查询，模型统一为 gpt-5-mini，比较 Direct SQL、SQL+、NatSQL-style proxy 和 SemQL-style proxy 四种生成目标。这里再次使用 proxy 的原因，是为了让模型在同样问题和同样数据库 schema 下生成不同表达形式，从而观察表达形式对 token、latency、valid rate 和执行结果的影响。

这组实验的重点不是证明 SQL+ 初次生成一定优于 Direct SQL。相反，当前结果显示 SQL+ 的 execution match 为 14/30，Direct SQL 为 12/30，差距不大；同时 SQL+ 的平均 token 和 latency 更高。这说明 SQL+ 在初次生成阶段会引入额外表达成本。这个结果对开题很重要，因为它提醒我们不能把 SQL+ 简单描述为“更省、更短、更准”，而要把研究重点放在“更容易诊断和修复”上。

【答辩备注】
如果老师问“SQL+ 初次生成成本更高，为什么还要做”，回答：本课题的假设不是 SQL+ 初次生成一定更便宜，而是 SQL+ 通过步骤化表示降低错误定位和局部修复难度。也就是说，SQL+ 的收益主要应该在 repairability 上体现，而不是只看第一轮生成。后续实验才会比较 error localization accuracy、patch minimality、repair rounds、repair token cost 和 repair latency，判断修复收益能否抵消初次生成阶段的额外开销。

这里的 NatSQL-style 和 SemQL-style 仍是代理表示，不代表完整系统。它们用于观察“如果把目标表达改成类似 NatSQL 或 SemQL 的形态，模型生成成本和有效率会发生什么变化”。不能把这页结果解释为 NatSQL 或 SemQL 原系统性能。

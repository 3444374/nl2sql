【汇报讲稿】
实验六进一步把“修复是否有效”拆成 repairability 指标，而不只看最终是否成功。样例仍然来自失败集。Direct SQL 使用单 Refiner 的修复输出；SQL+ 使用 Critic Agent、Skill Router 和 Repair Skills 的修复输出。这样可以比较直接修 SQL 和在 SQL+ 层修复的差异。

repair success 表示修复后的查询执行结果是否与 gold SQL 一致。error localization accuracy 表示 Critic 定位到的错误步骤或错误类型，是否与人工分析或 gold 差异中的预期错误区域有交集。patch minimality 表示实际修改范围是否接近必要修改范围，越小越说明没有大范围重写。average repair rounds 表示平均需要几轮修复才能通过执行验证。repair token cost 表示修复阶段模型调用消耗的 token。repair latency 表示修复流程耗时；当前 SQL+ 表中的本地 latency 主要覆盖 router 和 repair skill 执行，不完全包含所有 Critic API 耗时，因此需要在答辩中说明边界。

这些指标的意义是回答一个关键问题：SQL+ 初次生成更贵，但它是否能在修复阶段节省人力和减少重写风险。当前观察是 SQL+ 修复成功率和 patch 可控性更好，但 token 成本更高，因此后续要补齐端到端成本，判断修复收益是否抵消额外开销。

【答辩备注】
这页是从 accuracy 走向研究指标的关键。要强调本课题不是只追求最后对不对，还关心错在哪里、怎么修、修了多少、修几轮、花多少 token 和时间。这些指标更能体现 SQL+ 作为中间表示的研究价值。

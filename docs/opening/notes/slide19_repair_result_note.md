【汇报讲稿】
这一页展示反馈修复的对比结果。这里比较的不是“agent 数量越多越好”，而是“错误诊断、路由和局部修复是否真正形成有效分工”。从结果看，简单把 Schema、Critic、Refiner 串起来并没有明显提升，Schema-Critic-Refiner 和 Step-wise Critic-Refiner 都只有 3/13。原因是诊断结果如果不能稳定映射到可执行的修复操作，增加 agent 也可能只增加误差传播。

真正提升来自 Skill Router + Repair Skills：先把错误归类为 value、order、aggregation、join、projection 等类型，再调用对应的修复规则或修复策略，最后由执行器检查候选 patch 是否恢复正确结果。这里的 patch 是针对 SQL+ 局部步骤的修改，而不是重新生成整条 SQL。

【答辩备注】
如果老师问“为什么多智能体反而不一定好”，回答：多智能体的价值不在数量，而在中间产物是否可检查、可路由、可执行。没有 skill 和 executor 约束时，Critic 的诊断可能不能转化为有效修复；有 SQL+ 步骤和 repair skill 后，诊断才能变成局部 patch。

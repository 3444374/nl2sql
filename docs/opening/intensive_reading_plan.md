# 开题精读文献计划

本文档用于整理开题答辩要求中的 15 篇精读文献，并作为后续逐篇精读记录入口。来源为 `docs/opening/opening_report.md` 的“精读文献清单”和“主要参考文献”。

## 精读顺序

建议按“基础 benchmark -> 中间表示与约束生成 -> LLM Text-to-SQL -> 多智能体与反馈修正 -> 真实工作流 benchmark”的顺序读。这样能直接服务本课题主线：

```text
Natural language -> SQL+ -> SQL -> Execution feedback -> Critic Agent -> Skill Router -> Repair Skill
```

| 顺序 | 文献 | 原参考编号 | 阅读重点 | 和本课题的关系 | 精读状态 |
| --- | --- | --- | --- | --- | --- |
| 1 | Yu 等，Spider | [2] | 跨数据库 Text-to-SQL benchmark、复杂 SQL 分类、评测协议 | 支撑 Spider smoke test 的 benchmark 背景；答辩时需说明本课题只做小规模受支持子集验证 | 已精读 |
| 2 | Li 等，BIRD | [25] | 真实数据库、外部知识、执行效率、难例构造 | 支撑后续从自建 order 数据集迁移到真实数据库场景；不能把当前结果说成 BIRD benchmark 成绩 | 已精读 |
| 3 | Lei 等，Spider 2.0 | [20] | 企业级 Text-to-SQL workflow、真实操作链路、复杂任务评测 | 用于说明 Text-to-SQL 从单句 SQL 生成走向真实 workflow，本课题的反馈修正路线有现实意义 | 已精读 |
| 4 | Guo 等，IRNet/SemQL | [3] | 中间表示、语义解析、SQL 结构简化 | 直接支撑 SQL+ 作为中间表示的必要性；重点比较 SemQL 与 SQL+ 的差异 | 已精读 |
| 5 | Gan 等，NatSQL | [5] | 面向 Text-to-SQL 的 SQL 简化表达、降低结构复杂度 | SQL+ 的最近邻相关工作之一；重点找出 NatSQL 能解决和不能解决的问题 | 已精读 |
| 6 | Shute 等，Pipe Syntax in SQL | [21] | 管道式 SQL、线性数据流表达、传统 SQL 表达顺序问题 | SQL+ 语法设计的重要灵感来源；需强调本课题不是复刻 GoogleSQL Pipe Syntax | 待读 |
| 7 | Wang 等，RAT-SQL | [4] | schema linking、关系感知编码、复杂 schema 建模 | 支撑 Schema Agent 和 schema linking 错误分析 | 待读 |
| 8 | Scholak 等，PICARD | [6] | 语法约束解码、增量解析、无效 SQL 抑制 | 可作为 SQL+ parser/converter 与生成约束的对照 | 待读 |
| 9 | Li 等，RESDSQL | [7] | schema linking 与 skeleton parsing 解耦、粗到细 SQL 结构生成 | 支撑 Schema Agent、结构化中间步骤和复杂 SQL 规划；替换原 DAIL-SQL 精读位以强化正式来源 | 待读 |
| 10 | Pourreza 等，DIN-SQL | [10] | 分解式 in-context learning、自修正、任务拆解 | 支撑“分解生成 + 修正”的路线；对照本课题 SQL+ step-wise repair | 待读 |
| 11 | Wang 等，MAC-SQL | [11] | 多智能体协作、Decomposer/Selector/Refiner 等角色分工 | 支撑多智能体架构；对照本项目 Schema/Critic/Skill Router/Repair Skill | 待读 |
| 12 | Pourreza 等，CHESS | [12] | 检索、schema 选择、候选验证、执行反馈 | 支撑执行验证和候选选择思想；和本课题 repair loop 对照 | 待读 |
| 13 | Pourreza 等，CHASE-SQL | [13] | 多路径推理、候选生成、偏好优化选择 | 支撑多候选与选择策略，作为后续扩展方向而非当前核心结果 | 待读 |
| 14 | Li 等，SQL-Factory | [15] | 多智能体 SQL 数据生成、质量控制、大规模样例构造 | 用作后续扩充 SQL+ 样例和错误样例的数据构造参考 | 待读 |
| 15 | Ni 等，LEVER | [16] | execution-based verifier、候选程序验证、执行结果特征利用 | 支撑 Executor/Critic 对候选结果进行验证和筛选；替换原 SQLCritic 精读位以避免 arXiv-only 依赖 | 待读 |

## 单篇精读记录模板

每篇建议按同一结构做笔记，便于最后汇总到开题答辩和论文相关工作章节。

```markdown
## 序号. 论文标题

### 1. 一句话定位

### 2. 作者要解决的问题

### 3. 核心方法

### 4. 实验设置与主要结果

### 5. 关键贡献

### 6. 局限性

### 7. 和本课题的关系

### 8. 可用于开题答辩的说法

### 9. 可能被老师追问的问题

### 10. 精读结论
```

## 第一轮精读建议

第一轮不要追求逐字翻译，先把每篇放进课题坐标系里：

1. 这篇论文解决的是 Text-to-SQL 哪个环节的问题。
2. 它是否使用中间表示、分解、执行反馈、候选选择或多智能体。
3. 它和 SQL+ 的关系是“直接支撑、对照方案、评测背景、后续扩展”中的哪一种。
4. 答辩时如果被抽问，能否用 3-5 句话说明贡献、方法、局限和本课题借鉴点。

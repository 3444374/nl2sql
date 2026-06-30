# 开题汇报 PPT 结构稿 v4

题目：面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究

调整原则：本版把“动机测试”独立成完整汇报段落，按实验背景与设置、实验过程、结果表、结果分析和设计结论展开。先说明为什么设计 SQL+，再说明为什么需要多 Agent 和 repair skill，随后进入系统设计、可行性实验和初期验证实验。

视觉原则：整体风格保持简约、大气，主色只保留深蓝、灰和少量红色强调。每页用红色重点句突出本页结论，避免装饰性配色。

本地 SVG 图源：

- `docs/opening/assets/svg/system_architecture.svg`：SQL+ 多智能体反馈修正框架。
- `docs/opening/assets/svg/technical_route.svg`：研究方案与技术路线。
- `docs/opening/assets/svg/motivation_test_flow.svg`：动机测试推出系统设计的逻辑流程。

---

## 第 1 页：题目页

- 研究方向：Text-to-SQL / SQL+ 中间表示 / 多智能体 / 执行反馈修正。
- 汇报人、导师、专业、时间：待填写。
- 讲述重点：本课题不是做一次性 SQL 生成 Demo，而是研究生成失败后的诊断、路由和局部修复闭环。

## 第 2 页：汇报结构

| 部分 | 主要问题 | 对应内容 |
| --- | --- | --- |
| 背景与问题 | 为什么 Text-to-SQL 还不稳定 | 真实查询场景和 SQL 错误结构 |
| 研究发展 | 现有研究做到哪里 | benchmark、IR、约束解码、agentic NL2SQL |
| 动机测试 | 为什么需要 SQL+ 和多 Agent | 实验背景、实验过程、结果表、分析结论 |
| 系统设计 | 准备怎么做 | SQL+ 中间表示与多智能体反馈闭环 |
| 可行性与初期验证 | 当前做到了哪里 | 转换、修复、repair skill 和 Spider 小子集 |
| 后续计划 | 还要补什么 | 多组对比、消融、跨库评估和论文计划 |

## 第 3 页：背景与问题：自然语言查询需要可修复

| 错误层级 | 常见表现 | 为什么难修 |
| --- | --- | --- |
| schema linking | 表列选择、连接路径错误 | 会传导到 WHERE、GROUP 和 SELECT |
| value linking | 枚举值、日期、阈值错误 | 执行可能不报错，但结果语义错 |
| aggregation | COUNT、GROUP、HAVING 口径错误 | 涉及跨子句依赖 |
| projection/order | 输出列、排序字段、top-k 错误 | 结果看似合理但不符合问题 |

重点：本课题关注生成失败后的定位、路由和局部修复。

## 第 4 页：研究发展：从 benchmark 到 agentic NL2SQL

| 年份 | 代表方向 | 代表工作 | 对本课题的启发 |
| --- | --- | --- | --- |
| 2018 | 跨库 Text-to-SQL benchmark | Spider | 推动复杂 schema 泛化评测 |
| 2019 | 结构化中间表示 | IRNet / SemQL | 用 IR 降低 SQL 结构复杂度 |
| 2020 | 关系感知编码 | RAT-SQL | 强化 schema linking |
| 2021 | SQL 简化表达与语法约束 | NatSQL、PICARD | 简化目标表达、约束解码 |
| 2023 | LLM 分解与执行验证 | BIRD、DIN-SQL、LEVER | 用分解和执行反馈提高可靠性 |
| 2024 | 多路径与过程化 SQL | Pipe Syntax、CHESS、CHASE-SQL | 查询计划更强调过程化和可检查 |
| 2025 | Agentic 与数据合成 | Spider 2.0、MAC-SQL、SQL-Factory | 多角色协作和真实工作流成为趋势 |

## 第 5 页：当前研究与发展：benchmark、IR 与 agentic NL2SQL

| 方向 | 代表工作与年份 | 已解决问题 | 对本课题的启发 |
| --- | --- | --- | --- |
| 公开评测 | Spider 2018、BIRD 2023、Spider 2.0 2025 | 复杂 schema、真实数据、企业工作流 | 后续需要从小子集扩展到多库和真实方言 |
| 中间表示 | SemQL 2019、NatSQL 2021、Pipe Syntax 2024 | 降低 SQL 生成或表达复杂度 | SQL+ 要证明修复接口价值，而不只是换语法 |
| 约束与验证 | PICARD 2021、LEVER 2023 | 语法约束、执行验证、候选筛选 | 执行反馈需要进入诊断和 patch 过程 |
| Agentic NL2SQL | DIN-SQL 2023、CHESS 2024、CHASE-SQL 2024、MAC-SQL 2025 | 分解、多候选、多角色协作 | 需要更清楚的步骤级错误定位和 repair skill 评价 |
| 数据生成 | SQL-Factory 2025 | 多智能体生成高质量 SQL 数据 | 可用于后续扩充训练和评测样例 |

## 第 6 页：动机测试一：实验背景与设置

| 项目 | 设置 |
| --- | --- |
| 实验背景 | 第一次生成的 SQL 经常可执行但语义不对，需要判断问题来自表示形式、生成方式还是修复方式 |
| 核心问题 | 为什么设计 SQL+，为什么不能只靠单 Agent 或整条 SQL 重写 |
| 实验环境 | SQLite 内存数据库，自建订单分析数据集，模型为 gpt-5-mini |
| 样例规模 | 30 条自然语言查询；13 条 SQL+ prompt v2 已知失败样例；14 条 Direct SQL 失败样例 |
| 对比对象 | Direct SQL、NL2SQL+、SQL+、NatSQL-style proxy、SemQL-style proxy、Direct SQL Refiner、SQL+ Refiner、Router + Repair Skills |
| 评估指标 | execution match、valid rate、token、latency、alias dependency、cross-clause reference、repair success、patch minimality |

重点：动机测试先证明设计必要性，再进入系统架构。

## 第 7 页：动机测试二：实验过程

| 步骤 | 具体做法 | 回答的问题 |
| --- | --- | --- |
| 1 初次生成对比 | 同一批 30 条问题和同一 schema，分别生成 Direct SQL 与 SQL+，转换后执行并对齐 gold 结果 | 只换成 SQL+ 是否就能明显提升准确率 |
| 2 表示复杂度对比 | 把同一批 gold 查询整理成 SQL、SQL+、SemQL-style、NatSQL-style、Pipe-style，统计 token、别名依赖和跨子句引用 | SQL+ 的优势是不是来自更短表达 |
| 3 生成成本对比 | 用同一模型生成多种目标表示，记录 valid rate、execution match、总 token 和平均延迟 | SQL+ 是否有额外生成成本 |
| 4 修复策略对比 | 收集失败输出，分别交给 SQL+ Refiner、Direct SQL Refiner、Critic-Refiner 和 Router + Repair Skills 修复 | 多 Agent 与局部 repair skill 是否必要 |

重点：实验过程围绕一个问题展开，SQL+ 和多 Agent 是否真的让错误更容易被修。

## 第 8 页：动机测试三：结果表一，为什么设计 SQL+

| 测试项 | 关键结果 | 结果分析 |
| --- | --- | --- |
| Baseline | Direct SQL 16/30；NL2SQL+ prompt v2 17/30 | 只换输出格式提升很小，SQL+ 不能只靠初次生成准确率立论 |
| IR 复杂度 | SQL+ 平均 token 35.0333，高于 Standard SQL 31.5333 | SQL+ 不是更短的表示，不能用压缩长度解释价值 |
| 结构依赖 | SQL+ alias dependency 0.7，cross-clause reference 1.0；SQL 分别为 2.0333 和 2.3333 | SQL+ 的优势在于步骤边界更清楚，跨区域耦合更少 |
| 生成成本 | SQL+ execution match 14/30，平均 813.0333 tokens，9.2197s | SQL+ 有成本，必须在修复阶段体现收益 |

结论：SQL+ 不是为了更短，而是为了把错误落到可定位、可修改的步骤上。

## 第 9 页：动机测试四：结果表二，为什么使用多 Agent

| 方法 | 样例 | 修复结果 | 结果分析 |
| --- | --- | --- | --- |
| SQL+ non-gold Refiner v2 | 13 条 SQL+ 已知失败样例 | 4/13 | 粗粒度反馈不足，模型容易改不到关键步骤 |
| Direct SQL non-gold Refiner | 14 条 Direct SQL 失败样例 | 6/14 | 整条 SQL 修复能工作，但修改范围不稳定，解释性较弱 |
| Schema-Critic-Refiner | 13 条 SQL+ 已知失败样例 | 3/13 | 先诊断再重写不一定有效，诊断没有转化为明确 repair 动作 |
| Step-wise Critic-Refiner | 13 条 SQL+ 已知失败样例 | 3/13 | 步骤级诊断更细，但没有限制 patch 范围时仍不稳定 |
| Skill Router + Repair Skills v3 | 13 条 known-failure set | 13/13 | 按错误类型路由到局部 skill 后，修复范围更可控 |

结论：Agent 数量不是重点，诊断、路由、局部 patch 和执行验证才是关键。

## 第 10 页：动机测试五：结果分析与设计结论

| 实验观察 | 推出的设计要求 |
| --- | --- |
| 初次生成阶段，SQL+ 只比 Direct SQL 略高，且 token 和 latency 更高 | 不能把 SQL+ 设计成单纯的生成格式，必须服务于反馈修复 |
| SQL+ 的别名依赖和跨子句引用更少 | 需要把查询拆成步骤，让错误定位能落到 FROM、JOIN、WHERE、AGG、ORDER 等局部 |
| 单 Refiner 与简单 Critic 串联效果不稳 | 需要明确分工，Critic 负责诊断，Router 负责分流，Repair Skill 负责局部 patch |
| 分治 repair skill 在当前 known-failure set 上达到 13/13 | 需要保留 skill 化修复，并用 Executor 对候选 patch 做执行验证 |
| Spider fresh e2e 小子集可跑通但规模有限 | 后续必须扩展多库、多难度和更多错误类型，不能过度外推 |

因此，本课题设计的是 SQL+ 支撑下的多智能体反馈修正闭环。

## 第 11 页：研究不足与本课题切入点

- 中间表示多服务于初次生成，对执行反馈后的局部修复关注不足。
- Agent 系统常用于分解、候选生成和选择，错误不一定映射到可修复步骤。
- 评价指标多集中在 execution accuracy，需要补充 repairability 和成本指标。
- 本课题切入点：把 SQL+ 放在生成和修复链路中间，让 Critic、Router、Repair Skill 和 Executor 围绕 SQL+ 步骤工作。

## 第 12 页：提出的系统：SQL+ 多智能体反馈修正框架

```text
自然语言问题
-> SQL+ Generator
-> Translator
-> Executor
-> Critic Agent
-> Skill Router
-> Repair Skill
-> Executor
-> 最终 SQL / 结果 / 修复说明
```

核心思路：不整条重写 SQL，把错误压回 SQL+ 的局部步骤中修。

## 第 13 页：SQL+ 表达示例：把查询拆成步骤

| SQL+ 步骤 | 作用 | 可定位错误 |
| --- | --- | --- |
| FROM | 主表或起点关系 | 起点表错误 |
| JOIN | 连接路径 | 缺 join、冗余 join、连接方向 |
| WHERE | 过滤条件 | value linking、日期边界 |
| GROUP / AGG | 分组和聚合 | COUNT 口径、分组维度 |
| SELECT | 输出列 | 投影列缺失或多余 |
| ORDER / LIMIT | 排序和 top-k | 排序字段、方向、数量 |

## 第 14 页：系统架构设计：可观察的多智能体分工

| 模块 | 输入 | 输出 | 评价方式 |
| --- | --- | --- | --- |
| Schema Agent | 问题、schema、值域样例 | 相关表列、join path、候选值 | schema/value/join accuracy |
| SQL+ Generator | 问题、schema 上下文 | 初始 SQL+ | SQL+ valid、exec match |
| Critic Agent | SQL+、执行反馈、结果摘要 | 错误类型、可疑步骤、证据 | localization accuracy |
| Skill Router | Critic 输出、SQL+ 结构 | repair skill 路由 | router accuracy |
| Repair Skill | SQL+ 局部步骤、反馈 | 候选 patch | patch minimality |
| Executor | 候选 SQL | 执行结果、错误、最终选择 | repair success、latency |

## 第 15 页：实验结构设计：动机、可行性、对比、泛化

| 实验层次 | 对应实验 | 回答的问题 |
| --- | --- | --- |
| 动机测试 | baseline、IR 复杂度、生成成本、单 Refiner 对比 | 为什么不能只靠直接生成或整体重写 |
| 方案可行性 | SQL+ parser、translator、executor 闭环 | SQL+ 是否能稳定解析、转换和执行 |
| 机制可行性 | Critic -> Router -> Repair Skill -> Executor | 局部 skill 分治是否能修复已知错误类型 |
| 公开子集验证 | Spider concert_singer 小规模 fresh e2e 与 semantic repair | 能否离开自建数据集初步跑通 |
| 后续对比与消融 | 多表示、多修复策略、去模块实验 | 各模块是否真的贡献效果 |

## 第 16 页：前期可行性实验：总体设置

| 项目 | 当前设置 |
| --- | --- |
| 自建数据库 | 企业订单分析样例库 |
| 数据表 | customers、products、orders、order_items |
| 自然语言查询 | 30 条 |
| SQL+ 标准样例 | 30 条 |
| 修复样例 | 15 条规则修正样例；13 条 SQL+ prompt v2 已知失败样例 |
| 执行环境 | SQLite 内存数据库 |
| 模型 | gpt-5-mini |
| 评价方式 | 执行生成 SQL，并与 gold SQL 执行结果比较 |
| gold 边界 | gold SQL 只用于离线评估，非 gold 修复不把 gold 差异输入模型 |

## 第 17 页：实验一：SQL+ 表达与转换可行性

| 维度 | 内容 |
| --- | --- |
| 实验类型 | 验证系统和方案可行性的基础实验 |
| 实验设置 | 30 条人工 SQL+ 标准样例，覆盖过滤、join、聚合、排序、top-k |
| 实验过程 | SQL+ parser 解析 -> converter 转 SQL -> SQLite 执行 -> 与 gold SQL 结果比较 |
| 实验结果 | SQL+ 语法通过 30/30；SQL 可执行 30/30；执行一致 30/30 |
| 实验结论 | SQL+ 已形成可解析、可转换、可执行的最小闭环 |

## 第 18 页：实验二：反馈修正与 repairability

| 方法 | 初始失败 | SQL+ 有效 | SQL 可执行 | 修复成功 | 说明 |
| --- | ---: | ---: | ---: | ---: | --- |
| SQL+ 诊断辅助 Refiner | 13 | 13/13 | 13/13 | 13/13 | 使用 gold-derived differences |
| SQL+ 非 gold Refiner v2 | 13 | 13/13 | 12/13 | 4/13 | 执行反馈和粗粒度诊断 |
| Direct SQL 非 gold Refiner | 14 | - | 14/14 | 6/14 | 直接修标准 SQL |
| SQL+ Skill Router + Repair Skills v3 | 13 | 13/13 | 13/13 | 13/13 | Critic 路由到五类局部 skill |

结论：SQL+ 路线修复成功率和 patch 可控性更好，但 token 成本更高。

## 第 19 页：实验三：Repair Skill 分治结果

| Repair skill | 样例数 | 修复成功 | 覆盖的典型问题 |
| --- | ---: | ---: | --- |
| value-linking | 3 | 3/3 | 候选值替换、日期边界归一化、值过滤错误 |
| ORDER | 3 | 3/3 | 排序字段错误、升降序错误、LIMIT/Top-K 约束 |
| aggregation | 3 | 3/3 | COUNT 口径、GROUP 维度、AGG 别名、ORDER/HAVING 引用 |
| join | 3 | 3/3 | JOIN 方向、冗余 JOIN、缺失 JOIN、paid 过滤遗漏 |
| projection | 1 | 1/1 | 结果列多、列少或列顺序错误 |

边界：该 13/13 只对应当前 known-failure set，不能表述为完整 benchmark 成绩。

## 第 20 页：实验四：Spider 小规模公开子集

| 实验 | 样例 | SQL+ 有效 | SQL 可执行 | 执行一致 | 说明 |
| --- | ---: | ---: | ---: | ---: | --- |
| conversion smoke test | 20 | 20/20 | 20/20 | 20/20 | Spider gold SQL -> SQL+ -> SQL |
| fresh e2e generation | 20 | 19/20 | 19/20 | 19/20 | question + schema -> SQL+ |
| fresh e2e + semantic repair | 20 | 20/20 | 20/20 | 20/20 | 同一次 fresh 输出经 Router -> semantic repair skill |

边界：conversion smoke 使用 gold SQL 改写，不是端到端准确率；整体不是完整 Spider benchmark 跑分。

## 第 21 页：前期可行性分析小结

| 论证点 | 当前证据 | 结论 |
| --- | --- | --- |
| 表达可行 | SQL+ -> SQL，30/30 执行一致 | 表示和 translator 可用 |
| 修复更关键 | 单 Refiner 不稳，Router Skills 13/13 | 研究重点应放在 repairability |
| 分治机制有效 | 五类 skill 覆盖当前 known-failure set | 机制可行，但需扩展评测 |
| 公开子集已跑通 | Spider 20 条 fresh 19/20 -> 20/20 | 有迁移潜力，但不能过度外推 |
| 成本需补齐 | SQL+ token 更高 | 需要记录 token、latency、repair rounds |

## 第 22 页：后续实验设计与评价指标

| 实验组 | 目的 | 主要指标 |
| --- | --- | --- |
| Direct SQL / NL2SQL+ | 比较直接生成和 SQL+ 生成 | execution accuracy、valid rate、token、latency |
| SemQL/NatSQL/Pipe-style proxy | 比较中间表示形态 | 复杂度、转换、生成成本 |
| whole-query rewrite / single refiner / Router skills | 比较修复策略 | repair success、repair rounds、patch minimality |
| 消融实验 | 去掉 Critic、Router、skill、executor | 性能下降幅度、错误类型变化 |
| Spider/BIRD/达梦子集 | 验证迁移和方言适配 | exec match、方言错误、泛化失败类型 |

## 第 23 页：当前不足、风险控制与进度安排

| 风险 | 当前情况 | 控制方式 |
| --- | --- | --- |
| 样本规模小 | known-failure set 和 Spider 子集都较小 | 扩展失败集、Spider 多库和 BIRD 子集 |
| 结果被误读 | conversion smoke 来自 gold SQL | PPT 和论文中始终标注边界 |
| SQL+ 成本较高 | token 和 latency 未必占优 | 补齐成本实验，用 repairability 解释收益 |
| 方言适配不足 | 当前主要是 SQLite | 补达梦日期、分页、类型转换和函数规则 |

进度：07-08 月统一生成入口和扩充失败集；09-10 月完成消融和公开子集；11-12 月推进达梦适配和论文初稿。

## 第 24 页：预期创新点与总结

- SQL+ 中间表示：面向生成、转换、诊断和局部修复共同设计。
- 多智能体反馈修正框架：Critic、Router、Repair Skill 和 Executor 形成闭环。
- repairability 评价视角：不只看最终准确率，还看定位、路由、patch 范围和成本。
- 可复现实验体系：脚本、日志、开题材料和后续公开子集评测同步推进。

总结：SQL+ 的价值在于把查询计划拆成可检查、可路由、可局部修复的步骤。

## 第 25 页：主要参考文献

- Yu et al., Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task, EMNLP 2018.
- Guo et al., Towards Complex Text-to-SQL in Cross-Domain Database with Intermediate Representation, ACL 2019.
- Wang et al., RAT-SQL: Relation-Aware Schema Encoding and Linking for Text-to-SQL Parsers, ACL 2020.
- Gan et al., Natural SQL: Making SQL Easier to Infer from Natural Language Specifications, Findings of EMNLP 2021.
- Scholak et al., PICARD: Parsing Incrementally for Constrained Auto-Regressive Decoding from Language Models, EMNLP 2021.
- Li et al., Can LLM Already Serve as A Database Interface? A Big Bench for Large-Scale Database Grounded Text-to-SQLs, NeurIPS 2023.
- Nan et al., Enhancing Text-to-SQL Capabilities of Large Language Models: A Study on Prompt Design Strategies, EMNLP 2023.
- Dong et al., C3: Zero-shot Text-to-SQL with ChatGPT, arXiv 2023.
- Pourreza and Rafiei, DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction, NeurIPS 2023.
- Ni et al., Leveraging Execution Feedback for Program and Query Generation, 2023.
- Talaei et al., CHESS: Contextual Harnessing for Efficient SQL Synthesis, 2024.
- Pourreza et al., CHASE-SQL: Multi-Path Reasoning and Preference Optimized Candidate Selection in Text-to-SQL, 2024.
- GoogleSQL, Pipe Syntax in SQL, 2024.
- Liu et al., MAC-SQL: A Multi-Agent Collaborative Framework for Text-to-SQL, 2025.
- Lei et al., Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows, 2025.
- SQL-Factory: A Multi-Agent Framework for High-Quality and Large-Scale SQL Generation, 2025.

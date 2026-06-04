# 实验大纲与方向调整记录

## 课题定位

课题名称暂定为：面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究。

核心实验问题：

1. SQL+ 是否能降低复杂 SQL 查询的表达复杂度。
2. SQL+ 是否适合作为自然语言到 SQL 的中间表示。
3. SQL+ 层反馈修正是否比最终 SQL 层整体重生成更容易定位和修复错误。
4. 多智能体流程是否能提升生成、验证和修正的成功率。

## 当前实验主线

当前采用从小到大的实验路线：

1. 构造小型业务数据库和 SQL+ 样例，验证 SQL+ 到 SQL 的可执行闭环。
2. 构造错误 SQL+ 样例，验证执行反馈能否映射到 SQL+ 局部步骤并完成修正。
3. 扩充样例规模和查询复杂度，形成开题阶段可展示的数据集。
4. 加入单 Agent baseline，对比自然语言直接生成 SQL 与自然语言生成 SQL+。
5. 加入多 Agent 框架，对比标准 SQL 多智能体与 SQL+ 多智能体。
6. 引入公开数据集 Spider/BIRD 的子集，验证方法在公开 benchmark 上的可迁移性。

## 实验留痕机制

已创建项目级 Codex skill：

- `.codex/skills/nl2sql-experiment-tracker`
- `.codex/skills/nl2sql-sqlplus-research`
- `.codex/skills/nl2sql-repair-skill-lab`

使用规则：

- 每次规划、运行或复盘 NL2SQL+ 实验时，优先使用该 skill。
- 每次实验运行、模型运行、benchmark、失败实验或指标变化后，必须追加 `docs/project/experiment_log.md`。
- 非实验类项目过程，例如目录整理、GitHub 同步、开题材料修订、飞书文档写入和工作流调整，应记录到 `docs/project/project_log.md`，不要写入实验日志。
- 当实验结果影响下一步方向时，必须同步更新本文件。
- 失败实验也要记录，尤其要记录失败命令、错误信息、原因判断和下一步调整。
- 工作流、跨电脑同步、项目记忆或 agent 协作规则发生变化时，必须同步更新 `AGENTS.md`、相关 `.codex/skills/*/SKILL.md` 和 `docs/project/workflow_traceability.md`。
- 开题报告可引用的结果发生变化时，必须同步检查 `docs/opening/` 和 `docs/project/opening_preliminary_results.md`。

## 实验阶段规划

### 阶段一：SQL+ 表达与转换验证

目标：

- 定义 SQL+ 最小语法子集。
- 实现 SQL+ parser 和 SQL converter。
- 验证 SQL+ 能覆盖常见查询操作。
- 对比 SQL+ 转换 SQL 与人工标准 SQL 的执行结果。

当前状态：已完成初版。

产物：

- `data/schema.sql`
- `data/sqlplus_cases.jsonl`
- `src/sqlplus.py`
- `scripts/sqlplus/run_experiment.py`
- `docs/sqlplus/pre_experiment_report.md`

### 阶段二：SQL+ 层反馈修正验证

目标：

- 构造 schema 错误、字段错误、join 错误等错误样例。
- 收集数据库执行错误。
- 将错误映射回 SQL+ 的局部步骤。
- 验证局部修正后是否可以重新执行成功。

当前状态：已完成字段错误修正初版。

产物：

- `data/repair_cases.jsonl`
- `scripts/sqlplus/run_repair_experiment.py`
- `docs/sqlplus/repair_experiment_report.md`

### 阶段三：样例扩充与复杂度分层

目标：

- 将 SQL+ 样例扩充到 30 条以上。
- 按 simple、medium、hard 标注查询复杂度。
- 覆盖单表查询、多表 join、聚合、having、top-k、时间范围、子查询替代表达。
- 将错误样例扩充到 15 条以上。

当前状态：已完成初版。

建议产物：

- `data/sqlplus_cases.jsonl`
- `data/repair_cases.jsonl`
- `docs/sqlplus/dataset_summary.md`

### 阶段四：单 Agent baseline

目标：

- 设计自然语言直接生成 SQL 的 prompt。
- 设计自然语言生成 SQL+ 的 prompt。
- 比较两种路线的 SQL 可执行率、执行一致率、错误类型。

当前状态：已完成 prompt 设计、评估框架和 OpenAI API 运行脚本，已完成 `gpt-5-mini` Direct baseline、SQL+ prompt v1、SQL+ prompt v2 对比。

建议产物：

- `prompts/baseline/direct_sql.md`
- `prompts/baseline/sqlplus_generation.md`
- `scripts/baseline/run_llm_baseline.py`
- `docs/baseline/baseline_report.md`

### 阶段五：多智能体原型

目标：

- 形成 `Critic Agent -> Skill Router -> Repair Skill -> Executor` 的 SQL+ 反馈修正闭环。
- 保留 Intent Agent、Schema Agent、Planner Agent、SQL+ Generator Agent、Translator Agent 等组件作为初始生成和上下文组织模块。
- 记录各 Agent 的中间输出。
- 对比单 Agent、prompt-only 多 Agent、SQL+ Skill Router + Repair Skills 的生成和修复质量。
- 引入 Tool/RAG/Skill 增强机制，使 Agent 不只依赖 prompt，而能查询 schema、字段值、执行候选 patch 并验证结果。
- 参考 CHESS、CHASE-SQL、Tool-Assisted Agent、SQLCritic 等工作，重点验证多阶段诊断、候选生成、局部修复和执行验证是否能提升真实反馈修正能力。

当前状态：进行中。已完成 Refiner Agent、Schema-Critic-Refiner 初版、Step-wise Critic、ORDER/value-linking 分治实验、五类 repair skill 初版和 Skill Router v3 端到端实验。下一步优先扩展无报错但结果语义不匹配的诊断与复合修复能力。

建议产物：

- `src/agents/`
- `scripts/agents/run_multi_agent.py`
- `docs/agents/multi_agent_report.md`
- `prompts/agents/sqlplus_refiner.md`
- `scripts/agents/run_openai_refiner.py`
- `docs/agents/refiner_model_report.md`
- `src/tools/`
- `src/skills/`
- `scripts/agents/tools/`
- `docs/agents/tools/`

### 阶段六：公开数据集适配

目标：

- 选取 Spider 或 BIRD 的小规模子集。
- 将部分标准 SQL 改写为 SQL+。
- 验证 SQL+ 转换和反馈修正在公开数据集样例上的适用性。
- 从单一数据库 smoke test 扩展到多数据库、多难度和更多 SQL 结构，但开题阶段不追求完整排行榜成绩。

当前状态：已启动。已完成 Spider dev 小规模受支持子集 smoke test。

建议产物：

- `data/spider_subset/`
- `data/bird_subset/`
- `docs/sqlplus/public_dataset_report.md`
- `data/benchmarks/spider/`
- `scripts/benchmarks/run_spider_smoke.py`
- `docs/benchmarks/spider_smoke_report_20.md`

## 当前方向判断

当前阶段优先级：

1. 扩展 `Critic Agent -> Skill Router -> Repair Skill -> Executor` 闭环，覆盖无报错但结果语义不匹配和复合错误场景。
2. 强化 projection/SELECT 诊断，处理结果列多、列少、列顺序和明细标识保留等问题。
3. 强化 Schema/value lookup、SQL+ parser、SQL executor、candidate patch executor 等工具，让 Agent 的修复决策由检索和执行验证支撑。
4. 扩展 Spider/BIRD 小子集适配到多数据库、多难度和更多 SQL 结构，但不做完整 benchmark 排行榜目标。
5. 参考 SQL-Factory 的多智能体 SQL 数据生成思路，作为后续扩充 SQL+ 样例和错误样例的数据构造参考，不把它作为当前核心方法替代路线。

暂不优先处理：

- 完整多智能体工程化框架。
- 大规模公开 benchmark 跑分。
- 达梦数据库真实驱动适配。
- 大规模 SQL 工作负载自动生成系统。

原因：

开题阶段更需要证明研究方向可行、实验路径清晰、后续工作可落地。完整系统可以作为中后期实现目标。

最新方向判断：

- 诊断辅助 Refiner Agent 已在 13 条 SQL+ prompt v2 失败样例上达到 13/13 修复成功，说明结构化诊断可以驱动 SQL+ 层局部修正。
- 非 gold 执行反馈 Refiner Agent v2 在同样 13 条失败样例上达到 SQL+ 有效 13/13、SQL 可执行 12/13、修复成功 4/13，说明真实反馈修正难度明显更高。
- Direct SQL 非 gold 执行反馈 Refiner 在 14 条 Direct NL2SQL 失败样例上达到 SQL 可执行 14/14、修复成功 6/14，是当前 SQL+ 非 gold 单 Refiner 的必要对照组。
- SQL+ Schema-Critic-Refiner 初版已跑通，SQL+ 有效 13/13、SQL 可执行 13/13，但修复成功 3/13，低于单 Refiner 的 4/13。
- SQL+ Step-wise Critic-Refiner 已跑通，Critic 能输出逐步骤诊断，SQL+ 有效 13/13、SQL 可执行 12/13，但修复成功仍为 3/13。
- 诊断辅助实验使用了 gold-derived differences，应作为“反馈修正链路可行性验证”；非 gold 实验应作为“真实反馈修正挑战”的证据。
- 开题报告中应把当前结果表述为“反馈修正链路可行性验证”，不要表述为最终真实系统性能。
- 当前 Direct SQL 单 Refiner 暂时高于 SQL+ 单 Refiner，说明 SQL+ 的优势不能只靠粗粒度反馈 prompt 体现，下一步应从单 Refiner prompt 转向 `Schema Agent + Critic Agent + Refiner Agent`，先提升非 gold 错误定位质量。
- 当前多智能体初版说明：Agent 串联本身不会自动提升效果，Critic Agent 必须按 SQL+ 局部步骤输出更准确的诊断，否则会误导 Refiner。
- Step-wise Critic 提高了诊断粒度，但未提高修复成功率，说明下一步应做按错误类型分治和反事实执行，而不是继续扩大 prompt。
- ORDER/value-linking 分治实验已完成：ORDER-only 为 2/3，value-linking-only 为 3/3，说明按错误类型限制局部修复范围是有效方向。
- 仅依赖 prompt 的 Agent 已暴露出上限。下一步需要引入工具增强：Schema/value lookup、SQL+ parser、SQL executor、candidate patch executor，以及面向错误类型的 repair skill。
- Tool/Skill 辅助 value-linking 修复已完成初版：value lookup tool + value_linking_repair_skill 在 3 条 value-linking 样例上达到 SQL+ 有效 3/3、SQL 可执行 3/3、修复成功 3/3。
- 该结果说明 Agent 不应只依赖 prompt。对值链接、日期边界、候选 patch 选择等问题，应让 Agent 调用 schema/value 检索工具和执行验证工具，再由 repair skill 选择可执行候选。
- Tool/Skill 辅助 ORDER 修复已完成初版：ORDER repair skill 在 3 条 ORDER-only 样例上达到 SQL+ 有效 3/3、SQL 可执行 3/3、修复成功 3/3，高于此前 prompt-only ORDER Refiner 的 2/3。
- 该结果进一步支持“错误类型路由 + 局部 repair skill”的实验路线。下一步应将 aggregation 和 join 也设计成可执行候选生成与验证的 skill。
- Tool/Skill 辅助 aggregation 修复已完成初版：aggregation repair skill 在 3 条聚合样例上达到 SQL+ 有效 3/3、SQL 可执行 3/3、修复成功 3/3，覆盖冗余 id 分组、COUNT 口径、缺 GROUP 维度、AGG 别名和 ORDER 聚合别名引用。
- 当前 value-linking、ORDER、aggregation 三类局部 skill 均达到 3/3，小样例结果支持后续构建 `Critic Agent -> Skill Router -> Repair Skill -> Executor` 的闭环。
- Tool/Skill 辅助 join 修复已完成初版：join repair skill 在 3 条 join 相关样例上达到 SQL+ 有效 3/3、SQL 可执行 3/3、修复成功 3/3，覆盖 JOIN 方向规范化、冗余 JOIN 删除、缺失 JOIN 补全、缺少 paid 过滤和 join 影响的投影/聚合修复。
- 当前五类 repair skill（value-linking、ORDER、aggregation、join、projection）已完成初版。projection repair skill 在 q006 projection mismatch 上达到 SQL+ 有效 1/1、SQL 可执行 1/1、修复成功 1/1。
- Skill Router v3 端到端实验已完成：基于 Critic Agent 的 `likely_error_type`、局部步骤诊断和 SQL+ 结构特征自动路由五类 repair skill，在 13 条 SQL+ 失败样例上达到 SQL+ 有效 13/13、SQL 可执行 13/13、修复成功 13/13。
- Router v3 相比 SQL+ 非 gold 单 Refiner v2 的 4/13、Schema-Critic-Refiner 初版的 3/13 有明显提升。需要注意该结果仍是 13 条已知失败样例上的小规模验证，下一步应扩展无报错语义错和公开子集样例。
- Spider 小规模公开 benchmark smoke test 已完成：在 Spider dev 的 `concert_singer` 数据库中筛选 20 条当前 SQL+ 子集可覆盖的查询，达到 SQL+ 有效 20/20、SQL 可执行 20/20、执行一致 20/20。
- 该结果只能作为公开 benchmark 子集迁移可行性证据，不应表述为完整 Spider benchmark 跑分。后续需要扩展到多数据库、多难度和更多 SQL 结构。
- 开题报告新增 SQL-Factory、CHESS、CHASE-SQL、Tool-Assisted Agent、ReFoRCE、XiYan-SQL、SQLCritic 等文献后，实验路线不做大改。新增文献主要用于支撑多阶段、多智能体、执行反馈和候选验证的合理性。
- SQL-Factory 更适合作为后续数据扩充和 SQL 样例生成的参考，不替代本课题当前的 SQL+ 中间表示与反馈修正主线。
- 现阶段最小可落地闭环仍是：`Natural language -> SQL+ -> SQL -> Execution feedback -> Critic Agent -> Skill Router -> Repair Skill -> Executor`。

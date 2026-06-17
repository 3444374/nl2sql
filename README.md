# NL2SQL+ 开题前期实验

本目录用于支撑“面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究”的开题准备。

## 跨电脑同步

建议使用 GitHub 同步本项目。跨 Windows/macOS 的配置说明见：

- `AGENTS.md`：给 Codex/Agent 的项目级工作规则。
- `docs/project/cross_machine_setup.md`：GitHub 同步、另一台电脑初始化、API key 和 project skills 安装说明。
- `docs/project/workflow_traceability.md`：关键实验、代码修改、项目进展和方向调整的留痕规则。
- `docs/project/experiment_log.md`：只记录实验运行、指标、失败和实验方向调整。
- `docs/project/project_log.md`：记录非实验类项目过程，例如文档整理、同步、开题材料和工作流调整。
- `scripts/setup/install_project_skills.ps1`：将本仓库 `.codex/skills/` 下的项目 skills 安装到当前电脑的 Codex skills 目录。

新机器克隆后建议先执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup/install_project_skills.ps1
python scripts/sqlplus/run_experiment.py
python scripts/benchmarks/run_spider_smoke.py --limit 20
```

## 已完成内容

- 构造企业订单分析样例库：`data/schema.sql`
- 构造自然语言、标准 SQL、SQL+ 三元组：`data/sqlplus_cases.jsonl`
- 实现 SQL+ 子集解析与 SQL 转换：`src/sqlplus.py`
- 完成 SQL+ 转换和执行一致性实验：`scripts/sqlplus/run_experiment.py`
- 完成 SQL+ 层字段错误修正实验：`scripts/sqlplus/run_repair_experiment.py`
- 固化 SQL+ 语法说明：`docs/sqlplus/sqlplus_syntax.md`
- 设计单 Agent baseline prompt：`prompts/baseline/direct_sql.md`、`prompts/baseline/sqlplus_generation.md`
- 准备 baseline 评估框架：`scripts/baseline/prepare_baseline_inputs.py`、`scripts/baseline/run_baseline_eval.py`
- 准备 OpenAI baseline 运行脚本：`scripts/baseline/run_openai_baseline.py`
- 准备 SQL+ mismatch 诊断与 Refiner 验证：`scripts/agents/diagnostics/diagnose_sqlplus_mismatches.py`
- 完成诊断辅助 Refiner Agent 实验：`scripts/agents/refiner/run_openai_refiner.py`
- 完成非 gold 执行反馈 Refiner Agent 实验：`scripts/agents/refiner/build_feedback_refiner_inputs.py`、`scripts/agents/refiner/run_openai_feedback_refiner.py`
- 完成 Direct SQL 非 gold 执行反馈 Refiner 对照实验：`scripts/agents/refiner/build_direct_feedback_refiner_inputs.py`、`scripts/agents/refiner/run_openai_direct_feedback_refiner.py`
- 完成 SQL+ Schema-Critic-Refiner 多智能体初版实验：`scripts/agents/schema/build_sqlplus_schema_agent_inputs.py`、`scripts/agents/critic/run_openai_sqlplus_critic.py`
- 完成 SQL+ value lookup tool + repair skill 初版实验：`scripts/agents/tools/run_value_lookup_repair_skill.py`
- 完成 SQL+ ORDER repair skill 初版实验：`scripts/agents/tools/run_order_repair_skill.py`
- 完成 SQL+ aggregation repair skill 初版实验：`scripts/agents/tools/run_aggregation_repair_skill.py`
- 完成 SQL+ join repair skill 初版实验：`scripts/agents/tools/run_join_repair_skill.py`
- 完成 SQL+ Skill Router 端到端修复实验：`scripts/agents/pipeline/run_skill_router_experiment.py`
- 完成 Spider 小规模公开 benchmark smoke test：`scripts/benchmarks/run_spider_smoke.py`
- 完成 SQL+ 与 Standard SQL、SemQL-style、NatSQL-style、Pipe-style 的中间表示复杂度对比实验：`scripts/sqlplus/run_ir_complexity_eval.py`
- 完成 Direct SQL、SQL+、NatSQL-style、SemQL-style 的 IR 生成成本与执行效果对比实验：`scripts/sqlplus/run_ir_generation_cost_eval.py`

## 复现实验

```powershell
python scripts/sqlplus/run_experiment.py
python scripts/sqlplus/run_repair_experiment.py
python scripts/baseline/prepare_baseline_inputs.py
python scripts/baseline/create_oracle_baseline_outputs.py
python scripts/baseline/run_baseline_eval.py
python scripts/baseline/run_openai_baseline.py --dry-run
python scripts/agents/refiner/run_openai_refiner.py --dry-run
python scripts/agents/refiner/build_feedback_refiner_inputs.py
python scripts/agents/refiner/run_openai_feedback_refiner.py --dry-run
python scripts/agents/refiner/build_direct_feedback_refiner_inputs.py
python scripts/agents/refiner/run_openai_direct_feedback_refiner.py --dry-run
python scripts/agents/schema/build_sqlplus_schema_agent_inputs.py
python scripts/agents/critic/run_openai_sqlplus_critic.py --dry-run
python scripts/agents/pipeline/run_repairability_metrics.py
python scripts/sqlplus/run_ir_complexity_eval.py
python scripts/sqlplus/run_ir_generation_cost_eval.py
```

运行后会生成：

- `docs/sqlplus/pre_experiment_report.md`
- `docs/sqlplus/repair_experiment_report.md`
- `docs/baseline/baseline_report.md`
- `docs/agents/diagnostics/sqlplus_mismatch_diagnostics.md`
- `docs/agents/refiner/refiner_oracle_report.md`
- `docs/agents/refiner/refiner_model_report.md`
- `docs/agents/refiner/feedback_refiner_model_report.md`
- `docs/agents/refiner/direct_feedback_refiner_report.md`
- `docs/agents/pipeline/sqlplus_schema_critic_refiner_report.md`
- `docs/agents/pipeline/sqlplus_stepwise_critic_refiner_report.md`
- `docs/agents/pipeline/repairability_metrics_report.md`
- `docs/sqlplus/intermediate_representation_complexity_report.md`
- `docs/sqlplus/ir_generation_cost_report.md`

真实模型 baseline 运行说明：

- `docs/baseline/openai_baseline_runbook.md`

## 开题文档

- `docs/sqlplus/sqlplus_syntax.md`：SQL+ 语法、转换规则、与 GoogleSQL Pipe Syntax 的关系。
- `docs/baseline/baseline_design.md`：Direct NL2SQL 与 NL2SQL+ baseline 设计。
- `docs/sqlplus/dataset_summary.md`：当前样例数据集覆盖情况。

## 当前实验结果

- SQL+ 查询样例：30 条
- 错误修正样例：15 条
- SQL+ 语法通过率：30/30
- 转换 SQL 可执行率：30/30
- 与标准 SQL 执行结果一致率：30/30
- SQL+ 层修正成功率：15/15
- Baseline oracle sanity check：Direct 30/30，NL2SQL+ 30/30
- OpenAI baseline：脚本已完成，待设置 `OPENAI_API_KEY` 后运行真实模型输出
- SQL+ prompt v2：执行一致率 17/30
- SQL+ v2 失败诊断：13 条 semantic mismatch 已分类
- Oracle Refiner 修正链路：13/13
- 诊断辅助 Refiner Agent：13/13 修复成功，SQL+ 有效 13/13，SQL 可执行 13/13
- 非 gold 执行反馈 Refiner Agent v2：4/13 修复成功，SQL+ 有效 13/13，SQL 可执行 12/13
- Direct SQL 非 gold 执行反馈 Refiner：6/14 修复成功，SQL 可执行 14/14
- SQL+ Schema-Critic-Refiner 初版：3/13 修复成功，SQL+ 有效 13/13，SQL 可执行 13/13
- SQL+ Step-wise Critic-Refiner：3/13 修复成功，SQL+ 有效 13/13，SQL 可执行 12/13
- SQL+ ORDER-only 分治修复：2/3 修复成功
- SQL+ value-linking-only 分治修复：3/3 修复成功
- SQL+ value lookup tool + repair skill：3/3 修复成功，SQL+ 有效 3/3，SQL 可执行 3/3
- SQL+ ORDER repair skill：3/3 修复成功，SQL+ 有效 3/3，SQL 可执行 3/3
- SQL+ aggregation repair skill：3/3 修复成功，SQL+ 有效 3/3，SQL 可执行 3/3
- SQL+ join repair skill：3/3 修复成功，SQL+ 有效 3/3，SQL 可执行 3/3
- SQL+ projection repair skill：1/1 修复成功，SQL+ 有效 1/1，SQL 可执行 1/1
- SQL+ Skill Router + Repair Skills v3：13/13 修复成功，SQL+ 有效 13/13，SQL 可执行 13/13
- Repairability 指标对比：SQL+ Critic Router Skills 在 13 条 SQL+ 失败样例上修复成功 13/13，localization accuracy 0.7692，strict minimal patch rate 0.9231，平均 repair rounds 2.2308，平均 repair tokens 3813.9231；Direct SQL Refiner 在 14 条 Direct SQL 失败样例上修复成功 6/14，localization accuracy 0.8571，strict minimal patch rate 0.8571，平均 repair rounds 1，平均 repair tokens 1609.3571。Direct SQL 旧运行未记录 latency，SQL+ 本地 router/skill latency 不含 Critic API latency。
- Spider smoke test：20 条受支持 Spider dev 样例，SQL+ 有效 20/20，SQL 可执行 20/20，执行一致 20/20
- 中间表示复杂度对比：SQL+ 平均 token 数 35.0333，高于 Standard SQL 的 31.5333；SQL+ 平均别名依赖 0.7，低于 Standard SQL 的 2.0333；SQL+ 平均跨子句引用 1.0，低于 Standard SQL 的 2.3333；SQL+ 转换成功 30/30，平均转换时间约 0.007 ms
- IR 生成成本对比：Direct SQL 执行一致 12/30，SQL+ 14/30，NatSQL-style proxy 13/30，SemQL-style proxy 12/30；SQL+ 平均总 token 为 813.0333，高于 Direct SQL 的 599.1667 和 NatSQL-style proxy 的 740.7667；该实验为统一 prompt 下的受控对比，不替代既有 Direct NL2SQL baseline 16/30 和 SQL+ prompt v2 17/30。

说明：诊断辅助 Refiner Agent 使用了 gold-derived mismatch differences，只能证明“结构化反馈 -> SQL+ 局部修正 -> 执行验证”的链路可行，不能直接等同于完全真实的自主反馈修正能力。
非 gold 执行反馈实验更接近真实场景，结果说明仅靠单 Refiner prompt 不足以稳定完成复杂语义修复，后续需要 Schema Agent、Planner Agent 和 Critic Agent。
Direct SQL 修复对照组当前高于 SQL+ 单 Refiner，说明 SQL+ 的优势需要依赖更强的错误定位和局部修正机制，而不能只靠粗粒度反馈 prompt。
Schema-Critic-Refiner 初版没有提升成功率，说明多智能体必须提高 Critic 的结构化错误定位质量，不能只是形式上串联多个 Agent。
分治实验显示，按错误类型限制局部修改范围后，value-linking 类错误修复效果明显更稳定。
Tool/Skill 实验显示，value-linking 类错误适合通过字段值检索、候选 patch 执行验证和局部 repair skill 处理，后续 Agent 应引入工具能力而不是只依赖 prompt。
ORDER skill 实验显示，排序类错误也适合通过错误类型路由、候选 ORDER 生成和执行验证处理。
Aggregation skill 实验显示，聚合口径、GROUP 维度、AGG 投影和 ORDER 聚合别名引用可以在 SQL+ 局部步骤内修复。
Join skill 实验显示，JOIN 路径、冗余 JOIN、缺失 JOIN、paid 过滤和 join 影响的投影/聚合可以通过候选 patch 与执行验证局部修复。
Projection skill 实验显示，结果列多/少可以通过问题意图和 SELECT/AGG 局部候选裁剪修复。
Skill Router v3 实验显示，将 Critic Agent 的错误定位结果和 SQL+ 结构启发路由到局部 repair skill 后，端到端修复成功率从 SQL+ 单 Refiner 的 4/13 提升到 13/13。
Repairability 指标对比说明，SQL+ 修复收益主要体现在成功率和 patch minimality 上，但 Critic Agent 的 token 成本明显高于 Direct SQL 单 Refiner。当前旧输出没有完整 API latency，因此后续真实模型修复实验需要重新记录 `latency_seconds`。
Spider smoke test 说明当前 SQL+ 子集在公开 Spider 的简单/中等查询结构上具备初步迁移可行性，但该结果不是完整 Spider benchmark 跑分。
中间表示复杂度对比说明 SQL+ 当前不是通过缩短 token 获得优势，而是通过显式步骤边界、较少别名/跨子句依赖和确定性转换支撑后续错误定位与局部修复实验。
IR 生成成本对比说明 SQL+ 当前存在生成阶段的 token 和 latency 成本，后续应重点验证错误定位准确率、patch minimality、修复轮数和修复阶段成本，而不是只比较初次生成准确率。

## 开题可引用结论

1. SQL+ 可以把多表 JOIN、过滤、聚合、排序等复杂查询拆成线性步骤，适合作为 Text-to-SQL 的中间表示。
2. SQL+ 到标准 SQL 的规则转换可以稳定执行，说明 SQL+ 不只是概念设计，具备原型验证基础。
3. 执行错误可以映射回 SQL+ 的局部步骤，具备进一步发展为多智能体反馈修正机制的实验基础。

# Baseline Prompt 设计

## 目的

本阶段设计两个单 Agent baseline，用于后续比较：

1. Direct NL2SQL：自然语言直接生成标准 SQL。
2. NL2SQL+：自然语言先生成 SQL+，再由规则转换器生成标准 SQL。

比较目标：

- SQL 可执行率。
- 与标准 SQL 执行结果一致率。
- 错误类型分布。
- 复杂查询表现。
- 反馈修正便利性。

## Baseline A：Direct NL2SQL

输入：

- 数据库 schema。
- 自然语言问题。
- 若干 few-shot 示例。

输出：

- 一条标准 SQL。

评估方式：

```text
自然语言问题 -> LLM 生成 SQL -> SQLite/达梦执行 -> 与 gold SQL 结果比较
```

优势：

- 流程简单。
- 是 Text-to-SQL 常见基线。

风险：

- 复杂 JOIN、聚合和 HAVING 容易出错。
- 错误通常发生在最终 SQL 层，局部定位不直观。

Prompt 文件：

- `prompts/baseline/direct_sql.md`

## Baseline B：NL2SQL+

输入：

- 数据库 schema。
- SQL+ 语法说明。
- 自然语言问题。
- 若干 few-shot 示例。

输出：

- 一段 SQL+。

评估方式：

```text
自然语言问题 -> LLM 生成 SQL+ -> SQL+ 转 SQL -> 执行 -> 与 gold SQL 结果比较
```

优势：

- 查询步骤更线性。
- 适合逐步生成。
- 错误可以映射到 SQL+ 步骤。

风险：

- 增加一次 SQL+ 转换流程。
- 若 SQL+ 语法约束不清，LLM 可能生成不支持的操作。

Prompt 文件：

- `prompts/baseline/sqlplus_generation.md`

## 建议指标

| 指标 | 含义 |
| --- | --- |
| Valid SQL Rate | 最终 SQL 是否可执行 |
| Execution Match Rate | 生成 SQL 与 gold SQL 执行结果是否一致 |
| SQL+ Valid Rate | SQL+ 是否能被 parser 接受 |
| Conversion Success Rate | SQL+ 是否能成功转换成 SQL |
| Error Type Distribution | 字段、表、JOIN、聚合、语法等错误类型分布 |
| Repair Success Rate | 错误修正后是否可执行或结果一致 |

## 后续实验步骤

1. 固定 30 条 SQL+ 样例作为小规模评估集。
2. 对每条自然语言问题分别运行 Direct NL2SQL 和 NL2SQL+。
3. 保存模型输出，不覆盖原始 gold 数据。
4. 执行生成 SQL，记录错误和执行结果。
5. 输出 baseline 报告。

## 当前实现状态

已完成 baseline 评估框架：

- `scripts/baseline/prepare_baseline_inputs.py`：生成 30 条样例对应的 direct SQL prompt 和 SQL+ prompt。
- `scripts/baseline/create_oracle_baseline_outputs.py`：生成 gold SQL / gold SQL+ 的 oracle 输出，用于验证评估链路。
- `scripts/baseline/run_baseline_eval.py`：评估 direct SQL 输出和 SQL+ 输出，生成 `docs/baseline/baseline_report.md`。
- `scripts/baseline/run_openai_baseline.py`：调用 OpenAI Responses API 生成 Direct NL2SQL 与 NL2SQL+ 的真实模型输出。
- `docs/baseline/openai_baseline_runbook.md`：记录 `gpt-5-mini` baseline 运行步骤。

当前 `docs/baseline/baseline_report.md` 是 oracle sanity check，只说明评估脚本能够正常工作，不代表真实 LLM 能力。

当前机器尚未设置 `OPENAI_API_KEY`，因此真实模型 baseline 尚未运行。

## GPT-5 mini 初轮结果

已完成 30 条样例的 `gpt-5-mini` 初轮 baseline：

| 方法 | 样例数 | SQL+有效 | SQL可执行 | 执行结果一致 |
| --- | --- | --- | --- | --- |
| Direct NL2SQL | 30 | - | 30/30 | 16/30 |
| NL2SQL+ | 30 | 30/30 | 24/30 | 10/30 |

失败分析：

| 方法 | 错误类型 | 数量 |
| --- | --- | --- |
| Direct NL2SQL | semantic_mismatch | 14 |
| NL2SQL+ | semantic_mismatch | 14 |
| NL2SQL+ | schema_column_or_alias_error | 6 |

初步判断：

- Direct NL2SQL 的问题主要是 SQL 可执行但语义结果不一致。
- NL2SQL+ 的 SQL+ 语法有效率达到 30/30，说明模型基本能遵守 SQL+ 线性表达格式。
- NL2SQL+ 的 6 个执行错误主要是字段/别名错误，说明 SQL+ 转换器和 prompt 仍需优化，尤其是聚合别名、`AGG` 与 `ORDER`/`HAVING` 的关系。
- 当前初轮结果不能直接证明 SQL+ 优于 Direct NL2SQL，但能暴露“SQL+ 层可定位错误”的研究价值。

## SQL+ 转换器优化后复评估

针对初轮 NL2SQL+ 中的聚合别名问题，已优化 SQL+ 转换器：

- 支持 `AGG` 后出现 `SELECT` 时生成聚合子查询，再在外层投影。
- 支持 `HAVING` 中引用 `AGG` 别名时替换为完整聚合表达式。
- 支持聚合子查询外层 `SELECT` / `ORDER` 自动去除表别名前缀。

使用同一批 `gpt-5-mini` SQL+ 输出复评估后：

| 方法 | 样例数 | SQL+有效 | SQL可执行 | 执行结果一致 |
| --- | --- | --- | --- | --- |
| NL2SQL+ 优化前 | 30 | 30/30 | 24/30 | 10/30 |
| NL2SQL+ 优化后 | 30 | 30/30 | 30/30 | 13/30 |

结论：

- 转换器优化消除了 6 条 schema_column_or_alias_error。
- SQL+ 可执行率从 24/30 提升到 30/30。
- 执行结果一致率从 10/30 提升到 13/30。
- 剩余问题主要是 semantic_mismatch，应在下一阶段通过 prompt 约束、schema linking 和反馈修正继续处理。

## SQL+ Prompt v2 第二轮结果

使用优化后的 SQL+ prompt 重新调用 `gpt-5-mini` 生成 SQL+，并与同一批 Direct NL2SQL 输出对比：

| 方法 | 样例数 | SQL+有效 | SQL可执行 | 执行结果一致 |
| --- | --- | --- | --- | --- |
| Direct NL2SQL | 30 | - | 30/30 | 16/30 |
| NL2SQL+ prompt v1 | 30 | 30/30 | 30/30 | 13/30 |
| NL2SQL+ prompt v2 | 30 | 30/30 | 30/30 | 17/30 |

按难度观察：

| 方法 | simple | medium | hard |
| --- | --- | --- | --- |
| Direct NL2SQL | 2/6 | 10/18 | 4/6 |
| NL2SQL+ prompt v2 | 1/6 | 11/18 | 5/6 |

结论：

- SQL+ prompt v2 在整体执行一致率上超过 Direct NL2SQL：17/30 对 16/30。
- SQL+ prompt v2 在 medium 和 hard 查询上表现更好，说明线性中间表示对复杂查询有潜在优势。
- SQL+ prompt v2 在 simple 查询上低于 Direct，后续需要优化简单查询是否使用 `SELECT` 而不是不必要的 `GROUP/AGG`。
- 失败类型仍然主要是 semantic_mismatch，下一阶段应进入 schema linking、问题理解和反馈修正。

## SQL+ Mismatch 诊断与 Oracle Refiner

已对 SQL+ prompt v2 的 13 条失败样例进行结构化诊断：

| 诊断类型 | 数量 |
| --- | --- |
| filter_or_value_linking | 5 |
| order_or_limit_mismatch | 3 |
| aggregation_planning | 2 |
| schema_or_join_planning | 2 |
| projection_mismatch | 1 |

已生成：

- `data/sqlplus_mismatch_diagnostics.jsonl`
- `docs/agents/sqlplus_mismatch_diagnostics.md`
- `docs/agents/minimal_agent_design.md`
- `outputs/refiner/sqlplus_refiner_oracle.jsonl`
- `docs/agents/refiner_oracle_report.md`

Oracle Refiner 结果：

| 修正对象 | 样例数 | SQL+有效 | SQL可执行 | 执行结果一致 |
| --- | --- | --- | --- | --- |
| SQL+ v2 失败样例 | 13 | 13/13 | 13/13 | 13/13 |

该结果不代表真实 Refiner Agent 能力，只说明“诊断 -> 修正 SQL+ -> 转换 SQL -> 执行验证”的反馈修正管线已经打通。

真实模型实验时，需要将模型输出保存为：

```json
{"id":"q001","prediction":"..."}
```

然后运行：

```powershell
python scripts/baseline/run_baseline_eval.py --direct-output outputs/baseline/direct_model.jsonl --sqlplus-output outputs/baseline/sqlplus_model.jsonl --label "model name"
```


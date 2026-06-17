# 实验记录

本文件只记录实验相关内容，包括实验目的、配置、命令、指标、失败记录、结果分析，以及由实验结果引发的方向调整。

非实验类事项，例如目录整理、GitHub 同步、开题文档排版、飞书文档写入、项目规则调整等，记录到 `docs/project/project_log.md`。

## 2026-06-15 SQL+ 与中间表示表达复杂度对比实验

实验目的：

回应开题反馈中“为什么使用 SQL+、SQL+ 与 SemQL/NatSQL/Pipe Syntax 有何区别”的问题，比较同一批查询在 Standard SQL、SQL+、SemQL-style proxy、NatSQL-style proxy 和 Pipe-style proxy 下的表达复杂度、结构特征和转换开销。

涉及文件：

- `scripts/sqlplus/run_ir_complexity_eval.py`
- `data/sqlplus_cases.jsonl`
- `data/ir_complexity_detail.csv`
- `data/ir_complexity_summary.csv`
- `docs/sqlplus/intermediate_representation_complexity_report.md`
- `docs/sqlplus/intermediate_representation_comparison_plan.md`
- `docs/project/opening_preliminary_results.md`
- `docs/project/experiment_outline.md`

实验命令：

```powershell
python scripts/sqlplus/run_ir_complexity_eval.py
```

实验配置：

- 数据集：自建订单分析数据集 30 条查询。
- 输入：自然语言问题、gold SQL、gold SQL+。
- 对比表示：standard_sql、sqlplus、semql_style_proxy、natsql_style_proxy、pipe_style_proxy。
- 指标：token_count、line_count、step_or_clause_count、nesting_depth、join_path_length、schema_item_count、alias_dependency_count、cross_clause_reference_count、parse_time_ms、conversion_time_ms。
- 说明：SemQL-style、NatSQL-style、Pipe-style 均为开题阶段的 controlled proxy，不代表完整复现 IRNet/SemQL、NatSQL 或 GoogleSQL Pipe Syntax。

实验结果：

- Standard SQL 平均 token 数：31.5333；SQL+ 平均 token 数：35.0333。
- SQL+ 平均行数/步骤数：6.1333/6.1333；Standard SQL 为 5.9/5.9。
- SemQL-style proxy 平均嵌套深度：3.6667；SQL+ 为 0.6667。
- SQL+ 平均 alias dependency count：0.7；Standard SQL 为 2.0333。
- SQL+ 平均 cross-clause reference count：1.0；Standard SQL 为 2.3333。
- SQL+ 到 SQL 平均转换时间约 0.007 ms；转换成功：30/30。
- proxy 表示未实现完整转换器，因此 conversion success 记为 N/A，不记为失败。

问题与观察：

- SQL+ 当前并不比 Standard SQL 或 NatSQL-style proxy 更短，不能把 SQL+ 优势表述为“压缩查询长度”。
- SQL+ 的优势更适合表述为：显式步骤边界、较低嵌套程度、较少跨子句/别名依赖，以及可确定转换为 SQL。
- SemQL-style proxy 在本实验中的嵌套深度更高，适合作为语义结构化表示对照，但不天然对应步骤级局部修复。
- NatSQL-style proxy token 数较低，可作为后续生成成本对照，但本阶段不声称覆盖完整 NatSQL 规则。

方向调整：

- 开题报告中“为什么 SQL+”应从“更短、更简单”调整为“面向生成、转换、诊断、局部修复统一闭环的步骤化中间表示”。
- 后续必须继续做 repairability 指标实验，包括 error localization accuracy、router accuracy、patch minimality、average repair rounds、token cost 和 latency。

下一步：

- 设计生成成本实验：在同一模型、同一批样例下比较 Direct SQL、SQL+、NatSQL-style proxy、SemQL-style proxy 的 prompt/completion tokens、valid rate、execution accuracy 和 latency。
- 设计局部修复对比实验：比较 SQL 层整体修复、SQL+ 层局部修复、SemQL-style/NatSQL-style proxy 层修复的错误定位和 patch 范围。

## 2026-06-15 IR 生成成本与执行效果对比实验

实验目的：

比较同一批自然语言问题在 Direct SQL、SQL+、NatSQL-style proxy 和 SemQL-style proxy 四种生成目标下的 token 成本、生成延迟、表示有效率、SQL 可执行率和执行结果一致率，进一步回答“SQL+ 与其他中间表示相比有什么代价和收益”。

涉及文件：

- `scripts/sqlplus/run_ir_generation_cost_eval.py`
- `outputs/ir_generation/ir_generation_outputs.jsonl`
- `data/ir_generation_cost_detail.csv`
- `data/ir_generation_cost_summary.csv`
- `docs/sqlplus/ir_generation_cost_report.md`
- `docs/project/experiment_log.md`
- `docs/project/experiment_outline.md`
- `docs/project/opening_preliminary_results.md`
- `README.md`

实验命令：

```powershell
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User')
python scripts/sqlplus/run_ir_generation_cost_eval.py --run-api --resume --limit 1
python scripts/sqlplus/run_ir_generation_cost_eval.py --run-api --resume
python scripts/sqlplus/run_ir_generation_cost_eval.py
```

实验配置：

- 模型：`gpt-5-mini`。
- 样例数：30 条。
- API 调用：30 条样例 × 4 种生成目标，共 120 次调用；`--resume` 跳过已完成输出。
- 对比方法：Direct SQL、SQL+、NatSQL-style proxy、SemQL-style proxy。
- 评估方式：将模型输出转换为 SQL，在同一 SQLite 数据库上与 gold SQL 执行结果比较。
- 说明：NatSQL-style 和 SemQL-style 是受控 proxy，不代表完整复现 NatSQL 或 SemQL/IRNet。

实验结果：

| 方法 | 表示有效 | SQL 可执行 | 执行一致 | 平均输入 token | 平均输出 token | 平均总 token | 平均延迟 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct SQL | 30/30 | 30/30 | 12/30 | 287.6 | 311.5667 | 599.1667 | 6.5851s |
| SQL+ | 28/30 | 28/30 | 14/30 | 319.1333 | 493.9 | 813.0333 | 9.2197s |
| NatSQL-style proxy | 30/30 | 30/30 | 13/30 | 319.1333 | 421.6333 | 740.7667 | 6.2802s |
| SemQL-style proxy | 30/30 | 25/30 | 12/30 | 343.1333 | 685.8333 | 1028.9667 | 9.9684s |

问题与观察：

- SQL+ 的执行一致率为 14/30，略高于 NatSQL-style proxy 的 13/30 和 Direct SQL/SemQL-style proxy 的 12/30，但差距很小，不能表述为显著优势。
- SQL+ 的平均总 token 为 813.0333，高于 Direct SQL 的 599.1667 和 NatSQL-style proxy 的 740.7667，说明 SQL+ 生成存在额外成本。
- SQL+ 平均延迟为 9.2197s，高于 Direct SQL 的 6.5851s 和 NatSQL-style proxy 的 6.2802s。
- SQL+ 有 2 条样例生成了当前 parser 不支持的 `LEFT` step，导致表示有效率和 SQL 可执行率为 28/30。
- SemQL-style proxy 初次评估时因 converter 误匹配 `(orders ...)` 为 `(order ...)`，SQL 可执行率被低估为 10/30；修正 converter 后离线复评估为 25/30。
- SemQL-style proxy 平均总 token 最高，为 1028.9667，说明树状 S-expression 表达对当前模型和 prompt 来说成本较高。

方向调整：

- SQL+ 的开题论证不能只写“生成准确率更高”，因为当前小规模结果只是略高。
- 更合理的论证是：SQL+ 在生成成本上有代价，但提供步骤边界、低跨子句依赖和可局部修复空间；因此后续必须用 error localization、patch minimality、repair rounds 和 repair token/latency 来证明收益是否抵消成本。
- 下一步应围绕失败样例做修复成本对比：Direct SQL 整体重写 vs SQL+ 局部 repair skill vs NatSQL/SemQL-style proxy 层修复。

下一步：

- 统计四种方法失败样例的错误类型分布。
- 在同一失败集合上比较 SQL 层整体修复和 SQL+ 层局部修复的 token、latency、修复轮数和 patch 范围。

## 记录模板

```text
日期：
实验名称：
实验目的：
涉及文件：
实验命令：
实验配置：
实验结果：
问题与观察：
方向调整：
下一步：
```

## 2026-06-03 SQL+ 转 SQL 最小闭环实验

实验目的：

验证“自然语言问题 -> SQL+ 中间表示 -> 标准 SQL -> SQLite 执行”的最小闭环是否可行。

涉及文件：

- `data/schema.sql`
- `data/sqlplus_cases.jsonl`
- `src/sqlplus.py`
- `scripts/sqlplus/run_experiment.py`
- `docs/sqlplus/pre_experiment_report.md`

实验命令：

```powershell
python scripts/sqlplus/run_experiment.py
```

实验配置：

- 数据库：SQLite 内存数据库。
- 数据场景：企业订单分析。
- 数据表：customers、orders、order_items、products。
- 查询样例：6 条自然语言、标准 SQL、SQL+ 三元组。
- 查询类型：多表 JOIN、过滤、分组聚合、HAVING、排序、LIMIT。

实验结果：

- SQL+ 语法通过率：6/6。
- 转换 SQL 可执行率：6/6。
- 与标准 SQL 执行结果一致率：6/6。

问题与观察：

- 当前 SQL+ parser 是轻量规则解析，足够支撑开题前期实验，但还不是完整语法解析器。
- 当前样例数量较少，适合展示原型可行性，不适合支撑大规模结论。
- 当前 SQL+ 子集暂未覆盖窗口函数、嵌套查询、CTE、集合操作。

方向调整：

- 下一阶段优先扩充样例数量和查询复杂度。
- SQL+ 语法应保持小而清晰，避免开题阶段引入过多语法特性导致实验不可控。

下一步：

- 将 SQL+ 样例扩充到 30 条以上。
- 为每条样例增加复杂度标签和涉及操作标签。
- 编写 `docs/sqlplus/dataset_summary.md`，总结样例覆盖范围。

## 2026-06-03 SQL+ 层反馈修正实验

实验目的：

构造字段名错误类 SQL+ 查询，验证执行错误可以映射回 SQL+ 局部步骤，并通过局部修正恢复为可执行查询。

涉及文件：

- `data/repair_cases.jsonl`
- `scripts/sqlplus/run_repair_experiment.py`
- `docs/sqlplus/repair_experiment_report.md`

实验命令：

```powershell
python scripts/sqlplus/run_repair_experiment.py
```

实验配置：

- 数据库：SQLite 内存数据库。
- 错误类型：schema_column。
- 错误形式：字段名不存在，例如 `c.area`、`o.state`、`p.cat`。
- 修正方式：规则映射，将错误字段替换为正确字段。

实验结果：

- 初始失败样例：3/3。
- 修正后可执行样例：3/3。
- 修正成功率：3/3。

问题与观察：

- 当前修正实验只覆盖字段名错误，错误类型还不够丰富。
- 当前修正规则是人工映射，后续应替换或扩展为 Schema Agent + Refiner Agent 的协作修正。
- 该实验能够证明 SQL+ 的线性步骤适合进行局部错误定位和局部修正。

方向调整：

- 保留规则修正作为前期 baseline。
- 后续加入更多错误类型：表名错误、JOIN 条件错误、聚合字段错误、类型错误、函数不兼容。
- 后续比较 SQL+ 层局部修正与 SQL 层整体重生成。

下一步：

- 将错误修正样例扩充到 15 条以上。
- 在报告中增加错误类型分布。
- 增加修正前 SQL、修正后 SQL、错误 SQL+ 步骤定位信息。

## 2026-06-03 SQL+ 样例扩充与复杂度分层实验

实验目的：

将前期 SQL+ 查询样例从 6 条扩充到 30 条，覆盖更多查询复杂度和 SQL+ 操作类型，提升开题前期实验的覆盖面。

涉及文件：

- `data/sqlplus_cases.jsonl`
- `scripts/sqlplus/run_experiment.py`
- `docs/sqlplus/pre_experiment_report.md`
- `docs/sqlplus/dataset_summary.md`
- `README.md`

实验命令：

```powershell
python scripts/sqlplus/run_experiment.py
```

实验配置：

- 数据库：SQLite 内存数据库。
- 数据场景：企业订单分析。
- 查询样例：30 条自然语言、标准 SQL、SQL+ 三元组。
- 难度分布：simple 6 条，medium 18 条，hard 6 条。
- 操作覆盖：where、join、group、agg、having、order、limit、select。

实验结果：

- SQL+ 语法通过率：30/30。
- 转换 SQL 可执行率：30/30。
- 与标准 SQL 执行结果一致率：30/30。

问题与观察：

- 当前 SQL+ 子集已经覆盖开题阶段常见分析查询。
- `limit` 类样例数量较少，后续若做 Top-K 专门实验可以继续补充。
- 当前仍未覆盖窗口函数、CTE 和嵌套查询，这些可作为后续扩展点。

方向调整：

- 阶段三“样例扩充与复杂度分层”完成初版。
- 下一阶段应优先固化 SQL+ 语法说明，并准备单 Agent baseline。

下一步：

- 编写 SQL+ 语法说明文档。
- 设计 direct SQL 和 SQL+ generation 两类 baseline prompt。

## 2026-06-03 SQL+ 反馈修正样例扩充实验

实验目的：

将反馈修正样例从 3 条扩充到 15 条，覆盖字段名、表名和 JOIN 键错误，验证 SQL+ 层局部修正机制的可扩展性。

涉及文件：

- `data/repair_cases.jsonl`
- `scripts/sqlplus/run_repair_experiment.py`
- `docs/sqlplus/repair_experiment_report.md`
- `docs/sqlplus/dataset_summary.md`
- `README.md`

实验命令：

```powershell
python scripts/sqlplus/run_repair_experiment.py
```

实验配置：

- 数据库：SQLite 内存数据库。
- 错误样例：15 条。
- 错误类型分布：schema_column 10 条，join_key 3 条，table_name 2 条。
- 修正方式：规则映射修正，作为后续 Refiner Agent 的 baseline。

实验结果：

- 初始失败样例：15/15。
- 修正后可执行样例：15/15。
- 修正成功率：15/15。

问题与观察：

- 初次运行时 `r014` 失败，原因是修正规则 `oi.product -> oi.product_id` 与表名 `product p` 存在字符串匹配冲突。
- 修正方式是将表名规则收窄为 `FROM product p -> FROM products p` 并前置，复跑后全部通过。
- 该问题说明后续若使用规则或 Agent 修正，都需要明确错误定位粒度，避免过宽替换造成二次错误。

方向调整：

- 保留规则修正作为可解释 baseline。
- 后续引入 Schema Agent 时，应输出结构化修正动作，而不是仅输出自由文本替换。

下一步：

- 增加错误定位字段，例如错误发生在 `FROM`、`JOIN`、`WHERE`、`SELECT`、`AGG` 哪一步。
- 对比 SQL+ 层局部修正与 SQL 层整体重生成。

## 2026-06-03 Baseline 评估框架与 oracle sanity check

实验目的：

实现 Direct NL2SQL 与 NL2SQL+ 的统一评估框架，先用 gold SQL / gold SQL+ 作为 oracle 输出验证评估链路，再为后续真实模型输出评估做准备。

涉及文件：

- `scripts/baseline/prepare_baseline_inputs.py`
- `scripts/baseline/create_oracle_baseline_outputs.py`
- `scripts/baseline/run_baseline_eval.py`
- `data/baseline_prompts.jsonl`
- `outputs/baseline/direct_oracle.jsonl`
- `outputs/baseline/sqlplus_oracle.jsonl`
- `docs/baseline/baseline_report.md`
- `docs/baseline/baseline_design.md`
- `docs/project/experiment_outline.md`
- `README.md`

实验命令：

```powershell
python scripts/baseline/prepare_baseline_inputs.py
python scripts/baseline/create_oracle_baseline_outputs.py
python scripts/baseline/run_baseline_eval.py
```

实验配置：

- 样例数量：30 条。
- Direct NL2SQL oracle 输出：使用 `gold_sql`。
- NL2SQL+ oracle 输出：使用 `sqlplus`。
- 评估数据库：SQLite 内存数据库。
- 指标：SQL+ 有效率、SQL 可执行率、执行结果一致率、按难度分布统计。

实验结果：

- Direct NL2SQL oracle：SQL 可执行率 30/30，执行结果一致率 30/30。
- NL2SQL+ oracle：SQL+ 有效率 30/30，SQL 可执行率 30/30，执行结果一致率 30/30。

问题与观察：

- 当前结果是 oracle sanity check，只验证评估框架，不代表真实 LLM 生成能力。
- 评估脚本已经支持读取真实模型输出 JSONL，后续只需替换 `--direct-output` 和 `--sqlplus-output`。
- 输出格式固定为每行包含 `id` 和 `prediction`，便于接入不同模型。

方向调整：

- 阶段四从“prompt 设计完成”推进到“评估框架完成，待真实模型输出”。
- 下一步需要确认可用模型接口，或先手动采样少量模型输出进行试跑。

下一步：

- 接入模型生成 `outputs/baseline/direct_model.jsonl` 和 `outputs/baseline/sqlplus_model.jsonl`。
- 运行 `run_baseline_eval.py` 得到真实 Direct NL2SQL vs NL2SQL+ 对比结果。

## 2026-06-03 OpenAI GPT-5 mini smoke test 失败记录

实验目的：

验证当前环境是否可以调用 OpenAI Responses API，并尝试运行 1 条 Direct NL2SQL 与 NL2SQL+ smoke test。

涉及文件：

- `scripts/baseline/run_openai_baseline.py`
- `docs/project/experiment_log.md`

实验命令：

```powershell
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User')
python scripts/baseline/run_openai_baseline.py --model gpt-5-mini --limit 1 --method both --resume
```

实验配置：

- 模型：`gpt-5-mini`。
- 样例数：1 条。
- 方法：Direct NL2SQL 与 NL2SQL+。
- API key 来源：Windows 用户级环境变量。

实验结果：

- 沙箱内首次请求出现连接拒绝。
- 使用非沙箱网络重试后成功连接 OpenAI API。
- API 返回 `401 Unauthorized`，错误类型为 `invalid_api_key`。
- 未生成真实模型输出。

问题与观察：

- 网络访问本身已经打通。
- 当前环境变量中的 API key 无效，可能是已作废、复制不完整或不是 API 平台有效 key。
- 日志未记录任何 API key 内容。

方向调整：

- 暂停真实模型 baseline 运行。
- 先重新生成有效 API key 并更新用户级环境变量。

下一步：

- 删除当前无效 key。
- 在 OpenAI API Keys 页面重新生成 key。
- 更新用户级环境变量后重新运行 1 条 smoke test。

## 2026-06-03 OpenAI GPT-5 mini smoke test 成功记录

实验目的：

验证 `gpt-5-mini` 能否在当前环境中完成 Direct NL2SQL 与 NL2SQL+ 的真实模型输出，并通过 baseline 评估脚本检查执行结果。

涉及文件：

- `scripts/baseline/run_openai_baseline.py`
- `scripts/baseline/run_baseline_eval.py`
- `outputs/baseline/direct_model.jsonl`
- `outputs/baseline/sqlplus_model.jsonl`
- `docs/baseline/baseline_report.md`
- `docs/project/experiment_log.md`

实验命令：

```powershell
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User')
python scripts/baseline/run_openai_baseline.py --model gpt-5-mini --limit 1 --method both --resume
python scripts/baseline/run_baseline_eval.py --direct-output outputs/baseline/direct_model.jsonl --sqlplus-output outputs/baseline/sqlplus_model.jsonl --label "gpt-5-mini smoke test"
```

实验配置：

- 模型：`gpt-5-mini`。
- 样例数：1 条，`q001`。
- 方法：Direct NL2SQL 与 NL2SQL+。
- 评估模式：仅评估已有预测。

实验结果：

- Direct NL2SQL：已评估 1 条，SQL 可执行率 1/1，执行结果一致率 1/1。
- NL2SQL+：已评估 1 条，SQL+ 有效率 1/1，SQL 可执行率 1/1，执行结果一致率 1/1。
- `q001` 的真实模型输出已保存到 `outputs/baseline/`。

问题与观察：

- 初次评估时，脚本把未生成的 29 条样例也纳入统计，导致 smoke test 报告显示为 1/30。
- 已修正 `scripts/baseline/run_baseline_eval.py`，默认只评估已有预测；需要把缺失预测计入失败时再显式使用 `--include-missing`。
- Direct 输出包含 Markdown code fence，评估脚本可以正常清洗。
- SQL+ 输出符合当前 SQL+ parser 约束。

方向调整：

- 单条真实模型 smoke test 已通过，可以进入 30 条完整 baseline。
- 后续完整实验应使用 `--resume`，避免重复生成已完成样例。

下一步：

- 运行完整 30 条 `gpt-5-mini` baseline。
- 生成完整 `docs/baseline/baseline_report.md`，并分析 Direct NL2SQL 与 NL2SQL+ 的错误差异。

## 2026-06-03 GPT-5 mini 30 条完整 baseline

实验目的：

使用 `gpt-5-mini` 对 30 条样例分别运行 Direct NL2SQL 与 NL2SQL+，评估两条路线的 SQL 可执行率、执行结果一致率和失败类型。

涉及文件：

- `scripts/baseline/run_openai_baseline.py`
- `scripts/baseline/run_baseline_eval.py`
- `scripts/baseline/analyze_baseline_failures.py`
- `outputs/baseline/direct_model.jsonl`
- `outputs/baseline/sqlplus_model.jsonl`
- `docs/baseline/baseline_report.md`
- `docs/baseline/baseline_failure_analysis.md`
- `docs/baseline/baseline_design.md`
- `docs/project/experiment_outline.md`

实验命令：

```powershell
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User')
python scripts/baseline/run_openai_baseline.py --model gpt-5-mini --method both --resume
python scripts/baseline/run_openai_baseline.py --model gpt-5-mini --method sqlplus --resume
python scripts/baseline/run_baseline_eval.py --direct-output outputs/baseline/direct_model.jsonl --sqlplus-output outputs/baseline/sqlplus_model.jsonl --label "gpt-5-mini"
python scripts/baseline/analyze_baseline_failures.py
```

实验配置：

- 模型：`gpt-5-mini`。
- 样例数量：30 条。
- 方法：Direct NL2SQL 与 NL2SQL+。
- 评估模式：仅评估已有预测。
- 执行数据库：SQLite 内存数据库。

实验结果：

- Direct NL2SQL：SQL 可执行率 30/30，执行结果一致率 16/30。
- NL2SQL+：SQL+ 有效率 30/30，SQL 可执行率 24/30，执行结果一致率 10/30。
- Direct NL2SQL 失败类型：semantic_mismatch 14 条。
- NL2SQL+ 失败类型：semantic_mismatch 14 条，schema_column_or_alias_error 6 条。

问题与观察：

- 完整运行过程中，API 在 SQL+ q026 前出现一次远端连接断开；使用 `--resume` 续跑后补齐 q026-q030。
- Direct NL2SQL 全部 SQL 可执行，但有 14 条执行结果与 gold SQL 不一致。
- NL2SQL+ 全部 SQL+ 能被 parser 接受，说明模型基本能遵守 SQL+ 格式。
- NL2SQL+ 有 6 条转换后 SQL 执行失败，主要是聚合别名或字段引用错误，例如 `total_sales`、`order_amount`、`total_qty`。
- 初轮结果中 Direct NL2SQL 的执行一致率高于 NL2SQL+，说明当前 SQL+ prompt 和转换器还需要优化。

方向调整：

- 不把初轮结果包装成 SQL+ 已经优于 Direct NL2SQL。
- 将研究重点进一步落到“SQL+ 层错误可定位、可修复”，并把聚合别名错误作为后续反馈修正实验的重点。
- 下一轮先优化 SQL+ prompt 和转换器，再比较 NL2SQL+ 优化前后效果。

下一步：

- 检查 SQL+ 失败样例的模型输出。
- 优化 SQL+ prompt，要求 `AGG` 中的别名在 `ORDER`/`HAVING` 中使用一致。
- 改进 SQL+ 转换器对聚合查询的处理，并加入 SQL+ 层错误定位字段。

## 2026-06-03 SQL+ 聚合别名与 ORDER/HAVING 优化实验

实验目的：

针对 `gpt-5-mini` 初轮 NL2SQL+ 中暴露的 `AGG` 别名、`ORDER`/`HAVING` 引用和聚合后 `SELECT` 问题，优化 SQL+ 转换器和 SQL+ 生成 prompt，并使用已有模型输出离线复评估。

涉及文件：

- `src/sqlplus.py`
- `prompts/baseline/sqlplus_generation.md`
- `scripts/sqlplus/run_experiment.py`
- `scripts/baseline/run_baseline_eval.py`
- `scripts/baseline/analyze_baseline_failures.py`
- `docs/baseline/baseline_report.md`
- `docs/baseline/baseline_failure_analysis.md`
- `docs/baseline/baseline_design.md`
- `docs/project/experiment_log.md`

实验命令：

```powershell
python scripts/sqlplus/run_experiment.py
python scripts/sqlplus/run_repair_experiment.py
python scripts/baseline/run_baseline_eval.py --direct-output outputs/baseline/direct_model.jsonl --sqlplus-output outputs/baseline/sqlplus_model.jsonl --label "gpt-5-mini after converter optimization"
python scripts/baseline/analyze_baseline_failures.py
```

实验配置：

- 使用已有 `gpt-5-mini` SQL+ 模型输出，不重新调用 API。
- 优化点一：`AGG` 后出现 `SELECT` 时生成聚合子查询。
- 优化点二：`HAVING` 引用聚合别名时替换为完整聚合表达式。
- 优化点三：聚合子查询外层 `SELECT` / `ORDER` 自动去除表别名前缀。
- Prompt 优化：要求聚合查询优先把最终输出放在 `AGG`，避免不必要的 `SELECT after AGG`，并约束 `ORDER`/`HAVING` 的别名使用。

实验结果：

- Gold SQL+ 转换实验保持 30/30 语法通过、30/30 SQL 可执行、30/30 结果一致。
- 反馈修正实验保持 15/15 修正成功。
- NL2SQL+ 真实模型输出复评估：SQL+ 有效率 30/30，SQL 可执行率从 24/30 提升到 30/30，执行结果一致率从 10/30 提升到 13/30。
- SQL+ 的 schema_column_or_alias_error 从 6 条降为 0 条。

问题与观察：

- 转换器优化能显著提升 SQL+ 可执行率，说明初轮部分失败来自中间表示转换能力不足，而不是模型完全生成失败。
- 剩余 SQL+ 失败全部是 semantic_mismatch，说明下一阶段重点应转向语义约束、schema linking 和反馈修正。
- Prompt 已优化，但还未重新调用模型验证第二轮生成效果。

方向调整：

- SQL+ baseline 的下一步不再优先处理语法/执行错误，而是处理语义偏差。
- 后续可设计 Refiner Agent 针对 semantic_mismatch 进行结果级反馈修正。

下一步：

- 用优化后的 prompt 重新跑第二轮 NL2SQL+ baseline。
- 对比第一轮 SQL+ 输出与第二轮 SQL+ 输出，观察 prompt 是否减少语义偏差。

## 2026-06-03 SQL+ prompt v2 baseline 启动失败记录

实验目的：

使用优化后的 SQL+ prompt 重新运行 `gpt-5-mini` SQL+ baseline，输出到 `outputs/baseline/sqlplus_model_v2.jsonl`，并与第一轮 SQL+ baseline 对比。

涉及文件：

- `scripts/baseline/prepare_baseline_inputs.py`
- `scripts/baseline/run_openai_baseline.py`
- `data/baseline_prompts.jsonl`
- `docs/project/experiment_log.md`

实验命令：

```powershell
python scripts/baseline/prepare_baseline_inputs.py
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User')
python scripts/baseline/run_openai_baseline.py --model gpt-5-mini --method sqlplus --resume --sqlplus-output outputs/baseline/sqlplus_model_v2.jsonl
```

实验配置：

- 模型：`gpt-5-mini`。
- 方法：仅运行 NL2SQL+。
- 输出目标：`outputs/baseline/sqlplus_model_v2.jsonl`。
- Prompt：已优化 AGG 别名、ORDER/HAVING 引用和字面值保持约束。

实验结果：

- `prepare_baseline_inputs.py` 成功刷新 30 条 prompt 输入。
- OpenAI API 调用失败，返回 `401 Unauthorized`，错误类型为 `invalid_api_key`。
- 未生成第二轮 SQL+ 模型输出。

问题与观察：

- 失败发生在 API 鉴权阶段，与 SQL+ prompt、转换器和评估脚本无关。
- 当前用户级环境变量中的 API key 无效或已过期/被撤销。
- 日志未记录任何 API key 内容。

方向调整：

- 暂停 SQL+ prompt v2 真实模型实验。
- 待 API key 恢复后，继续运行同一条命令即可。

下一步：

- 重新确认 OpenAI API key 是否有效。
- 更新用户级环境变量后，继续运行 SQL+ prompt v2 baseline。

## 2026-06-03 SQL+ prompt v2 第二轮 baseline

实验目的：

使用优化后的 SQL+ prompt 重新运行 `gpt-5-mini` SQL+ baseline，验证 prompt 约束是否能减少语义偏差，并与 Direct NL2SQL 和第一轮 SQL+ 结果对比。

涉及文件：

- `prompts/baseline/sqlplus_generation.md`
- `scripts/baseline/prepare_baseline_inputs.py`
- `scripts/baseline/run_openai_baseline.py`
- `scripts/baseline/run_baseline_eval.py`
- `scripts/baseline/analyze_baseline_failures.py`
- `outputs/baseline/sqlplus_model_v2.jsonl`
- `docs/baseline/baseline_report.md`
- `docs/baseline/baseline_failure_analysis_v2.md`
- `docs/baseline/baseline_design.md`
- `docs/project/experiment_outline.md`
- `docs/project/experiment_log.md`

实验命令：

```powershell
python scripts/baseline/prepare_baseline_inputs.py
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User')
python scripts/baseline/run_openai_baseline.py --model gpt-5-mini --method sqlplus --resume --sqlplus-output outputs/baseline/sqlplus_model_v2.jsonl
python scripts/baseline/run_openai_baseline.py --model gpt-5-mini --method sqlplus --resume --sqlplus-output outputs/baseline/sqlplus_model_v2.jsonl --retries 8 --delay-seconds 3
python scripts/baseline/run_baseline_eval.py --direct-output outputs/baseline/direct_model.jsonl --sqlplus-output outputs/baseline/sqlplus_model_v2.jsonl --label "gpt-5-mini sqlplus prompt v2"
python scripts/baseline/analyze_baseline_failures.py --sqlplus-output outputs/baseline/sqlplus_model_v2.jsonl --report docs/baseline/baseline_failure_analysis_v2.md
```

实验配置：

- 模型：`gpt-5-mini`。
- 样例数量：30 条。
- 方法：仅重新运行 NL2SQL+，Direct NL2SQL 复用第一轮输出。
- Prompt：SQL+ prompt v2。
- 评估数据库：SQLite 内存数据库。

实验结果：

- SQL+ prompt v2 输出数量：30 条。
- NL2SQL+ prompt v2：SQL+ 有效率 30/30，SQL 可执行率 30/30，执行结果一致率 17/30。
- Direct NL2SQL：SQL 可执行率 30/30，执行结果一致率 16/30。
- SQL+ prompt v2 失败类型：semantic_mismatch 13 条。

阶段对比：

| 阶段 | SQL+有效 | SQL可执行 | 执行结果一致 |
| --- | --- | --- | --- |
| SQL+ prompt v1 原始评估 | 30/30 | 24/30 | 10/30 |
| 转换器优化后复评估 | 30/30 | 30/30 | 13/30 |
| SQL+ prompt v2 第二轮 | 30/30 | 30/30 | 17/30 |

问题与观察：

- 第二轮运行期间出现多次临时网络中断，包括 SSL EOF、连接重置和不完整读取。
- 已为 `run_openai_baseline.py` 增加重试机制，并通过 `--resume`、`--retries 8`、`--delay-seconds 3` 完成全部输出。
- SQL+ prompt v2 在整体结果上超过 Direct NL2SQL：17/30 对 16/30。
- SQL+ prompt v2 在 medium 和 hard 查询上更好：medium 11/18，hard 5/6；Direct 为 medium 10/18，hard 4/6。
- SQL+ prompt v2 在 simple 查询上较弱：1/6，Direct 为 2/6。

方向调整：

- 当前结果可以作为开题前期实验的重要证据：SQL+ 经过转换器与 prompt 优化后，在复杂查询上表现出优势。
- 后续不应继续单纯调 prompt，应转向多智能体：Schema Agent 负责字段和值链接，Planner Agent 负责步骤规划，Refiner Agent 负责 semantic_mismatch 修正。

下一步：

- 增加 SQL+ 错误定位字段。
- 设计最小 Schema Agent / Planner Agent 输出格式。
- 针对 semantic_mismatch 失败样例做反馈修正实验。

## 2026-06-03 SQL+ semantic mismatch 诊断与 Oracle Refiner 实验

实验目的：

对 SQL+ prompt v2 的 13 条 semantic_mismatch 失败样例进行结构化诊断，形成最小 Refiner Agent 输入，并用 oracle refiner 验证反馈修正评估链路是否可行。

涉及文件：

- `scripts/agents/diagnose_sqlplus_mismatches.py`
- `scripts/agents/create_oracle_refiner_outputs.py`
- `scripts/baseline/run_baseline_eval.py`
- `docs/agents/minimal_agent_design.md`
- `data/sqlplus_mismatch_diagnostics.jsonl`
- `docs/agents/sqlplus_mismatch_diagnostics.md`
- `outputs/refiner/sqlplus_refiner_oracle.jsonl`
- `docs/agents/refiner_oracle_report.md`
- `docs/baseline/baseline_design.md`
- `docs/project/experiment_outline.md`
- `README.md`

实验命令：

```powershell
python scripts/agents/diagnose_sqlplus_mismatches.py
python scripts/agents/create_oracle_refiner_outputs.py
python scripts/baseline/run_baseline_eval.py --direct-output outputs\baseline\direct_model.jsonl --sqlplus-output outputs\refiner\sqlplus_refiner_oracle.jsonl --label "oracle refiner on sqlplus v2 failures" --report docs\agents\refiner_oracle_report.md
```

实验配置：

- 输入：`outputs/baseline/sqlplus_model_v2.jsonl`。
- 诊断对象：SQL+ prompt v2 中执行结果不一致的样例。
- 修正方式：oracle refiner，将失败样例修正为对应 gold SQL+，用于验证评估链路。
- 评估数据库：SQLite 内存数据库。

实验结果：

- SQL+ prompt v2 失败样例：13 条。
- 诊断分类：filter_or_value_linking 5 条，order_or_limit_mismatch 3 条，aggregation_planning 2 条，schema_or_join_planning 2 条，projection_mismatch 1 条。
- Oracle Refiner：SQL+ 有效率 13/13，SQL 可执行率 13/13，执行结果一致率 13/13。

问题与观察：

- 初次诊断时未清理 Markdown code fence，导致 q012/q027 被误判为 execution_error；已修复诊断脚本。
- 失败样例主要集中在值链接、排序遗漏、聚合规划和投影列不一致。
- Oracle Refiner 结果只证明管线可行，不代表真实 Refiner Agent 能力。

方向调整：

- 下一步应调用真实 LLM 作为 Refiner Agent，输入 `data/sqlplus_mismatch_diagnostics.jsonl`，输出修正后的 SQL+。
- Refiner prompt 应重点约束：保留数据库字面值、补齐 ORDER/LIMIT、修正 GROUP/AGG/SELECT 差异。

下一步：

- 设计 `prompts/agents/sqlplus_refiner.md`。
- 实现 `scripts/agents/run_openai_refiner.py`。
- 对 13 条失败样例运行真实 Refiner Agent，并评估修正成功率。

## 2026-06-03 诊断辅助 Refiner Agent 实验

实验目的：

验证真实 LLM Refiner Agent 是否能够根据结构化 mismatch 诊断，对 SQL+ prompt v2 的失败样例进行局部修正，并通过 SQL+ 转 SQL、SQLite 执行和 gold SQL 结果对比完成闭环评估。

涉及文件：

- `prompts/agents/sqlplus_refiner.md`
- `scripts/agents/run_openai_refiner.py`
- `outputs/refiner/sqlplus_refiner_model.jsonl`
- `docs/agents/refiner_model_report.md`
- `docs/agents/refiner_model_diagnostics.md`
- `data/refiner_model_diagnostics.jsonl`
- `docs/agents/minimal_agent_design.md`
- `docs/project/experiment_outline.md`
- `README.md`

实验命令：

```powershell
python scripts/agents/run_openai_refiner.py --dry-run --limit 1
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_refiner.py --model gpt-5-mini --resume --retries 8 --delay-seconds 3
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_refiner_model.jsonl --label "gpt-5-mini diagnosis-assisted refiner" --report docs/agents/refiner_model_report.md
python scripts/agents/diagnose_sqlplus_mismatches.py --predictions outputs/refiner/sqlplus_refiner_model.jsonl --jsonl-output data/refiner_model_diagnostics.jsonl --report docs/agents/refiner_model_diagnostics.md
```

实验配置：

- 模型：`gpt-5-mini`。
- 输入：`data/sqlplus_mismatch_diagnostics.jsonl`。
- 样例数：13 条，来自 SQL+ prompt v2 的执行结果不一致样例。
- 输出格式：严格 JSON，包含 `id`、`prediction`、`repair_actions`。
- 评估数据库：SQLite 内存数据库。

实验结果：

- Refiner 输出：13/13。
- JSON 解析失败：0/13。
- SQL+ 有效率：13/13。
- SQL 可执行率：13/13。
- 执行结果一致率：13/13。
- 剩余 mismatch 诊断：0 条。
- API token 统计：input 11066，output 5250，total 16316。
- 修复来源分类：filter_or_value_linking 5 条，order_or_limit_mismatch 3 条，aggregation_planning 2 条，schema_or_join_planning 2 条，projection_mismatch 1 条。

问题与观察：

- 当前诊断输入包含 gold-derived mismatch differences，因此该实验属于诊断辅助修复，不是完全自主反馈修正。
- 结果说明结构化差异信息足以驱动 LLM 在 SQL+ 层做局部修正，并保持 SQL+ 语法、转换和执行链路稳定。
- Refiner prompt 的 JSON 输出约束有效，本轮没有 Markdown fence 或解析失败。
- `python -m py_compile` 在当前 Windows 环境中尝试写 `__pycache__` 时出现权限拒绝，但脚本 dry-run 和真实运行均正常，不影响实验结果。

方向调整：

- 下一步应构造非 gold 的真实反馈修正输入，只保留问题、schema、原始 SQL+、转换 SQL、执行结果预览、错误类型、行数异常和启发式诊断。
- 需要实现真实反馈 Refiner 数据构造脚本，用来替代当前 gold-derived diagnostics。
- 开题报告中应将本实验描述为“反馈修正链路可行性验证”，不要表述为最终系统真实性能。

下一步：

- 设计 `execution-feedback-only` Refiner 输入格式。
- 实现从 SQL+ v2 失败结果生成真实反馈样例的脚本。
- 在不提供 gold SQL+ / gold differences 的条件下运行 Refiner Agent，并统计修复成功率。

## 2026-06-03 非 gold 执行反馈 Refiner Agent 实验

实验目的：

验证在不提供 gold SQL、gold SQL+、gold result rows、字段级 gold differences 的条件下，Refiner Agent 是否能够仅根据执行反馈、schema、原始 SQL+、结果预览和粗粒度错误类型修复 SQL+。

涉及文件：

- `prompts/agents/sqlplus_feedback_refiner.md`
- `scripts/agents/build_feedback_refiner_inputs.py`
- `scripts/agents/run_openai_feedback_refiner.py`
- `data/feedback_refiner_inputs.jsonl`
- `data/feedback_refiner_inputs_v2.jsonl`
- `outputs/refiner/sqlplus_feedback_refiner_model.jsonl`
- `outputs/refiner/sqlplus_feedback_refiner_model_v2.jsonl`
- `outputs/refiner/sqlplus_feedback_refiner_model_v2_retry.jsonl`
- `outputs/refiner/sqlplus_feedback_refiner_model_v2_merged.jsonl`
- `docs/agents/feedback_refiner_model_report.md`
- `docs/agents/feedback_refiner_model_diagnostics_v2_merged.md`
- `docs/project/experiment_outline.md`
- `README.md`

实验命令：

```powershell
python scripts/agents/build_feedback_refiner_inputs.py
python scripts/agents/run_openai_feedback_refiner.py --dry-run --limit 1
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_feedback_refiner.py --model gpt-5-mini --resume --retries 8 --delay-seconds 3
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_feedback_refiner_model.jsonl --label "gpt-5-mini execution-feedback-only refiner" --report docs/agents/feedback_refiner_model_report_raw.md
python scripts/agents/build_feedback_refiner_inputs.py --output data/feedback_refiner_inputs_v2.jsonl --report docs/agents/feedback_refiner_inputs_v2.md
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_feedback_refiner.py --inputs data/feedback_refiner_inputs_v2.jsonl --output outputs/refiner/sqlplus_feedback_refiner_model_v2.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_feedback_refiner.py --inputs data/feedback_refiner_inputs_v2_retry.jsonl --output outputs/refiner/sqlplus_feedback_refiner_model_v2_retry.jsonl --model gpt-5-mini --max-output-tokens 2500 --resume --retries 8 --delay-seconds 3
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_feedback_refiner_model_v2_merged.jsonl --label "gpt-5-mini execution-feedback-only refiner v2 merged" --report docs/agents/feedback_refiner_model_report_raw_v2_merged.md
python scripts/agents/diagnose_sqlplus_mismatches.py --predictions outputs/refiner/sqlplus_feedback_refiner_model_v2_merged.jsonl --jsonl-output data/feedback_refiner_model_diagnostics_v2_merged.jsonl --report docs/agents/feedback_refiner_model_diagnostics_v2_merged.md
```

实验配置：

- 模型：`gpt-5-mini`。
- 输入来源：SQL+ prompt v2 的 13 条失败样例。
- 输入限制：不包含 gold SQL、gold SQL+、gold result rows、字段级 gold differences。
- 反馈信息：原始 SQL+、转换 SQL、执行状态、结果行数、结果预览、粗粒度错误类别、schema 和已知数据库值。
- 评估方式：修复 SQL+ 转 SQL 后执行，与 gold SQL 执行结果比较。gold 只用于离线评估，不进入模型输入。

实验结果：

- Execution-feedback Refiner v1：SQL+ 有效 10/13，SQL 可执行 9/13，修复成功 3/13，JSON 解析失败 1/13。
- Execution-feedback Refiner v2 merged：SQL+ 有效 13/13，SQL 可执行 12/13，修复成功 4/13，JSON 解析失败 0/13。
- v2 merged token：input 14919，output 11370，total 26289。
- v2 merged 成功样例：q006、q017、q019、q026。
- v2 merged 剩余失败：order_or_limit_mismatch 3 条，filter_or_value_linking 2 条，aggregation_planning 2 条，schema_or_join_planning 1 条，execution_error 1 条。

问题与观察：

- 第一轮 prompt 未显式禁止 `LEFT JOIN`，模型生成了当前 SQL+ 子集不支持的 `LEFT JOIN`。
- 第二轮增加“不允许 LEFT JOIN / subquery / WITH”等约束后，SQL+ 有效率从 10/13 提升到 13/13。
- 第二轮有 q013 空输出、q025 输出截断；提高 `max_output_tokens` 后重跑并合并，解析失败降为 0/13。
- 非 gold 输入下，模型能修复部分数据库值链接问题，例如 `canceled` -> `cancelled`，也能修复部分排序方向问题。
- 隐含排序、聚合口径、投影列和 join 路径错误仍难以仅靠单 Refiner prompt 稳定修复。

方向调整：

- 诊断辅助 Refiner 的 13/13 可以证明 SQL+ 层结构化修正链路可行。
- 非 gold 执行反馈 Refiner 的 4/13 更接近真实系统能力，说明单 Refiner prompt 不足，需要多智能体分工。
- 下一步应实现 Critic Agent 和 Schema Agent，让它们在不使用 gold 的情况下生成更具体的错误定位，再交给 Refiner Agent。

下一步：

- 设计 `Schema Agent` 输出格式：相关表、字段、join 路径、候选数据库值。
- 设计 `Critic Agent` 输出格式：基于执行反馈的错误定位，不包含 gold answer。
- 构建 `Schema/Critic -> Refiner` 的两阶段反馈修正实验。

## 2026-06-03 Direct SQL 非 gold 执行反馈 Refiner 对照实验

实验目的：

补齐 Direct NL2SQL 的非 gold 执行反馈修正对照组，用于比较“直接修标准 SQL”和“修 SQL+ 中间表示”的效果差异。

涉及文件：

- `prompts/agents/direct_sql_feedback_refiner.md`
- `scripts/agents/build_direct_feedback_refiner_inputs.py`
- `scripts/agents/run_openai_direct_feedback_refiner.py`
- `data/direct_feedback_refiner_inputs.jsonl`
- `data/direct_feedback_refiner_inputs_retry.jsonl`
- `outputs/refiner/direct_feedback_refiner_model.jsonl`
- `outputs/refiner/direct_feedback_refiner_model_retry.jsonl`
- `outputs/refiner/direct_feedback_refiner_model_merged.jsonl`
- `docs/agents/direct_feedback_refiner_report.md`
- `docs/project/experiment_outline.md`
- `README.md`

实验命令：

```powershell
python scripts/agents/build_direct_feedback_refiner_inputs.py
python scripts/agents/run_openai_direct_feedback_refiner.py --dry-run --limit 1
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_direct_feedback_refiner.py --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1800
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_direct_feedback_refiner.py --inputs data/direct_feedback_refiner_inputs_retry.jsonl --output outputs/refiner/direct_feedback_refiner_model_retry.jsonl --model gpt-5-mini --max-output-tokens 2600 --resume --retries 8 --delay-seconds 3
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/direct_feedback_refiner_model_merged.jsonl --sqlplus-output outputs/refiner/empty_sqlplus.jsonl --label "gpt-5-mini direct-sql execution-feedback refiner merged" --report docs/agents/direct_feedback_refiner_report_raw_merged.md
```

实验配置：

- 模型：`gpt-5-mini`。
- 输入来源：Direct NL2SQL baseline 的失败样例。
- 输入限制：不包含 gold SQL、gold result rows、字段级 gold differences。
- 反馈信息：原 SQL、执行状态、结果行数、结果预览、粗粒度错误类别、schema 和已知数据库值。
- 评估方式：修复 SQL 执行后，与 gold SQL 执行结果比较。gold 只用于离线评估，不进入模型输入。

实验结果：

- Direct NL2SQL 初始失败样例：14 条。
- Direct SQL Refiner 合并后：SQL 可执行 14/14，修复成功 6/14，JSON 解析失败 0/14。
- 难度分布：simple 3/4，medium 2/8，hard 1/2。
- 成功样例：q002、q003、q005、q007、q019、q023。
- Token：input 12000，output 10531，total 22531。

对比观察：

- Direct SQL Feedback Refiner：6/14。
- SQL+ Feedback Refiner v2 merged：4/13。
- 当前小数据集和单 Refiner prompt 设置下，Direct SQL 修复略高于 SQL+ 修复。
- 这不说明 SQL+ 方案失败，而说明粗粒度反馈没有发挥 SQL+ 分步表示的优势。

方向调整：

- 开题中应把 Direct SQL 反馈修正作为必要 baseline，而不是回避它。
- 当前结果可以反向支撑多智能体必要性：如果只用单 Refiner prompt，SQL+ 优势不明显；必须引入 Schema Agent 和 Critic Agent，把错误定位映射到 SQL+ 局部步骤。
- 下一步应设计同等信息条件下的 Critic Agent，对 Direct SQL 和 SQL+ 都提供非 gold 结构化诊断，再比较两者修复成功率。

下一步：

- 实现非 gold Critic Agent prompt。
- 生成 `critic_diagnosis` 输入，不包含 gold answer。
- 运行 `Critic -> Refiner` 两阶段实验，对比 Direct SQL 和 SQL+。

## 2026-06-03 SQL+ Schema-Critic-Refiner 多智能体初版实验

实验目的：

引入 `Schema Agent + Critic Agent + Refiner Agent`，将 SQL+ 非 gold 反馈修正拆成 schema 分析、错误定位和局部修复三个阶段，验证多智能体是否优于单 Refiner prompt。

涉及文件：

- `prompts/agents/sqlplus_critic.md`
- `prompts/agents/sqlplus_critic_refiner.md`
- `scripts/agents/build_sqlplus_schema_agent_inputs.py`
- `scripts/agents/run_openai_sqlplus_critic.py`
- `scripts/agents/build_critic_refiner_inputs.py`
- `data/sqlplus_schema_agent_inputs.jsonl`
- `data/sqlplus_schema_agent_inputs_retry.jsonl`
- `data/sqlplus_critic_refiner_inputs_merged.jsonl`
- `outputs/agents/sqlplus_critic_model.jsonl`
- `outputs/agents/sqlplus_critic_model_retry.jsonl`
- `outputs/agents/sqlplus_critic_model_merged.jsonl`
- `outputs/refiner/sqlplus_critic_refiner_model.jsonl`
- `docs/agents/sqlplus_schema_critic_refiner_report.md`
- `docs/project/experiment_outline.md`
- `README.md`

实验命令：

```powershell
python scripts/agents/build_sqlplus_schema_agent_inputs.py
python scripts/agents/run_openai_sqlplus_critic.py --dry-run --limit 1
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_sqlplus_critic.py --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1800
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_sqlplus_critic.py --inputs data/sqlplus_schema_agent_inputs_retry.jsonl --output outputs/agents/sqlplus_critic_model_retry.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 3000
python scripts/agents/build_critic_refiner_inputs.py --critic-output outputs/agents/sqlplus_critic_model_merged.jsonl --output data/sqlplus_critic_refiner_inputs_merged.jsonl --report docs/agents/sqlplus_critic_refiner_inputs_merged.md
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_feedback_refiner.py --inputs data/sqlplus_critic_refiner_inputs_merged.jsonl --prompt-template prompts/agents/sqlplus_critic_refiner.md --output outputs/refiner/sqlplus_critic_refiner_model.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1800
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_critic_refiner_model.jsonl --label "gpt-5-mini schema-critic-refiner sqlplus" --report docs/agents/sqlplus_schema_critic_refiner_report_raw.md
python scripts/agents/diagnose_sqlplus_mismatches.py --predictions outputs/refiner/sqlplus_critic_refiner_model.jsonl --jsonl-output data/sqlplus_schema_critic_refiner_diagnostics.jsonl --report docs/agents/sqlplus_schema_critic_refiner_diagnostics.md
```

实验配置：

- 模型：`gpt-5-mini`。
- 输入来源：SQL+ prompt v2 的 13 条失败样例。
- 输入限制：不包含 gold SQL、gold SQL+、gold result rows、字段级 gold differences。
- Schema Agent：规则生成相关表、字段、join 路径和候选数据库值。
- Critic Agent：LLM 生成非 gold 错误定位。
- Refiner Agent：根据 Schema/Critic 输出修正 SQL+。

实验结果：

- Critic 输出：13/13，重跑截断样例后 JSON 解析失败 0/13。
- Critic 分类：filter_or_value 7 条，order_or_limit 6 条。
- Refiner 输出：13/13，SQL+ 有效 13/13，SQL 可执行 13/13，修复成功 3/13。
- 成功样例：q002、q017、q026。
- Critic token：31367。
- Refiner token：26313。

对比观察：

- SQL+ 非 gold 单 Refiner v2：4/13。
- SQL+ Schema-Critic-Refiner 初版：3/13。
- Direct SQL 非 gold Refiner：6/14。
- 诊断辅助 SQL+ Refiner：13/13。

问题与观察：

- 本轮多智能体初版没有提升成功率，反而低于单 Refiner。
- Critic Agent 没有识别出 aggregation、schema_or_join、projection 等复杂错误，过度集中在 filter/value 和 order/limit。
- Schema Agent 当前只是启发式候选 schema，不足以明确自然语言中的指标、输出列、排序意图和 join 必要性。
- 结果说明多智能体不能只是形式串联；Critic 的诊断质量决定 Refiner 的上限。

方向调整：

- 保留当前结果作为多智能体初版和问题发现实验。
- 下一步不应继续简单加 agent，而应提升 Critic 的结构化诊断能力。
- Critic 应按 SQL+ 步骤逐项检查：FROM/JOIN/WHERE/GROUP/AGG/SELECT/ORDER/LIMIT。
- Schema Agent 应输出自然语言解析结果：实体、指标、过滤条件、排序意图、输出列和候选值。

下一步：

- 设计 step-wise Critic Agent，强制逐步输出每个 SQL+ step 的 correct/suspicious/missing 状态。
- 对失败类型分治：先优化 order/value 两类，再处理 aggregation/join。
- 在同等 Critic 信息下重新比较 SQL+ 与 Direct SQL 修复。

## 2026-06-04 agents 目录整理与 Step-wise Critic 改良实验

实验目的：

整理 agents 相关文件结构，并改良 Critic Agent：将原来的粗粒度错误分类改为按 SQL+ 步骤逐项诊断，验证是否能提升 SQL+ 非 gold 反馈修正成功率。

目录整理：

```text
prompts/agents/schema
prompts/agents/critic
prompts/agents/refiner

scripts/agents/schema
scripts/agents/critic
scripts/agents/refiner
scripts/agents/diagnostics
scripts/agents/pipeline

docs/agents/schema
docs/agents/critic
docs/agents/refiner
docs/agents/diagnostics
docs/agents/pipeline

outputs/agents/critic
```

涉及文件：

- `prompts/agents/critic/sqlplus_critic.md`
- `prompts/agents/refiner/sqlplus_critic_refiner.md`
- `scripts/agents/schema/build_sqlplus_schema_agent_inputs.py`
- `scripts/agents/critic/run_openai_sqlplus_critic.py`
- `scripts/agents/refiner/run_openai_feedback_refiner.py`
- `scripts/agents/pipeline/build_critic_refiner_inputs.py`
- `outputs/agents/critic/sqlplus_critic_stepwise_model_merged.jsonl`
- `outputs/refiner/sqlplus_stepwise_critic_refiner_model_merged.jsonl`
- `docs/agents/pipeline/sqlplus_stepwise_critic_refiner_report.md`
- `docs/project/experiment_outline.md`
- `README.md`

实验命令：

```powershell
python scripts/agents/schema/build_sqlplus_schema_agent_inputs.py --output data/sqlplus_schema_agent_inputs_stepwise.jsonl --report docs/agents/schema/sqlplus_schema_agent_inputs_stepwise.md
python scripts/agents/critic/run_openai_sqlplus_critic.py --inputs data/sqlplus_schema_agent_inputs_stepwise.jsonl --output outputs/agents/critic/sqlplus_critic_stepwise_model.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 2600
python scripts/agents/critic/run_openai_sqlplus_critic.py --inputs data/sqlplus_schema_agent_inputs_stepwise_retry.jsonl --output outputs/agents/critic/sqlplus_critic_stepwise_model_retry.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 4200
python scripts/agents/pipeline/build_critic_refiner_inputs.py --schema-inputs data/sqlplus_schema_agent_inputs_stepwise.jsonl --critic-output outputs/agents/critic/sqlplus_critic_stepwise_model_merged.jsonl --output data/sqlplus_critic_refiner_inputs_stepwise_merged.jsonl --report docs/agents/pipeline/sqlplus_critic_refiner_inputs_stepwise_merged.md
python scripts/agents/refiner/run_openai_feedback_refiner.py --inputs data/sqlplus_critic_refiner_inputs_stepwise_merged.jsonl --prompt-template prompts/agents/refiner/sqlplus_critic_refiner.md --output outputs/refiner/sqlplus_stepwise_critic_refiner_model.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 2000
python scripts/agents/refiner/run_openai_feedback_refiner.py --inputs data/sqlplus_critic_refiner_inputs_stepwise_retry.jsonl --prompt-template prompts/agents/refiner/sqlplus_critic_refiner.md --output outputs/refiner/sqlplus_stepwise_critic_refiner_model_retry.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 3600
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_stepwise_critic_refiner_model_merged.jsonl --label "gpt-5-mini stepwise-critic-refiner sqlplus merged" --report docs/agents/pipeline/sqlplus_stepwise_critic_refiner_report_raw_merged.md
python scripts/agents/diagnostics/diagnose_sqlplus_mismatches.py --predictions outputs/refiner/sqlplus_stepwise_critic_refiner_model_merged.jsonl --jsonl-output data/sqlplus_stepwise_critic_refiner_diagnostics_merged.jsonl --report docs/agents/pipeline/sqlplus_stepwise_critic_refiner_diagnostics_merged.md
```

实验配置：

- 模型：`gpt-5-mini`。
- 输入样例：SQL+ prompt v2 的 13 条失败样例。
- 输入限制：不包含 gold SQL、gold SQL+、gold result rows、字段级 gold differences。
- Critic 输出：强制包含 8 个 step diagnosis：FROM/JOIN/WHERE/GROUP/AGG/SELECT/ORDER/LIMIT。

实验结果：

- Step-wise Critic 输出：13/13。
- Critic JSON 解析失败：0/13。
- Critic 类型：order_or_limit 6 条，filter_or_value 6 条，aggregation 1 条。
- Critic localized step：ORDER 6，WHERE 6，JOIN 2，LIMIT 1，GROUP 1，AGG 1，SELECT 1。
- Critic token：49581。
- Refiner 输出：13/13。
- SQL+ 有效：13/13。
- SQL 可执行：12/13。
- 修复成功：3/13。
- Refiner token：35688。
- 成功样例：q002、q017、q026。

问题与观察：

- Step-wise Critic 的诊断粒度明显高于旧 Critic，能定位 JOIN/GROUP/AGG/SELECT 等局部步骤。
- 但最终修复成功率仍为 3/13，没有超过 SQL+ 单 Refiner v2 的 4/13。
- Refiner 对多个 suspicious/missing 步骤的联合修复仍不稳定。
- Step-wise Critic 成本较高，Critic + Refiner 总 token 约 85269。
- 迁移目录后 `build_sqlplus_schema_agent_inputs.py` 出现一次中文关键词编码损坏，已修复为稳定 UTF-8 关键词。

方向调整：

- 多智能体方向保留，但不继续盲目扩大 prompt。
- 下一步应做错误类型分治：先分别优化 ORDER、value linking、aggregation、join 四类错误。
- 对 aggregation/join 错误，需要引入候选 patch 和反事实执行，而不是只依赖 Critic 文本提示。

下一步：

- 设计 order-only 修复实验，先把 order_or_limit_mismatch 修复率做高。
- 设计 value-linking 修复实验，利用 known values 做候选替换。
- 再处理 aggregation/join 的候选 patch 生成与执行验证。

## 2026-06-04 SQL+ ORDER/value-linking 分治修复实验

实验目的：

将 SQL+ 反馈修正按错误类型拆开，分别验证 ORDER-only 和 value-linking-only 两类局部修复是否比全局 Refiner 更稳定。

涉及文件：

- `prompts/agents/refiner/sqlplus_order_only_refiner.md`
- `prompts/agents/refiner/sqlplus_value_only_refiner.md`
- `scripts/agents/pipeline/build_divide_refiner_inputs.py`
- `data/sqlplus_order_only_refiner_inputs.jsonl`
- `data/sqlplus_value_only_refiner_inputs.jsonl`
- `outputs/refiner/sqlplus_order_only_refiner_model_merged.jsonl`
- `outputs/refiner/sqlplus_value_only_refiner_model.jsonl`
- `docs/agents/pipeline/sqlplus_divide_refiner_report.md`
- `docs/project/experiment_outline.md`
- `README.md`

实验命令：

```powershell
python scripts/agents/pipeline/build_divide_refiner_inputs.py --kind order
python scripts/agents/pipeline/build_divide_refiner_inputs.py --kind value
python scripts/agents/refiner/run_openai_feedback_refiner.py --inputs data/sqlplus_order_only_refiner_inputs.jsonl --prompt-template prompts/agents/refiner/sqlplus_order_only_refiner.md --output outputs/refiner/sqlplus_order_only_refiner_model.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1200
python scripts/agents/refiner/run_openai_feedback_refiner.py --inputs data/sqlplus_value_only_refiner_inputs.jsonl --prompt-template prompts/agents/refiner/sqlplus_value_only_refiner.md --output outputs/refiner/sqlplus_value_only_refiner_model.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1400
python scripts/agents/refiner/run_openai_feedback_refiner.py --inputs data/sqlplus_order_only_refiner_inputs_retry.jsonl --prompt-template prompts/agents/refiner/sqlplus_order_only_refiner.md --output outputs/refiner/sqlplus_order_only_refiner_model_retry.jsonl --model gpt-5-mini --resume --retries 8 --delay-seconds 3 --max-output-tokens 1200
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_order_only_refiner_model_merged.jsonl --label "gpt-5-mini sqlplus order-only refiner merged" --report docs/agents/pipeline/sqlplus_order_only_refiner_report_raw_merged.md
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_value_only_refiner_model.jsonl --label "gpt-5-mini sqlplus value-only refiner" --report docs/agents/pipeline/sqlplus_value_only_refiner_report_raw.md
```

实验配置：

- 模型：`gpt-5-mini`。
- ORDER-only 样例：q002、q003、q005。
- value-linking-only 样例：q004、q017、q026。
- 输入限制：不包含 gold SQL、gold SQL+、gold result rows、字段级 gold differences。
- ORDER-only 只允许修改 ORDER/LIMIT。
- value-linking-only 只允许修改 WHERE。

实验结果：

- ORDER-only：SQL+ 有效 3/3，SQL 可执行 3/3，修复成功 2/3，成功 q002、q003，失败 q005。
- value-linking-only：SQL+ 有效 3/3，SQL 可执行 3/3，修复成功 3/3，成功 q004、q017、q026。
- ORDER-only token：3863。
- value-linking-only token：3973。

问题与观察：

- value-linking 类错误在候选值明确、只允许改 WHERE 的条件下非常稳定。
- ORDER-only 的 q005 仍失败，模型将 row-order mismatch 修成 `ORDER oi.item_id ASC`，没有从“数量”推断出 `ORDER oi.quantity DESC`。
- 这说明 ORDER 意图识别需要更强的规则或 Critic，不应只依赖“确定性排序”启发。

方向调整：

- 分治策略有效，尤其适合 value-linking 类错误。
- 下一步应继续做 aggregation-only 和 join-only 分治实验。
- ORDER 类需要补充“输出数值列优先级”和“业务语义排序”规则。

下一步：

- 单独优化 q005 所属的隐式 ORDER 意图识别。
- 扩展 value-linking 到更多候选值错误。
- 做 aggregation-only 分治实验。

## 2026-06-04 SQL+ value lookup tool + repair skill 实验

实验目的：

验证在 value-linking 错误上，引入工具和 skill 是否比纯 prompt Refiner 更稳定。工具负责检索数据库已知字段值、生成候选 WHERE patch、执行候选 SQL；skill 负责按错误类型约束修复范围并选择候选。

涉及文件：

- `scripts/agents/tools/run_value_lookup_repair_skill.py`
- `outputs/refiner/sqlplus_value_lookup_skill_outputs_v3.jsonl`
- `docs/agents/tools/value_lookup_repair_skill_report_v3.md`
- `docs/project/experiment_outline.md`

实验命令：

```powershell
python scripts/agents/tools/run_value_lookup_repair_skill.py --output outputs/refiner/sqlplus_value_lookup_skill_outputs_v3.jsonl --report docs/agents/tools/value_lookup_repair_skill_report_v3.md
```

实验配置：

- 输入样例：`data/sqlplus_value_only_refiner_inputs.jsonl`
- 样例数量：3 条，q004、q017、q026
- 工具能力：SQLite 执行、字段值检索、SQL+ parser、SQL+ 到 SQL 转换、候选 patch 执行验证
- gold SQL 只用于离线评估，不进入候选生成和修复选择

实验结果：

- SQL+ 有效：3/3
- SQL 可执行：3/3
- 修复成功：3/3
- q004：将 `o.order_date > '2025-03-15'` 归一化为 `o.order_date >= '2025-03-01'`
- q017：将 `canceled` 修正为数据库真实值 `cancelled`
- q026：将 `canceled` 修正为数据库真实值 `cancelled`

问题与观察：

- 第一次工具版本在 q026 上误选原查询，因为结果行数更多；修正为优先选择“已知字段值替换”候选后解决。
- 第二次工具版本在 q004 上误把日期字面量当作普通枚举值替换；修正为跳过 date 列的字面量值检索后解决。
- 工具增强适合处理可枚举字段值、状态值拼写、日期边界归一化等错误。

方向调整：

- Agent 设计需要加入 tool/RAG/skill 层，不应只依赖 prompt。
- value-linking 错误后续应交给 Schema Agent 提供候选字段值，再由 value_linking_repair_skill 生成和执行候选 patch。
- 下一步可以继续把 ORDER、aggregation、join 也设计成独立 skill，并与 Critic Agent 输出的错误类型路由结合。

## 2026-06-04 SQL+ ORDER repair skill 实验

实验目的：

验证 ORDER/LIMIT 类错误是否可以通过局部 repair skill 稳定修复，尤其是此前 prompt-only ORDER Refiner 失败的 q005。

涉及文件：

- `scripts/agents/tools/run_order_repair_skill.py`
- `outputs/refiner/sqlplus_order_skill_outputs_v1.jsonl`
- `docs/agents/tools/order_repair_skill_report_v1.md`
- `docs/project/experiment_outline.md`

实验命令：

```powershell
python scripts/agents/tools/run_order_repair_skill.py --output outputs/refiner/sqlplus_order_skill_outputs_v1.jsonl --report docs/agents/tools/order_repair_skill_report_v1.md
```

实验配置：

- 输入样例：`data/sqlplus_order_only_refiner_inputs.jsonl`
- 样例数量：3 条，q002、q003、q005
- 工具能力：SQL+ parser、SQL+ 到 SQL 转换、SQLite 执行验证、SELECT 列启发式排序候选生成
- gold SQL 只用于离线评估，不进入候选生成和修复选择

实验结果：

- SQL+ 有效：3/3
- SQL 可执行：3/3
- 修复成功：3/3
- q002：选择 `ORDER c.customer_name ASC`
- q003：选择 `ORDER p.price DESC`
- q005：选择 `ORDER oi.quantity DESC`

问题与观察：

- q005 失败点被修复，说明“投影中的非 id 数值 measure 优先降序”这一启发式对当前 ORDER 错误有效。
- ORDER 类错误和 value-linking 类错误类似，适合用局部候选生成 + 执行验证处理，而不是让模型整体重写 SQL+。
- 当前 ORDER skill 仍是小样例启发式，后续需要在更多排序场景中验证，例如多字段排序、Top-K、日期排序、聚合别名排序。

方向调整：

- 将后续多智能体框架调整为 Critic Agent 输出错误类型，Skill Router 路由到 value-linking/order/aggregation/join repair skill。
- 下一步优先做 aggregation repair skill，因为当前失败集中还包含聚合口径、HAVING/ORDER 引用和聚合别名问题。

## 2026-06-04 SQL+ aggregation repair skill 实验

实验目的：

验证聚合类错误是否可以通过局部 repair skill 修复，重点处理 GROUP 维度、AGG 投影、COUNT 口径、AGG 别名、HAVING/ORDER 引用。

涉及文件：

- `data/sqlplus_aggregation_repair_inputs.jsonl`
- `scripts/agents/tools/run_aggregation_repair_skill.py`
- `outputs/refiner/sqlplus_aggregation_skill_outputs_v1.jsonl`
- `outputs/refiner/sqlplus_aggregation_skill_outputs_v2.jsonl`
- `docs/agents/tools/aggregation_repair_skill_report_v1.md`
- `docs/agents/tools/aggregation_repair_skill_report_v2.md`
- `docs/project/experiment_outline.md`

实验命令：

```powershell
python -B scripts/agents/tools/run_aggregation_repair_skill.py --output outputs/refiner/sqlplus_aggregation_skill_outputs_v1.jsonl --report docs/agents/tools/aggregation_repair_skill_report_v1.md
python -B scripts/agents/tools/run_aggregation_repair_skill.py --output outputs/refiner/sqlplus_aggregation_skill_outputs_v2.jsonl --report docs/agents/tools/aggregation_repair_skill_report_v2.md
```

实验配置：

- 输入样例：`data/sqlplus_aggregation_repair_inputs.jsonl`
- 样例数量：3 条，q013、q015、q021
- 工具能力：SQL+ parser、SQL+ 到 SQL 转换、SQLite 执行验证、聚合候选 patch 生成
- gold SQL 只用于离线评估，不进入候选生成和修复选择

实验结果：

- v1：SQL+ 有效 3/3，SQL 可执行 3/3，修复成功 2/3
- v2：SQL+ 有效 3/3，SQL 可执行 3/3，修复成功 3/3
- q013：移除冗余 `c.customer_id` 分组和投影，补充按聚合别名降序排序
- q015：将 `COUNT(c.customer_id)` 归一化为 `COUNT(*)`，补充 `ORDER customer_count DESC`
- q021：补充 `GROUP p.category` 和 `AGG p.category, SUM(oi.quantity) AS total_quantity`

问题与观察：

- v1 失败在 q021，错误选择了 `o.status` 作为 GROUP 维度；v2 调整为业务维度优先，即 `category/level/city/name` 优先于 `status`。
- 聚合错误通常不是语法错误，而是输出维度、聚合口径和排序引用错误。
- SQL+ 分步结构使这类修复可以限制在 GROUP/AGG/HAVING/ORDER 层，避免整体重写。

方向调整：

- value-linking、ORDER、aggregation 三类 skill 均已在小样例上达到 3/3，说明 `Critic Agent -> Skill Router -> Repair Skill -> Executor` 是当前最有实验支撑的路线。
- 下一步应处理 join repair skill，重点修复 join 路径、冗余 join、缺少 WHERE paid 条件和连接方向规范化。

## 2026-06-04 SQL+ join repair skill 实验

实验目的：

验证 join 相关错误是否可以通过局部 repair skill 修复，重点处理 JOIN 路径错误、冗余 JOIN、缺失 JOIN、缺少 paid 过滤条件和连接方向规范化。

涉及文件：

- `data/sqlplus_join_repair_inputs.jsonl`
- `scripts/agents/tools/run_join_repair_skill.py`
- `outputs/refiner/sqlplus_join_skill_outputs_v1.jsonl`
- `outputs/refiner/sqlplus_join_skill_outputs_v2.jsonl`
- `docs/agents/tools/join_repair_skill_report_v1.md`
- `docs/agents/tools/join_repair_skill_report_v2.md`
- `docs/project/experiment_outline.md`

实验命令：

```powershell
python -B scripts/agents/tools/run_join_repair_skill.py --output outputs/refiner/sqlplus_join_skill_outputs_v1.jsonl --report docs/agents/tools/join_repair_skill_report_v1.md
python -B scripts/agents/tools/run_join_repair_skill.py --output outputs/refiner/sqlplus_join_skill_outputs_v2.jsonl --report docs/agents/tools/join_repair_skill_report_v2.md
```

实验配置：

- 输入样例：`data/sqlplus_join_repair_inputs.jsonl`
- 样例数量：3 条，q019、q022、q025
- 工具能力：SQL+ parser、SQL+ 到 SQL 转换、SQLite 执行验证、JOIN 候选 patch 生成
- gold SQL 只用于离线评估，不进入候选生成和修复选择

实验结果：

- v1：SQL+ 有效 3/3，SQL 可执行 3/3，修复成功 2/3
- v2：SQL+ 有效 3/3，SQL 可执行 3/3，修复成功 3/3
- q019：规范化 `orders` 与 `order_items` 的连接方向，补充按 `order_amount` 降序排序
- q022：删除冗余 `products` join，补充 `o.status = 'paid'`，去掉冗余 `c.customer_id`，将 `COUNT(DISTINCT p.category)` 修为 `COUNT(DISTINCT oi.product_id)`
- q025：补充 `products p` join，将投影从商品编号改为商品名称，并规范化金额别名

问题与观察：

- v1 失败在 q025，因为初版只在 SQL+ 中已出现 `p.` 或 `product_name` 时才补 products join；v2 增加规则：当 SELECT 中存在 `oi.product_id` 和单项金额表达式时，推断需要补 products join 并输出商品名称。
- join 错误通常会连带影响 SELECT、AGG、ORDER，因此 join repair skill 需要允许修复 JOIN 直接影响的投影和聚合字段。
- JOIN 方向规范化本身不改变执行结果，但有助于可解释性和后续 SQL+ 层定位。

方向调整：

- 四类局部 skill 已完成：value-linking、ORDER、aggregation、join。
- 下一步应实现 Skill Router，把 Critic Agent 输出的错误类型路由到对应 skill，并评估端到端修复成功率。

## 2026-06-04 SQL+ Skill Router 端到端修复实验

实验目的：

实现 Skill Router，将 Critic Agent 输出的错误类型和局部步骤诊断自动路由到 value-linking、ORDER、aggregation、join 四类 repair skill，并评估端到端修复成功率。

涉及文件：

- `scripts/agents/pipeline/run_skill_router_experiment.py`
- `outputs/refiner/sqlplus_skill_router_outputs_v1.jsonl`
- `outputs/refiner/sqlplus_skill_router_outputs_v2.jsonl`
- `docs/agents/pipeline/sqlplus_skill_router_report_v1.md`
- `docs/agents/pipeline/sqlplus_skill_router_report_v2.md`
- `scripts/agents/tools/run_order_repair_skill.py`
- `docs/agents/tools/order_repair_skill_report_v2.md`
- `docs/project/experiment_outline.md`

实验命令：

```powershell
python -B scripts/agents/pipeline/run_skill_router_experiment.py --output outputs/refiner/sqlplus_skill_router_outputs_v1.jsonl --report docs/agents/pipeline/sqlplus_skill_router_report_v1.md
python -B scripts/agents/tools/run_order_repair_skill.py --output outputs/refiner/sqlplus_order_skill_outputs_v2.jsonl --report docs/agents/tools/order_repair_skill_report_v2.md
python -B scripts/agents/pipeline/run_skill_router_experiment.py --output outputs/refiner/sqlplus_skill_router_outputs_v2.jsonl --report docs/agents/pipeline/sqlplus_skill_router_report_v2.md
```

实验配置：

- 输入样例：`data/sqlplus_critic_refiner_inputs_stepwise_merged.jsonl`
- 样例数量：13 条 SQL+ prompt v2 失败样例
- Critic 信息：使用现有非 gold Step-wise Critic Agent 输出，包括 `likely_error_type` 和 `localized_steps`
- Router 依据：Critic 类型、localized steps、SQL+ 是否包含 AGG/JOIN/ORDER/WHERE 等结构特征
- Skill 能力：value lookup、ORDER、aggregation、join
- gold SQL 只用于离线评估，不进入 Router 路由和 repair skill 候选选择

实验结果：

- v1：SQL+ 有效 13/13，SQL 可执行 13/13，修复成功 11/13
- v2：SQL+ 有效 13/13，SQL 可执行 13/13，修复成功 12/13
- v2 相比 SQL+ 非 gold 单 Refiner v2 的 4/13、Schema-Critic-Refiner 初版的 3/13 有明显提升

v2 路由结果：

- order：4 条，成功 3/4
- order -> aggregation：2 条，成功 2/2
- value：1 条，成功 1/1
- value -> order：2 条，成功 2/2
- join -> aggregation：1 条，成功 1/1
- value -> join：1 条，成功 1/1
- value -> aggregation -> join -> order：1 条，成功 1/1
- value -> join -> aggregation -> order：1 条，成功 1/1

问题与观察：

- v1 失败 q026，因为 ORDER skill 选择了 `c.customer_name ASC`；v2 调整为 `order_id` 优先后修复成功。
- v2 唯一失败 q006，错误类型为 projection mismatch：生成 SQL+ 多输出了 `p.product_id`，当前四类 skill 不负责投影列删除。
- Router 不能只依赖 Critic 的一级错误类型。q013、q021、q025 等样例需要结合 SQL+ 结构特征触发复合 skill 链。

方向调整：

- 当前最强实验路线已经从纯 Refiner 转向 `Critic Agent -> Skill Router -> Repair Skill -> Executor`。
- 下一步可补充 projection repair skill，处理 q006 这类“结果列多/少”的错误。
- 开题报告中应强调：多智能体效果来自角色拆分、工具调用、错误类型路由和可执行候选验证，而不是简单串联多个 LLM prompt。

## 2026-06-04 Spider 小规模公开 benchmark smoke test

实验目的：

在开题阶段引入公开 benchmark 子集，验证当前 SQL+ 表达与转换机制是否能迁移到 Spider 的真实跨数据库样例。该实验不追求完整排行榜分数，只验证受支持 SQL 子集的可行性。

涉及文件：

- `data/benchmarks/spider/dev.json`
- `data/benchmarks/spider/tables.json`
- `data/benchmarks/spider/database/concert_singer/concert_singer.sqlite`
- `data/benchmarks/spider/spider_smoke_sqlplus_10.jsonl`
- `data/benchmarks/spider/spider_smoke_sqlplus_20.jsonl`
- `scripts/benchmarks/run_spider_smoke.py`
- `docs/benchmarks/spider_smoke_report_10.md`
- `docs/benchmarks/spider_smoke_report_20.md`

实验命令：

```powershell
python -B scripts/benchmarks/run_spider_smoke.py --limit 10 --output data/benchmarks/spider/spider_smoke_sqlplus_10.jsonl --report docs/benchmarks/spider_smoke_report_10.md
python -B scripts/benchmarks/run_spider_smoke.py --limit 20 --output data/benchmarks/spider/spider_smoke_sqlplus_20.jsonl --report docs/benchmarks/spider_smoke_report_20.md
```

实验配置：

- 数据集：Spider dev 公开样例子集
- 数据库：`concert_singer`
- 样例数量：20 条
- 查询类型：count、select、where、order、limit、group、aggregation、simple join
- 筛选策略：排除当前 SQL+ 子集暂不支持的 union/intersect/except/subquery/in/like/between/or/distinct/case 等复杂结构
- 评估方式：将 Spider gold SQL 改写为 SQL+，再由 SQL+ 转换器转回 SQL，在 SQLite 上比较执行结果

实验结果：

- 10 条 smoke test：SQL+ 有效 10/10，SQL 可执行 10/10，执行一致 10/10
- 20 条 smoke test：SQL+ 有效 20/20，SQL 可执行 20/20，执行一致 20/20

问题与观察：

- 当前 SQL+ 子集能够覆盖 Spider 中一部分常见 easy/medium 查询结构，包括聚合、排序、limit、分组和简单 join。
- 该实验是小规模受支持子集验证，不是完整 Spider benchmark 跑分，不能与排行榜方法直接比较。
- 当前 SQL+ 仍缺少对复杂子查询、集合运算、复杂布尔条件、distinct、窗口函数等结构的支持。

方向调整：

- 开题材料中可以加入 Spider smoke test，证明本课题不只在自建数据集上可行，也具备公开 benchmark 子集迁移可行性。
- 后续应扩展到多数据库 Spider 子集，并逐步支持更多 SQL 结构。

## 2026-06-04 Projection repair skill 与 Skill Router v3

目的：

- 补齐当前 Skill Router 唯一未修复的 q006 projection mismatch。
- 验证结果列多/少是否可以通过 SQL+ `SELECT` 局部候选裁剪和执行验证修复。
- 将 projection repair skill 接入 `Critic Agent -> Skill Router -> Repair Skill -> Executor` 端到端闭环。

涉及文件：

- `scripts/agents/tools/run_projection_repair_skill.py`
- `data/sqlplus_projection_repair_inputs.jsonl`
- `scripts/agents/pipeline/run_skill_router_experiment.py`
- `outputs/refiner/sqlplus_projection_skill_outputs.jsonl`
- `outputs/refiner/sqlplus_skill_router_outputs_v3.jsonl`
- `docs/agents/tools/projection_repair_skill_report.md`
- `docs/agents/pipeline/sqlplus_skill_router_report_v3.md`
- `README.md`
- `docs/project/opening_preliminary_results.md`
- `docs/project/experiment_outline.md`
- `docs/opening/opening_report.md`
- `docs/opening/README.md`
- `.codex/skills/nl2sql-repair-skill-lab/SKILL.md`

执行命令：

```powershell
python -B scripts/agents/tools/run_projection_repair_skill.py
python -B scripts/agents/pipeline/run_skill_router_experiment.py --output outputs/refiner/sqlplus_skill_router_outputs_v3.jsonl --report docs/agents/pipeline/sqlplus_skill_router_report_v3.md
python3 -B scripts/agents/tools/run_projection_repair_skill.py
python3 -B scripts/agents/pipeline/run_skill_router_experiment.py --output outputs/refiner/sqlplus_skill_router_outputs_v3.jsonl --report docs/agents/pipeline/sqlplus_skill_router_report_v3.md
```

结果：

- 本机 shell 中 `python` 命令不可用，两条 `python -B ...` 首次验证命令均失败，错误为 `zsh:1: command not found: python`。
- 改用 `python3` 后 projection repair skill 运行成功：样例 1 条，SQL+ 有效 1/1，SQL 可执行 1/1，修复成功 1/1。
- q006 修复动作为删除未被问题要求的 `p.product_id` 投影，输出 `p.product_name, p.price`。
- Skill Router v3 运行成功：13 条 SQL+ 失败样例，SQL+ 有效 13/13，SQL 可执行 13/13，修复成功 13/13。

问题与观察：

- projection skill 初次接入 router 后曾误伤 q025：join skill 已把明细查询修到 gold 对齐，但 projection 又删除了 `oi.item_id`。
- 修正方式：收紧 router 的 projection 触发条件，仅在同一 alias 同时出现 id 与 name/price 等描述列时按结构启发触发；projection skill 遇到“明细”类问题时保留 `item_id` / `order_id`。
- q006 的 Critic Agent 仍将真实 projection mismatch 标为 `order_or_limit`，说明 Critic 的 SELECT/projection 诊断仍需增强；router v3 目前依靠 SQL+ 结构启发补救该诊断缺口。

方向调整：

- 当前 13 条已知 SQL+ 失败样例上的 Skill Router 指标从 12/13 更新为 13/13。
- repair skill 覆盖从 value-linking、ORDER、aggregation、join 四类扩展到 value-linking、ORDER、aggregation、join、projection 五类。
- 下一步重点从“补 projection repair skill”调整为“扩展无报错语义错诊断、projection/SELECT 诊断稳定性、复合错误路由顺序和公开子集覆盖”。

## 2026-06-15 Repairability 指标对比实验

实验目的：

- 在 IR 生成成本实验之后，继续比较修复阶段收益是否能够抵消 SQL+ 的生成成本。
- 统一统计 error localization accuracy、patch minimality、average repair rounds、repair token cost 和 repair latency 可用性。
- 对比 Direct SQL 单 Refiner 与 SQL+ `Critic Agent -> Skill Router -> Repair Skills -> Executor`。

涉及文件：

- `scripts/agents/pipeline/run_repairability_metrics.py`
- `scripts/agents/pipeline/run_skill_router_experiment.py`
- `outputs/refiner/sqlplus_skill_router_outputs_v3.jsonl`
- `outputs/agents/critic/sqlplus_critic_stepwise_model_merged.jsonl`
- `outputs/refiner/direct_feedback_refiner_model_merged.jsonl`
- `data/repairability_metrics_detail.csv`
- `data/repairability_metrics_summary.csv`
- `docs/agents/pipeline/repairability_metrics_report.md`

执行命令：

```powershell
python scripts/agents/pipeline/run_repairability_metrics.py
```

实验配置：

- 数据集：自建订单分析数据集上的已知失败样例。
- SQL+ 修复组：13 条 SQL+ prompt v2 已知失败样例，使用 Step-wise Critic 输出、Skill Router v3 和五类 repair skill。
- Direct SQL 对照组：14 条 Direct SQL 已知失败样例，使用既有 Direct SQL execution-feedback Refiner 输出。
- 交集子集：9 条两组共有 ID，用于补充观察。
- patch minimality 为离线评价指标，使用 gold 差异计算，不参与候选修复选择。

实验结果：

- Direct SQL Refiner：14 条，修复成功 6/14，localization accuracy 0.8571，strict minimal patch rate 0.8571，平均 patch minimality 0.8571，平均 repair rounds 1，平均 repair tokens 1609.3571。
- SQL+ Critic Router Skills：13 条，修复成功 13/13，localization accuracy 0.7692，router accuracy 1.0000，strict minimal patch rate 0.9231，平均 patch minimality 0.9744，平均 repair rounds 2.2308，平均 repair tokens 3813.9231。
- Direct SQL Refiner overlap：9 条，修复成功 4/9，localization accuracy 0.8889，strict minimal patch rate 0.8889，平均 patch minimality 0.8889，平均 repair rounds 1，平均 repair tokens 1583.2222。
- SQL+ Critic Router Skills overlap：9 条，修复成功 9/9，localization accuracy 0.7778，router accuracy 1.0000，strict minimal patch rate 0.8889，平均 patch minimality 0.9630，平均 repair rounds 2.3333，平均 repair tokens 4001.7778。

问题与观察：

- SQL+ 修复成功率和 patch minimality 优于 Direct SQL 单 Refiner，但平均 repair token 更高。
- SQL+ Critic 的 localized steps 并非总是直接命中 gold 差异，例如 q006、q013、q025 仍依赖 Router 的结构启发补救。
- 当前 Direct SQL Refiner 和 SQL+ Critic 的历史 API 输出没有记录真实 latency，因此无法完整比较端到端 repair latency。
- 本次脚本只能测 SQL+ 本地 router/repair skill latency，该耗时不包含 Critic Agent API 调用，不能作为完整 SQL+ 延迟优势来表述。

方向调整：

- 后续真实模型修复实验必须记录 `latency_seconds`，并区分 Critic latency、repair skill latency、SQL execution latency 和总 latency。
- SQL+ 的研究论证应写成“以更高 Critic token 成本换取更高修复成功率和更可控局部 patch”，不要写成“成本更低”。
- 下一步应优化 Critic 输出长度，尝试轻量 Critic 或 rule/tool-assisted critic，降低 SQL+ 修复阶段 token 成本。

## 2026-06-18 Spider SQL+ multi-agent fresh end-to-end run and generic repair update

实验目的：

- 验证 Spider `concert_singer` 20 条小子集上，当前 SQL+ 多智能体流程是否能够从自然语言和 schema 端到端生成可执行 SQL。
- 区分 conversion smoke test 与真实端到端生成结果。
- 检查通用 semantic repair skill 是否能提升端到端结果，而不是依赖 Spider 题号、数据库专用硬编码或 gold SQL。

执行命令：

```powershell
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python -B scripts/benchmarks/run_spider_multi_agent_sqlplus.py --limit 20 --model gpt-5-mini --repair-rounds 1 --use-generic-repair --output outputs/benchmarks/spider_sqlplus_multi_agent_e2e_v3_fresh.jsonl --report docs/benchmarks/spider_sqlplus_multi_agent_e2e_report_v3_fresh.md

Copy-Item outputs/benchmarks/spider_sqlplus_multi_agent_e2e_v3_fresh.jsonl outputs/benchmarks/spider_sqlplus_multi_agent_e2e_v3_fresh_generic_repair.jsonl -Force
python -B scripts/benchmarks/run_spider_multi_agent_sqlplus.py --limit 20 --model gpt-5-mini --repair-rounds 1 --reevaluate-only --use-generic-repair --output outputs/benchmarks/spider_sqlplus_multi_agent_e2e_v3_fresh_generic_repair.jsonl --report docs/benchmarks/spider_sqlplus_multi_agent_e2e_report_v3_fresh_generic_repair.md
```

运行流程：

1. Schema Agent/上下文构造：从 Spider SQLite 数据库读取表和字段，形成 schema 文本。
2. SQL+ Generator Agent：输入自然语言问题和 schema，调用 `gpt-5-mini` 生成 SQL+。
3. SQL+ Parser / Translator：用 `src/sqlplus.py` 检查 SQL+ 并转换为 SQL。
4. Executor：在 Spider SQLite 数据库上执行转换后的 SQL。
5. Refiner Agent：当 SQL+ 解析或 SQL 执行失败时，输入问题、schema、上一版 SQL+ 和错误信息，最多修复一轮。
6. Generic Semantic Repair Skill：基于问题词义、schema 字段、SQL+ 结构、parser 反馈和执行反馈做局部规则修复；不使用 Spider case ID、数据库专用硬编码或 gold SQL。
7. Offline Evaluator：只在最终评价阶段使用 gold SQL 执行结果计算 execution match。

实验结果：

- Fresh v3 run：20 条，SQL+ valid 19/20，SQL executable 19/20，execution match 19/20，平均 total tokens 1160.3，平均 latency 8.7563s。
- 对同一次 fresh 输出补充通用 semantic repair 后离线重评估：SQL+ valid 20/20，SQL executable 20/20，execution match 20/20。

修复内容：

- 强化 SQL+ generation/refiner prompt：极值实体查询使用 `ORDER + LIMIT`，top-k 聚合使用 `AGG` 保存排序别名并用 `SELECT` 控制最终输出列。
- 增加通用 semantic repair：规范 `AGGREGATE/FILTER/GROUP BY/ORDER BY` 等非 SQL+ 输出；修复 youngest/oldest 自连接退化；补充 top-k 聚合投影；将计数排序默认规范为 `count(*)`；为 year top-k 并列排序加入稳定 tie-break。

边界说明：

- 该结果只适用于当前 Spider `concert_singer` 20 条小子集，不是完整 Spider benchmark 成绩。
- Gold SQL 只用于离线 evaluation，不进入 Generator、Refiner 或 Generic Semantic Repair Skill。
- `20/20` 不能表述为纯一次生成正确率，应表述为“fresh 端到端生成 + 通用 SQL+ semantic repair 后的小子集结果”。

方向调整：

- 后续需要将通用 repair skill 从当前脚本中进一步拆成正式 Agent/Skill 模块，并在更多 Spider 数据库和更复杂 SQL 结构上验证泛化能力。
- 开题材料中应强调：SQL+ 的优势体现在步骤化错误定位和局部 patch，而不是保证初次生成一定正确。

## 2026-06-18 Formal Skill Router -> semantic repair skill split and Spider multi-db scaffold

实验目的：

- 将 Spider 端到端脚本中内联的 generic semantic repair 拆成正式 `Skill Router -> semantic repair skill` 路径。
- 验证拆分后不回退当前 Spider `concert_singer` 20-case 子集结果。
- 为后续多 Spider 数据库泛化实验准备可复用的 candidate subset 构建脚本。

代码变更：

- 新增 `scripts/agents/tools/semantic_repair_skill.py`。
- 新增 `scripts/agents/pipeline/spider_sqlplus_repair_router.py`。
- 修改 `scripts/benchmarks/run_spider_multi_agent_sqlplus.py`，改为通过 Router 调用 semantic repair skill。
- 新增 `scripts/benchmarks/build_spider_multidb_subset.py`。
- 新增报告 `docs/benchmarks/spider_multidb_extension_report.md`。

验证命令：

```powershell
python -B -c "import sys; sys.path.insert(0,'scripts/agents/pipeline'); sys.path.insert(0,'scripts/agents/tools'); import spider_sqlplus_repair_router, semantic_repair_skill; print('router_import_ok')"
python -B scripts/benchmarks/run_spider_multi_agent_sqlplus.py --limit 1 --dry-run
Copy-Item outputs/benchmarks/spider_sqlplus_multi_agent_e2e_v3_fresh.jsonl outputs/benchmarks/spider_sqlplus_multi_agent_e2e_v3_router_repair.jsonl -Force
python -B scripts/benchmarks/run_spider_multi_agent_sqlplus.py --limit 20 --model gpt-5-mini --repair-rounds 1 --reevaluate-only --use-generic-repair --output outputs/benchmarks/spider_sqlplus_multi_agent_e2e_v3_router_repair.jsonl --report docs/benchmarks/spider_sqlplus_multi_agent_e2e_report_v3_router_repair.md
python -B scripts/benchmarks/build_spider_multidb_subset.py --per-db 5 --max-dbs 5
python -B scripts/benchmarks/run_spider_multi_agent_sqlplus.py --cases data/benchmarks/spider/spider_multidb_candidate_subset.jsonl --limit 5 --dry-run
```

实验结果：

- Router/semantic skill import：通过。
- 拆分后对同一 fresh v3 输出重评估：SQL+ valid 20/20，SQL executable 20/20，execution match 20/20。
- 本地 Spider 多库扫描：仅检测到 1 个 SQLite 数据库 `concert_singer`，生成 5 条 candidate subset。

边界说明：

- 当前多库泛化实验尚未真正运行，因为本地缺少完整 Spider `database/` 目录。
- 当前 `20/20` 仍只限于 `concert_singer` 20-case 子集，不是完整 Spider benchmark，也不是多数据库结果。
- semantic repair skill 不使用 Spider case ID、数据库专用硬编码或 gold SQL。

方向调整：

- 下一步需要补齐 Spider 多数据库 SQLite 文件后，运行 `build_spider_multidb_subset.py` 和 `run_spider_multi_agent_sqlplus.py --cases ...` 做真实多库端到端验证。
- 如果多库结果下降，应优先分析 schema linking、prompt examples 对 `concert_singer` 的偏置、semantic repair 规则跨 schema 适用性。

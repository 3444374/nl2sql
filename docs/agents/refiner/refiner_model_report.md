# 诊断辅助 Refiner Agent 实验报告

## 实验性质

本实验验证 `Refiner Agent` 能否根据结构化 SQL+ mismatch 诊断，对 SQL+ prompt v2 的失败样例进行局部修正。

注意：当前输入 `data/sqlplus_mismatch_diagnostics.jsonl` 包含 gold-derived mismatch differences，因此本实验属于“诊断辅助修复实验”，用于验证反馈修正链路可行性，不代表完全自主的真实 Refiner 能力。

## 实验输入

- 失败来源：`outputs/baseline/sqlplus_model_v2.jsonl`
- 诊断输入：`data/sqlplus_mismatch_diagnostics.jsonl`
- 样例数量：13 条 SQL+ prompt v2 执行结果不一致样例
- 模型：`gpt-5-mini`
- Prompt：`prompts/agents/sqlplus_refiner.md`
- 输出：`outputs/refiner/sqlplus_refiner_model.jsonl`

## 实验命令

```powershell
python scripts/agents/run_openai_refiner.py --dry-run --limit 1
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User'); python scripts/agents/run_openai_refiner.py --model gpt-5-mini --resume --retries 8 --delay-seconds 3
python scripts/baseline/run_baseline_eval.py --direct-output outputs/refiner/empty_direct.jsonl --sqlplus-output outputs/refiner/sqlplus_refiner_model.jsonl --label "gpt-5-mini diagnosis-assisted refiner" --report docs/agents/refiner_model_report.md
python scripts/agents/diagnose_sqlplus_mismatches.py --predictions outputs/refiner/sqlplus_refiner_model.jsonl --jsonl-output data/refiner_model_diagnostics.jsonl --report docs/agents/refiner_model_diagnostics.md
```

## 总体结果

| 指标 | 结果 |
| --- | --- |
| Refiner 输出数 | 13/13 |
| JSON 解析失败 | 0/13 |
| SQL+ 有效 | 13/13 |
| SQL 可执行 | 13/13 |
| 执行结果一致 | 13/13 |
| 剩余 mismatch | 0 |
| API input tokens | 11066 |
| API output tokens | 5250 |
| API total tokens | 16316 |

## 难度分布

| 难度 | 样例数 | 修复成功 |
| --- | --- | --- |
| simple | 5 | 5/5 |
| medium | 7 | 7/7 |
| hard | 1 | 1/1 |

## 修复来源分类

| 原始失败类型 | 数量 | 修复成功 |
| --- | --- | --- |
| filter_or_value_linking | 5 | 5/5 |
| order_or_limit_mismatch | 3 | 3/3 |
| aggregation_planning | 2 | 2/2 |
| schema_or_join_planning | 2 | 2/2 |
| projection_mismatch | 1 | 1/1 |

## 结论

本实验说明，在结构化诊断信息存在的条件下，LLM 能够稳定地把错误定位到 SQL+ 的局部步骤，并生成可解析、可转换、可执行且结果正确的修正 SQL+。

该结果可以支撑开题报告中的“SQL+ 层反馈修正机制具备可行性”论证，但不能作为最终真实系统性能。下一步需要去掉 gold-derived differences，仅使用执行反馈、schema、原 SQL+、结果预览和启发式错误类型进行修正。

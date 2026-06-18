---
name: nl2sql-sqlplus-research
description: Use for SQL+ thesis work in this repository, especially when designing SQL+ syntax, writing opening-report claims, adapting Spider/BIRD subsets, or deciding how to phrase feasibility and research significance.
---

# NL2SQL+ SQL+ Research Skill

Use this skill for research-facing work in this repo.

## Core Thesis

The project studies SQL+ as a generation- and repair-friendly intermediate representation for Text-to-SQL. Do not frame the work as a generic Text-to-SQL demo.

Preferred positioning:

```text
Natural language -> SQL+ intermediate representation -> executable SQL
-> execution feedback -> SQL+ local repair
```

## Claim Discipline

Use precise claims:

- Self-built order dataset SQL+ conversion: `30/30`.
- SQL+ prompt v2: `17/30`.
- Direct NL2SQL: `16/30`.
- Skill Router + Repair Skills v3: `13/13` on the current known-failure set.
- Spider conversion smoke test: `20/20` on a supported small Spider dev subset, using Spider gold SQL -> SQL+ -> SQL.
- Spider SQL+ fresh e2e on the same 20-case subset: `19/20`; the same fresh output after `Skill Router -> semantic repair skill` re-evaluation: `20/20`.

Do not claim:

- Full Spider benchmark score.
- End-to-end Spider generation score from the conversion smoke test.
- Full BIRD benchmark support.
- Production-ready Dameng SQL dialect support.
- Autonomous gold-free diagnosis when a result used gold-derived differences.
- Broad benchmark repair performance from the current 13-case known-failure-set result.

## Opening Report Workflow

When writing opening materials, include:

1. Background and significance.
2. Related work: Text-to-SQL, benchmarks, SQL extensions, multi-agent repair.
3. Research questions.
4. SQL+ syntax and conversion.
5. Multi-agent framework.
6. Preliminary experiments.
7. Limitations and future work.

When a research-facing claim changes, update the claim in all relevant places:

- `docs/project/experiment_log.md`
- `docs/project/project_log.md` when the change is documentation, workflow, sync, or opening-material process work rather than an experiment result
- `docs/project/experiment_outline.md`
- `docs/project/opening_preliminary_results.md`
- `docs/opening/opening_report.md`
- `docs/opening/opening_ppt.md`
- `README.md` when it is a headline project result

Do not leave opening-report conclusions ahead of the measured evidence.

## Benchmark Scope

Spider conversion smoke test is a public benchmark subset validation of SQL+ expression/conversion coverage. State it as:

```text
在 Spider dev 的小规模受支持子集上完成 conversion smoke test：先将 Spider gold SQL 改写为 SQL+，再由 SQL+ 转回 SQL 并比较执行结果，用于验证 SQL+ 表达与转换机制对公开 benchmark 结构的初步覆盖能力。
```

Spider end-to-end generation should be stated separately:

```text
在同一 `concert_singer` 20 条小子集上，fresh SQL+ 端到端生成结果为 19/20；同一次 fresh 输出经 `Skill Router -> semantic repair skill` 后离线重评估为 20/20。gold SQL 只用于最终评价，不进入生成或修复。
```

Do not present it as:

```text
完整 Spider benchmark 跑分。
Spider conversion smoke test 的端到端生成准确率。
```

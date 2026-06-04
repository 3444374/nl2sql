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
- Spider smoke test: `20/20` on a supported small Spider dev subset.

Do not claim:

- Full Spider benchmark score.
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

Spider smoke test is a public benchmark subset validation. State it as:

```text
在 Spider dev 的小规模受支持子集上完成 smoke test，验证 SQL+ 表达与转换机制对公开 benchmark 的初步迁移可行性。
```

Do not present it as:

```text
完整 Spider benchmark 跑分。
```

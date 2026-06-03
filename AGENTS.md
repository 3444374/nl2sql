# AGENTS.md

This repository supports the graduate opening project:

`面向 SQL+ 简化查询表达的多智能体自然语言数据库查询生成与反馈修正方法研究`

Agents working in this repo should follow these project-specific rules.

## Project Goal

The work is not a simple Text-to-SQL demo. The research hypothesis is:

1. SQL is structurally complex for LLM generation and repair.
2. SQL+ provides a linear, step-wise intermediate representation.
3. Multi-agent diagnosis, skill routing, local repair skills, and execution feedback can improve repairability and interpretability.

The current core route is:

```text
Natural language
-> SQL+
-> SQL
-> Execution feedback
-> Critic Agent
-> Skill Router
-> Repair Skill
-> Executor
```

## Repository Map

- `src/sqlplus.py`: SQL+ parser and SQL converter.
- `data/`: local datasets and generated experiment inputs.
- `data/benchmarks/spider/`: Spider smoke-test subset files.
- `scripts/sqlplus/`: deterministic SQL+ conversion and rule-repair experiments.
- `scripts/baseline/`: Direct NL2SQL and NL2SQL+ baseline scripts.
- `scripts/agents/`: agent, critic, refiner, skill-router, and repair-skill experiments.
- `scripts/benchmarks/`: public benchmark subset scripts.
- `prompts/`: prompt templates.
- `docs/project/experiment_outline.md`: living experiment roadmap.
- `docs/project/experiment_log.md`: chronological experiment log. Always append, never rewrite history.
- `docs/opening/`: graduate opening report and PPT draft.
- `.codex/skills/`: portable project skills.

## Required Working Rules

1. Before running or changing experiments, read `docs/project/experiment_outline.md`.
2. After any meaningful experiment, append to `docs/project/experiment_log.md`.
3. If a result changes direction, update `docs/project/experiment_outline.md`.
4. Keep opening-stage claims precise:
   - `SQL+ Skill Router + Repair Skills` result is `12/13` on 13 SQL+ failure cases.
   - `Spider smoke test` is `20/20` on a supported small Spider dev subset, not a full benchmark score.
5. Do not commit API keys, `.env`, local secrets, or user-specific environment files.
6. Do not present gold-derived diagnostics as real autonomous repair results.
7. Prefer small, reproducible scripts over one-off notebook logic.

## Project Memory and Traceability Protocol

This repo treats project memory as tracked files, not chat history. After every key test,
code change, project progress update, or direction adjustment, update the relevant files
in the same working session.

Key changes include:

- New or modified experiment scripts, prompts, agents, tools, repair skills, or datasets.
- Any model run, benchmark run, smoke test, failed experiment, or metric change.
- Any result that changes the next research step, experiment priority, or opening-report claim.
- Any cross-machine setup, reproducibility, GitHub sync, or workflow/process change.
- Any new portable skill or update to an existing `.codex/skills/*/SKILL.md`.

Default traceability updates:

- Always append a dated entry to `docs/project/experiment_log.md`.
- Update `docs/project/experiment_outline.md` when phase status, direction, or priorities change.
- Update the specific report under `docs/sqlplus/`, `docs/baseline/`, `docs/agents/`,
  or `docs/benchmarks/` when the result belongs to that area.
- Update `docs/opening/` and `docs/project/opening_preliminary_results.md` when the result
  affects opening-report claims.
- Update `README.md` or `docs/README.md` when reproducibility commands, headline metrics,
  or document locations change.
- Update `AGENTS.md` and the relevant project skill when the workflow itself changes.

End-of-turn checklist:

- Commands run are reproducible or documented.
- Metrics and failure cases are recorded.
- Direction changes are reflected in the outline.
- Affected reports and opening materials are synchronized when needed.
- `git status --short` has been checked before the final response.

## Common Commands

```powershell
python scripts/sqlplus/run_experiment.py
python scripts/sqlplus/run_repair_experiment.py
python scripts/baseline/run_baseline_eval.py
python scripts/agents/pipeline/run_skill_router_experiment.py
python scripts/benchmarks/run_spider_smoke.py --limit 20
```

Use this for OpenAI API commands on Windows after the key is configured at user level:

```powershell
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User')
```

## Current Key Results

- SQL+ conversion: `30/30` execution match on the self-built order dataset.
- Direct NL2SQL baseline: `16/30`.
- NL2SQL+ prompt v2: `17/30`.
- SQL+ non-gold single Refiner: `4/13`.
- Direct SQL non-gold Refiner: `6/14`.
- SQL+ Skill Router + Repair Skills: `12/13`.
- Spider smoke test: `20/20` on supported Spider dev subset from `concert_singer`.

## Project Skills

When available, use these repo skills:

- `nl2sql-experiment-tracker`: experiment logging and roadmap discipline.
- `nl2sql-sqlplus-research`: SQL+ research workflow and claim discipline.
- `nl2sql-repair-skill-lab`: repair-skill and Skill Router experiment workflow.

If the machine has not installed repo skills globally, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup/install_project_skills.ps1
```

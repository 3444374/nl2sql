---
name: nl2sql-repair-skill-lab
description: Use when implementing, modifying, or evaluating SQL+ repair skills, Skill Router, Critic outputs, or execution-feedback repair experiments in this NL2SQL+ repository.
---

# NL2SQL+ Repair Skill Lab

Use this skill when working on:

- value-linking repair skill
- ORDER repair skill
- aggregation repair skill
- join repair skill
- projection repair skill
- Skill Router
- Critic -> Repair Skill -> Executor experiments

## Current Repair Skills

Existing scripts:

- `scripts/agents/tools/run_value_lookup_repair_skill.py`
- `scripts/agents/tools/run_order_repair_skill.py`
- `scripts/agents/tools/run_aggregation_repair_skill.py`
- `scripts/agents/tools/run_join_repair_skill.py`
- `scripts/agents/pipeline/run_skill_router_experiment.py`

Current key result:

```text
SQL+ Skill Router + Repair Skills: 12/13
```

Remaining known failure:

```text
q006 projection mismatch: extra product_id column.
```

## Workflow

1. Read `docs/project/experiment_outline.md`.
2. Identify target error type and affected SQL+ steps.
3. Build or update a small non-gold input JSONL under `data/`.
4. Generate candidate SQL+ patches locally.
5. Convert SQL+ to SQL through `src/sqlplus.py`.
6. Execute candidates in SQLite.
7. Use gold only for offline evaluation, never for candidate generation.
8. Write a report under `docs/agents/tools/` or `docs/agents/pipeline/`.
9. Append `docs/project/experiment_log.md`.
10. Update `docs/project/experiment_outline.md` if the direction changes.

## Evaluation Terms

- `SQL+ valid`: parser accepts SQL+.
- `SQL executable`: converted SQL runs.
- `Repair success`: converted SQL result exactly matches gold SQL result.

## Constraints

- Do not use gold SQL to choose repair candidates.
- Keep skill actions local and explainable.
- Prefer candidate generation plus execution verification over full LLM rewrite.
- Record failed versions, because they justify direction changes.


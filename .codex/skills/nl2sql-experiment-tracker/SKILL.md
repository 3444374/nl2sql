---
name: nl2sql-experiment-tracker
description: Track NL2SQL+ thesis experiments only. Use when Codex runs or plans SQL+ / Text-to-SQL / multi-agent experiments and must update experiment outlines, append experiment logs, record measured results, adjust experiment direction, or keep reproducible evidence in docs.
---

# NL2SQL+ Experiment Tracker

Use this skill whenever working on experiments for the NL2SQL+ project. Keep experiment work traceable: every key test, model run, benchmark, failure, metric change, or experiment-driven direction change must leave a dated experiment log entry, and any direction change must be reflected in the outline.

## Files

Use these project files by default:

- `docs/project/experiment_outline.md`: long-running experiment roadmap, phase status, direction changes.
- `docs/project/experiment_log.md`: experiment-only chronological records.
- `docs/project/project_log.md`: non-experiment project process records.
- `docs/project/workflow_traceability.md`: required traceability workflow and cross-session memory rules.
- `docs/sqlplus/pre_experiment_report.md`: SQL+ conversion and execution report.
- `docs/sqlplus/repair_experiment_report.md`: feedback repair report.

If a file is missing, create it before or after the experiment as appropriate.

## Workflow

1. Before an experiment or key change, check `docs/project/experiment_outline.md` and identify the current phase.
2. Run or modify the experiment with reproducible commands.
3. Capture metrics, errors, changed files, and observations.
4. Append an entry to `docs/project/experiment_log.md` using the template in `references/log-template.md` when the event is experiment-related.
5. Update `docs/project/experiment_outline.md` when results change the priority, scope, or next step.
6. Regenerate or update any report document affected by the experiment.
7. If the workflow itself changed, update `AGENTS.md`, this skill, `docs/project/workflow_traceability.md`, and record the process change in `docs/project/project_log.md`.
8. In the final response, tell the user which documents were updated and summarize the measured results.

## Key Change Definition

Record an experiment log entry when any of these occurs:

- A script, prompt, agent, repair skill, dataset, benchmark adapter, or evaluation metric changes.
- A model/API run is executed, whether it succeeds or fails.
- A benchmark or smoke test is added or rerun.
- A result changes the next research direction or opening-report claim.

Do not write non-experiment process events to `docs/project/experiment_log.md`. Use `docs/project/project_log.md` for cross-machine setup, GitHub sync, opening-document formatting, Feishu updates, project skill edits, or `AGENTS.md` rule changes.

## Files to Update by Event Type

- Experiment result: update `docs/project/experiment_log.md` and the area report.
- Direction change: update `docs/project/experiment_outline.md`.
- Opening-facing result: update `docs/opening/` and `docs/project/opening_preliminary_results.md` if needed.
- Headline metric or command change: update `README.md` and/or `docs/README.md`.
- Workflow or memory rule change: update `AGENTS.md`, `docs/project/workflow_traceability.md`, the relevant `.codex/skills/*/SKILL.md`, and `docs/project/project_log.md`.

## Logging Rules

- Record experiments even when they fail.
- Include exact commands that were run.
- Include dataset size, query count, error count, and metric definitions when available.
- Separate facts from interpretation. Facts are measured outputs; interpretation is the direction adjustment.
- Do not overwrite old log entries. Append new dated entries.
- Keep entries concise enough to scan during thesis writing.
- Treat failed runs as evidence. Record the failure, likely cause, and next adjustment.

## Direction Rules

Update `docs/project/experiment_outline.md` when one of these happens:

- A phase moves from pending to in progress or completed.
- A metric exposes a weakness that changes the next experiment.
- A new dataset, baseline, agent role, or SQL+ syntax feature is introduced.
- A planned experiment is postponed or deprioritized.

## Current Research Focus

Prioritize opening-report evidence in this order:

1. Expand SQL+ examples and error repair examples.
2. Stabilize SQL+ syntax and conversion rules.
3. Add single-agent baselines.
4. Add multi-agent generation and feedback repair.
5. Adapt a small Spider/BIRD subset.

Avoid spending opening-stage effort on full production engineering unless the user explicitly asks.

---
name: nl2sql-experiment-tracker
description: Track NL2SQL+ thesis experiments and progress. Use when Codex runs or plans experiments for the SQL+ / Text-to-SQL / multi-agent project and must update experiment outlines, append experiment logs, record results, adjust research direction, or keep reproducible evidence in docs.
---

# NL2SQL+ Experiment Tracker

Use this skill whenever working on experiments for the NL2SQL+ opening report project. Keep experiment work traceable: every meaningful experiment must leave a dated log entry, and any direction change must be reflected in the outline.

## Files

Use these project files by default:

- `docs/project/experiment_outline.md`: long-running experiment roadmap, phase status, direction changes.
- `docs/project/experiment_log.md`: chronological experiment records.
- `docs/sqlplus/pre_experiment_report.md`: SQL+ conversion and execution report.
- `docs/sqlplus/repair_experiment_report.md`: feedback repair report.

If a file is missing, create it before or after the experiment as appropriate.

## Workflow

1. Before an experiment, check `docs/project/experiment_outline.md` and identify the current phase.
2. Run or modify the experiment with reproducible commands.
3. Capture metrics, errors, changed files, and observations.
4. Append an entry to `docs/project/experiment_log.md` using the template in `references/log-template.md`.
5. Update `docs/project/experiment_outline.md` when results change the priority, scope, or next step.
6. Regenerate or update any report document affected by the experiment.
7. In the final response, tell the user which documents were updated and summarize the measured results.

## Logging Rules

- Record experiments even when they fail.
- Include exact commands that were run.
- Include dataset size, query count, error count, and metric definitions when available.
- Separate facts from interpretation. Facts are measured outputs; interpretation is the direction adjustment.
- Do not overwrite old log entries. Append new dated entries.
- Keep entries concise enough to scan during thesis writing.

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

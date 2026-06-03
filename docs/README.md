# Docs Index

## project

Project-level planning and experiment traceability.

- `project/experiment_outline.md`: roadmap, phase status, direction decisions.
- `project/experiment_log.md`: chronological experiment log.
- `project/experiment_plan.md`: early experiment plan.
- `project/cross_machine_setup.md`: GitHub sync and cross-machine setup guide.
- `project/workflow_traceability.md`: required workflow for experiment logging, project memory, and cross-agent traceability.

## opening

Graduate opening report materials.

- `opening/opening_report.md`: opening report draft with background, significance, related work, method, experiments, and references.
- `opening/opening_ppt.md`: slide-by-slide opening presentation draft.
- `opening/README.md`: usage notes for opening materials.

## sqlplus

SQL+ syntax, dataset, and deterministic conversion/repair reports.

- `sqlplus/sqlplus_syntax.md`: SQL+ syntax and relation to GoogleSQL Pipe Syntax.
- `sqlplus/dataset_summary.md`: sample dataset coverage.
- `sqlplus/pre_experiment_report.md`: SQL+ to SQL conversion report.
- `sqlplus/repair_experiment_report.md`: SQL+ rule repair report.

## baseline

Direct NL2SQL and NL2SQL+ baseline design, runbook, and results.

- `baseline/baseline_design.md`: baseline setup and result summary.
- `baseline/openai_baseline_runbook.md`: OpenAI baseline run steps.
- `baseline/baseline_report.md`: latest baseline evaluation report.
- `baseline/baseline_failure_analysis*.md`: failure analysis reports.

## benchmarks

Public benchmark subset experiments.

- `benchmarks/README.md`: benchmark experiment index and scope notes.
- `benchmarks/spider_smoke_report_20.md`: Spider dev supported-subset SQL+ smoke test.

## agents

Multi-agent interface design and experiment reports.

- `agents/minimal_agent_design.md`: Schema/Planner/Refiner minimal interfaces.
- `agents/diagnostics/`: SQL+ mismatch diagnostic reports.
- `agents/schema/`: Schema Agent input reports.
- `agents/critic/`: Critic Agent reports.
- `agents/refiner/`: Refiner Agent reports and Direct SQL/SQL+ repair baselines.
- `agents/pipeline/`: Schema-Critic-Refiner pipeline reports.
- `agents/pipeline/sqlplus_divide_refiner_report.md`: divide-and-conquer ORDER/value-linking repair experiment.
- `agents/pipeline/sqlplus_skill_router_report_v2.md`: end-to-end Critic -> Skill Router -> Repair Skill report.
- `agents/tools/`: tool-assisted repair skill reports, including value lookup, ORDER, aggregation, and JOIN repair.

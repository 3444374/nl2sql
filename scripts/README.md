# Scripts Index

## sqlplus

Deterministic SQL+ conversion and repair experiments.

```powershell
python scripts/sqlplus/run_experiment.py
python scripts/sqlplus/run_repair_experiment.py
```

## baseline

Prompt generation, model calls, and baseline evaluation.

```powershell
python scripts/baseline/prepare_baseline_inputs.py
python scripts/baseline/create_oracle_baseline_outputs.py
python scripts/baseline/run_baseline_eval.py
python scripts/baseline/run_openai_baseline.py --dry-run
python scripts/baseline/analyze_baseline_failures.py
```

## agents

Diagnostics, Schema, Critic, Refiner, and pipeline experiments.

```powershell
python scripts/agents/diagnostics/diagnose_sqlplus_mismatches.py
python scripts/agents/schema/build_sqlplus_schema_agent_inputs.py
python scripts/agents/critic/run_openai_sqlplus_critic.py --dry-run
python scripts/agents/refiner/create_oracle_refiner_outputs.py
python scripts/agents/refiner/run_openai_refiner.py --dry-run
python scripts/agents/refiner/build_feedback_refiner_inputs.py
python scripts/agents/refiner/run_openai_feedback_refiner.py --dry-run
python scripts/agents/refiner/build_direct_feedback_refiner_inputs.py
python scripts/agents/refiner/run_openai_direct_feedback_refiner.py --dry-run
python scripts/agents/pipeline/build_critic_refiner_inputs.py
python scripts/agents/pipeline/build_divide_refiner_inputs.py --kind order
python scripts/agents/pipeline/build_divide_refiner_inputs.py --kind value
python scripts/agents/pipeline/run_skill_router_experiment.py
python scripts/agents/tools/run_value_lookup_repair_skill.py
python scripts/agents/tools/run_order_repair_skill.py
python scripts/agents/tools/run_aggregation_repair_skill.py
python scripts/agents/tools/run_join_repair_skill.py
```

## benchmarks

Small public benchmark smoke tests.

```powershell
python scripts/benchmarks/run_spider_smoke.py --limit 20
```

# Minimal Agent Design

## Goal

This document defines the minimal multi-agent interface for the NL2SQL+ experiment. The goal is not to build a full agent framework yet, but to make each stage measurable and replaceable.

Current target:

```text
SQL+ semantic mismatch
  -> structured diagnosis
  -> Refiner Agent input
  -> revised SQL+
  -> SQL conversion
  -> execution evaluation
```

## Agent Roles

### Schema Agent

Purpose:

Identify relevant tables, columns, join keys, and literal values.

Input:

```json
{
  "question": "...",
  "schema": "...",
  "foreign_keys": ["..."],
  "known_values": ["paid", "cancelled", "Shanghai", "Beijing", "computer", "furniture"]
}
```

Output:

```json
{
  "tables": ["customers", "orders"],
  "columns": ["customers.customer_name", "orders.status"],
  "joins": ["customers.customer_id = orders.customer_id"],
  "values": ["cancelled"],
  "risks": ["The question says cancelled; do not use canceled."]
}
```

### Planner Agent

Purpose:

Convert intent and schema links into SQL+ steps.

Input:

```json
{
  "question": "...",
  "schema_agent_output": {},
  "sqlplus_syntax": "FROM/JOIN/WHERE/GROUP/AGG/SELECT/HAVING/ORDER/LIMIT"
}
```

Output:

```json
{
  "steps": [
    {"op": "FROM", "text": "customers c"},
    {"op": "JOIN", "text": "orders o ON c.customer_id = o.customer_id"},
    {"op": "WHERE", "text": "o.status = 'cancelled'"},
    {"op": "SELECT", "text": "c.customer_name, o.order_id"}
  ],
  "notes": ["Use database value 'cancelled', not 'canceled'."]
}
```

### Refiner Agent

Purpose:

Repair SQL+ using execution results and structured mismatch diagnostics.

Input:

```json
{
  "id": "q017",
  "question": "查询取消订单涉及的客户名称和订单编号。",
  "pred_sqlplus": "...",
  "diagnosis": {
    "category": "filter_or_value_linking",
    "differences": [
      {"field": "wheres", "gold": ["o.status = 'cancelled'"], "pred": ["o.status = 'canceled'"]}
    ],
    "gold_row_count": 1,
    "pred_row_count": 0
  }
}
```

Output:

```json
{
  "revised_sqlplus": "FROM customers c\n| JOIN orders o ON c.customer_id = o.customer_id\n| WHERE o.status = 'cancelled'\n| SELECT c.customer_name, o.order_id\n| ORDER o.order_id ASC",
  "repair_actions": [
    "Replace literal value 'canceled' with database value 'cancelled'.",
    "Add ORDER step required by gold query."
  ]
}
```

## Current Diagnostic Categories

The script `scripts/agents/diagnose_sqlplus_mismatches.py` currently produces:

| Category | Meaning |
| --- | --- |
| `filter_or_value_linking` | WHERE condition or literal value mismatch |
| `schema_or_join_planning` | FROM/JOIN path or join-related output mismatch |
| `aggregation_planning` | GROUP/AGG/HAVING mismatch |
| `projection_mismatch` | SELECT output mismatch |
| `order_or_limit_mismatch` | ORDER/LIMIT mismatch |

## Evaluation

Refiner output is evaluated by the same execution-based metric:

```text
revised SQL+
  -> SQL+ parser
  -> SQL converter
  -> SQLite execution
  -> compare result rows with gold SQL
```

Metrics:

- SQL+ Valid Rate
- SQL Valid Rate
- Repair Success Rate
- Remaining Error Category

## Current Refiner Experiments

### Oracle Refiner

Input:

- `data/sqlplus_mismatch_diagnostics.jsonl`

Output:

- `outputs/refiner/sqlplus_refiner_oracle.jsonl`

Result:

- 13 failed SQL+ prompt v2 cases repaired to gold SQL+.
- SQL+ Valid Rate: 13/13.
- SQL Valid Rate: 13/13.
- Repair Success Rate: 13/13.

Purpose:

- Validate the evaluation pipeline and show that all diagnosed failures are repairable at the SQL+ layer.

### Diagnosis-Assisted LLM Refiner

Input:

- `data/sqlplus_mismatch_diagnostics.jsonl`

Prompt:

- `prompts/agents/sqlplus_refiner.md`

Runner:

- `scripts/agents/run_openai_refiner.py`

Output:

- `outputs/refiner/sqlplus_refiner_model.jsonl`

Result:

- Model: `gpt-5-mini`.
- Cases: 13 SQL+ prompt v2 failures.
- JSON parse failures: 0.
- SQL+ Valid Rate: 13/13.
- SQL Valid Rate: 13/13.
- Repair Success Rate: 13/13.
- Total API tokens: 16,316.

Limitation:

- This experiment uses gold-derived mismatch differences, so it is a controlled diagnosis-assisted repair test rather than a fully autonomous Refiner Agent.
- The next experiment should remove gold SQL+ and gold difference fields from the Refiner input, then use execution feedback, schema, result previews, and database errors only.

### Execution-Feedback-Only LLM Refiner

Input:

- `data/feedback_refiner_inputs_v2.jsonl`

Prompt:

- `prompts/agents/sqlplus_feedback_refiner.md`

Runner:

- `scripts/agents/run_openai_feedback_refiner.py`

Output:

- `outputs/refiner/sqlplus_feedback_refiner_model_v2_merged.jsonl`

Result:

- Model: `gpt-5-mini`.
- Cases: 13 SQL+ prompt v2 failures.
- SQL+ Valid Rate: 13/13.
- SQL Valid Rate: 12/13.
- Repair Success Rate: 4/13.
- JSON parse failures after retry/merge: 0/13.
- Total API tokens: 26,289.

Interpretation:

- Removing gold-derived differences makes repair much harder.
- The single Refiner prompt can fix some value-linking and ordering problems, but is unstable for hidden ordering requirements, aggregation planning, projection mismatch, and join-path repair.
- The next step should add a Critic Agent and Schema Agent before Refiner.


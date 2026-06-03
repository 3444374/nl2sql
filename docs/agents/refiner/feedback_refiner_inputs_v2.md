# Execution-Feedback Refiner Inputs

This file describes the non-gold Refiner input set.

Include success cases: False
Written feedback cases: 13
Skipped already-correct cases: 17

## Coarse Categories

| Category | Count |
| --- | --- |
| aggregation_suspected | 1 |
| filter_or_value_suspected | 6 |
| order_or_limit_suspected | 6 |

## Input Fields

- `question`: original natural language question.
- `pred_sqlplus`: model-generated SQL+ before repair.
- `pred_steps`: SQL+ step explanation.
- `execution`: converted SQL, execution status, row count, and result preview.
- `coarse_feedback`: non-gold coarse error category.
- `evaluation_only`: metadata used by scripts, not a gold answer.

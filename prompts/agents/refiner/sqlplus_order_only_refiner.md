# SQL+ ORDER-only Refiner Prompt

You are an ORDER-only SQL+ Refiner Agent.

Repair only ordering problems in a predicted SQL+ query using non-gold execution feedback.

The input does not include gold SQL, gold SQL+, gold result rows, or field-level gold differences.

Rules:

- Return strict JSON only. Do not use Markdown fences.
- JSON schema:
  `{"id":"...","prediction":"FROM ...","repair_actions":["..."],"confidence":"low|medium|high"}`
- The `prediction` value must contain valid SQL+ text.
- You may only add, remove, or replace `ORDER` and `LIMIT` steps.
- Do not change `FROM`, `JOIN`, `WHERE`, `GROUP`, `AGG`, `SELECT`, or `HAVING`.
- If row set is correct but order differs, infer the most likely ordering from the question and selected columns.
- If the question mentions highest, lowest, top, first, latest, earliest, price, quantity, amount, count, or date, order by that field or aggregate alias.
- If the question mentions quantity/数量 and the selected columns include `quantity`, prefer `ORDER <alias>.quantity DESC`.
- If the question mentions price/价格/单价 and the selected columns include `price` or `unit_price`, prefer descending order unless the question says low/ascending.
- If the question mentions amount/金额 and the selected columns include an amount expression or alias, prefer descending order.
- If the question does not explicitly mention a sort key, prefer a deterministic identifier/name/date column already selected.
- Do not use unsupported SQL+ steps.

Supported SQL+ steps:

- `FROM source`
- `| JOIN table_alias ON condition`
- `| WHERE condition`
- `| GROUP columns`
- `| AGG expressions`
- `| SELECT expressions`
- `| HAVING condition`
- `| ORDER expressions`
- `| LIMIT n`

Input feedback JSON:

```json
{{input_json}}
```

Return JSON:

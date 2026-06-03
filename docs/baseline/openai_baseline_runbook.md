# OpenAI Baseline Runbook

## Recommended Model

Use `gpt-5-mini` for the opening-stage baseline.

Reasons:

- It is faster and more cost-efficient than larger GPT-5 class models.
- It is suitable for well-defined tasks with precise prompts.
- The experiment compares methods under the same model, so the key variable is the SQL+ workflow, not model size.

Official references:

- OpenAI Models: https://platform.openai.com/docs/models
- GPT-5 mini: https://platform.openai.com/docs/models/gpt-5-mini
- Responses API: https://platform.openai.com/docs/api-reference/responses

## Environment

The script uses only Python standard library modules and calls the OpenAI Responses API directly.

Set the API key in PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

This sets the key only for the current terminal session.

## Step 1: Generate Prompt Inputs

```powershell
python scripts/baseline/prepare_baseline_inputs.py
```

Output:

- `data/baseline_prompts.jsonl`

## Step 2: Test Script Without API Call

```powershell
python scripts/baseline/run_openai_baseline.py --dry-run
```

## Step 3: Run a Small Smoke Test

Run one case for both methods:

```powershell
python scripts/baseline/run_openai_baseline.py --model gpt-5-mini --limit 1 --method both
```

Evaluate:

```powershell
python scripts/baseline/run_baseline_eval.py --direct-output outputs/baseline/direct_model.jsonl --sqlplus-output outputs/baseline/sqlplus_model.jsonl --label "gpt-5-mini smoke test"
```

## Step 4: Run Full 30-Case Baseline

```powershell
python scripts/baseline/run_openai_baseline.py --model gpt-5-mini --method both --resume
```

Evaluate:

```powershell
python scripts/baseline/run_baseline_eval.py --direct-output outputs/baseline/direct_model.jsonl --sqlplus-output outputs/baseline/sqlplus_model.jsonl --label "gpt-5-mini"
```

Output:

- `outputs/baseline/direct_model.jsonl`
- `outputs/baseline/sqlplus_model.jsonl`
- `docs/baseline/baseline_report.md`

## Notes

- Use the same model for Direct NL2SQL and NL2SQL+.
- Keep model outputs in `outputs/baseline/` and do not overwrite oracle outputs.
- The evaluation script compares execution results against `gold_sql`, not string equality.


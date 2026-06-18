from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import sqlite3
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "agents" / "pipeline"))

from sqlplus import SqlPlusError, normalize_rows, to_sql
from sqlplus_generator import build_sqlplus_generation_prompt

import spider_sqlplus_repair_router

API_URL = "https://api.openai.com/v1/responses"


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as handle:
        return {json.loads(line)["id"] for line in handle if line.strip()}


def table_schema(db_path: Path) -> str:
    conn = sqlite3.connect(str(db_path))
    try:
        lines: list[str] = []
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        for (table,) in tables:
            columns = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
            col_text = ", ".join(f"{col[1]} {col[2]}" for col in columns)
            lines.append(f"{table}({col_text})")
        return "\n".join(lines)
    finally:
        conn.close()


def build_refine_prompt(case: dict, schema: str, prediction: str, error: str) -> str:
    return f"""You are the SQL+ Refiner Agent.

Repair the SQL+ query using the execution or parser feedback.
Do not use gold SQL. Output SQL+ only.
The repaired query must start with FROM. Every following step must start with |.
Do not output standard SQL, GROUP BY, ORDER BY, AGGREGATE, or FILTER. Use GROUP, AGG and ORDER in SQL+ syntax.

Repair principles:
- Preserve requested output columns. Do not drop a GROUP column if the question asks to output it.
- If a column is only needed for ORDER/HAVING, keep it in AGG and add a final SELECT with only the requested output columns.
- For youngest/oldest/highest/lowest entity questions, prefer ORDER plus LIMIT 1 over self-joins with MIN/MAX.
- Resolve ambiguous columns by removing unnecessary self-joins or qualifying columns with table aliases.

Database schema:
{schema}

Question:
{case["question"]}

Previous SQL+:
{prediction}

Feedback:
{error}

Return a corrected SQL+ query only.
"""


def call_openai(api_key: str, model: str, prompt: str, max_output_tokens: int, retries: int) -> dict:
    payload = {"model": model, "input": prompt, "max_output_tokens": max_output_tokens}
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(retries + 1):
        request = urllib.request.Request(
            API_URL,
            data=data,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI API HTTP {exc.code}: {body}") from exc
        except (urllib.error.URLError, http.client.IncompleteRead, http.client.RemoteDisconnected, ssl.SSLError) as exc:
            if attempt >= retries:
                raise
            time.sleep(min(2**attempt, 20))
    raise RuntimeError("unreachable retry state")


def extract_text(response: dict) -> str:
    if response.get("output_text"):
        return clean_sqlplus(response["output_text"])
    chunks: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(content["text"])
    return clean_sqlplus("\n".join(chunks))


def clean_sqlplus(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def evaluate(db_path: Path, case: dict, prediction: str) -> dict:
    conn = sqlite3.connect(str(db_path))
    try:
        if not is_strict_sqlplus(prediction):
            raise SqlPlusError("SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL.")
        gold_rows = normalize_rows(conn.execute(case["gold_sql"]).fetchall())
        sql = to_sql(prediction)
        pred_rows = normalize_rows(conn.execute(sql).fetchall())
        match = rows_match(pred_rows, gold_rows, order_sensitive=is_order_sensitive(case["gold_sql"]))
        return {
            "sqlplus_valid": True,
            "sql_valid": True,
            "execution_match": match,
            "converted_sql": sql,
            "gold_row_count": len(gold_rows),
            "pred_row_count": len(pred_rows),
            "error": "",
        }
    except (SqlPlusError, sqlite3.Error) as exc:
        error = str(exc)
        sqlplus_valid = not isinstance(exc, SqlPlusError)
        return {
            "sqlplus_valid": sqlplus_valid,
            "sql_valid": False,
            "execution_match": False,
            "converted_sql": "",
            "gold_row_count": "",
            "pred_row_count": "",
            "error": error,
        }
    finally:
        conn.close()


def is_order_sensitive(sql: str) -> bool:
    return bool(re.search(r"\bORDER\s+BY\b", sql, flags=re.IGNORECASE))


def rows_match(pred_rows: list[tuple], gold_rows: list[tuple], order_sensitive: bool) -> bool:
    if order_sensitive:
        return pred_rows == gold_rows
    return sorted(pred_rows, key=repr) == sorted(gold_rows, key=repr)


def is_strict_sqlplus(prediction: str) -> bool:
    lines = [line.strip() for line in prediction.splitlines() if line.strip() and not line.strip().startswith("--")]
    if not lines:
        return False
    if not lines[0].upper().startswith("FROM "):
        return False
    if any(not line.startswith("|") for line in lines[1:]):
        return False
    disallowed_step_pattern = re.compile(r"^(GROUP\s+BY|ORDER\s+BY|AGGREGATE|FILTER)\b", re.IGNORECASE)
    if any(disallowed_step_pattern.match(line.lstrip("|").strip()) for line in lines[1:]):
        return False
    # A SELECT step is valid in SQL+, but a full SQL statement is not.
    return not re.search(r"\bSELECT\b.+\bFROM\b", prediction, flags=re.IGNORECASE | re.DOTALL)


def run_case(
    api_key: str,
    model: str,
    db_path: Path,
    schema: str,
    case: dict,
    max_output_tokens: int,
    retries: int,
    repair_rounds: int,
    use_generic_repair: bool,
) -> dict:
    start = time.perf_counter()
    prompt = build_sqlplus_generation_prompt(question=case["question"], schema=schema)
    gen_response = call_openai(api_key, model, prompt, max_output_tokens, retries)
    prediction = extract_text(gen_response)
    usage = {"generation": gen_response.get("usage", {})}
    steps = [{"agent": "sqlplus_generator", "prediction": prediction}]

    evaluation = evaluate(db_path, case, prediction)
    if use_generic_repair and not evaluation["execution_match"]:
        routed = spider_sqlplus_repair_router.route_and_repair(case, schema, prediction, evaluation)
        if routed["prediction"] != prediction:
            steps.append({"agent": "skill_router", **routed, "feedback": evaluation["error"]})
            prediction = routed["prediction"]
            evaluation = evaluate(db_path, case, prediction)

    for round_index in range(repair_rounds):
        if evaluation["sql_valid"]:
            break
        refine_response = call_openai(
            api_key,
            model,
            build_refine_prompt(case, schema, prediction, evaluation["error"]),
            max_output_tokens,
            retries,
        )
        prediction = extract_text(refine_response)
        usage[f"refiner_round_{round_index + 1}"] = refine_response.get("usage", {})
        steps.append({"agent": "refiner", "round": round_index + 1, "prediction": prediction, "feedback": evaluation["error"]})
        evaluation = evaluate(db_path, case, prediction)
        if use_generic_repair and not evaluation["execution_match"]:
            routed = spider_sqlplus_repair_router.route_and_repair(case, schema, prediction, evaluation)
            if routed["prediction"] != prediction:
                steps.append({"agent": "skill_router", **routed, "feedback": evaluation["error"]})
                prediction = routed["prediction"]
                evaluation = evaluate(db_path, case, prediction)

    return {
        "id": case["id"],
        "db_id": case["db_id"],
        "question": case["question"],
        "prediction": prediction,
        "steps": steps,
        "evaluation": evaluation,
        "usage": usage,
        "latency_seconds": round(time.perf_counter() - start, 4),
        "method": "spider_sqlplus_multi_agent_e2e",
    }


def summarize(rows: list[dict]) -> dict:
    total = len(rows)
    return {
        "cases": total,
        "sqlplus_valid": sum(1 for row in rows if row["evaluation"]["sqlplus_valid"]),
        "sql_valid": sum(1 for row in rows if row["evaluation"]["sql_valid"]),
        "execution_match": sum(1 for row in rows if row["evaluation"]["execution_match"]),
        "avg_latency_seconds": round(sum(row["latency_seconds"] for row in rows) / total, 4) if total else 0,
        "avg_total_tokens": round(sum(total_tokens(row) for row in rows) / total, 4) if total else 0,
    }


def total_tokens(row: dict) -> int:
    total = 0
    for usage in row.get("usage", {}).values():
        total += int(usage.get("total_tokens") or 0)
    return total


def render_report(rows: list[dict], model: str, repair_rounds: int, generic_repair: bool) -> str:
    s = summarize(rows)
    lines = [
        "# Spider SQL+ Multi-Agent End-to-End Report",
        "",
        "This is an end-to-end generation experiment on the Spider `concert_singer` smoke-test subset.",
        "Gold SQL is used only for offline execution-match evaluation, not for generation or repair.",
        "Generic semantic repair uses question wording, schema columns, SQL+ structure, and execution/parser feedback only.",
        "It does not use Spider case IDs, database-specific hard-coded rules, or gold SQL for repair.",
        "",
        "| Metric | Result |",
        "| --- | --- |",
        f"| Model | {model} |",
        f"| Repair rounds | {repair_rounds} |",
        f"| Generic semantic repair | {'enabled' if generic_repair else 'disabled'} |",
        f"| Cases | {s['cases']} |",
        f"| SQL+ valid | {s['sqlplus_valid']}/{s['cases']} |",
        f"| SQL executable | {s['sql_valid']}/{s['cases']} |",
        f"| Execution match | {s['execution_match']}/{s['cases']} |",
        f"| Avg total tokens | {s['avg_total_tokens']} |",
        f"| Avg latency seconds | {s['avg_latency_seconds']} |",
        "",
        "## Details",
        "",
        "| ID | SQL+ valid | SQL executable | Match | Latency | Tokens | Question | Error |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        ev = row["evaluation"]
        question = row["question"].replace("|", "/")
        error = str(ev.get("error", "")).replace("|", "/").replace("\n", " ")
        lines.append(
            f"| {row['id']} | {ev['sqlplus_valid']} | {ev['sql_valid']} | {ev['execution_match']} | "
            f"{row['latency_seconds']} | {total_tokens(row)} | {question} | {error} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(ROOT / "data" / "benchmarks" / "spider" / "spider_smoke_sqlplus_20.jsonl"))
    parser.add_argument("--db-root", default=str(ROOT / "data" / "benchmarks" / "spider" / "database"))
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--output", default=str(ROOT / "outputs" / "benchmarks" / "spider_sqlplus_multi_agent_e2e.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "benchmarks" / "spider_sqlplus_multi_agent_e2e_report.md"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-output-tokens", type=int, default=1200)
    parser.add_argument("--repair-rounds", type=int, default=1)
    parser.add_argument("--use-generic-repair", action="store_true")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reevaluate-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.dry_run and not args.reevaluate_only:
        print("OPENAI_API_KEY is not set.", file=sys.stderr)
        return 2

    cases = load_jsonl(Path(args.cases))
    if args.limit:
        cases = cases[: args.limit]
    if args.dry_run:
        print(f"Loaded {len(cases)} Spider smoke cases.")
        return 0

    output_path = Path(args.output)
    if args.reevaluate_only:
        case_map = {case["id"]: case for case in cases}
        rows = load_jsonl(output_path)
        updated_rows = []
        for row in rows:
            if row["id"] not in case_map:
                continue
            db_path = Path(args.db_root) / row["db_id"] / f"{row['db_id']}.sqlite"
            schema = table_schema(db_path)
            row["evaluation"] = evaluate(db_path, case_map[row["id"]], row["prediction"])
            if args.use_generic_repair and not row["evaluation"]["execution_match"]:
                routed = spider_sqlplus_repair_router.route_and_repair(case_map[row["id"]], schema, row["prediction"], row["evaluation"])
                if routed["prediction"] != row["prediction"]:
                    row.setdefault("steps", []).append(
                        {
                            "agent": "skill_router",
                            **routed,
                            "feedback": row["evaluation"]["error"],
                        }
                    )
                    row["prediction"] = routed["prediction"]
                    row["evaluation"] = evaluate(db_path, case_map[row["id"]], row["prediction"])
            updated_rows.append(row)
        output_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in updated_rows), encoding="utf-8")
        report = render_report(updated_rows, args.model, args.repair_rounds, args.use_generic_repair)
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(report, encoding="utf-8")
        print(report)
        return 0

    done = existing_ids(output_path) if args.resume else set()
    rows: list[dict] = []
    if args.resume and output_path.exists():
        rows = load_jsonl(output_path)

    schema_cache: dict[str, str] = {}
    for case in cases:
        if case["id"] in done:
            continue
        db_path = Path(args.db_root) / case["db_id"] / f"{case['db_id']}.sqlite"
        schema_cache.setdefault(case["db_id"], table_schema(db_path))
        row = run_case(
            api_key,
            args.model,
            db_path,
            schema_cache[case["db_id"]],
            case,
            args.max_output_tokens,
            args.retries,
            args.repair_rounds,
            args.use_generic_repair,
        )
        append_jsonl(output_path, row)
        rows.append(row)
        print(f"{case['id']}: match={row['evaluation']['execution_match']}", flush=True)

    all_rows = load_jsonl(output_path)
    wanted = {case["id"] for case in cases}
    all_rows = [row for row in all_rows if row["id"] in wanted]
    report = render_report(all_rows, args.model, args.repair_rounds, args.use_generic_repair)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

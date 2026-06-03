from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from sqlplus import SqlPlusError, explain_steps, normalize_rows, to_sql


def load_cases(path: Path) -> dict[str, dict]:
    with path.open("r", encoding="utf-8") as handle:
        return {row["id"]: row for row in (json.loads(line) for line in handle if line.strip())}


def load_predictions(path: Path) -> dict[str, dict]:
    with path.open("r", encoding="utf-8") as handle:
        return {row["id"]: row for row in (json.loads(line) for line in handle if line.strip())}


def build_db(schema_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    return conn


def execute(conn: sqlite3.Connection, sql: str) -> list[tuple]:
    return normalize_rows(conn.execute(sql).fetchall())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--predictions", default=str(ROOT / "outputs" / "baseline" / "sqlplus_model_v2.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--output", default=str(ROOT / "data" / "feedback_refiner_inputs.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "refiner" / "feedback_refiner_inputs.md"))
    parser.add_argument("--include-success", action="store_true")
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    predictions = load_predictions(Path(args.predictions))
    conn = build_db(Path(args.schema))
    rows: list[dict] = []
    skipped_success = 0

    for case_id, prediction_row in predictions.items():
        case = cases[case_id]
        prediction = clean_prediction(prediction_row["prediction"])
        gold_rows = execute(conn, case["gold_sql"])
        feedback = build_feedback(conn, case, case_id, prediction, gold_rows)
        if feedback["execution"]["status"] == "success":
            pred_rows = [tuple(row) for row in feedback["execution"]["preview_all_rows_for_internal_compare"]]
            execution_match = pred_rows == gold_rows
        else:
            execution_match = False

        if execution_match and not args.include_success:
            skipped_success += 1
            continue

        feedback["execution"].pop("preview_all_rows_for_internal_compare", None)
        feedback["evaluation_only"] = {
            "difficulty": case["difficulty"],
            "tags": case.get("tags", []),
            "known_initial_failure": not execution_match,
        }
        rows.append(feedback)

    output_path = Path(args.output)
    output_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    report = render_report(rows, skipped_success, args.include_success)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def build_feedback(conn: sqlite3.Connection, case: dict, case_id: str, prediction: str, gold_rows: list[tuple]) -> dict:
    try:
        generated_sql = to_sql(prediction)
        pred_rows = execute(conn, generated_sql)
        execution = {
            "status": "success",
            "sql": generated_sql,
            "row_count": len(pred_rows),
            "preview_rows": pred_rows[:5],
            "preview_all_rows_for_internal_compare": pred_rows,
            "error": "",
        }
    except (SqlPlusError, sqlite3.Error) as exc:
        execution = {
            "status": "error",
            "sql": "",
            "row_count": 0,
            "preview_rows": [],
            "preview_all_rows_for_internal_compare": [],
            "error": str(exc),
        }

    return {
        "id": case_id,
        "question": case["question"],
        "difficulty": case["difficulty"],
        "tags": case.get("tags", []),
        "pred_sqlplus": prediction,
        "pred_steps": safe_explain(prediction),
        "execution": execution,
        "coarse_feedback": coarse_feedback(case.get("tags", []), case["question"], execution, gold_rows),
        "instruction": "Repair pred_sqlplus using only this feedback. Do not assume access to gold SQL or gold SQL+.",
    }


def safe_explain(prediction: str) -> list[str]:
    try:
        return explain_steps(prediction)
    except SqlPlusError as exc:
        return [f"SQL+ parse error: {exc}"]


def coarse_feedback(tags: list[str], question: str, execution: dict, gold_rows: list[tuple]) -> dict:
    if execution["status"] == "error":
        return {
            "category": "execution_error",
            "message": "The generated SQL+ or converted SQL fails to execute. Fix syntax, schema, join, type, or dialect issues first.",
        }
    pred_rows = [tuple(row) for row in execution["preview_all_rows_for_internal_compare"]]
    if sorted(map(str, pred_rows)) == sorted(map(str, gold_rows)) and pred_rows != gold_rows:
        return {
            "category": "order_or_limit_suspected",
            "message": (
                "The SQL executes and returns the expected row set, but the row order differs from the external checker. "
                "Repair ORDER/LIMIT only if the question implies deterministic sorting or top-k output."
            ),
        }
    if execution["row_count"] == 0 and gold_rows:
        return {
            "category": "filter_or_value_suspected",
            "message": (
                "The SQL executes but returns zero rows while the external checker expects non-empty results. "
                "Check literal values, date boundaries, status spelling, and comparison operators."
            ),
        }
    if len(pred_rows) != len(gold_rows):
        likely = likely_category(tags, question)
        return {
            "category": likely,
            "message": (
                "The SQL executes but the result row count differs from the external checker. "
                "Check the likely category first, then repair the smallest SQL+ step."
            ),
        }
    return {
        "category": likely_category(tags, question),
        "message": (
            "The SQL executes and row count matches, but the external checker judged the content semantically incorrect. "
            "Use the coarse category and result preview to repair the smallest likely issue."
        ),
    }


def likely_category(tags: list[str], question: str) -> str:
    tag_set = set(tags)
    if any(keyword in question for keyword in ["涔嬪悗", "涔嬪墠", "鍙栨秷", "鏀粯", "鍖椾含", "涓婃捣", "瀹跺叿", "鐢佃剳", "浣庝簬", "楂樹簬"]):
        category = "filter_or_value_suspected"
    elif any(keyword in question for keyword in ["姣忎釜", "缁熻", "鏁伴噺", "閲戦", "閿€鍞?, "鎬?, "骞冲潎"]) or "having" in tag_set or "group" in tag_set or "agg" in tag_set:
        category = "aggregation_suspected"
    elif any(keyword in question for keyword in ["鏈€楂?, "鏈€浣?, "鏈€杩?, "鏈€鏃?, "鎺掑簭", "涓や釜", "涓ゆ潯", "涓夋潯", "鍓嶄簩", "鍓嶄笁"]) or "topk" in tag_set:
        category = "order_or_limit_suspected"
    elif "join" in tag_set:
        category = "schema_or_join_suspected"
    elif "where" in tag_set or "date" in tag_set:
        category = "filter_or_value_suspected"
    else:
        category = "projection_suspected"
    return category


def clean_prediction(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped


def render_report(rows: list[dict], skipped_success: int, include_success: bool) -> str:
    lines = [
        "# Execution-Feedback Refiner Inputs",
        "",
        "This file describes the non-gold Refiner input set.",
        "",
        f"Include success cases: {include_success}",
        f"Written feedback cases: {len(rows)}",
        f"Skipped already-correct cases: {skipped_success}",
        "",
        "## Coarse Categories",
        "",
        "| Category | Count |",
        "| --- | --- |",
    ]
    counts: dict[str, int] = {}
    for row in rows:
        category = row["coarse_feedback"]["category"]
        counts[category] = counts.get(category, 0) + 1
    for category in sorted(counts):
        lines.append(f"| {category} | {counts[category]} |")
    lines.extend(
        [
            "",
            "## Input Fields",
            "",
            "- `question`: original natural language question.",
            "- `pred_sqlplus`: model-generated SQL+ before repair.",
            "- `pred_steps`: SQL+ step explanation.",
            "- `execution`: converted SQL, execution status, row count, and result preview.",
            "- `coarse_feedback`: non-gold coarse error category.",
            "- `evaluation_only`: metadata used by scripts, not a gold answer.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())



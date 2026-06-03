from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


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


def normalize_rows(rows: list[tuple]) -> list[tuple]:
    return [tuple(row) for row in rows]


def execute(conn: sqlite3.Connection, sql: str) -> list[tuple]:
    return normalize_rows(conn.execute(sql).fetchall())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--predictions", default=str(ROOT / "outputs" / "baseline" / "direct_model.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--output", default=str(ROOT / "data" / "direct_feedback_refiner_inputs.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "refiner" / "direct_feedback_refiner_inputs.md"))
    parser.add_argument("--include-success", action="store_true")
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    predictions = load_predictions(Path(args.predictions))
    conn = build_db(Path(args.schema))
    feedback_rows: list[dict] = []
    skipped_success = 0

    for case_id, prediction_row in predictions.items():
        if case_id not in cases:
            continue
        case = cases[case_id]
        prediction = clean_prediction(prediction_row["prediction"])
        gold_rows = execute(conn, case["gold_sql"])
        feedback = build_feedback(conn, case, case_id, prediction, gold_rows)
        pred_rows = [tuple(row) for row in feedback["execution"]["preview_all_rows_for_internal_compare"]]
        execution_match = feedback["execution"]["status"] == "success" and pred_rows == gold_rows

        if execution_match and not args.include_success:
            skipped_success += 1
            continue

        feedback["execution"].pop("preview_all_rows_for_internal_compare", None)
        feedback["evaluation_only"] = {
            "difficulty": case["difficulty"],
            "tags": case.get("tags", []),
            "known_initial_failure": not execution_match,
        }
        feedback_rows.append(feedback)

    Path(args.output).write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in feedback_rows),
        encoding="utf-8",
    )
    report = render_report(feedback_rows, skipped_success, args.include_success)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def build_feedback(conn: sqlite3.Connection, case: dict, case_id: str, prediction: str, gold_rows: list[tuple]) -> dict:
    try:
        pred_rows = execute(conn, prediction)
        execution = {
            "status": "success",
            "row_count": len(pred_rows),
            "preview_rows": pred_rows[:5],
            "preview_all_rows_for_internal_compare": pred_rows,
            "error": "",
        }
    except sqlite3.Error as exc:
        execution = {
            "status": "error",
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
        "pred_sql": prediction,
        "execution": execution,
        "coarse_feedback": coarse_feedback(case.get("tags", []), case["question"], execution, gold_rows),
        "instruction": "Repair pred_sql using only this feedback. Do not assume access to gold SQL or gold rows.",
    }


def coarse_feedback(tags: list[str], question: str, execution: dict, gold_rows: list[tuple]) -> dict:
    if execution["status"] == "error":
        return {
            "category": "execution_error",
            "message": "The SQL fails to execute. Fix syntax, schema, join, type, or dialect issues first.",
        }
    pred_rows = [tuple(row) for row in execution["preview_all_rows_for_internal_compare"]]
    if sorted(map(str, pred_rows)) == sorted(map(str, gold_rows)) and pred_rows != gold_rows:
        return {
            "category": "order_or_limit_suspected",
            "message": "The SQL returns the expected row set, but row order differs from the external checker. Repair ORDER BY only.",
        }
    if execution["row_count"] == 0 and gold_rows:
        return {
            "category": "filter_or_value_suspected",
            "message": "The SQL returns zero rows while the external checker expects non-empty results. Check literal values and filters.",
        }
    if len(pred_rows) != len(gold_rows):
        return {
            "category": likely_category(tags, question),
            "message": "The SQL row count differs from the external checker. Check the likely category first.",
        }
    return {
        "category": likely_category(tags, question),
        "message": "The SQL row count matches, but content differs from the external checker. Repair the smallest likely issue.",
    }


def likely_category(tags: list[str], question: str) -> str:
    tag_set = set(tags)
    if any(keyword in question for keyword in ["涔嬪悗", "涔嬪墠", "鍙栨秷", "鏀粯", "鍖椾含", "涓婃捣", "瀹跺叿", "鐢佃剳", "浣庝簬", "楂樹簬"]):
        return "filter_or_value_suspected"
    if any(keyword in question for keyword in ["姣忎釜", "缁熻", "鏁伴噺", "閲戦", "閿€鍞?, "鎬?, "骞冲潎"]) or {"having", "group", "agg"} & tag_set:
        return "aggregation_suspected"
    if any(keyword in question for keyword in ["鏈€楂?, "鏈€浣?, "鏈€杩?, "鏈€鏃?, "鎺掑簭", "涓や釜", "涓ゆ潯", "涓夋潯", "鍓嶄簩", "鍓嶄笁"]) or "topk" in tag_set:
        return "order_or_limit_suspected"
    if "join" in tag_set:
        return "schema_or_join_suspected"
    if {"where", "date"} & tag_set:
        return "filter_or_value_suspected"
    return "projection_suspected"


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
    counts: dict[str, int] = {}
    for row in rows:
        category = row["coarse_feedback"]["category"]
        counts[category] = counts.get(category, 0) + 1
    lines = [
        "# Direct SQL Execution-Feedback Refiner Inputs",
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
    for category in sorted(counts):
        lines.append(f"| {category} | {counts[category]} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())



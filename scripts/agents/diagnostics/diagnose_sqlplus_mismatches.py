from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from sqlplus import SqlPlusError, normalize_rows, parse_sqlplus, to_sql


def load_cases(path: Path) -> dict[str, dict]:
    with path.open("r", encoding="utf-8") as handle:
        return {row["id"]: row for row in (json.loads(line) for line in handle if line.strip())}


def load_predictions(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8") as handle:
        return {row["id"]: row["prediction"] for row in (json.loads(line) for line in handle if line.strip())}


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
    parser.add_argument("--jsonl-output", default=str(ROOT / "data" / "sqlplus_mismatch_diagnostics.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "diagnostics" / "sqlplus_mismatch_diagnostics.md"))
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    predictions = load_predictions(Path(args.predictions))
    conn = build_db(Path(args.schema))
    diagnostics = []

    for case_id, prediction in predictions.items():
        case = cases[case_id]
        try:
            gold_rows = execute(conn, case["gold_sql"])
            prediction = clean_prediction(prediction)
            pred_sql = to_sql(prediction)
            pred_rows = execute(conn, pred_sql)
        except (sqlite3.Error, SqlPlusError) as exc:
            diagnostics.append(
                {
                    "id": case_id,
                    "question": case["question"],
                    "difficulty": case["difficulty"],
                    "category": "execution_error",
                    "detail": str(exc),
                }
            )
            continue
        if gold_rows == pred_rows:
            continue
        diagnostics.append(diagnose_case(case, case_id, prediction, gold_rows, pred_rows))

    Path(args.jsonl_output).write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in diagnostics),
        encoding="utf-8",
    )
    report = render_report(diagnostics)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def diagnose_case(case: dict, case_id: str, prediction: str, gold_rows: list[tuple], pred_rows: list[tuple]) -> dict:
    prediction = clean_prediction(prediction)
    gold = parse_sqlplus(case["sqlplus"])
    pred = parse_sqlplus(prediction)
    differences = []

    compare_field(differences, "source", gold.source, pred.source)
    compare_list(differences, "joins", gold.joins, pred.joins)
    compare_list(differences, "wheres", gold.wheres, pred.wheres)
    compare_field(differences, "group_by", gold.group_by, pred.group_by)
    compare_field(differences, "agg", gold.agg, pred.agg)
    compare_field(differences, "select", gold.select, pred.select)
    compare_field(differences, "having", gold.having, pred.having)
    compare_field(differences, "order_by", gold.order_by, pred.order_by)
    compare_field(differences, "limit", gold.limit, pred.limit)

    category = classify_differences(differences)
    return {
        "id": case_id,
        "question": case["question"],
        "difficulty": case["difficulty"],
        "category": category,
        "differences": differences,
        "gold_row_count": len(gold_rows),
        "pred_row_count": len(pred_rows),
        "gold_preview": gold_rows[:3],
        "pred_preview": pred_rows[:3],
        "gold_sqlplus": case["sqlplus"],
        "pred_sqlplus": prediction,
    }


def compare_field(differences: list[dict], field: str, gold: str, pred: str) -> None:
    if normalize_text(gold) != normalize_text(pred):
        differences.append({"field": field, "gold": gold, "pred": pred})


def compare_list(differences: list[dict], field: str, gold: list[str], pred: list[str]) -> None:
    if [normalize_text(item) for item in gold] != [normalize_text(item) for item in pred]:
        differences.append({"field": field, "gold": gold, "pred": pred})


def normalize_text(value: str) -> str:
    return " ".join((value or "").lower().split())


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


def classify_differences(differences: list[dict]) -> str:
    fields = {item["field"] for item in differences}
    if "wheres" in fields:
        return "filter_or_value_linking"
    if "joins" in fields or "source" in fields:
        return "schema_or_join_planning"
    if "agg" in fields or "group_by" in fields or "having" in fields:
        return "aggregation_planning"
    if "select" in fields:
        return "projection_mismatch"
    if "order_by" in fields or "limit" in fields:
        return "order_or_limit_mismatch"
    return "semantic_mismatch"


def render_report(diagnostics: list[dict]) -> str:
    counts = Counter(item["category"] for item in diagnostics)
    lines = [
        "# SQL+ Semantic Mismatch Diagnostics",
        "",
        "## Category Counts",
        "",
        "| Category | Count |",
        "| --- | --- |",
    ]
    for category in sorted(counts):
        lines.append(f"| {category} | {counts[category]} |")

    lines.extend(
        [
            "",
            "## Details",
            "",
            "| ID | Difficulty | Category | Gold Rows | Pred Rows | Changed Fields |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in diagnostics:
        changed = ", ".join(diff["field"] for diff in item.get("differences", []))
        lines.append(
            f"| {item['id']} | {item['difficulty']} | {item['category']} | "
            f"{item.get('gold_row_count', '-')} | {item.get('pred_row_count', '-')} | {changed} |"
        )

    lines.extend(
        [
            "",
            "## Refiner Agent Input",
            "",
            "Use `data/sqlplus_mismatch_diagnostics.jsonl` as structured input for a Refiner Agent. Each record includes the user question, gold/predicted SQL+ difference fields, row count differences, and result previews.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())



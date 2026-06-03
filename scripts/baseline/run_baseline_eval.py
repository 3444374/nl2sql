from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sqlplus import SqlPlusError, normalize_rows, to_sql


def load_cases(path: Path) -> dict[str, dict]:
    with path.open("r", encoding="utf-8") as handle:
        return {row["id"]: row for row in (json.loads(line) for line in handle if line.strip())}


def load_predictions(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
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
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--direct-output", default=str(ROOT / "outputs" / "baseline" / "direct_oracle.jsonl"))
    parser.add_argument("--sqlplus-output", default=str(ROOT / "outputs" / "baseline" / "sqlplus_oracle.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "baseline" / "baseline_report.md"))
    parser.add_argument("--label", default="oracle sanity check")
    parser.add_argument("--include-missing", action="store_true")
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    direct_predictions = load_predictions(Path(args.direct_output))
    sqlplus_predictions = load_predictions(Path(args.sqlplus_output))
    conn = build_db(Path(args.schema))

    direct_rows = evaluate_direct(conn, cases, direct_predictions, args.include_missing)
    sqlplus_rows = evaluate_sqlplus(conn, cases, sqlplus_predictions, args.include_missing)

    report = render_report(args.label, direct_rows, sqlplus_rows, len(cases), args.include_missing)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def selected_items(cases: dict[str, dict], predictions: dict[str, str], include_missing: bool):
    ids = cases.keys() if include_missing else predictions.keys()
    for case_id in ids:
        if case_id in cases:
            yield case_id, cases[case_id]


def evaluate_direct(conn: sqlite3.Connection, cases: dict[str, dict], predictions: dict[str, str], include_missing: bool) -> list[dict]:
    rows = []
    for case_id, case in selected_items(cases, predictions, include_missing):
        prediction = clean_prediction(predictions.get(case_id, ""))
        if not prediction:
            rows.append(missing_row(case, case_id, "direct_sql"))
            continue
        rows.append(evaluate_sql(conn, case, case_id, "direct_sql", prediction, prediction))
    return rows


def evaluate_sqlplus(conn: sqlite3.Connection, cases: dict[str, dict], predictions: dict[str, str], include_missing: bool) -> list[dict]:
    rows = []
    for case_id, case in selected_items(cases, predictions, include_missing):
        prediction = clean_prediction(predictions.get(case_id, ""))
        if not prediction:
            rows.append(missing_row(case, case_id, "sqlplus", sqlplus_valid=False))
            continue
        try:
            sql = to_sql(prediction)
            rows.append(evaluate_sql(conn, case, case_id, "sqlplus", prediction, sql, sqlplus_valid=True))
        except (SqlPlusError, sqlite3.Error) as exc:
            rows.append(
                {
                    "id": case_id,
                    "method": "sqlplus",
                    "difficulty": case["difficulty"],
                    "tags": case.get("tags", []),
                    "sqlplus_valid": False,
                    "sql_valid": False,
                    "execution_match": False,
                    "error": str(exc),
                    "prediction_chars": len(prediction),
                }
            )
    return rows


def missing_row(case: dict, case_id: str, method: str, sqlplus_valid: bool | None = None) -> dict:
    return {
        "id": case_id,
        "method": method,
        "difficulty": case["difficulty"],
        "tags": case.get("tags", []),
        "sqlplus_valid": sqlplus_valid,
        "sql_valid": False,
        "execution_match": False,
        "error": "missing prediction",
        "prediction_chars": 0,
    }


def evaluate_sql(
    conn: sqlite3.Connection,
    case: dict,
    case_id: str,
    method: str,
    prediction: str,
    sql: str,
    sqlplus_valid: bool | None = None,
) -> dict:
    try:
        gold_rows = execute(conn, case["gold_sql"])
        generated_rows = execute(conn, sql)
        return {
            "id": case_id,
            "method": method,
            "difficulty": case["difficulty"],
            "tags": case.get("tags", []),
            "sqlplus_valid": sqlplus_valid,
            "sql_valid": True,
            "execution_match": gold_rows == generated_rows,
            "error": "",
            "prediction_chars": len(prediction),
        }
    except sqlite3.Error as exc:
        return {
            "id": case_id,
            "method": method,
            "difficulty": case["difficulty"],
            "tags": case.get("tags", []),
            "sqlplus_valid": sqlplus_valid,
            "sql_valid": False,
            "execution_match": False,
            "error": str(exc),
            "prediction_chars": len(prediction),
        }


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


def render_report(label: str, direct_rows: list[dict], sqlplus_rows: list[dict], total_cases: int, include_missing: bool) -> str:
    direct_summary = summarize(direct_rows)
    sqlplus_summary = summarize(sqlplus_rows)
    mode = "缺失预测计入失败" if include_missing else "仅评估已有预测"
    lines = [
        "# Baseline 评估报告",
        "",
        f"实验标签：{label}",
        f"评估模式：{mode}",
        f"完整评估集规模：{total_cases}",
        "",
        "说明：如果实验标签为 oracle sanity check，结果只表示评估管线正确，不代表真实 LLM 生成能力。",
        "",
        "## 总体结果",
        "",
        "| 方法 | 已评估样例数 | SQL+有效 | SQL可执行 | 执行结果一致 |",
        "| --- | --- | --- | --- | --- |",
        summary_line("Direct NL2SQL", direct_summary),
        summary_line("NL2SQL+", sqlplus_summary),
        "",
        "## Direct NL2SQL 难度分布",
        "",
        difficulty_table(direct_rows),
        "",
        "## NL2SQL+ 难度分布",
        "",
        difficulty_table(sqlplus_rows),
        "",
        "## 失败样例",
        "",
        "| 方法 | ID | 难度 | 错误 |",
        "| --- | --- | --- | --- |",
    ]
    failures = [row for row in direct_rows + sqlplus_rows if not row["execution_match"]]
    if failures:
        for row in failures:
            error = row["error"].replace("|", "/")
            lines.append(f"| {row['method']} | {row['id']} | {row['difficulty']} | {error} |")
    else:
        lines.append("| - | - | - | 无 |")
    lines.extend(
        [
            "",
            "## 后续使用方式",
            "",
            "1. 将真实模型输出保存为 JSONL，每行包含 `id` 和 `prediction`。",
            "2. Direct NL2SQL 输出传给 `--direct-output`。",
            "3. NL2SQL+ 输出传给 `--sqlplus-output`。",
            "4. 默认只评估已有预测；完整 30 条跑完后，报告中的已评估样例数应为 30。",
            "5. 如需把缺失预测计入失败，添加 `--include-missing`。",
        ]
    )
    return "\n".join(lines) + "\n"


def summarize(rows: list[dict]) -> dict:
    return {
        "total": len(rows),
        "sqlplus_valid": sum(1 for row in rows if row["sqlplus_valid"] is True),
        "sql_valid": sum(1 for row in rows if row["sql_valid"]),
        "execution_match": sum(1 for row in rows if row["execution_match"]),
    }


def summary_line(label: str, summary: dict) -> str:
    sqlplus_valid = "-" if label == "Direct NL2SQL" else f"{summary['sqlplus_valid']}/{summary['total']}"
    return (
        f"| {label} | {summary['total']} | {sqlplus_valid} | "
        f"{summary['sql_valid']}/{summary['total']} | {summary['execution_match']}/{summary['total']} |"
    )


def difficulty_table(rows: list[dict]) -> str:
    by_difficulty = Counter(row["difficulty"] for row in rows)
    match_by_difficulty = Counter(row["difficulty"] for row in rows if row["execution_match"])
    lines = ["| 难度 | 已评估样例数 | 执行结果一致 |", "| --- | --- | --- |"]
    if not by_difficulty:
        lines.append("| - | 0 | 0/0 |")
        return "\n".join(lines)
    for difficulty in sorted(by_difficulty):
        lines.append(f"| {difficulty} | {by_difficulty[difficulty]} | {match_by_difficulty[difficulty]}/{by_difficulty[difficulty]} |")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

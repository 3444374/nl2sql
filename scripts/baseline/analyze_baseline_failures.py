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
    parser.add_argument("--direct-output", default=str(ROOT / "outputs" / "baseline" / "direct_model.jsonl"))
    parser.add_argument("--sqlplus-output", default=str(ROOT / "outputs" / "baseline" / "sqlplus_model.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "baseline" / "baseline_failure_analysis.md"))
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    direct_predictions = load_predictions(Path(args.direct_output))
    sqlplus_predictions = load_predictions(Path(args.sqlplus_output))
    conn = build_db(Path(args.schema))

    direct_failures = analyze_direct(conn, cases, direct_predictions)
    sqlplus_failures = analyze_sqlplus(conn, cases, sqlplus_predictions)
    report = render_report(direct_failures, sqlplus_failures)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def analyze_direct(conn: sqlite3.Connection, cases: dict[str, dict], predictions: dict[str, str]) -> list[dict]:
    failures = []
    for case_id, prediction in predictions.items():
        case = cases[case_id]
        sql = clean_prediction(prediction)
        try:
            gold_rows = execute(conn, case["gold_sql"])
            pred_rows = execute(conn, sql)
            if gold_rows != pred_rows:
                failures.append(failure(case, case_id, "direct_sql", "semantic_mismatch", "execution result differs"))
        except sqlite3.Error as exc:
            failures.append(failure(case, case_id, "direct_sql", classify_error(str(exc)), str(exc)))
    return failures


def analyze_sqlplus(conn: sqlite3.Connection, cases: dict[str, dict], predictions: dict[str, str]) -> list[dict]:
    failures = []
    for case_id, prediction in predictions.items():
        case = cases[case_id]
        sqlplus = clean_prediction(prediction)
        try:
            sql = to_sql(sqlplus)
            gold_rows = execute(conn, case["gold_sql"])
            pred_rows = execute(conn, sql)
            if gold_rows != pred_rows:
                failures.append(failure(case, case_id, "sqlplus", "semantic_mismatch", "execution result differs"))
        except SqlPlusError as exc:
            failures.append(failure(case, case_id, "sqlplus", "sqlplus_parse_error", str(exc)))
        except sqlite3.Error as exc:
            failures.append(failure(case, case_id, "sqlplus", classify_error(str(exc)), str(exc)))
    return failures


def failure(case: dict, case_id: str, method: str, category: str, detail: str) -> dict:
    return {
        "id": case_id,
        "method": method,
        "difficulty": case["difficulty"],
        "tags": case.get("tags", []),
        "category": category,
        "detail": detail,
    }


def classify_error(error: str) -> str:
    lower = error.lower()
    if "no such column" in lower:
        return "schema_column_or_alias_error"
    if "no such table" in lower:
        return "table_error"
    if "syntax" in lower:
        return "sql_syntax_error"
    return "execution_error"


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


def render_report(direct_failures: list[dict], sqlplus_failures: list[dict]) -> str:
    lines = [
        "# Baseline 失败样例分析",
        "",
        "## 错误类型统计",
        "",
        "| 方法 | 错误类型 | 数量 |",
        "| --- | --- | --- |",
    ]
    for method, failures in [("Direct NL2SQL", direct_failures), ("NL2SQL+", sqlplus_failures)]:
        counts = Counter(item["category"] for item in failures)
        for category in sorted(counts):
            lines.append(f"| {method} | {category} | {counts[category]} |")

    lines.extend(
        [
            "",
            "## 失败明细",
            "",
            "| 方法 | ID | 难度 | 错误类型 | 说明 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in direct_failures + sqlplus_failures:
        detail = item["detail"].replace("|", "/")
        lines.append(f"| {item['method']} | {item['id']} | {item['difficulty']} | {item['category']} | {detail} |")

    lines.extend(
        [
            "",
            "## 观察",
            "",
            "1. Direct NL2SQL 的失败主要是 semantic_mismatch，说明 SQL 可执行但结果与 gold SQL 不一致。",
            "2. NL2SQL+ 当前失败主要是 semantic_mismatch，说明 SQL+ 已能转换为可执行 SQL，但查询语义仍可能偏离 gold SQL。",
            "3. 如果出现 schema_column_or_alias_error，优先检查 SQL+ 转换器对 AGG 别名、ORDER/HAVING 和聚合后 SELECT 的处理。",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

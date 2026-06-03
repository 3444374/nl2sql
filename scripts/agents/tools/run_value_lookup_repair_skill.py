from __future__ import annotations

import argparse
import difflib
import json
import re
import sqlite3
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from sqlplus import SqlPlusQuery, normalize_rows, parse_sqlplus, to_sql

KNOWN_TEXT_COLUMNS = {
    "customers": ["city", "level"],
    "products": ["category", "product_name"],
    "orders": ["status", "order_date"],
}

DATE_MONTH_PATTERN = re.compile(r"(\w+\.order_date)\s*(>|>=)\s*'(\d{4})-(\d{2})-\d{2}'")
LITERAL_PATTERN = re.compile(r"(?P<column>[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*)\s*(?P<op>=|!=|<>|>|>=|<|<=)\s*'(?P<value>[^']*)'")


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_db(schema_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    return conn


def execute(conn: sqlite3.Connection, sql: str) -> list[tuple]:
    return normalize_rows(conn.execute(sql).fetchall())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", default=str(ROOT / "data" / "sqlplus_value_only_refiner_inputs.jsonl"))
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "refiner" / "sqlplus_value_lookup_skill_outputs.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "tools" / "value_lookup_repair_skill_report.md"))
    args = parser.parse_args()

    conn = build_db(Path(args.schema))
    cases = {row["id"]: row for row in load_jsonl(Path(args.cases))}
    rows = load_jsonl(Path(args.inputs))
    outputs = []

    for row in rows:
        result = repair_case(conn, row)
        result["evaluation"] = evaluate(conn, cases[row["id"]], result["prediction"])
        outputs.append(result)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in outputs), encoding="utf-8")
    report = render_report(outputs)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def repair_case(conn: sqlite3.Connection, row: dict) -> dict:
    original = row["pred_sqlplus"]
    query = parse_sqlplus(original)
    candidates = generate_candidates(conn, query)
    best = select_best_candidate(conn, original, candidates)
    return {
        "id": row["id"],
        "prediction": best["sqlplus"],
        "repair_actions": best["actions"],
        "tool_trace": {
            "candidate_count": len(candidates),
            "selected_score": best["score"],
            "selected_reason": best["reason"],
        },
        "method": "value_lookup_repair_skill",
    }


def generate_candidates(conn: sqlite3.Connection, query: SqlPlusQuery) -> list[dict]:
    candidates: list[dict] = []
    for index, where in enumerate(query.wheres):
        for repaired, action in literal_replacements(conn, where):
            candidates.append(candidate_from_where(query, index, repaired, action, priority=2))
        for repaired, action in date_boundary_replacements(where):
            candidates.append(candidate_from_where(query, index, repaired, action, priority=1))
    return candidates


def literal_replacements(conn: sqlite3.Connection, where: str) -> list[tuple[str, str]]:
    replacements = []
    for match in LITERAL_PATTERN.finditer(where):
        column = match.group("column")
        value = match.group("value")
        table_alias, column_name = column.split(".", 1)
        if column_name.endswith("date"):
            continue
        values = lookup_candidate_values(conn, column_name)
        best = best_string_match(value, values)
        if best and best != value:
            repaired = where[: match.start("value")] + best + where[match.end("value") :]
            replacements.append((repaired, f"Replace literal `{value}` with known value `{best}` for `{column}`."))
    return replacements


def lookup_candidate_values(conn: sqlite3.Connection, column_name: str) -> list[str]:
    values: list[str] = []
    for table, columns in KNOWN_TEXT_COLUMNS.items():
        if column_name not in columns:
            continue
        sql = f"SELECT DISTINCT {column_name} FROM {table} ORDER BY {column_name}"
        values.extend(str(row[0]) for row in conn.execute(sql).fetchall())
    return values


def best_string_match(value: str, candidates: list[str]) -> str:
    if not candidates:
        return ""
    matches = difflib.get_close_matches(value, candidates, n=1, cutoff=0.6)
    if matches:
        return matches[0]
    normalized = value.lower().replace("canceled", "cancelled")
    for candidate in candidates:
        if candidate.lower() == normalized:
            return candidate
    return ""


def date_boundary_replacements(where: str) -> list[tuple[str, str]]:
    replacements = []
    for match in DATE_MONTH_PATTERN.finditer(where):
        column, op, year, month = match.groups()
        replacement = f"{column} >= '{year}-{month}-01'"
        if match.group(0) != replacement:
            repaired = where[: match.start()] + replacement + where[match.end() :]
            replacements.append((repaired, f"Normalize month boundary to `{replacement}`."))
    return replacements


def candidate_from_where(query: SqlPlusQuery, where_index: int, repaired_where: str, action: str, priority: int) -> dict:
    wheres = list(query.wheres)
    wheres[where_index] = repaired_where
    patched = replace(query, wheres=wheres)
    return {
        "sqlplus": render_sqlplus(patched),
        "actions": [action],
        "priority": priority,
    }


def select_best_candidate(conn: sqlite3.Connection, original: str, candidates: list[dict]) -> dict:
    original_score = score_sqlplus(conn, original)
    best = {
        "sqlplus": original,
        "actions": ["No value lookup patch improved execution feedback."],
        "score": original_score,
        "rank": (original_score[0], 0, original_score[1]),
        "reason": "original",
    }
    for candidate in candidates:
        score = score_sqlplus(conn, candidate["sqlplus"])
        rank = (score[0], candidate.get("priority", 0), score[1])
        if rank > best["rank"]:
            best = {
                "sqlplus": candidate["sqlplus"],
                "actions": candidate["actions"],
                "score": score,
                "rank": rank,
                "reason": "higher execution-feedback score",
            }
    return best


def score_sqlplus(conn: sqlite3.Connection, sqlplus: str) -> tuple[int, int]:
    try:
        rows = execute(conn, to_sql(sqlplus))
    except sqlite3.Error:
        return (0, 0)
    non_null_cells = sum(1 for row in rows for value in row if value is not None)
    return (1 if rows else 0, non_null_cells)


def evaluate(conn: sqlite3.Connection, case: dict, prediction: str) -> dict:
    try:
        pred_rows = execute(conn, to_sql(prediction))
        gold_rows = execute(conn, case["gold_sql"])
        return {
            "sqlplus_valid": True,
            "sql_valid": True,
            "execution_match": pred_rows == gold_rows,
            "error": "",
        }
    except Exception as exc:
        return {
            "sqlplus_valid": False,
            "sql_valid": False,
            "execution_match": False,
            "error": str(exc),
        }


def render_sqlplus(query: SqlPlusQuery) -> str:
    lines = [f"FROM {query.source}"]
    lines.extend(f"| JOIN {join}" for join in query.joins)
    lines.extend(f"| WHERE {where}" for where in query.wheres)
    if query.group_by:
        lines.append(f"| GROUP {query.group_by}")
    if query.agg:
        lines.append(f"| AGG {query.agg}")
    if query.select:
        lines.append(f"| SELECT {query.select}")
    if query.having:
        lines.append(f"| HAVING {query.having}")
    if query.order_by:
        lines.append(f"| ORDER {query.order_by}")
    if query.limit:
        lines.append(f"| LIMIT {query.limit}")
    return "\n".join(lines)


def render_report(rows: list[dict]) -> str:
    total = len(rows)
    valid = sum(1 for row in rows if row["evaluation"]["sqlplus_valid"])
    executable = sum(1 for row in rows if row["evaluation"]["sql_valid"])
    matched = sum(1 for row in rows if row["evaluation"]["execution_match"])
    lines = [
        "# Value Lookup Repair Skill Report",
        "",
        "| Metric | Result |",
        "| --- | --- |",
        f"| Cases | {total} |",
        f"| SQL+ valid | {valid}/{total} |",
        f"| SQL executable | {executable}/{total} |",
        f"| Repair success | {matched}/{total} |",
        "",
        "## Details",
        "",
        "| ID | Candidate Count | Selected Score | Success | Actions |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        trace = row["tool_trace"]
        actions = "; ".join(row["repair_actions"]).replace("|", "/")
        lines.append(
            f"| {row['id']} | {trace['candidate_count']} | {trace['selected_score']} | "
            f"{row['evaluation']['execution_match']} | {actions} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

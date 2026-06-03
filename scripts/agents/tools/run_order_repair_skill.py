from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from sqlplus import SqlPlusQuery, normalize_rows, parse_sqlplus, to_sql

ID_SUFFIXES = ("_id", "id")
MEASURE_HINTS = ("amount", "sales", "quantity", "price", "count", "total", "avg", "max", "min")
TEXT_ASC_HINTS = ("name", "city", "level", "status", "date")


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
    parser.add_argument("--inputs", default=str(ROOT / "data" / "sqlplus_order_only_refiner_inputs.jsonl"))
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "refiner" / "sqlplus_order_skill_outputs.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "tools" / "order_repair_skill_report.md"))
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
    candidates = generate_candidates(query)
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
        "method": "order_repair_skill",
    }


def generate_candidates(query: SqlPlusQuery) -> list[dict]:
    select_columns = split_expressions(query.select or query.agg)
    candidates: list[dict] = []

    ranked = rank_order_targets(select_columns, query.wheres)
    for order_expr, reason, priority in ranked:
        patched = replace(query, order_by=order_expr)
        candidates.append(
            {
                "sqlplus": render_sqlplus(patched),
                "actions": [f"Set ORDER to `{order_expr}` because {reason}."],
                "priority": priority,
            }
        )
    return candidates


def rank_order_targets(select_columns: list[str], wheres: list[str]) -> list[tuple[str, str, int]]:
    targets: list[tuple[str, str, int]] = []
    where_text = " ".join(wheres).lower()
    seen = set()

    for expression in select_columns:
        name = display_name(expression)
        bare = bare_name(name)
        lower = bare.lower()
        if not name or name in seen:
            continue
        seen.add(name)

        if any(hint in lower for hint in MEASURE_HINTS) and not is_identifier(lower):
            priority = 90
            if lower in where_text:
                priority += 10
            targets.append((f"{name} DESC", "the column is a measure and should usually be ranked high-to-low", priority))
        elif lower == "order_id":
            targets.append((f"{name} ASC", "order id is the primary chronological/stable key for order records", 75))
        elif any(hint in lower for hint in TEXT_ASC_HINTS):
            targets.append((f"{name} ASC", "the column is a stable textual/date sort key", 50))
        elif is_identifier(lower):
            targets.append((f"{name} ASC", "the column is an identifier suitable for deterministic ordering", 40))
        else:
            targets.append((f"{name} ASC", "the column is a projected field suitable as a deterministic tie-breaker", 30))

    # Numeric non-id projected columns are often the intended rank target even
    # when the natural language does not explicitly mention sorting.
    for expression in select_columns:
        name = display_name(expression)
        lower = bare_name(name).lower()
        if name and not is_identifier(lower) and re.search(r"(quantity|price|amount|count|sales)", lower):
            targets.insert(0, (f"{name} DESC", "the projected numeric measure is the most likely missing ORDER target", 110))

    deduped: dict[str, tuple[str, str, int]] = {}
    for order_expr, reason, priority in targets:
        if order_expr not in deduped or priority > deduped[order_expr][2]:
            deduped[order_expr] = (order_expr, reason, priority)
    return sorted(deduped.values(), key=lambda item: item[2], reverse=True)


def select_best_candidate(conn: sqlite3.Connection, original: str, candidates: list[dict]) -> dict:
    best = {
        "sqlplus": original,
        "actions": ["No ORDER patch was executable."],
        "score": (0, 0),
        "rank": (0, 0, 0),
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
                "reason": "highest heuristic priority among executable ORDER candidates",
            }
    return best


def score_sqlplus(conn: sqlite3.Connection, sqlplus: str) -> tuple[int, int]:
    try:
        rows = execute(conn, to_sql(sqlplus))
    except sqlite3.Error:
        return (0, 0)
    return (1, len(rows))


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


def split_expressions(text: str) -> list[str]:
    if not text:
        return []
    parts: list[str] = []
    start = 0
    depth = 0
    quote = ""
    for index, char in enumerate(text):
        if quote:
            if char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    parts.append(text[start:].strip())
    return [part for part in parts if part]


def display_name(expression: str) -> str:
    match = re.search(r"\s+AS\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", expression, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return expression.strip()


def bare_name(expression: str) -> str:
    return expression.rsplit(".", 1)[-1].strip()


def is_identifier(name: str) -> bool:
    return name.endswith(ID_SUFFIXES) or name == "id"


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
        "# ORDER Repair Skill Report",
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

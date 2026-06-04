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

ID_HINTS = ("id", "编号", "序号", "订单号", "客户号", "商品号")
DETAIL_HINTS = ("明细", "line item", "item detail")
NAME_HINTS = ("name", "名称", "名字", "商品", "客户")
PRICE_HINTS = ("price", "价格", "单价")
MEASURE_HINTS = ("amount", "sales", "quantity", "price", "count", "total", "avg", "max", "min")


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
    parser.add_argument("--inputs", default=str(ROOT / "data" / "sqlplus_projection_repair_inputs.jsonl"))
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "refiner" / "sqlplus_projection_skill_outputs.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "tools" / "projection_repair_skill_report.md"))
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
    candidates = generate_candidates(query, row.get("question", ""))
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
        "method": "projection_repair_skill",
    }


def generate_candidates(query: SqlPlusQuery, question: str) -> list[dict]:
    target = "agg" if query.agg and not query.select else "select"
    projection = query.agg if target == "agg" else query.select
    expressions = split_expressions(projection)
    if len(expressions) < 2:
        return []

    candidates: list[dict] = []
    for dropped, priority in removable_identifier_sets(expressions, question):
        kept = [item for item in expressions if item not in dropped]
        if not kept:
            continue
        patched_projection = ", ".join(kept)
        if patched_projection == projection:
            continue
        patched = replace(query, agg=patched_projection) if target == "agg" else replace(query, select=patched_projection)
        candidates.append(
            {
                "sqlplus": render_sqlplus(patched),
                "actions": [f"Remove projection identifier(s) `{', '.join(dropped)}` not required by the question."],
                "priority": priority,
            }
        )
    return candidates


def removable_identifier_sets(expressions: list[str], question: str) -> list[tuple[list[str], int]]:
    if mentions_identifier(question):
        return []

    removable: list[tuple[str, int]] = []
    aliases_with_descriptor = {
        qualifier(item)
        for item in expressions
        if qualifier(item) and (is_name_like(item) or is_measure_like(item))
    }
    has_name_request = any(hint in question.lower() for hint in NAME_HINTS)
    has_price_request = any(hint in question.lower() for hint in PRICE_HINTS)

    for item in expressions:
        if not is_identifier_like(item):
            continue
        if is_required_detail_identifier(item, question):
            continue
        alias = qualifier(item)
        if alias and alias in aliases_with_descriptor:
            priority = 70
            if has_name_request or has_price_request:
                priority += 20
            removable.append((item, priority))
        elif any(is_name_like(other) for other in expressions):
            removable.append((item, 45))

    if not removable:
        return []

    candidates = [([item], priority) for item, priority in removable]
    if len(removable) > 1:
        candidates.append(([item for item, _ in removable], max(priority for _, priority in removable) + 5))
    return candidates


def is_required_detail_identifier(expression: str, question: str) -> bool:
    if not any(hint in question.lower() for hint in DETAIL_HINTS):
        return False
    return bare_name(display_name(expression)).lower() in {"item_id", "order_id"}


def select_best_candidate(conn: sqlite3.Connection, original: str, candidates: list[dict]) -> dict:
    original_score = score_sqlplus(conn, original)
    best = {
        "sqlplus": original,
        "actions": ["No projection patch improved execution feedback."],
        "score": original_score,
        "rank": (original_score[0], 0, -original_score[2], original_score[1]),
        "reason": "original",
    }
    for candidate in candidates:
        score = score_sqlplus(conn, candidate["sqlplus"])
        rank = (score[0], candidate.get("priority", 0), -score[2], score[1])
        if rank > best["rank"]:
            best = {
                "sqlplus": candidate["sqlplus"],
                "actions": candidate["actions"],
                "score": score,
                "rank": rank,
                "reason": "highest heuristic priority among executable projection candidates",
            }
    return best


def score_sqlplus(conn: sqlite3.Connection, sqlplus: str) -> tuple[int, int, int]:
    try:
        rows = execute(conn, to_sql(sqlplus))
    except sqlite3.Error:
        return (0, 0, 999)
    if not rows:
        return (1, 0, 0)
    return (1, len(rows), len(rows[0]))


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


def mentions_identifier(question: str) -> bool:
    return any(hint in question.lower() for hint in ID_HINTS)


def is_identifier_like(expression: str) -> bool:
    name = bare_name(display_name(expression)).lower()
    return name == "id" or name.endswith("_id")


def is_name_like(expression: str) -> bool:
    name = bare_name(display_name(expression)).lower()
    return "name" in name or "名称" in name


def is_measure_like(expression: str) -> bool:
    name = bare_name(display_name(expression)).lower()
    return any(hint in name for hint in MEASURE_HINTS)


def display_name(expression: str) -> str:
    match = re.search(r"\s+AS\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", expression, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return expression.strip()


def bare_name(expression: str) -> str:
    return expression.rsplit(".", 1)[-1].strip()


def qualifier(expression: str) -> str:
    match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\.[A-Za-z_][A-Za-z0-9_]*\b", expression)
    return match.group(1) if match else ""


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
        "# Projection Repair Skill Report",
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

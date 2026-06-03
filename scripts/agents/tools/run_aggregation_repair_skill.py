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

AGG_ALIAS_PATTERN = re.compile(r"\s+AS\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", re.IGNORECASE)
COUNT_ID_PATTERN = re.compile(r"COUNT\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*_id\s*\)", re.IGNORECASE)
EQUALITY_PATTERN = re.compile(r"(?P<column>[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*)\s*=\s*'[^']+'")
MEASURE_ALIAS_HINTS = ("count", "total", "amount", "sales", "quantity", "price", "avg", "max", "min", "orders")


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
    parser.add_argument("--inputs", default=str(ROOT / "data" / "sqlplus_aggregation_repair_inputs.jsonl"))
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "refiner" / "sqlplus_aggregation_skill_outputs.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "tools" / "aggregation_repair_skill_report.md"))
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
        "method": "aggregation_repair_skill",
    }


def generate_candidates(query: SqlPlusQuery) -> list[dict]:
    states: list[dict] = [{"query": query, "actions": [], "priority": 0}]
    seen = {render_sqlplus(query)}

    for _ in range(4):
        next_states = list(states)
        for state in states:
            for patched, action, priority in transformations(state["query"]):
                rendered = render_sqlplus(patched)
                if rendered in seen:
                    continue
                seen.add(rendered)
                next_states.append(
                    {
                        "query": patched,
                        "actions": state["actions"] + [action],
                        "priority": state["priority"] + priority,
                    }
                )
        if len(next_states) == len(states):
            break
        states = next_states

    return [
        {"sqlplus": render_sqlplus(state["query"]), "actions": state["actions"], "priority": state["priority"]}
        for state in states
        if state["actions"]
    ]


def transformations(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    patches: list[tuple[SqlPlusQuery, str, int]] = []
    patches.extend(remove_redundant_identifier_dimensions(query))
    patches.extend(normalize_count_star(query))
    patches.extend(add_missing_group_dimension_from_filter(query))
    patches.extend(add_or_replace_order_by_aggregate_alias(query))
    patches.extend(normalize_having_alias_reference(query))
    return patches


def remove_redundant_identifier_dimensions(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    if not query.group_by or not query.agg:
        return []
    group_items = split_expressions(query.group_by)
    agg_items = split_expressions(query.agg)
    removable = [item for item in group_items if bare_name(item).endswith("_id")]
    if not removable:
        return []

    # Keep human-readable dimensions such as customer_name when both id and name
    # are projected; this avoids leaking technical ids into the result.
    readable_exists = any(not bare_name(item).endswith("_id") for item in group_items)
    if not readable_exists:
        return []

    new_group = [item for item in group_items if item not in removable]
    new_agg = [item for item in agg_items if item not in removable]
    if not new_group or new_group == group_items:
        return []
    patched = replace(query, group_by=", ".join(new_group), agg=", ".join(new_agg))
    return [(patched, f"Remove redundant identifier dimension(s) `{', '.join(removable)}` from GROUP/AGG.", 50)]


def normalize_count_star(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    if not query.agg or "COUNT" not in query.agg.upper():
        return []
    repaired = COUNT_ID_PATTERN.sub("COUNT(*)", query.agg)
    if repaired == query.agg:
        return []
    return [(replace(query, agg=repaired), "Normalize `COUNT(id)` to `COUNT(*)` for row-count aggregation.", 20)]


def add_missing_group_dimension_from_filter(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    if query.group_by or not query.agg:
        return []
    aggregate_items = split_expressions(query.agg)
    if not aggregate_items or any(not is_aggregate_expression(item) for item in aggregate_items):
        return []

    candidates = []
    for where in query.wheres:
        for match in EQUALITY_PATTERN.finditer(where):
            column = match.group("column")
            priority = filtered_dimension_priority(column)
            patched = replace(query, group_by=column, agg=f"{column}, {query.agg}")
            candidates.append((patched, f"Add filtered dimension `{column}` to GROUP/AGG so the aggregate keeps its business label.", priority))
    return candidates


def filtered_dimension_priority(column: str) -> int:
    lower = bare_name(column).lower()
    if lower in {"status"}:
        return 15
    if any(hint in lower for hint in ("category", "level", "city", "name")):
        return 60
    return 35


def add_or_replace_order_by_aggregate_alias(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    if not query.agg:
        return []
    alias = best_aggregate_alias(query.agg)
    if not alias:
        return []
    order_by = f"{alias} DESC"
    if query.order_by == order_by:
        return []
    return [(replace(query, order_by=order_by), f"Order grouped results by aggregate alias `{alias}` descending.", 35)]


def normalize_having_alias_reference(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    if not query.having or not query.agg:
        return []
    aliases = aggregate_aliases(query.agg)
    patches = []
    for alias in aliases:
        if re.search(rf"\b{re.escape(alias)}\b", query.having):
            continue
        aggregate_expr = expression_for_alias(query.agg, alias)
        if aggregate_expr and aggregate_expr in query.having:
            patched = replace(query, having=query.having.replace(aggregate_expr, alias))
            patches.append((patched, f"Normalize HAVING aggregate expression to alias `{alias}`.", 10))
    return patches


def select_best_candidate(conn: sqlite3.Connection, original: str, candidates: list[dict]) -> dict:
    original_score = score_sqlplus(conn, original)
    best = {
        "sqlplus": original,
        "actions": ["No aggregation patch improved execution feedback."],
        "score": original_score,
        "rank": (original_score[0], 0, original_score[1], original_score[2]),
        "reason": "original",
    }
    for candidate in candidates:
        score = score_sqlplus(conn, candidate["sqlplus"])
        rank = (score[0], candidate.get("priority", 0), score[1], score[2])
        if rank > best["rank"]:
            best = {
                "sqlplus": candidate["sqlplus"],
                "actions": candidate["actions"],
                "score": score,
                "rank": rank,
                "reason": "highest heuristic priority among executable aggregation candidates",
            }
    return best


def score_sqlplus(conn: sqlite3.Connection, sqlplus: str) -> tuple[int, int, int]:
    try:
        rows = execute(conn, to_sql(sqlplus))
    except sqlite3.Error:
        return (0, 0, 0)
    if not rows:
        return (1, 0, 0)
    column_count = len(rows[0])
    return (1, column_count, len(rows))


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


def is_aggregate_expression(expression: str) -> bool:
    return bool(re.search(r"\b(COUNT|SUM|AVG|MAX|MIN)\s*\(", expression, flags=re.IGNORECASE))


def aggregate_aliases(agg: str) -> list[str]:
    aliases = []
    for item in split_expressions(agg):
        if is_aggregate_expression(item):
            match = AGG_ALIAS_PATTERN.search(item)
            if match:
                aliases.append(match.group(1))
    return aliases


def best_aggregate_alias(agg: str) -> str:
    aliases = aggregate_aliases(agg)
    if not aliases:
        return ""
    for alias in aliases:
        lower = alias.lower()
        if any(hint in lower for hint in MEASURE_ALIAS_HINTS):
            return alias
    return aliases[-1]


def expression_for_alias(agg: str, alias: str) -> str:
    for item in split_expressions(agg):
        match = AGG_ALIAS_PATTERN.search(item)
        if match and match.group(1) == alias:
            return item[: match.start()].strip()
    return ""


def bare_name(expression: str) -> str:
    return expression.rsplit(".", 1)[-1].strip()


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
        "# Aggregation Repair Skill Report",
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

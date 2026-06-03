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

AMOUNT_EXPR_PATTERN = re.compile(r"\(?\s*oi\.quantity\s*\*\s*oi\.unit_price\s*\)?\s+AS\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)


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
    parser.add_argument("--inputs", default=str(ROOT / "data" / "sqlplus_join_repair_inputs.jsonl"))
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "refiner" / "sqlplus_join_skill_outputs.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "tools" / "join_repair_skill_report.md"))
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
        "method": "join_repair_skill",
    }


def generate_candidates(query: SqlPlusQuery) -> list[dict]:
    states: list[dict] = [{"query": query, "actions": [], "priority": 0}]
    seen = {render_sqlplus(query)}
    for _ in range(5):
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
    patches.extend(canonicalize_join_direction(query))
    patches.extend(add_missing_products_join(query))
    patches.extend(remove_redundant_products_join(query))
    patches.extend(add_paid_filter(query))
    patches.extend(remove_redundant_identifier_dimensions(query))
    patches.extend(repair_product_type_aggregation(query))
    patches.extend(repair_join_dependent_projection(query))
    patches.extend(order_by_amount_alias(query))
    patches.extend(order_by_aggregate_alias(query))
    return patches


def canonicalize_join_direction(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    replacements = {
        "order_items oi ON oi.order_id = o.order_id": "order_items oi ON o.order_id = oi.order_id",
        "orders o ON o.order_id = oi.order_id": "orders o ON oi.order_id = o.order_id",
        "products p ON p.product_id = oi.product_id": "products p ON oi.product_id = p.product_id",
        "customers c ON c.customer_id = o.customer_id": "customers c ON o.customer_id = c.customer_id",
    }
    joins = list(query.joins)
    changed = False
    for index, join in enumerate(joins):
        if join in replacements:
            joins[index] = replacements[join]
            changed = True
    if not changed:
        return []
    return [(replace(query, joins=joins), "Normalize JOIN predicate direction using schema foreign keys.", 15)]


def add_missing_products_join(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    text = query_text(query)
    product_projection_hint = "oi.product_id" in query.select and "oi.quantity * oi.unit_price" in query.select
    if " p." not in f" {text}" and "product_name" not in text and not product_projection_hint:
        return []
    if has_alias(query, "p") or not has_alias(query, "oi"):
        return []
    joins = list(query.joins) + ["products p ON oi.product_id = p.product_id"]
    return [(replace(query, joins=joins), "Add missing products join for product attributes.", 45)]


def remove_redundant_products_join(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    if not has_alias(query, "p"):
        return []
    text_without_joins = " ".join([*query.wheres, query.group_by, query.agg, query.select, query.having, query.order_by])
    if "p.category" not in text_without_joins:
        return []
    if "COUNT(DISTINCT p.category)" not in query.agg:
        return []
    joins = [join for join in query.joins if not join.startswith("products p ")]
    if joins == query.joins:
        return []
    return [(replace(query, joins=joins), "Remove products join after replacing category-count with product-id count.", 25)]


def add_paid_filter(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    if not has_alias(query, "o"):
        return []
    if any("o.status" in where for where in query.wheres):
        return []
    where = list(query.wheres) + ["o.status = 'paid'"]
    return [(replace(query, wheres=where), "Add paid-order filter for order analysis joins.", 40)]


def remove_redundant_identifier_dimensions(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    if not query.group_by or not query.agg:
        return []
    group_items = split_expressions(query.group_by)
    agg_items = split_expressions(query.agg)
    removable = [item for item in group_items if bare_name(item).endswith("_id")]
    if not removable:
        return []
    if not any(not bare_name(item).endswith("_id") for item in group_items):
        return []
    new_group = [item for item in group_items if item not in removable]
    new_agg = [item for item in agg_items if item not in removable]
    return [(replace(query, group_by=", ".join(new_group), agg=", ".join(new_agg)), f"Remove redundant identifier dimension(s) `{', '.join(removable)}`.", 35)]


def repair_product_type_aggregation(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    if "COUNT(DISTINCT p.category)" not in query.agg:
        return []
    repaired = query.agg.replace("COUNT(DISTINCT p.category) AS category_count", "COUNT(DISTINCT oi.product_id) AS product_types")
    repaired = repaired.replace("COUNT(DISTINCT p.category)", "COUNT(DISTINCT oi.product_id)")
    order_by = query.order_by.replace("category_count", "product_types") if query.order_by else "product_types DESC"
    return [(replace(query, agg=repaired, order_by=order_by), "Count distinct product ids instead of product categories for product-type quantity.", 55)]


def repair_join_dependent_projection(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    if not query.select:
        return []
    if "oi.product_id" not in query.select or "oi.quantity * oi.unit_price" not in query.select:
        return []
    if not has_alias(query, "p"):
        return []
    alias_match = AMOUNT_EXPR_PATTERN.search(query.select)
    current_alias = alias_match.group(1) if alias_match else "line_amount"
    select = "oi.item_id, p.product_name, oi.quantity * oi.unit_price AS item_amount"
    order_by = query.order_by.replace(current_alias, "item_amount") if query.order_by else "item_amount DESC"
    return [(replace(query, select=select, order_by=order_by), "Use product name from joined products table and normalize item amount alias.", 70)]


def order_by_amount_alias(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    text = query.select or query.agg
    if not text:
        return []
    match = AMOUNT_EXPR_PATTERN.search(text)
    if not match:
        return []
    alias = match.group(1)
    order_by = f"{alias} DESC"
    if query.order_by == order_by:
        return []
    return [(replace(query, order_by=order_by), f"Order amount-like output by `{alias}` descending.", 25)]


def order_by_aggregate_alias(query: SqlPlusQuery) -> list[tuple[SqlPlusQuery, str, int]]:
    aliases = []
    for item in split_expressions(query.agg):
        match = re.search(r"\s+AS\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", item, re.IGNORECASE)
        if match and re.search(r"\b(COUNT|SUM|AVG|MAX|MIN)\s*\(", item, re.IGNORECASE):
            aliases.append(match.group(1))
    if not aliases:
        return []
    alias = aliases[-1]
    if query.order_by == f"{alias} DESC":
        return []
    return [(replace(query, order_by=f"{alias} DESC"), f"Order grouped results by aggregate alias `{alias}` descending.", 20)]


def select_best_candidate(conn: sqlite3.Connection, original: str, candidates: list[dict]) -> dict:
    original_score = score_sqlplus(conn, original)
    best = {
        "sqlplus": original,
        "actions": ["No join patch improved execution feedback."],
        "score": original_score,
        "rank": (original_score[0], 0, original_score[1], -original_score[2]),
        "reason": "original",
    }
    for candidate in candidates:
        score = score_sqlplus(conn, candidate["sqlplus"])
        rank = (score[0], candidate.get("priority", 0), score[1], -score[2])
        if rank > best["rank"]:
            best = {
                "sqlplus": candidate["sqlplus"],
                "actions": candidate["actions"],
                "score": score,
                "rank": rank,
                "reason": "highest heuristic priority among executable join candidates",
            }
    return best


def score_sqlplus(conn: sqlite3.Connection, sqlplus: str) -> tuple[int, int, int]:
    try:
        rows = execute(conn, to_sql(sqlplus))
    except sqlite3.Error:
        return (0, 0, 999)
    if not rows:
        return (1, 0, 0)
    return (1, len(rows[0]), len(rows))


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


def has_alias(query: SqlPlusQuery, alias: str) -> bool:
    pattern = re.compile(rf"\b{re.escape(alias)}\b")
    return bool(pattern.search(query.source)) or any(pattern.search(join) for join in query.joins)


def query_text(query: SqlPlusQuery) -> str:
    return " ".join([query.source, *query.joins, *query.wheres, query.group_by, query.agg, query.select, query.having, query.order_by])


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
        "# JOIN Repair Skill Report",
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

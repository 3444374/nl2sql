from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "agents" / "tools"))

from sqlplus import normalize_rows, parse_sqlplus, to_sql

import run_aggregation_repair_skill as aggregation_skill
import run_join_repair_skill as join_skill
import run_order_repair_skill as order_skill
import run_value_lookup_repair_skill as value_skill


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
    parser.add_argument("--inputs", default=str(ROOT / "data" / "sqlplus_critic_refiner_inputs_stepwise_merged.jsonl"))
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "refiner" / "sqlplus_skill_router_outputs.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "pipeline" / "sqlplus_skill_router_report.md"))
    args = parser.parse_args()

    conn = build_db(Path(args.schema))
    cases = {row["id"]: row for row in load_jsonl(Path(args.cases))}
    rows = load_jsonl(Path(args.inputs))
    outputs = []

    for row in rows:
        routed = route_and_repair(conn, row)
        routed["evaluation"] = evaluate(conn, cases[row["id"]], routed["prediction"])
        outputs.append(routed)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in outputs), encoding="utf-8")
    report = render_report(outputs)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def route_and_repair(conn: sqlite3.Connection, row: dict) -> dict:
    initial = row["pred_sqlplus"]
    plan = routing_plan(row)
    current = initial
    traces = []
    actions = []

    for skill_name in plan:
        repair_input = dict(row)
        repair_input["pred_sqlplus"] = current
        result = run_skill(conn, skill_name, repair_input)
        current = result["prediction"]
        traces.append(
            {
                "skill": skill_name,
                "candidate_count": result.get("tool_trace", {}).get("candidate_count"),
                "selected_score": result.get("tool_trace", {}).get("selected_score"),
                "selected_reason": result.get("tool_trace", {}).get("selected_reason"),
            }
        )
        actions.extend(f"{skill_name}: {action}" for action in result.get("repair_actions", []))

    return {
        "id": row["id"],
        "prediction": current,
        "routing_plan": plan,
        "repair_actions": actions or ["No supported repair skill was routed."],
        "tool_trace": traces,
        "critic_agent": {
            "likely_error_type": row.get("critic_agent", {}).get("likely_error_type", ""),
            "localized_steps": [step.get("step") for step in row.get("critic_agent", {}).get("localized_steps", [])],
        },
        "method": "skill_router",
    }


def routing_plan(row: dict) -> list[str]:
    critic = row.get("critic_agent", {})
    likely = str(critic.get("likely_error_type", "")).lower()
    localized_steps = {str(step.get("step", "")).upper() for step in critic.get("localized_steps", [])}
    sqlplus = row["pred_sqlplus"]
    query = parse_sqlplus(sqlplus)
    plan: list[str] = []

    if likely in {"filter_or_value", "filter_or_value_linking"} or "WHERE" in localized_steps:
        add(plan, "value")
    if likely in {"schema_or_join", "schema_or_join_planning", "join"} or "JOIN" in localized_steps:
        add(plan, "join")
    if likely in {"aggregation", "aggregation_planning"} or {"GROUP", "AGG", "HAVING"} & localized_steps:
        add(plan, "aggregation")
    if likely in {"order_or_limit", "order_or_limit_mismatch"} or {"ORDER", "LIMIT"} & localized_steps:
        add(plan, "order")

    # SQL+ structure can expose compound errors that the critic labels too
    # coarsely, e.g. value-linking plus missing aggregation dimensions.
    if query.agg:
        add(plan, "aggregation")
    if query.joins:
        text = " ".join([query.source, *query.joins, query.select, query.agg])
        if "oi.product_id" in text or "p.category" in text or any(" p " in f" {join} " for join in query.joins):
            add(plan, "join")
    if not query.order_by and (query.select or query.agg):
        add(plan, "order")

    return plan


def add(plan: list[str], skill_name: str) -> None:
    if skill_name not in plan:
        plan.append(skill_name)


def run_skill(conn: sqlite3.Connection, skill_name: str, row: dict) -> dict:
    if skill_name == "value":
        return value_skill.repair_case(conn, row)
    if skill_name == "order":
        return order_skill.repair_case(conn, row)
    if skill_name == "aggregation":
        return aggregation_skill.repair_case(conn, row)
    if skill_name == "join":
        return join_skill.repair_case(conn, row)
    raise ValueError(f"Unsupported skill: {skill_name}")


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


def render_report(rows: list[dict]) -> str:
    total = len(rows)
    valid = sum(1 for row in rows if row["evaluation"]["sqlplus_valid"])
    executable = sum(1 for row in rows if row["evaluation"]["sql_valid"])
    matched = sum(1 for row in rows if row["evaluation"]["execution_match"])
    by_route: dict[str, list[bool]] = {}
    for row in rows:
        key = " -> ".join(row["routing_plan"]) or "unsupported"
        by_route.setdefault(key, []).append(row["evaluation"]["execution_match"])

    lines = [
        "# SQL+ Skill Router End-to-End Report",
        "",
        "| Metric | Result |",
        "| --- | --- |",
        f"| Cases | {total} |",
        f"| SQL+ valid | {valid}/{total} |",
        f"| SQL executable | {executable}/{total} |",
        f"| Repair success | {matched}/{total} |",
        "",
        "## Route Summary",
        "",
        "| Route | Cases | Success |",
        "| --- | --- | --- |",
    ]
    for route, results in sorted(by_route.items()):
        lines.append(f"| {route} | {len(results)} | {sum(1 for item in results if item)}/{len(results)} |")

    lines.extend(
        [
            "",
            "## Details",
            "",
            "| ID | Critic Type | Route | Success | Actions |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        route = " -> ".join(row["routing_plan"]) or "unsupported"
        actions = "; ".join(row["repair_actions"]).replace("|", "/")
        critic_type = row["critic_agent"]["likely_error_type"]
        lines.append(f"| {row['id']} | {critic_type} | {route} | {row['evaluation']['execution_match']} | {actions} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

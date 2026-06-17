from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
import time
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "agents" / "pipeline"))

from sqlplus import normalize_rows, parse_sqlplus, to_sql
import run_skill_router_experiment as skill_router


STEP_TO_SKILL = {
    "WHERE": "value",
    "JOIN": "join",
    "GROUP": "aggregation",
    "AGG": "aggregation",
    "HAVING": "aggregation",
    "SELECT": "projection",
    "ORDER": "order",
    "LIMIT": "order",
}

CATEGORY_TO_STEPS = {
    "filter_or_value": {"WHERE"},
    "filter_or_value_linking": {"WHERE"},
    "filter_or_value_suspected": {"WHERE"},
    "order_or_limit": {"ORDER", "LIMIT"},
    "order_or_limit_mismatch": {"ORDER", "LIMIT"},
    "order_or_limit_suspected": {"ORDER", "LIMIT"},
    "aggregation": {"GROUP", "AGG", "HAVING"},
    "aggregation_planning": {"GROUP", "AGG", "HAVING"},
    "aggregation_suspected": {"GROUP", "AGG", "HAVING"},
    "schema_or_join": {"JOIN"},
    "schema_or_join_planning": {"JOIN"},
    "schema_or_join_suspected": {"JOIN"},
    "join": {"JOIN"},
    "projection": {"SELECT"},
    "projection_mismatch": {"SELECT"},
    "projection_suspected": {"SELECT"},
    "execution_error": {"FROM", "JOIN", "WHERE", "SELECT", "GROUP", "AGG", "HAVING", "ORDER", "LIMIT"},
}

SQL_CLAUSE_TO_STEP = {
    "select": "SELECT",
    "from_join": "JOIN",
    "where": "WHERE",
    "group": "GROUP",
    "having": "HAVING",
    "order": "ORDER",
    "limit": "LIMIT",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_jsonl_map(path: Path) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in load_jsonl(path)}


def build_db(schema_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    return conn


def execute(conn: sqlite3.Connection, sql: str) -> list[tuple]:
    return normalize_rows(conn.execute(sql).fetchall())


def eval_sql(conn: sqlite3.Connection, prediction: str, gold_sql: str) -> dict[str, Any]:
    try:
        return {
            "sql_valid": True,
            "execution_match": execute(conn, prediction) == execute(conn, gold_sql),
            "error": "",
        }
    except Exception as exc:
        return {"sql_valid": False, "execution_match": False, "error": str(exc)}


def eval_sqlplus(conn: sqlite3.Connection, prediction: str, gold_sql: str) -> dict[str, Any]:
    try:
        sql = to_sql(prediction)
        return {
            "sqlplus_valid": True,
            "sql_valid": True,
            "execution_match": execute(conn, sql) == execute(conn, gold_sql),
            "error": "",
        }
    except Exception as exc:
        return {"sqlplus_valid": False, "sql_valid": False, "execution_match": False, "error": str(exc)}


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().rstrip(";")).lower()


def sqlplus_fields(text: str) -> dict[str, Any]:
    query = parse_sqlplus(text)
    return {
        "FROM": query.source,
        "JOIN": tuple(query.joins),
        "WHERE": tuple(query.wheres),
        "GROUP": query.group_by,
        "AGG": query.agg,
        "HAVING": query.having,
        "SELECT": query.select,
        "ORDER": query.order_by,
        "LIMIT": query.limit,
    }


def changed_sqlplus_steps(before: str, after: str) -> set[str]:
    try:
        b = sqlplus_fields(before)
        a = sqlplus_fields(after)
    except Exception:
        return set()
    return {step for step in b if b[step] != a[step]}


def expected_sqlplus_steps(initial_sqlplus: str, gold_sqlplus: str) -> set[str]:
    return changed_sqlplus_steps(initial_sqlplus, gold_sqlplus)


def clean_sql(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped


def sql_clauses(sql: str) -> dict[str, str]:
    text = clean_sql(sql).strip().rstrip(";")
    compact = re.sub(r"\s+", " ", text)
    upper = compact.upper()
    positions: list[tuple[str, int]] = []
    for name, pattern in [
        ("select", r"\bSELECT\b"),
        ("from", r"\bFROM\b"),
        ("where", r"\bWHERE\b"),
        ("group", r"\bGROUP\s+BY\b"),
        ("having", r"\bHAVING\b"),
        ("order", r"\bORDER\s+BY\b"),
        ("limit", r"\bLIMIT\b"),
    ]:
        match = re.search(pattern, upper)
        if match:
            positions.append((name, match.start()))
    positions.sort(key=lambda item: item[1])
    chunks: dict[str, str] = {}
    for index, (name, start) in enumerate(positions):
        end = positions[index + 1][1] if index + 1 < len(positions) else len(compact)
        chunks[name] = compact[start:end].strip()
    from_join = chunks.get("from", "")
    return {
        "select": chunks.get("select", ""),
        "from_join": from_join,
        "where": chunks.get("where", ""),
        "group": chunks.get("group", ""),
        "having": chunks.get("having", ""),
        "order": chunks.get("order", ""),
        "limit": chunks.get("limit", ""),
    }


def changed_sql_steps(before_sql: str, after_sql: str) -> set[str]:
    before = sql_clauses(before_sql)
    after = sql_clauses(after_sql)
    return {SQL_CLAUSE_TO_STEP[name] for name in before if norm(before[name]) != norm(after[name])}


def expected_sql_steps(initial_sql: str, gold_sql: str) -> set[str]:
    return changed_sql_steps(initial_sql, gold_sql)


def localized_steps_from_category(category: str) -> set[str]:
    return CATEGORY_TO_STEPS.get(category, set())


def expected_skills(steps: set[str]) -> set[str]:
    return {STEP_TO_SKILL[step] for step in steps if step in STEP_TO_SKILL}


def patch_minimality(changed: set[str], expected: set[str]) -> float:
    if not changed:
        return 1.0 if not expected else 0.0
    return len(changed & expected) / len(changed)


def is_minimal_patch(changed: set[str], expected: set[str]) -> bool:
    return bool(changed) and changed <= expected


def usage_total(row: dict[str, Any]) -> int:
    usage = row.get("usage") or {}
    return int(usage.get("total_tokens") or 0)


def measure_sqlplus_router_latency(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> dict[str, float]:
    timings: dict[str, float] = {}
    for row in rows:
        started = time.perf_counter()
        skill_router.route_and_repair(conn, row)
        timings[row["id"]] = time.perf_counter() - started
    return timings


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    if not total:
        return {}
    return {
        "cases": total,
        "repair_success": sum(1 for row in rows if row["repair_success"]),
        "localization_accuracy": sum(1 for row in rows if row["localization_correct"]) / total,
        "strict_minimal_patch_rate": sum(1 for row in rows if row["strict_minimal_patch"]) / total,
        "avg_patch_minimality": mean(row["patch_minimality"] for row in rows),
        "router_accuracy": mean(float(row["router_correct"]) for row in rows if row["router_correct"] != "")
        if any(row["router_correct"] != "" for row in rows)
        else None,
        "avg_changed_steps": mean(row["changed_step_count"] for row in rows),
        "avg_expected_steps": mean(row["expected_step_count"] for row in rows),
        "avg_repair_rounds": mean(row["repair_rounds"] for row in rows),
        "avg_repair_tokens": mean(row["repair_tokens"] for row in rows),
        "avg_repair_latency_sec": mean(row["repair_latency_sec"] for row in rows if row["repair_latency_sec"] is not None)
        if any(row["repair_latency_sec"] is not None for row in rows)
        else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--sqlplus-inputs", default=str(ROOT / "data" / "sqlplus_critic_refiner_inputs_stepwise_merged.jsonl"))
    parser.add_argument("--sqlplus-outputs", default=str(ROOT / "outputs" / "refiner" / "sqlplus_skill_router_outputs_v3.jsonl"))
    parser.add_argument("--sqlplus-critic", default=str(ROOT / "outputs" / "agents" / "critic" / "sqlplus_critic_stepwise_model_merged.jsonl"))
    parser.add_argument("--direct-inputs", default=str(ROOT / "data" / "direct_feedback_refiner_inputs.jsonl"))
    parser.add_argument("--direct-outputs", default=str(ROOT / "outputs" / "refiner" / "direct_feedback_refiner_model_merged.jsonl"))
    parser.add_argument("--detail-output", default=str(ROOT / "data" / "repairability_metrics_detail.csv"))
    parser.add_argument("--summary-output", default=str(ROOT / "data" / "repairability_metrics_summary.csv"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "pipeline" / "repairability_metrics_report.md"))
    args = parser.parse_args()

    cases = load_jsonl_map(Path(args.cases))
    conn = build_db(Path(args.schema))

    sqlplus_inputs = load_jsonl_map(Path(args.sqlplus_inputs))
    sqlplus_outputs = load_jsonl_map(Path(args.sqlplus_outputs))
    critic_outputs = load_jsonl_map(Path(args.sqlplus_critic))
    direct_inputs = load_jsonl_map(Path(args.direct_inputs))
    direct_outputs = load_jsonl_map(Path(args.direct_outputs))

    sqlplus_latency = measure_sqlplus_router_latency(conn, [sqlplus_inputs[row_id] for row_id in sqlplus_outputs])

    detail_rows: list[dict[str, Any]] = []
    for row_id, output in sqlplus_outputs.items():
        initial = sqlplus_inputs[row_id]["pred_sqlplus"]
        case = cases[row_id]
        expected = expected_sqlplus_steps(initial, case["sqlplus"])
        changed = changed_sqlplus_steps(initial, output["prediction"])
        localized = set(output.get("critic_agent", {}).get("localized_steps") or [])
        routed = set(output.get("routing_plan") or [])
        exp_skills = expected_skills(expected)
        evaluation = eval_sqlplus(conn, output["prediction"], case["gold_sql"])
        detail_rows.append(
            {
                "method": "sqlplus_critic_router_skills",
                "id": row_id,
                "repair_success": evaluation["execution_match"],
                "expected_steps": ",".join(sorted(expected)),
                "localized_steps": ",".join(sorted(localized)),
                "changed_steps": ",".join(sorted(changed)),
                "routing_plan": "->".join(output.get("routing_plan") or []),
                "localization_correct": bool(localized & expected),
                "router_correct": bool(routed & exp_skills) if exp_skills else True,
                "strict_minimal_patch": is_minimal_patch(changed, expected),
                "patch_minimality": patch_minimality(changed, expected),
                "changed_step_count": len(changed),
                "expected_step_count": len(expected),
                "repair_rounds": len(output.get("routing_plan") or []),
                "repair_tokens": usage_total(critic_outputs.get(row_id, {})),
                "repair_latency_sec": sqlplus_latency.get(row_id),
                "latency_note": "local deterministic router+skills only; critic API latency was not captured",
            }
        )

    for row_id, output in direct_outputs.items():
        if row_id not in direct_inputs or row_id not in cases:
            continue
        initial = direct_inputs[row_id]["pred_sql"]
        prediction = clean_sql(output["prediction"])
        case = cases[row_id]
        expected = expected_sql_steps(initial, case["gold_sql"])
        changed = changed_sql_steps(initial, prediction)
        category = direct_inputs[row_id]["coarse_feedback"]["category"]
        localized = localized_steps_from_category(category)
        evaluation = eval_sql(conn, prediction, case["gold_sql"])
        detail_rows.append(
            {
                "method": "direct_sql_feedback_refiner",
                "id": row_id,
                "repair_success": evaluation["execution_match"],
                "expected_steps": ",".join(sorted(expected)),
                "localized_steps": ",".join(sorted(localized)),
                "changed_steps": ",".join(sorted(changed)),
                "routing_plan": "single_refiner",
                "localization_correct": bool(localized & expected),
                "router_correct": "",
                "strict_minimal_patch": is_minimal_patch(changed, expected),
                "patch_minimality": patch_minimality(changed, expected),
                "changed_step_count": len(changed),
                "expected_step_count": len(expected),
                "repair_rounds": 1,
                "repair_tokens": usage_total(output),
                "repair_latency_sec": None,
                "latency_note": "not captured by the earlier OpenAI refiner run",
            }
        )

    summary_rows = []
    for method in sorted({row["method"] for row in detail_rows}):
        rows = [row for row in detail_rows if row["method"] == method]
        summary = summarize(rows)
        summary["method"] = method
        summary_rows.append(summary)

    overlap_ids = sorted(set(sqlplus_outputs) & set(direct_outputs))
    for method in sorted({row["method"] for row in detail_rows}):
        rows = [row for row in detail_rows if row["method"] == method and row["id"] in overlap_ids]
        summary = summarize(rows)
        summary["method"] = method + "_overlap"
        summary_rows.append(summary)

    write_csv(Path(args.detail_output), detail_rows)
    write_csv(Path(args.summary_output), summary_rows)
    report = render_report(summary_rows, detail_rows, overlap_ids)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def render_report(summary_rows: list[dict[str, Any]], detail_rows: list[dict[str, Any]], overlap_ids: list[str]) -> str:
    lines = [
        "# Repairability Metrics Report",
        "",
        "This report compares repair-stage metrics after the IR generation-cost experiment.",
        "",
        "Scope notes:",
        "",
        "- SQL+ uses `Critic Agent -> Skill Router -> Repair Skills -> Executor` on the current 13-case SQL+ known-failure set.",
        "- Direct SQL uses the existing single Refiner Agent outputs. The earlier OpenAI run did not record per-call latency, so direct repair latency is marked as N/A.",
        "- SQL+ repair token cost counts the Step-wise Critic Agent usage. Local deterministic repair skills add no model tokens.",
        "- SQL+ repair latency measures local router and repair-skill execution only. Critic API latency was not captured in the earlier run.",
        "- Patch minimality is an offline metric computed against gold differences and is not used to choose repairs.",
        "",
        f"Overlap IDs for cross-method subset: {', '.join(overlap_ids)}",
        "",
        "## Summary",
        "",
        "| Method | Cases | Success | Localization Acc. | Strict Minimal Patch | Avg Patch Minimality | Avg Rounds | Avg Repair Tokens | Avg Repair Latency |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        lines.append(
            "| {method} | {cases} | {success}/{cases} | {loc} | {strict} | {patch} | {rounds} | {tokens} | {latency} |".format(
                method=row["method"],
                cases=row["cases"],
                success=row["repair_success"],
                loc=fmt(row["localization_accuracy"]),
                strict=fmt(row["strict_minimal_patch_rate"]),
                patch=fmt(row["avg_patch_minimality"]),
                rounds=fmt(row["avg_repair_rounds"]),
                tokens=fmt(row["avg_repair_tokens"]),
                latency=fmt(row["avg_repair_latency_sec"]),
            )
        )

    lines.extend(
        [
            "",
            "## Router Accuracy",
            "",
            "| Method | Router Accuracy |",
            "| --- | ---: |",
        ]
    )
    for row in summary_rows:
        lines.append(f"| {row['method']} | {fmt(row.get('router_accuracy'))} |")

    lines.extend(
        [
            "",
            "## Detail",
            "",
            "| Method | ID | Success | Expected Steps | Localized Steps | Changed Steps | Minimality | Rounds | Tokens | Latency Note |",
            "| --- | --- | ---: | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in detail_rows:
        lines.append(
            "| {method} | {id} | {success} | {expected} | {localized} | {changed} | {patch} | {rounds} | {tokens} | {note} |".format(
                method=row["method"],
                id=row["id"],
                success=row["repair_success"],
                expected=row["expected_steps"] or "-",
                localized=row["localized_steps"] or "-",
                changed=row["changed_steps"] or "-",
                patch=fmt(row["patch_minimality"]),
                rounds=row["repair_rounds"],
                tokens=row["repair_tokens"],
                note=row["latency_note"],
            )
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

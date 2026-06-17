from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "agents" / "tools"))

import semantic_repair_skill


def route_and_repair(case: dict, schema: str, prediction: str, evaluation: dict) -> dict:
    """Route Spider SQL+ endpoint failures to reusable repair skills.

    The router uses only question text, schema text, SQL+ prediction, and
    parser/execution feedback. Gold SQL is intentionally not part of the input.
    """
    row = {
        "id": case.get("id", ""),
        "question": case.get("question", ""),
        "schema": schema,
        "pred_sqlplus": prediction,
        "evaluation": evaluation,
    }
    plan = routing_plan(row)
    current = prediction
    traces: list[dict] = []
    actions: list[str] = []

    for skill_name in plan:
        skill_input = dict(row)
        skill_input["pred_sqlplus"] = current
        result = run_skill(skill_name, skill_input)
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
        "prediction": current,
        "routing_plan": plan,
        "repair_actions": actions,
        "tool_trace": traces,
        "method": "spider_sqlplus_repair_router",
    }


def routing_plan(row: dict) -> list[str]:
    plan: list[str] = []
    if semantic_repair_skill.should_route(row):
        plan.append("semantic")
    return plan


def run_skill(skill_name: str, row: dict) -> dict:
    if skill_name == "semantic":
        return semantic_repair_skill.repair_case(row)
    raise ValueError(f"Unsupported Spider SQL+ repair skill: {skill_name}")

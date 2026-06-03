from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema-inputs", default=str(ROOT / "data" / "sqlplus_schema_agent_inputs.jsonl"))
    parser.add_argument("--critic-output", default=str(ROOT / "outputs" / "agents" / "critic" / "sqlplus_critic_model.jsonl"))
    parser.add_argument("--output", default=str(ROOT / "data" / "sqlplus_critic_refiner_inputs.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "pipeline" / "sqlplus_critic_refiner_inputs.md"))
    args = parser.parse_args()

    schema_rows = {row["id"]: row for row in load_jsonl(Path(args.schema_inputs))}
    critic_rows = {row["id"]: row for row in load_jsonl(Path(args.critic_output))}
    combined = []
    for case_id, row in schema_rows.items():
        if case_id not in critic_rows:
            continue
        item = dict(row)
        item["critic_agent"] = strip_runtime_fields(critic_rows[case_id])
        combined.append(item)

    Path(args.output).write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in combined), encoding="utf-8")
    report = render_report(combined)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def strip_runtime_fields(row: dict) -> dict:
    return {key: value for key, value in row.items() if key not in {"raw_output", "response_id", "usage", "model", "method"}}


def render_report(rows: list[dict]) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        kind = row["critic_agent"].get("likely_error_type", "unknown")
        counts[kind] = counts.get(kind, 0) + 1
    lines = [
        "# SQL+ Critic-Guided Refiner Inputs",
        "",
        f"Rows: {len(rows)}",
        "",
        "| Critic Error Type | Count |",
        "| --- | --- |",
    ]
    for kind in sorted(counts):
        lines.append(f"| {kind} | {counts[kind]} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())




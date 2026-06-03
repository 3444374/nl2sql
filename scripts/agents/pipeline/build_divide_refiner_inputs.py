from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

PRESETS = {
    "order": {"q002", "q003", "q005"},
    "value": {"q004", "q017", "q026"},
}


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", default=str(ROOT / "data" / "feedback_refiner_inputs_v2.jsonl"))
    parser.add_argument("--kind", choices=sorted(PRESETS), required=True)
    parser.add_argument("--output")
    parser.add_argument("--report")
    args = parser.parse_args()

    rows = load_jsonl(Path(args.inputs))
    wanted = PRESETS[args.kind]
    selected = []
    for row in rows:
        if row["id"] in wanted:
            item = dict(row)
            item["divide_experiment"] = {
                "kind": args.kind,
                "allowed_edits": ["ORDER", "LIMIT"] if args.kind == "order" else ["WHERE"],
                "note": "Non-gold divide-and-conquer input. Gold is not included in model input.",
            }
            selected.append(item)

    output = Path(args.output or ROOT / "data" / f"sqlplus_{args.kind}_only_refiner_inputs.jsonl")
    report = Path(args.report or ROOT / "docs" / "agents" / "pipeline" / f"sqlplus_{args.kind}_only_refiner_inputs.md")
    output.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in selected), encoding="utf-8")
    report.write_text(render_report(args.kind, selected), encoding="utf-8")
    print(render_report(args.kind, selected))
    return 0


def render_report(kind: str, rows: list[dict]) -> str:
    lines = [
        f"# SQL+ {kind.title()}-only Refiner Inputs",
        "",
        f"Rows: {len(rows)}",
        "",
        "| ID | Coarse Feedback | Allowed Edits |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        feedback = row.get("coarse_feedback", {}).get("category", "")
        edits = ", ".join(row["divide_experiment"]["allowed_edits"])
        lines.append(f"| {row['id']} | {feedback} | {edits} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

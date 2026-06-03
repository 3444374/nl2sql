from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load_cases(path: Path) -> dict[str, dict]:
    with path.open("r", encoding="utf-8") as handle:
        return {row["id"]: row for row in (json.loads(line) for line in handle if line.strip())}


def load_diagnostics(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--diagnostics", default=str(ROOT / "data" / "sqlplus_mismatch_diagnostics.jsonl"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "refiner" / "sqlplus_refiner_oracle.jsonl"))
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    diagnostics = load_diagnostics(Path(args.diagnostics))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for item in diagnostics:
            case = cases[item["id"]]
            row = {
                "id": item["id"],
                "prediction": case["sqlplus"],
                "source_category": item["category"],
                "repair_actions": ["oracle_refiner: replace predicted SQL+ with gold SQL+ for pipeline validation"],
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(diagnostics)} oracle refiner outputs to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_cases(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--direct-output", default=str(ROOT / "outputs" / "baseline" / "direct_oracle.jsonl"))
    parser.add_argument("--sqlplus-output", default=str(ROOT / "outputs" / "baseline" / "sqlplus_oracle.jsonl"))
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    Path(args.direct_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.sqlplus_output).parent.mkdir(parents=True, exist_ok=True)

    with Path(args.direct_output).open("w", encoding="utf-8", newline="\n") as direct_handle:
        for case in cases:
            direct_handle.write(json.dumps({"id": case["id"], "prediction": case["gold_sql"]}, ensure_ascii=False) + "\n")

    with Path(args.sqlplus_output).open("w", encoding="utf-8", newline="\n") as sqlplus_handle:
        for case in cases:
            sqlplus_handle.write(json.dumps({"id": case["id"], "prediction": case["sqlplus"]}, ensure_ascii=False) + "\n")

    print(f"Wrote oracle outputs for {len(cases)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

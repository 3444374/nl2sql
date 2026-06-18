from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sqlplus_generator import build_sqlplus_generation_prompt


def load_cases(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--direct-template", default=str(ROOT / "prompts" / "baseline" / "direct_sql.md"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--output", default=str(ROOT / "data" / "baseline_prompts.jsonl"))
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    direct_template = Path(args.direct_template).read_text(encoding="utf-8")
    schema = Path(args.schema).read_text(encoding="utf-8")

    with Path(args.output).open("w", encoding="utf-8", newline="\n") as handle:
        for case in cases:
            row = {
                "id": case["id"],
                "question": case["question"],
                "difficulty": case["difficulty"],
                "tags": case.get("tags", []),
                "direct_prompt": direct_template.replace("{{question}}", case["question"]),
                "sqlplus_prompt": build_sqlplus_generation_prompt(question=case["question"], schema=schema),
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(cases)} baseline prompts to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

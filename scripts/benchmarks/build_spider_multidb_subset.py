from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SUPPORTED_PATTERNS = [
    "count",
    "how many",
    "average",
    "maximum",
    "minimum",
    "ordered",
    "descending",
    "highest",
    "lowest",
    "youngest",
    "oldest",
    "most",
    "each",
]
UNSUPPORTED_SQL = [" union ", " intersect ", " except ", " nested "]


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def available_db_ids(db_root: Path) -> set[str]:
    return {path.parent.name for path in db_root.glob("*/*.sqlite")}


def is_candidate(row: dict) -> bool:
    question = row["question"].lower()
    sql = f" {row['query'].lower()} "
    if any(item in sql for item in UNSUPPORTED_SQL):
        return False
    return any(pattern in question for pattern in SUPPORTED_PATTERNS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", default=str(ROOT / "data" / "benchmarks" / "spider" / "dev.json"))
    parser.add_argument("--db-root", default=str(ROOT / "data" / "benchmarks" / "spider" / "database"))
    parser.add_argument("--per-db", type=int, default=5)
    parser.add_argument("--max-dbs", type=int, default=5)
    parser.add_argument("--output", default=str(ROOT / "data" / "benchmarks" / "spider" / "spider_multidb_candidate_subset.jsonl"))
    args = parser.parse_args()

    dev_rows = load_json(Path(args.dev))
    db_ids = available_db_ids(Path(args.db_root))
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in dev_rows:
        if row["db_id"] not in db_ids or not is_candidate(row):
            continue
        if len(grouped[row["db_id"]]) >= args.per_db:
            continue
        grouped[row["db_id"]].append(row)
        if len(grouped) >= args.max_dbs and all(len(items) >= args.per_db for items in grouped.values()):
            break

    output_rows = []
    for db_id in sorted(grouped)[: args.max_dbs]:
        for index, row in enumerate(grouped[db_id], start=1):
            output_rows.append(
                {
                    "id": f"{db_id}_{index:03d}",
                    "db_id": db_id,
                    "question": row["question"],
                    "gold_sql": row["query"],
                }
            )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in output_rows), encoding="utf-8")

    print(f"Available SQLite databases: {len(db_ids)}")
    print("Database IDs: " + ", ".join(sorted(db_ids)))
    print(f"Selected cases: {len(output_rows)}")
    print(f"Output: {output_path}")
    if len(db_ids) < 2:
        print("Warning: only one Spider SQLite database is available locally. Add the full Spider database/ directory to run true multi-db evaluation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

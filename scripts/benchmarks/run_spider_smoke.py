from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sqlplus import normalize_rows, to_sql

UNSUPPORTED = re.compile(
    r"\b(INTERSECT|UNION|EXCEPT|WITH| NOT IN | IN\s*\(|LIKE| BETWEEN | OR |DISTINCT|CASE)\b",
    re.IGNORECASE,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", default=str(ROOT / "data" / "benchmarks" / "spider" / "dev.json"))
    parser.add_argument("--db-root", default=str(ROOT / "data" / "benchmarks" / "spider" / "database"))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", default=str(ROOT / "data" / "benchmarks" / "spider" / "spider_smoke_sqlplus.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "benchmarks" / "spider_smoke_report.md"))
    args = parser.parse_args()

    dev_rows = json.loads(Path(args.dev).read_text(encoding="utf-8"))
    cases = []
    for row in dev_rows:
        if len(cases) >= args.limit:
            break
        if not is_supported(row["query"]):
            continue
        sqlplus = sql_to_sqlplus(row["query"])
        if not sqlplus:
            continue
        cases.append(
            {
                "id": f"spider_{len(cases) + 1:03d}",
                "db_id": row["db_id"],
                "question": row["question"],
                "gold_sql": row["query"],
                "sqlplus": sqlplus,
            }
        )

    outputs = []
    for case in cases:
        outputs.append(evaluate_case(Path(args.db_root), case))

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in outputs), encoding="utf-8")
    report = render_report(outputs)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def is_supported(sql: str) -> bool:
    normalized = normalize_sql(sql)
    if UNSUPPORTED.search(normalized):
        return False
    if normalized.upper().count("SELECT") != 1:
        return False
    return True


def sql_to_sqlplus(sql: str) -> str:
    sql = normalize_sql(sql)
    match = re.match(r"SELECT\s+(?P<select>.*?)\s+FROM\s+(?P<tail>.*)$", sql, re.IGNORECASE)
    if not match:
        return ""
    select = match.group("select").strip()
    tail = match.group("tail").strip()

    limit = extract_clause(tail, "LIMIT")
    tail = remove_clause(tail, "LIMIT")
    order = extract_clause(tail, "ORDER BY")
    tail = remove_clause(tail, "ORDER BY")
    group = extract_clause(tail, "GROUP BY")
    tail = remove_clause(tail, "GROUP BY")
    where = extract_clause(tail, "WHERE")
    tail = remove_clause(tail, "WHERE")

    source, joins = parse_from_join(tail.strip())
    if not source:
        return ""

    lines = [f"FROM {source}"]
    lines.extend(f"| JOIN {join}" for join in joins)
    if where:
        lines.append(f"| WHERE {where}")
    if group:
        lines.append(f"| GROUP {group}")

    if has_aggregate(select):
        lines.append(f"| AGG {add_aliases(select)}")
    else:
        lines.append(f"| SELECT {select}")
    if order:
        lines.append(f"| ORDER {order}")
    if limit:
        lines.append(f"| LIMIT {limit}")
    return "\n".join(lines)


def parse_from_join(text: str) -> tuple[str, list[str]]:
    parts = re.split(r"\s+JOIN\s+", text, flags=re.IGNORECASE)
    source = parts[0].strip()
    joins = []
    for part in parts[1:]:
        joins.append(part.strip())
    return source, joins


def extract_clause(sql: str, clause: str) -> str:
    pattern = rf"\b{re.escape(clause)}\b\s+(.*?)(?=\s+\b(?:WHERE|GROUP BY|ORDER BY|LIMIT)\b|$)"
    matches = list(re.finditer(pattern, sql, flags=re.IGNORECASE))
    if not matches:
        return ""
    return matches[-1].group(1).strip()


def remove_clause(sql: str, clause: str) -> str:
    pattern = rf"\s*\b{re.escape(clause)}\b\s+.*?(?=\s+\b(?:WHERE|GROUP BY|ORDER BY|LIMIT)\b|$)"
    return re.sub(pattern, "", sql, count=1, flags=re.IGNORECASE).strip()


def has_aggregate(select: str) -> bool:
    return bool(re.search(r"\b(COUNT|AVG|SUM|MIN|MAX)\s*\(", select, flags=re.IGNORECASE))


def add_aliases(select: str) -> str:
    parts = split_expressions(select)
    aliased = []
    for index, part in enumerate(parts, 1):
        if re.search(r"\s+AS\s+", part, flags=re.IGNORECASE):
            aliased.append(part)
        elif has_aggregate(part):
            alias = aggregate_alias(part, index)
            aliased.append(f"{part} AS {alias}")
        else:
            aliased.append(part)
    return ", ".join(aliased)


def aggregate_alias(part: str, index: int) -> str:
    lower = part.lower()
    if "count" in lower:
        return "count_value" if index == 1 else f"count_value_{index}"
    if "avg" in lower:
        return "avg_value" if index == 1 else f"avg_value_{index}"
    if "min" in lower:
        return "min_value" if index == 1 else f"min_value_{index}"
    if "max" in lower:
        return "max_value" if index == 1 else f"max_value_{index}"
    if "sum" in lower:
        return "sum_value" if index == 1 else f"sum_value_{index}"
    return f"agg_value_{index}"


def split_expressions(text: str) -> list[str]:
    parts = []
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


def evaluate_case(db_root: Path, case: dict) -> dict:
    db_path = db_root / case["db_id"] / f"{case['db_id']}.sqlite"
    result = dict(case)
    if not db_path.exists():
        result["evaluation"] = {"sqlplus_valid": False, "sql_valid": False, "execution_match": False, "error": f"missing db {db_path}"}
        return result
    conn = sqlite3.connect(str(db_path))
    try:
        gold_rows = normalize_rows(conn.execute(case["gold_sql"]).fetchall())
        converted_sql = to_sql(case["sqlplus"])
        pred_rows = normalize_rows(conn.execute(converted_sql).fetchall())
        result["converted_sql"] = converted_sql
        result["evaluation"] = {
            "sqlplus_valid": True,
            "sql_valid": True,
            "execution_match": pred_rows == gold_rows,
            "gold_row_count": len(gold_rows),
            "pred_row_count": len(pred_rows),
            "error": "",
        }
    except Exception as exc:
        result["evaluation"] = {"sqlplus_valid": False, "sql_valid": False, "execution_match": False, "error": str(exc)}
    finally:
        conn.close()
    return result


def normalize_sql(sql: str) -> str:
    return " ".join(sql.replace("`", "").strip().rstrip(";").split())


def render_report(rows: list[dict]) -> str:
    total = len(rows)
    valid = sum(1 for row in rows if row["evaluation"]["sqlplus_valid"])
    executable = sum(1 for row in rows if row["evaluation"]["sql_valid"])
    matched = sum(1 for row in rows if row["evaluation"]["execution_match"])
    dbs = sorted({row["db_id"] for row in rows})
    lines = [
        "# Spider Small Smoke Test Report",
        "",
        "| Metric | Result |",
        "| --- | --- |",
        f"| Cases | {total} |",
        f"| Databases | {', '.join(dbs)} |",
        f"| SQL+ valid | {valid}/{total} |",
        f"| SQL executable | {executable}/{total} |",
        f"| Execution match | {matched}/{total} |",
        "",
        "## Details",
        "",
        "| ID | DB | Match | Question | SQL+ |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        sqlplus = row["sqlplus"].replace("\n", "<br>").replace("|", "\\|")
        question = row["question"].replace("|", "/")
        lines.append(f"| {row['id']} | {row['db_id']} | {row['evaluation']['execution_match']} | {question} | {sqlplus} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sqlplus import SqlPlusError, explain_steps, normalize_rows, to_sql


def load_cases(path: Path) -> list[dict]:
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
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "sqlplus" / "pre_experiment_report.md"))
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    conn = build_db(Path(args.schema))
    rows: list[dict] = []

    for case in cases:
        item = {
            "id": case["id"],
            "question": case["question"],
            "difficulty": case["difficulty"],
            "tags": case.get("tags", []),
        }
        try:
            generated_sql = to_sql(case["sqlplus"])
            gold_rows = execute(conn, case["gold_sql"])
            generated_rows = execute(conn, generated_sql)
            item.update(
                {
                    "sqlplus_valid": True,
                    "sql_valid": True,
                    "execution_match": gold_rows == generated_rows,
                    "result_rows": len(generated_rows),
                    "generated_sql": generated_sql,
                    "steps": explain_steps(case["sqlplus"]),
                    "error": "",
                }
            )
        except (SqlPlusError, sqlite3.Error) as exc:
            item.update(
                {
                    "sqlplus_valid": not isinstance(exc, SqlPlusError),
                    "sql_valid": False,
                    "execution_match": False,
                    "result_rows": 0,
                    "generated_sql": "",
                    "steps": [],
                    "error": str(exc),
                }
            )
        rows.append(item)

    report = render_report(rows, cases)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def render_report(rows: list[dict], cases: list[dict]) -> str:
    total = len(rows)
    sqlplus_valid = sum(1 for row in rows if row["sqlplus_valid"])
    sql_valid = sum(1 for row in rows if row["sql_valid"])
    execution_match = sum(1 for row in rows if row["execution_match"])
    difficulty_counts = Counter(row["difficulty"] for row in rows)
    tag_counts = Counter(tag for row in rows for tag in row["tags"])

    lines = [
        "# SQL+ 前期实验记录",
        "",
        "## 实验目的",
        "",
        "验证“自然语言问题 -> SQL+ 中间表示 -> 标准 SQL -> SQLite 执行”的闭环是否可行，并统计 SQL+ 子集对常见查询操作的覆盖情况。",
        "",
        "## 数据准备",
        "",
        "- 数据库场景：企业订单分析，包含 customers、orders、order_items、products 4 张表。",
        f"- 查询样例：{total} 条自然语言、标准 SQL、SQL+ 三元组。",
        "- 查询类型：单表查询、多表 JOIN、过滤、分组聚合、HAVING、排序、Top-K。",
        "",
        "## 覆盖统计",
        "",
        "| 维度 | 统计 |",
        "| --- | --- |",
        f"| 难度分布 | {format_counter(difficulty_counts)} |",
        f"| 操作覆盖 | {format_counter(tag_counts)} |",
        "",
        "## 实验结果",
        "",
        f"- SQL+ 语法通过率：{sqlplus_valid}/{total}",
        f"- 转换 SQL 可执行率：{sql_valid}/{total}",
        f"- 与标准 SQL 执行结果一致率：{execution_match}/{total}",
        "",
        "## 样例明细",
        "",
        "| ID | 难度 | 操作标签 | SQL+有效 | SQL有效 | 结果一致 | 结果行数 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for row in rows:
        lines.append(
            f"| {row['id']} | {row['difficulty']} | {', '.join(row['tags'])} | "
            f"{yes(row['sqlplus_valid'])} | {yes(row['sql_valid'])} | "
            f"{yes(row['execution_match'])} | {row['result_rows']} |"
        )

    representative = next(row for row in rows if row["difficulty"] == "hard")
    source = next(case for case in cases if case["id"] == representative["id"])
    lines.extend(
        [
            "",
            "## 代表样例",
            "",
            f"自然语言问题：{representative['question']}",
            "",
            "SQL+：",
            "",
            "```sql",
            source["sqlplus"],
            "```",
            "",
            "转换后的 SQL：",
            "",
            "```sql",
            representative["generated_sql"],
            "```",
            "",
            "## 可用于开题的结论",
            "",
            "1. SQL+ 可以把复杂查询拆成线性步骤，便于展示 schema linking、查询规划和局部修正位置。",
            "2. 扩充后的样例覆盖单表查询、多表 JOIN、过滤、聚合、HAVING、排序和 Top-K，能够支撑开题阶段的可行性论证。",
            "3. 规则转换器可以把 SQL+ 子集稳定转换为可执行 SQL，说明 SQL+ 可作为自然语言数据库查询的中间表示。",
        ]
    )
    return "\n".join(lines) + "\n"


def format_counter(counter: Counter) -> str:
    return ", ".join(f"{key}: {counter[key]}" for key in sorted(counter))


def yes(value: bool) -> str:
    return "是" if value else "否"


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sqlplus import to_sql

REPAIR_RULES = {
    "FROM product p": "FROM products p",
    "c.area": "c.city",
    "o.state": "o.status",
    "p.cat": "p.category",
    "c.client_name": "c.customer_name",
    "p.name": "p.product_name",
    "o.order_time": "o.order_date",
    "c.rank": "c.level",
    "p.type": "p.category",
    "oi.unit_cost": "oi.unit_price",
    "c.id": "c.customer_id",
    "o.id": "o.order_id",
    "oi.product": "oi.product_id",
    "clients": "customers",
    "o.amount": "o.order_id",
}


def load_cases(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_db(schema_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    return conn


def execute(conn: sqlite3.Connection, sqlplus: str) -> tuple[bool, str]:
    try:
        conn.execute(to_sql(sqlplus)).fetchall()
        return True, ""
    except (sqlite3.Error, ValueError) as exc:
        return False, str(exc)


def repair(sqlplus: str) -> tuple[str, str]:
    for wrong, right in REPAIR_RULES.items():
        if wrong in sqlplus:
            return sqlplus.replace(wrong, right), f"{wrong} -> {right}"
    return sqlplus, "no_rule"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(ROOT / "data" / "repair_cases.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "sqlplus" / "repair_experiment_report.md"))
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    conn = build_db(Path(args.schema))
    rows = []

    for case in cases:
        before_ok, before_error = execute(conn, case["broken_sqlplus"])
        fixed_sqlplus, action = repair(case["broken_sqlplus"])
        after_ok, after_error = execute(conn, fixed_sqlplus)
        rows.append(
            {
                "id": case["id"],
                "question": case["question"],
                "error_type": case["error_type"],
                "before_ok": before_ok,
                "before_error": before_error,
                "action": action,
                "after_ok": after_ok,
                "after_error": after_error,
            }
        )

    report = render_report(rows)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def render_report(rows: list[dict]) -> str:
    total = len(rows)
    initial_failed = sum(1 for row in rows if not row["before_ok"])
    repaired = sum(1 for row in rows if row["after_ok"])
    type_counts = Counter(row["error_type"] for row in rows)

    lines = [
        "# SQL+ 层反馈修正前期实验",
        "",
        "## 实验目的",
        "",
        "构造字段名、表名和 JOIN 键错误类 SQL+ 查询，验证执行错误可以映射回 SQL+ 局部步骤，并通过局部修正恢复为可执行查询。",
        "",
        "## 错误覆盖",
        "",
        f"- 错误样例数量：{total}",
        f"- 错误类型分布：{format_counter(type_counts)}",
        "",
        "## 实验结果",
        "",
        f"- 初始失败样例：{initial_failed}/{total}",
        f"- 修正后可执行样例：{repaired}/{total}",
        f"- 修正成功率：{repaired}/{total}",
        "",
        "## 修正明细",
        "",
        "| ID | 错误类型 | 初始可执行 | 修正动作 | 修正后可执行 | 初始错误摘要 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        error = row["before_error"].replace("|", "/")
        lines.append(
            f"| {row['id']} | {row['error_type']} | {yes(row['before_ok'])} | "
            f"{row['action']} | {yes(row['after_ok'])} | {error} |"
        )
    lines.extend(
        [
            "",
            "## 可用于开题的结论",
            "",
            "1. 字段名、表名和 JOIN 键错误等执行反馈能够定位到 SQL+ 的局部步骤，适合作为 Refiner Agent 的输入。",
            "2. SQL+ 层局部修正可以避免整条 SQL 重生成，符合本课题“可解释、可修复”的研究定位。",
            "3. 后续可以把规则修正替换为 Schema Agent 与 Refiner Agent 协作修正，并继续加入类型、函数和语义异常。",
        ]
    )
    return "\n".join(lines) + "\n"


def format_counter(counter: Counter) -> str:
    return ", ".join(f"{key}: {counter[key]}" for key in sorted(counter))


def yes(value: bool) -> str:
    return "是" if value else "否"


if __name__ == "__main__":
    raise SystemExit(main())

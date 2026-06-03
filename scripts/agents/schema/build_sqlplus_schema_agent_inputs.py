from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

SCHEMA = {
    "customers": ["customer_id", "customer_name", "city", "level"],
    "products": ["product_id", "product_name", "category", "price"],
    "orders": ["order_id", "customer_id", "order_date", "status"],
    "order_items": ["item_id", "order_id", "product_id", "quantity", "unit_price"],
}

FOREIGN_KEYS = [
    "orders.customer_id = customers.customer_id",
    "order_items.order_id = orders.order_id",
    "order_items.product_id = products.product_id",
]

KNOWN_VALUES = {
    "customers.city": ["Shanghai", "Beijing", "Shenzhen", "Hangzhou"],
    "customers.level": ["gold", "silver", "bronze"],
    "orders.status": ["paid", "pending", "cancelled"],
    "products.category": ["computer", "furniture", "office"],
    "products.product_name": ["Laptop Pro", "Office Chair", "Monitor 27", "Standing Desk", "Wireless Mouse"],
}

KEYWORDS = {
    "customers": ["客户", "customer", "等级", "城市", "名称"],
    "products": ["商品", "product", "类别", "价格", "家具", "电脑"],
    "orders": ["订单", "order", "支付", "取消", "日期"],
    "order_items": ["明细", "数量", "单价", "金额", "销售"],
}


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", default=str(ROOT / "data" / "feedback_refiner_inputs_v2.jsonl"))
    parser.add_argument("--output", default=str(ROOT / "data" / "sqlplus_schema_agent_inputs.jsonl"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "agents" / "schema" / "sqlplus_schema_agent_inputs.md"))
    args = parser.parse_args()

    rows = load_jsonl(Path(args.inputs))
    enriched = []
    for row in rows:
        item = dict(row)
        item["schema_agent"] = schema_agent(row)
        enriched.append(item)

    Path(args.output).write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in enriched), encoding="utf-8")
    report = render_report(enriched)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


def schema_agent(row: dict) -> dict:
    question = row.get("question", "")
    pred = row.get("pred_sqlplus", "")
    mentioned_tables = tables_from_sqlplus(pred) | tables_from_question(question)
    if not mentioned_tables:
        mentioned_tables = {"customers", "products", "orders", "order_items"}

    columns = []
    for table in sorted(mentioned_tables):
        for column in SCHEMA[table]:
            columns.append(f"{table}.{column}")

    return {
        "relevant_tables": sorted(mentioned_tables),
        "available_columns": columns,
        "join_paths": relevant_join_paths(mentioned_tables),
        "candidate_values": KNOWN_VALUES,
        "query_intent_hints": intent_hints(question),
        "constraints": [
            "Use only supported SQL+ steps.",
            "Do not use LEFT JOIN, WITH, subqueries, or standard SQL clauses.",
            "Use exact known database values when filtering city, level, status, or category.",
        ],
    }


def tables_from_sqlplus(text: str) -> set[str]:
    tables = set()
    for table in SCHEMA:
        if re.search(rf"\b{re.escape(table)}\b", text):
            tables.add(table)
    return tables


def tables_from_question(question: str) -> set[str]:
    tables = set()
    for table, keywords in KEYWORDS.items():
        if any(keyword in question for keyword in keywords):
            tables.add(table)
    return tables


def relevant_join_paths(tables: set[str]) -> list[str]:
    if len(tables) <= 1:
        return []
    return [fk for fk in FOREIGN_KEYS if any(part.split(".")[0] in tables for part in fk.split(" = "))]


def intent_hints(question: str) -> list[str]:
    hints = []
    if any(word in question for word in ["每个", "统计", "数量", "金额", "总", "销售"]):
        hints.append("Question likely requires GROUP/AGG.")
    if any(word in question for word in ["最高", "最低", "前", "最近", "最早", "排序"]):
        hints.append("Question likely requires ORDER and possibly LIMIT.")
    if any(word in question for word in ["北京", "上海", "家具", "电脑", "取消", "支付", "之后", "之前", "高于", "低于"]):
        hints.append("Question likely requires WHERE filters and exact database values.")
    return hints


def render_report(rows: list[dict]) -> str:
    lines = [
        "# SQL+ Schema Agent Inputs",
        "",
        f"Rows: {len(rows)}",
        "",
        "| ID | Relevant Tables | Intent Hints |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        schema = row["schema_agent"]
        tables = ", ".join(schema["relevant_tables"])
        hints = "; ".join(schema["query_intent_hints"]).replace("|", "/")
        lines.append(f"| {row['id']} | {tables} | {hints} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())



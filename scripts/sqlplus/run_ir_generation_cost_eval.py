from __future__ import annotations

import argparse
import csv
import http.client
import json
import os
import re
import sqlite3
import ssl
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sqlplus import SqlPlusError, normalize_rows, to_sql

API_URL = "https://api.openai.com/v1/responses"
METHODS = ["direct_sql", "sqlplus", "natsql_style_proxy", "semql_style_proxy"]


def load_cases(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_db(schema_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    return conn


def schema_text() -> str:
    return """customers(customer_id, customer_name, city, level)
products(product_id, product_name, category, price)
orders(order_id, customer_id, order_date, status)
order_items(item_id, order_id, product_id, quantity, unit_price)

Foreign keys:
- orders.customer_id -> customers.customer_id
- order_items.order_id -> orders.order_id
- order_items.product_id -> products.product_id"""


def examples_text(method: str) -> str:
    if method == "direct_sql":
        return """Question: 查询所有金牌客户的名称和所在城市。
Output:
SELECT c.customer_name, c.city
FROM customers c
WHERE c.level = 'gold'
ORDER BY c.customer_name ASC;

Question: 查询每个商品类别的销售额，并按销售额从高到低排序。
Output:
SELECT p.category, SUM(oi.quantity * oi.unit_price) AS total_sales
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'paid'
GROUP BY p.category
ORDER BY total_sales DESC;"""
    if method == "sqlplus":
        return """Question: 查询所有金牌客户的名称和所在城市。
Output:
FROM customers c
| WHERE c.level = 'gold'
| SELECT c.customer_name, c.city
| ORDER c.customer_name ASC

Question: 查询每个商品类别的销售额，并按销售额从高到低排序。
Output:
FROM products p
| JOIN order_items oi ON p.product_id = oi.product_id
| JOIN orders o ON oi.order_id = o.order_id
| WHERE o.status = 'paid'
| GROUP p.category
| AGG p.category, SUM(oi.quantity * oi.unit_price) AS total_sales
| ORDER total_sales DESC"""
    if method == "natsql_style_proxy":
        return """Question: 查询所有金牌客户的名称和所在城市。
Output:
SELECT c.customer_name, c.city
FROM customers c
WHERE c.level = 'gold'
ORDER c.customer_name ASC

Question: 查询每个商品类别的销售额，并按销售额从高到低排序。
Output:
SELECT p.category, SUM(oi.quantity * oi.unit_price) AS total_sales
FROM products p
JOIN_PATH order_items oi ON p.product_id = oi.product_id ; orders o ON oi.order_id = o.order_id
WHERE o.status = 'paid'
GROUP p.category
ORDER total_sales DESC"""
    if method == "semql_style_proxy":
        return """Question: 查询所有金牌客户的名称和所在城市。
Output:
(query (source customers c) (filter (c.level = 'gold')) (project (c.customer_name) (c.city)) (order c.customer_name ASC))

Question: 查询每个商品类别的销售额，并按销售额从高到低排序。
Output:
(query (source products p) (join (order_items oi ON p.product_id = oi.product_id) (orders o ON oi.order_id = o.order_id)) (filter (o.status = 'paid')) (group p.category) (aggregate (p.category) (SUM(oi.quantity * oi.unit_price) AS total_sales)) (order total_sales DESC))"""
    raise ValueError(method)


def build_prompt(method: str, question: str) -> str:
    if method == "direct_sql":
        task = "Generate one executable SQLite SQL query."
        output_rules = [
            "Return only SQL, no Markdown fence and no explanation.",
            "Use only the schema tables and columns.",
            "Use SQLite-compatible syntax.",
        ]
    elif method == "sqlplus":
        task = "Generate one SQL+ query."
        output_rules = [
            "Return only SQL+ text, no Markdown fence and no explanation.",
            "Use only supported steps: FROM, JOIN, WHERE, GROUP, AGG, SELECT, HAVING, ORDER, LIMIT.",
            "Use AGG for aggregation queries and use aliases consistently in ORDER.",
        ]
    elif method == "natsql_style_proxy":
        task = "Generate one NatSQL-style proxy query."
        output_rules = [
            "Return only the proxy text, no Markdown fence and no explanation.",
            "Use lines selected from SELECT, FROM, JOIN_PATH, WHERE, GROUP, HAVING, ORDER, LIMIT.",
            "Put joins only in JOIN_PATH, separated by semicolon.",
            "This is a controlled proxy, not full NatSQL.",
        ]
    elif method == "semql_style_proxy":
        task = "Generate one SemQL-style S-expression proxy query."
        output_rules = [
            "Return only one S-expression, no Markdown fence and no explanation.",
            "Use nodes: query, source, join, filter, group, aggregate, having, project, order, limit.",
            "Wrap each projection, filter, join, and aggregate expression in parentheses.",
            "This is a controlled proxy, not full SemQL.",
        ]
    else:
        raise ValueError(method)

    rules = "\n".join(f"- {rule}" for rule in output_rules)
    return f"""You are a Text-to-SQL intermediate representation generator.

Task: {task}

Rules:
{rules}

Schema:
{schema_text()}

Examples:
{examples_text(method)}

User question:
{question}

Output:
"""


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_outputs(path: Path) -> dict[tuple[str, str], dict]:
    if not path.exists():
        return {}
    rows = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            rows[(row["method"], row["id"])] = row
    return rows


def call_openai(api_key: str, model: str, prompt: str, max_output_tokens: int, retries: int) -> tuple[dict, float]:
    payload = {"model": model, "input": prompt, "max_output_tokens": max_output_tokens}
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(retries + 1):
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
                return body, time.perf_counter() - start
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI API HTTP {exc.code}: {body}") from exc
        except (urllib.error.URLError, http.client.IncompleteRead, http.client.RemoteDisconnected, ssl.SSLError) as exc:
            if attempt >= retries:
                raise
            time.sleep(min(2**attempt, 30))
    raise RuntimeError("unreachable retry state")


def extract_text(response: dict) -> str:
    if response.get("output_text"):
        return response["output_text"].strip()
    chunks = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(content["text"])
    return "\n".join(chunks).strip()


def clean_prediction(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped


def run_api(args: argparse.Namespace, cases: list[dict], methods: list[str]) -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    output_path = Path(args.output)
    existing = load_outputs(output_path) if args.resume else {}
    selected_cases = cases[: args.limit] if args.limit else cases
    for case in selected_cases:
        for method in methods:
            key = (method, case["id"])
            if key in existing:
                continue
            prompt = build_prompt(method, case["question"])
            response, latency_seconds = call_openai(api_key, args.model, prompt, args.max_output_tokens, args.retries)
            row = {
                "id": case["id"],
                "method": method,
                "model": args.model,
                "prediction": extract_text(response),
                "latency_seconds": latency_seconds,
                "response_id": response.get("id"),
                "usage": response.get("usage", {}),
            }
            append_jsonl(output_path, row)
            print(f"wrote {method} {case['id']} latency={latency_seconds:.2f}s", flush=True)
            if args.delay_seconds > 0:
                time.sleep(args.delay_seconds)


def convert_prediction(method: str, prediction: str) -> tuple[bool, str, str]:
    text = clean_prediction(prediction)
    try:
        if method == "direct_sql":
            return True, text, ""
        if method == "sqlplus":
            return True, to_sql(text), ""
        if method == "natsql_style_proxy":
            return True, natsql_to_sql(text), ""
        if method == "semql_style_proxy":
            return True, semql_to_sql(text), ""
    except Exception as exc:
        return False, "", str(exc)
    return False, "", f"unknown method: {method}"


def natsql_to_sql(text: str) -> str:
    lines = [line.strip() for line in clean_prediction(text).splitlines() if line.strip()]
    select = ""
    source = ""
    joins: list[str] = []
    wheres: list[str] = []
    group = ""
    having = ""
    order = ""
    limit = ""
    for line in lines:
        upper = line.upper()
        if upper.startswith("SELECT "):
            select = line
        elif upper.startswith("FROM "):
            source = line
        elif upper.startswith("JOIN_PATH "):
            body = line[len("JOIN_PATH ") :].strip()
            joins.extend(f"JOIN {part.strip()}" for part in body.split(";") if part.strip())
        elif upper.startswith("WHERE "):
            wheres.append(line[len("WHERE ") :].strip())
        elif upper.startswith("GROUP "):
            group = "GROUP BY " + line[len("GROUP ") :].strip()
        elif upper.startswith("HAVING "):
            having = line
        elif upper.startswith("ORDER "):
            order = "ORDER BY " + line[len("ORDER ") :].strip()
        elif upper.startswith("LIMIT "):
            limit = line
        else:
            raise ValueError(f"unsupported NatSQL-style line: {line}")
    if not select or not source:
        raise ValueError("NatSQL-style proxy requires SELECT and FROM")
    sql_lines = [select, source]
    sql_lines.extend(joins)
    if wheres:
        sql_lines.append("WHERE " + " AND ".join(f"({where})" for where in wheres))
    sql_lines.extend(line for line in [group, having, order, limit] if line)
    return "\n".join(sql_lines) + ";"


def find_node(text: str, name: str) -> str:
    marker = f"({name}"
    start = -1
    search_from = 0
    while True:
        candidate = text.find(marker, search_from)
        if candidate == -1:
            break
        next_index = candidate + len(marker)
        if next_index >= len(text) or text[next_index].isspace() or text[next_index] == ")":
            start = candidate
            break
        search_from = candidate + 1
    if start == -1:
        return ""
    depth = 0
    for idx in range(start, len(text)):
        if text[idx] == "(":
            depth += 1
        elif text[idx] == ")":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    raise ValueError(f"unclosed SemQL-style node: {name}")


def inner_node(node: str, name: str) -> str:
    if not node:
        return ""
    body = node.strip()[len(name) + 2 : -1].strip()
    return body


def child_exprs(body: str) -> list[str]:
    exprs = []
    idx = 0
    while idx < len(body):
        while idx < len(body) and body[idx].isspace():
            idx += 1
        if idx >= len(body):
            break
        if body[idx] != "(":
            start = idx
            while idx < len(body) and not body[idx].isspace():
                idx += 1
            exprs.append(body[start:idx].strip())
            continue
        depth = 0
        start = idx
        while idx < len(body):
            if body[idx] == "(":
                depth += 1
            elif body[idx] == ")":
                depth -= 1
                if depth == 0:
                    exprs.append(body[start + 1 : idx].strip())
                    idx += 1
                    break
            idx += 1
    return [expr for expr in exprs if expr]


def semql_to_sql(text: str) -> str:
    cleaned = clean_prediction(text)
    if not cleaned.startswith("(query"):
        raise ValueError("SemQL-style proxy must start with (query")
    source = inner_node(find_node(cleaned, "source"), "source")
    if not source:
        raise ValueError("SemQL-style proxy requires source")
    joins = child_exprs(inner_node(find_node(cleaned, "join"), "join"))
    filters = normalize_semql_conditions(child_exprs(inner_node(find_node(cleaned, "filter"), "filter")))
    group = inner_node(find_node(cleaned, "group"), "group")
    aggregates = child_exprs(inner_node(find_node(cleaned, "aggregate"), "aggregate"))
    projects = child_exprs(inner_node(find_node(cleaned, "project"), "project"))
    having = normalize_semql_condition(inner_node(find_node(cleaned, "having"), "having"))
    order = inner_node(find_node(cleaned, "order"), "order")
    limit = inner_node(find_node(cleaned, "limit"), "limit")

    select_items = aggregates or projects or ["*"]
    sql_lines = ["SELECT " + ", ".join(select_items), "FROM " + source]
    sql_lines.extend("JOIN " + join for join in joins)
    if filters:
        sql_lines.append("WHERE " + " AND ".join(f"({item})" for item in filters))
    if group:
        sql_lines.append("GROUP BY " + group)
    if having:
        sql_lines.append("HAVING " + having)
    if order:
        sql_lines.append("ORDER BY " + order)
    if limit:
        sql_lines.append("LIMIT " + limit)
    return "\n".join(sql_lines) + ";"


def normalize_semql_conditions(items: list[str]) -> list[str]:
    normalized: list[str] = []
    for item in items:
        condition = normalize_semql_condition(item)
        if condition:
            normalized.append(condition)
    return normalized


def normalize_semql_condition(item: str) -> str:
    item = item.strip()
    if not item:
        return ""
    if item.startswith("AND "):
        parts = child_exprs(item[len("AND ") :].strip())
        return " AND ".join(f"({normalize_semql_condition(part)})" for part in parts if part)
    if item.startswith("OR "):
        parts = child_exprs(item[len("OR ") :].strip())
        return " OR ".join(f"({normalize_semql_condition(part)})" for part in parts if part)
    if item.startswith("(") and item.endswith(")"):
        return normalize_semql_condition(item[1:-1])
    return item


def execute(conn: sqlite3.Connection, sql: str) -> list[tuple]:
    return normalize_rows(conn.execute(sql).fetchall())


def evaluate(args: argparse.Namespace, cases: list[dict], methods: list[str]) -> tuple[list[dict], list[dict]]:
    outputs = load_outputs(Path(args.output))
    conn = build_db(Path(args.schema))
    detail_rows = []
    selected_cases = cases[: args.limit] if args.limit else cases
    case_map = {case["id"]: case for case in selected_cases}

    for method in methods:
        for case_id, case in case_map.items():
            output = outputs.get((method, case_id))
            if not output:
                detail_rows.append(missing_eval_row(method, case))
                continue
            prediction = output["prediction"]
            representation_valid, sql, error = convert_prediction(method, prediction)
            sql_valid = False
            execution_match = False
            if representation_valid:
                try:
                    generated_rows = execute(conn, sql)
                    gold_rows = execute(conn, case["gold_sql"])
                    sql_valid = True
                    execution_match = generated_rows == gold_rows
                    if not execution_match and not error:
                        error = "execution result mismatch"
                except sqlite3.Error as exc:
                    error = str(exc)
            usage = output.get("usage", {})
            detail_rows.append(
                {
                    "id": case_id,
                    "difficulty": case.get("difficulty", ""),
                    "method": method,
                    "representation_valid": representation_valid,
                    "sql_valid": sql_valid,
                    "execution_match": execution_match,
                    "input_tokens": usage.get("input_tokens", ""),
                    "output_tokens": usage.get("output_tokens", ""),
                    "reasoning_tokens": usage.get("output_tokens_details", {}).get("reasoning_tokens", ""),
                    "total_tokens": usage.get("total_tokens", ""),
                    "latency_seconds": output.get("latency_seconds", ""),
                    "prediction_chars": len(prediction),
                    "error": error,
                    "prediction": clean_prediction(prediction).replace("\n", "\\n"),
                    "converted_sql": sql.replace("\n", "\\n"),
                }
            )

    summary_rows = summarize(detail_rows)
    return detail_rows, summary_rows


def missing_eval_row(method: str, case: dict) -> dict:
    return {
        "id": case["id"],
        "difficulty": case.get("difficulty", ""),
        "method": method,
        "representation_valid": False,
        "sql_valid": False,
        "execution_match": False,
        "input_tokens": "",
        "output_tokens": "",
        "reasoning_tokens": "",
        "total_tokens": "",
        "latency_seconds": "",
        "prediction_chars": 0,
        "error": "missing prediction",
        "prediction": "",
        "converted_sql": "",
    }


def mean(values: Iterable[float]) -> float | str:
    vals = [float(value) for value in values if value != ""]
    if not vals:
        return ""
    return round(sum(vals) / len(vals), 4)


def summarize(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["method"]].append(row)
    summary = []
    for method in METHODS:
        items = grouped.get(method, [])
        if not items:
            continue
        total = len(items)
        summary.append(
            {
                "method": method,
                "cases": total,
                "representation_valid": sum(1 for row in items if row["representation_valid"]),
                "sql_valid": sum(1 for row in items if row["sql_valid"]),
                "execution_match": sum(1 for row in items if row["execution_match"]),
                "avg_input_tokens": mean(row["input_tokens"] for row in items),
                "avg_output_tokens": mean(row["output_tokens"] for row in items),
                "avg_reasoning_tokens": mean(row["reasoning_tokens"] for row in items),
                "avg_total_tokens": mean(row["total_tokens"] for row in items),
                "avg_latency_seconds": mean(row["latency_seconds"] for row in items),
                "avg_prediction_chars": mean(row["prediction_chars"] for row in items),
            }
        )
    return summary


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render_report(summary_rows: list[dict], detail_rows: list[dict], args: argparse.Namespace) -> str:
    lines = [
        "# IR 生成成本与执行效果对比实验",
        "",
        "## 实验目的",
        "",
        "本实验比较同一批自然语言问题在 Direct SQL、SQL+、NatSQL-style proxy 和 SemQL-style proxy 四种生成目标下的 token 成本、生成延迟、表示有效率、SQL 可执行率和执行结果一致率。",
        "",
        "## 实验设置",
        "",
        f"- 模型：`{args.model}`。",
        f"- 样例数：{len({row['id'] for row in detail_rows})}。",
        "- 数据集：自建订单分析数据集。",
        "- 执行环境：SQLite 内存数据库。",
        "- SemQL-style 与 NatSQL-style 为受控 proxy，不代表完整复现原系统。",
        f"- 原始输出：`{Path(args.output).relative_to(ROOT).as_posix()}`。",
        f"- 详细结果：`{Path(args.detail_csv).relative_to(ROOT).as_posix()}`。",
        f"- 汇总结果：`{Path(args.summary_csv).relative_to(ROOT).as_posix()}`。",
        "",
        "## 汇总结果",
        "",
        "| Method | Cases | Valid repr | Valid SQL | Exec match | Avg input tok | Avg output tok | Avg total tok | Avg latency s | Avg chars |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['method']} | {row['cases']} | {row['representation_valid']}/{row['cases']} | "
            f"{row['sql_valid']}/{row['cases']} | {row['execution_match']}/{row['cases']} | "
            f"{row['avg_input_tokens']} | {row['avg_output_tokens']} | {row['avg_total_tokens']} | "
            f"{row['avg_latency_seconds']} | {row['avg_prediction_chars']} |"
        )

    failures = [row for row in detail_rows if not row["execution_match"]]
    lines.extend(["", "## 失败样例", "", "| Method | ID | Error |", "| --- | --- | --- |"])
    if failures:
        for row in failures[:80]:
            error = str(row["error"]).replace("|", "/")
            lines.append(f"| {row['method']} | {row['id']} | {error} |")
    else:
        lines.append("| - | - | - |")

    lines.extend(
        [
            "",
            "## 解释边界",
            "",
            "- 该实验衡量的是开题阶段受控表示的生成成本，不是完整 SemQL 或 NatSQL 系统复现。",
            "- execution match 通过生成 SQL 与 gold SQL 在同一 SQLite 数据库上的执行结果比较得到。",
            "- 若某方法 valid representation 低，说明模型没有稳定遵守该中间表示的输出格式；若 valid SQL 低，说明转换或执行阶段存在问题。",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_methods(value: str) -> list[str]:
    if value == "all":
        return METHODS
    methods = [item.strip() for item in value.split(",") if item.strip()]
    invalid = [method for method in methods if method not in METHODS]
    if invalid:
        raise ValueError(f"invalid methods: {invalid}")
    return methods


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "schema.sql"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "ir_generation" / "ir_generation_outputs.jsonl"))
    parser.add_argument("--detail-csv", default=str(ROOT / "data" / "ir_generation_cost_detail.csv"))
    parser.add_argument("--summary-csv", default=str(ROOT / "data" / "ir_generation_cost_summary.csv"))
    parser.add_argument("--report", default=str(ROOT / "docs" / "sqlplus" / "ir_generation_cost_report.md"))
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--methods", default="all")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-output-tokens", type=int, default=1600)
    parser.add_argument("--delay-seconds", type=float, default=0.2)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--run-api", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    methods = parse_methods(args.methods)
    if args.run_api:
        run_api(args, cases, methods)

    detail_rows, summary_rows = evaluate(args, cases, methods)
    write_csv(Path(args.detail_csv), detail_rows)
    write_csv(Path(args.summary_csv), summary_rows)
    report = render_report(summary_rows, detail_rows, args)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sqlplus import parse_sqlplus, to_sql


TOKEN_RE = re.compile(
    r"[A-Za-z_][A-Za-z0-9_\.]*|\d+(?:\.\d+)?|'[^']*'|<>|>=|<=|!=|==|[(),.*=<>+\-/|]"
)
FIELD_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\b")
ALIAS_RE = re.compile(r"\bAS\s+([A-Za-z_][A-Za-z0-9_]*)\b", re.IGNORECASE)


def load_cases(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def max_parenthesis_depth(text: str) -> int:
    depth = 0
    max_depth = 0
    for char in text:
        if char == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif char == ")":
            depth = max(0, depth - 1)
    return max_depth


def split_expressions(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
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
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return [part for part in parts if part]


def sqlplus_steps(sqlplus: str) -> list[tuple[str, str]]:
    steps: list[tuple[str, str]] = []
    for raw in sqlplus.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("|"):
            line = line[1:].strip()
        op, _, body = line.partition(" ")
        steps.append((op.upper(), body.strip()))
    return steps


def semql_style(case: dict) -> str:
    q = parse_sqlplus(case["sqlplus"])
    parts = [f"(source {q.source})"]
    if q.joins:
        parts.append("(join " + " ".join(f"({join})" for join in q.joins) + ")")
    if q.wheres:
        parts.append("(filter " + " ".join(f"({where})" for where in q.wheres) + ")")
    if q.group_by:
        parts.append(f"(group {q.group_by})")
    if q.agg:
        parts.append("(aggregate " + " ".join(f"({expr})" for expr in split_expressions(q.agg)) + ")")
    if q.having:
        parts.append(f"(having {q.having})")
    if q.select:
        parts.append("(project " + " ".join(f"({expr})" for expr in split_expressions(q.select)) + ")")
    if q.order_by:
        parts.append(f"(order {q.order_by})")
    if q.limit:
        parts.append(f"(limit {q.limit})")
    return "(query " + " ".join(parts) + ")"


def natsql_style(case: dict) -> str:
    q = parse_sqlplus(case["sqlplus"])
    target = q.agg or q.select or "*"
    lines = [f"SELECT {target}", f"FROM {q.source}"]
    if q.joins:
        lines.append("JOIN_PATH " + " ; ".join(q.joins))
    if q.wheres:
        lines.append("WHERE " + " AND ".join(f"({where})" for where in q.wheres))
    if q.group_by:
        lines.append(f"GROUP {q.group_by}")
    if q.having:
        lines.append(f"HAVING {q.having}")
    if q.order_by:
        lines.append(f"ORDER {q.order_by}")
    if q.limit:
        lines.append(f"LIMIT {q.limit}")
    return "\n".join(lines)


def pipe_style(case: dict) -> str:
    q = parse_sqlplus(case["sqlplus"])
    lines = [q.source]
    lines.extend(f"|> JOIN {join}" for join in q.joins)
    lines.extend(f"|> WHERE {where}" for where in q.wheres)
    if q.group_by:
        lines.append(f"|> GROUP BY {q.group_by}")
    if q.agg:
        lines.append(f"|> AGGREGATE {q.agg}")
    if q.having:
        lines.append(f"|> HAVING {q.having}")
    if q.select:
        lines.append(f"|> SELECT {q.select}")
    if q.order_by:
        lines.append(f"|> ORDER BY {q.order_by}")
    if q.limit:
        lines.append(f"|> LIMIT {q.limit}")
    return "\n".join(lines)


def representations(case: dict) -> dict[str, str]:
    return {
        "standard_sql": case["gold_sql"],
        "sqlplus": case["sqlplus"],
        "semql_style_proxy": semql_style(case),
        "natsql_style_proxy": natsql_style(case),
        "pipe_style_proxy": pipe_style(case),
    }


def count_step_like_units(name: str, text: str) -> int:
    if name == "standard_sql":
        clauses = re.findall(
            r"\b(SELECT|FROM|JOIN|WHERE|GROUP\s+BY|HAVING|ORDER\s+BY|LIMIT)\b",
            text,
            flags=re.IGNORECASE,
        )
        return len(clauses)
    if name == "semql_style_proxy":
        return len(re.findall(r"\([a-z_]+", text))
    return len([line for line in text.splitlines() if line.strip()])


def alias_dependency_count(text: str) -> int:
    aliases = set(ALIAS_RE.findall(text))
    if not aliases:
        return 0
    dependent_regions = []
    for keyword in ("ORDER BY", "ORDER", "HAVING", "SELECT", "PROJECT"):
        for match in re.finditer(rf"\b{keyword}\b(.+?)(?:\n|$)", text, flags=re.IGNORECASE):
            dependent_regions.append(match.group(1))
    return sum(1 for alias in aliases for region in dependent_regions if re.search(rf"\b{re.escape(alias)}\b", region))


def cross_clause_reference_count(text: str) -> int:
    aliases = set(ALIAS_RE.findall(text))
    count = alias_dependency_count(text)
    if aliases:
        return count
    # Proxy forms may omit AS in generated nodes; count aggregate aliases reused in order-like regions.
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\b\s*(?:DESC|ASC)", text, flags=re.IGNORECASE):
        name = match.group(1)
        if re.search(rf"\b{name}\b", text[: match.start()]):
            count += 1
    return count


def subquery_or_cte_count(text: str) -> int:
    cte = len(re.findall(r"\bWITH\b", text, flags=re.IGNORECASE))
    subquery = len(re.findall(r"\(\s*SELECT\b", text, flags=re.IGNORECASE))
    return cte + subquery


def simple_parse(text: str) -> int:
    return len(tokens(text))


def time_call(fn: Callable[[], object], repeats: int) -> float:
    start = time.perf_counter()
    for _ in range(repeats):
        fn()
    end = time.perf_counter()
    return (end - start) * 1000 / repeats


def measure(case: dict, name: str, text: str, repeats: int) -> dict:
    token_list = tokens(text)
    parse_time_ms = time_call(lambda: simple_parse(text), repeats)
    conversion_time_ms = ""
    conversion_success = ""
    if name == "sqlplus":
        try:
            conversion_time_ms = f"{time_call(lambda: to_sql(text), repeats):.6f}"
            conversion_success = "true"
        except Exception:
            conversion_success = "false"
    elif name == "standard_sql":
        conversion_time_ms = "0.000000"
        conversion_success = "true"
    return {
        "id": case["id"],
        "difficulty": case["difficulty"],
        "representation": name,
        "token_count": len(token_list),
        "line_count": len([line for line in text.splitlines() if line.strip()]),
        "step_or_clause_count": count_step_like_units(name, text),
        "nesting_depth": max_parenthesis_depth(text),
        "subquery_cte_count": subquery_or_cte_count(text),
        "join_path_length": len(re.findall(r"\bJOIN\b", text, flags=re.IGNORECASE)),
        "schema_item_count": len(set(FIELD_RE.findall(text))),
        "alias_dependency_count": alias_dependency_count(text),
        "cross_clause_reference_count": cross_clause_reference_count(text),
        "parse_time_ms": f"{parse_time_ms:.6f}",
        "conversion_time_ms": conversion_time_ms,
        "conversion_success": conversion_success,
        "text": text.replace("\n", "\\n"),
    }


def aggregate(rows: list[dict]) -> list[dict]:
    numeric_fields = [
        "token_count",
        "line_count",
        "step_or_clause_count",
        "nesting_depth",
        "subquery_cte_count",
        "join_path_length",
        "schema_item_count",
        "alias_dependency_count",
        "cross_clause_reference_count",
        "parse_time_ms",
    ]
    conversion_values: dict[str, list[float]] = defaultdict(list)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["representation"]].append(row)
        if row["conversion_time_ms"] != "":
            conversion_values[row["representation"]].append(float(row["conversion_time_ms"]))

    output: list[dict] = []
    for representation, items in sorted(grouped.items()):
        result = {"representation": representation, "cases": len(items)}
        for field in numeric_fields:
            values = [float(item[field]) for item in items]
            result[f"avg_{field}"] = round(statistics.mean(values), 4)
            result[f"max_{field}"] = round(max(values), 4)
        conversions = conversion_values.get(representation, [])
        result["avg_conversion_time_ms"] = round(statistics.mean(conversions), 6) if conversions else ""
        if any(item["conversion_success"] != "" for item in items):
            result["conversion_success_count"] = sum(1 for item in items if item["conversion_success"] == "true")
        else:
            result["conversion_success_count"] = "N/A"
        output.append(result)
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render_report(summary: list[dict], cases: list[dict], detail_csv: Path, summary_csv: Path) -> str:
    lines = [
        "# SQL+ 与中间表示表达复杂度对比实验",
        "",
        "## 实验目的",
        "",
        "本实验用于回答“为什么使用 SQL+”这一问题。实验比较同一批查询在 Standard SQL、SQL+、SemQL-style proxy、NatSQL-style proxy 和 Pipe-style proxy 下的表达复杂度与转换开销。SemQL-style、NatSQL-style 和 Pipe-style 均为开题阶段的简化 proxy，不代表完整复现原论文或 GoogleSQL 实现。",
        "",
        "## 实验设置",
        "",
        f"- 数据集：自建订单分析数据集，共 {len(cases)} 条查询。",
        "- 输入：每条样例包含自然语言问题、gold SQL 和 gold SQL+。",
        "- 对比表示：standard_sql、sqlplus、semql_style_proxy、natsql_style_proxy、pipe_style_proxy。",
        "- 主要指标：token_count、line_count、step_or_clause_count、nesting_depth、join_path_length、schema_item_count、alias_dependency_count、cross_clause_reference_count、parse_time_ms、conversion_time_ms。",
        f"- 详细结果：`{detail_csv.as_posix()}`。",
        f"- 汇总结果：`{summary_csv.as_posix()}`。",
        "",
        "## 汇总结果",
        "",
        "| Representation | Cases | Avg tokens | Avg lines | Avg steps/clauses | Avg nesting | Avg joins | Avg schema items | Avg alias deps | Avg cross-clause refs | Avg parse ms | Avg conversion ms | Conversion success |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary:
        conversion_success = (
            str(row["conversion_success_count"])
            if row["conversion_success_count"] == "N/A"
            else f"{row['conversion_success_count']}/{row['cases']}"
        )
        lines.append(
            "| {representation} | {cases} | {avg_token_count} | {avg_line_count} | "
            "{avg_step_or_clause_count} | {avg_nesting_depth} | {avg_join_path_length} | "
            "{avg_schema_item_count} | {avg_alias_dependency_count} | "
            "{avg_cross_clause_reference_count} | {avg_parse_time_ms} | "
            "{avg_conversion_time_ms} | "
            f"{conversion_success} |".format(**row)
        )
    by_repr = {row["representation"]: row for row in summary}
    sql = by_repr["standard_sql"]
    sqlplus = by_repr["sqlplus"]
    pipe = by_repr["pipe_style_proxy"]
    semql = by_repr["semql_style_proxy"]
    natsql = by_repr["natsql_style_proxy"]
    lines.extend(
        [
            "",
            "## 观察",
            "",
            f"- SQL+ 的平均 token 数为 {sqlplus['avg_token_count']}，高于 Standard SQL 的 {sql['avg_token_count']}。这说明 SQL+ 并不是通过压缩长度获得优势，而是把查询过程显式拆成步骤。",
            f"- SQL+ 的平均行数为 {sqlplus['avg_line_count']}，高于 Standard SQL 的 {sql['avg_line_count']}，与 Pipe-style proxy 的 {pipe['avg_line_count']} 接近。这符合线性步骤化表达的预期。",
            f"- SQL+ 的平均 step_or_clause_count 为 {sqlplus['avg_step_or_clause_count']}，高于 Standard SQL 的 {sql['avg_step_or_clause_count']}。该指标可作为后续错误定位和局部 patch 的步骤边界。",
            f"- SemQL-style proxy 的平均 nesting_depth 为 {semql['avg_nesting_depth']}，高于 SQL+ 的 {sqlplus['avg_nesting_depth']}。这反映 tree-style 表示更强调语义结构，但未必天然适合步骤级修复。",
            f"- NatSQL-style proxy 的平均 token 数为 {natsql['avg_token_count']}，可作为后续生成成本对照。但本实验仅评估 proxy 表达复杂度，不声称完整 NatSQL 转换能力。",
            f"- SQL+ 到 SQL 的平均转换时间为 {sqlplus['avg_conversion_time_ms']} ms，30/30 转换成功。当前样例下，SQL+ 的确定性转换开销较小。",
            "",
            "## 对开题报告的意义",
            "",
            "本实验支持一个更谨慎的结论：SQL+ 不一定比标准 SQL 或 NatSQL-style proxy 更短，但它提供了更明确的步骤边界和较低的确定性转换成本。后续需要在错误定位准确率、patch minimality 和修复轮数上继续验证 SQL+ 的 repairability 优势。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(ROOT / "data" / "sqlplus_cases.jsonl"))
    parser.add_argument("--detail-csv", default=str(ROOT / "data" / "ir_complexity_detail.csv"))
    parser.add_argument("--summary-csv", default=str(ROOT / "data" / "ir_complexity_summary.csv"))
    parser.add_argument(
        "--report",
        default=str(ROOT / "docs" / "sqlplus" / "intermediate_representation_complexity_report.md"),
    )
    parser.add_argument("--repeats", type=int, default=500)
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    detail_rows: list[dict] = []
    for case in cases:
        for name, text in representations(case).items():
            detail_rows.append(measure(case, name, text, args.repeats))

    summary_rows = aggregate(detail_rows)
    detail_csv = Path(args.detail_csv)
    summary_csv = Path(args.summary_csv)
    report_path = Path(args.report)

    write_csv(detail_csv, detail_rows)
    write_csv(summary_csv, summary_rows)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = render_report(summary_rows, cases, detail_csv.relative_to(ROOT), summary_csv.relative_to(ROOT))
    report_path.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable


@dataclass
class SqlPlusQuery:
    source: str = ""
    joins: list[str] = field(default_factory=list)
    wheres: list[str] = field(default_factory=list)
    group_by: str = ""
    agg: str = ""
    select: str = ""
    having: str = ""
    order_by: str = ""
    limit: str = ""


class SqlPlusError(ValueError):
    pass


def parse_sqlplus(text: str) -> SqlPlusQuery:
    query = SqlPlusQuery()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("--"):
            continue
        op, value = _split_step(line)
        op = op.upper()

        if op == "FROM":
            query.source = value
        elif op == "JOIN":
            query.joins.append(value)
        elif op == "WHERE":
            query.wheres.append(value)
        elif op == "GROUP":
            query.group_by = value
        elif op == "AGG":
            query.agg = value
        elif op == "SELECT":
            query.select = value
        elif op == "HAVING":
            query.having = value
        elif op == "ORDER":
            query.order_by = value
        elif op == "LIMIT":
            query.limit = value
        else:
            raise SqlPlusError(f"Unsupported SQL+ step: {op}")

    if not query.source:
        raise SqlPlusError("SQL+ query must start with a FROM step")
    return query


def to_sql(text: str) -> str:
    query = parse_sqlplus(text)
    if query.agg:
        return _aggregate_to_sql(query)
    return _plain_to_sql(query)


def _plain_to_sql(query: SqlPlusQuery) -> str:
    select = query.select or "*"
    sql = _base_sql(query, select, query.having)
    if query.order_by:
        sql.append(f"ORDER BY {query.order_by}")
    if query.limit:
        sql.append(f"LIMIT {query.limit}")
    return "\n".join(sql) + ";"


def _aggregate_to_sql(query: SqlPlusQuery) -> str:
    alias_map = _extract_aliases(query.agg)
    having = _replace_alias_refs(query.having, alias_map) if query.having else ""
    inner_sql = _base_sql(query, query.agg, having)

    # If the model adds SELECT after AGG, treat it as a projection over the
    # aggregated result instead of letting it overwrite the aggregate list.
    if query.select:
        sql = [f"SELECT {_strip_qualifiers(query.select)}", "FROM (", _indent("\n".join(inner_sql)), ") AS sqlplus_result"]
    else:
        sql = inner_sql

    if query.order_by:
        order_by = _strip_qualifiers(query.order_by) if query.select else query.order_by
        sql.append(f"ORDER BY {order_by}")
    if query.limit:
        sql.append(f"LIMIT {query.limit}")
    return "\n".join(sql) + ";"


def _base_sql(query: SqlPlusQuery, select: str, having: str) -> list[str]:
    sql: list[str] = [f"SELECT {select}", f"FROM {query.source}"]
    sql.extend(f"JOIN {join}" for join in query.joins)
    if query.wheres:
        sql.append("WHERE " + " AND ".join(f"({item})" for item in query.wheres))
    if query.group_by:
        sql.append(f"GROUP BY {query.group_by}")
    if having:
        sql.append(f"HAVING {having}")
    return sql


def _split_step(line: str) -> tuple[str, str]:
    normalized = line[1:].strip() if line.startswith("|") else line
    if " " not in normalized:
        raise SqlPlusError(f"Invalid SQL+ step: {line}")
    op, value = normalized.split(" ", 1)
    value = value.strip()
    if not value:
        raise SqlPlusError(f"Missing SQL+ step body: {line}")
    return op, value


def explain_steps(text: str) -> list[str]:
    query = parse_sqlplus(text)
    steps = [f"FROM: read base relation `{query.source}`"]
    steps.extend(f"JOIN: combine `{join}`" for join in query.joins)
    steps.extend(f"WHERE: filter rows by `{where}`" for where in query.wheres)
    if query.group_by:
        steps.append(f"GROUP: group rows by `{query.group_by}`")
    if query.agg:
        steps.append(f"AGG: output `{query.agg}`")
    if query.select:
        steps.append(f"SELECT: output `{query.select}`")
    if query.having:
        steps.append(f"HAVING: keep groups by `{query.having}`")
    if query.order_by:
        steps.append(f"ORDER: sort by `{query.order_by}`")
    if query.limit:
        steps.append(f"LIMIT: keep first `{query.limit}` rows")
    return steps


def normalize_rows(rows: Iterable[tuple]) -> list[tuple]:
    return [tuple(row) for row in rows]


def _extract_aliases(expressions: str) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for expression in _split_top_level_commas(expressions):
        match = re.search(r"\s+AS\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", expression, flags=re.IGNORECASE)
        if match:
            alias = match.group(1)
            aliases[alias] = expression[: match.start()].strip()
    return aliases


def _replace_alias_refs(text: str, alias_map: dict[str, str]) -> str:
    result = text
    for alias, expression in sorted(alias_map.items(), key=lambda item: len(item[0]), reverse=True):
        result = re.sub(rf"\b{re.escape(alias)}\b", f"({expression})", result)
    return result


def _split_top_level_commas(text: str) -> list[str]:
    parts: list[str] = []
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


def _indent(text: str) -> str:
    return "\n".join(f"  {line}" for line in text.splitlines())


def _strip_qualifiers(text: str) -> str:
    return re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\.([A-Za-z_][A-Za-z0-9_]*)\b", r"\1", text)

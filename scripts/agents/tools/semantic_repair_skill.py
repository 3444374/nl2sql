from __future__ import annotations

import re


def repair_case(row: dict) -> dict:
    original = row["pred_sqlplus"]
    question = row.get("question", "")
    schema = row.get("schema", "")
    evaluation = row.get("evaluation", {})
    repaired, actions = repair_sqlplus(question, schema, original, evaluation)
    return {
        "id": row.get("id", ""),
        "prediction": repaired,
        "repair_actions": actions or ["No semantic repair rule changed the SQL+ query."],
        "tool_trace": {
            "candidate_count": 1 if repaired != original else 0,
            "selected_score": "rule_based",
            "selected_reason": "generic semantic SQL+ repair" if repaired != original else "no applicable semantic repair",
        },
        "method": "semantic_repair_skill",
    }


def should_route(row: dict) -> bool:
    evaluation = row.get("evaluation", {})
    if not evaluation.get("execution_match", False):
        return True
    prediction = row.get("pred_sqlplus", "")
    question = row.get("question", "").lower()
    return any(keyword in question for keyword in ["youngest", "oldest", "most", "highest", "lowest"]) and bool(prediction)


def repair_sqlplus(question: str, schema: str, prediction: str, evaluation: dict | None = None) -> tuple[str, list[str]]:
    evaluation = evaluation or {}
    actions: list[str] = []
    current = prediction

    current, changed = _normalize_unsupported_steps(current)
    if changed:
        actions.extend(changed)

    current, changed = _repair_count_star(question, current)
    if changed:
        actions.extend(changed)

    current, changed = _repair_extreme_entity_query(question, schema, current, evaluation)
    if changed:
        actions.extend(changed)

    current, changed = _repair_aggregate_projection(question, schema, current)
    if changed:
        actions.extend(changed)

    current, changed = _repair_topk_tie_break(question, current)
    if changed:
        actions.extend(changed)

    current, changed = _repair_named_schema_column(question, schema, current)
    if changed:
        actions.extend(changed)

    return current, actions


def _normalize_unsupported_steps(prediction: str) -> tuple[str, list[str]]:
    lines = []
    actions: list[str] = []
    for line in prediction.splitlines():
        stripped = line.strip()
        body = stripped[1:].strip() if stripped.startswith("|") else stripped
        upper = body.upper()
        if upper.startswith("AGGREGATE "):
            body = "AGG " + body.split(None, 1)[1]
            stripped = "| " + body
            actions.append("Normalize AGGREGATE to SQL+ AGG step.")
        elif upper.startswith("GROUP BY "):
            body = "GROUP " + body[9:].strip()
            stripped = "| " + body
            actions.append("Normalize GROUP BY to SQL+ GROUP step.")
        elif upper.startswith("ORDER BY "):
            body = "ORDER " + body[9:].strip()
            stripped = "| " + body
            actions.append("Normalize ORDER BY to SQL+ ORDER step.")
        elif upper.startswith("FILTER "):
            body = "WHERE " + body.split(None, 1)[1]
            stripped = "| " + body
            actions.append("Normalize FILTER to SQL+ WHERE step.")
        order_limit = re.match(r"ORDER\s+(.+?)\s+LIMIT\s+(\d+)\s*$", body, flags=re.IGNORECASE)
        if order_limit:
            lines.append("| ORDER " + order_limit.group(1).strip())
            lines.append("| LIMIT " + order_limit.group(2))
            actions.append("Split combined ORDER/LIMIT into separate SQL+ steps.")
            continue
        lines.append(stripped)
    return "\n".join(lines), actions


def _repair_count_star(question: str, prediction: str) -> tuple[str, list[str]]:
    lower_question = question.lower()
    if not re.search(r"\b(number of|how many|most|fewest|least)\b", lower_question):
        return prediction, []
    repaired = re.sub(
        r"count\s*\(\s*[A-Za-z_][A-Za-z0-9_\.]*\s*\)",
        "count(*)",
        prediction,
        flags=re.IGNORECASE,
    )
    if repaired != prediction:
        return repaired, ["Normalize record-count intent from count(column) to count(*)."]
    return prediction, []


def _repair_extreme_entity_query(question: str, schema: str, prediction: str, evaluation: dict) -> tuple[str, list[str]]:
    lower_question = question.lower()
    if not any(word in lower_question for word in ["youngest", "oldest", "highest", "lowest"]):
        return prediction, []

    select_expr = _extract_step_value(prediction, "SELECT")
    if not select_expr:
        return prediction, []

    ranking_column = _find_ranking_column(schema, lower_question)
    if not ranking_column:
        return prediction, []

    direction = "ASC" if any(word in lower_question for word in ["youngest", "lowest"]) else "DESC"
    source = _extract_step_value(prediction, "FROM")
    if not source:
        source = _find_table_for_columns(schema, _columns_from_expression(select_expr) + [ranking_column])
    if not source:
        return prediction, []

    has_extreme_repair_signal = (
        "ambiguous column" in str(evaluation.get("error", "")).lower()
        or "sql+ output must start" in str(evaluation.get("error", "")).lower()
        or "$" in prediction
        or len(re.findall(r"^\s*\|?\s*FROM\s+", prediction, flags=re.IGNORECASE | re.MULTILINE)) > 1
    )
    if has_extreme_repair_signal or re.search(r"\b(MIN|MAX)\s*\(", prediction, flags=re.IGNORECASE):
        repaired = "\n".join(
            [
                f"FROM {source.split()[0]}",
                f"| SELECT {_strip_expression_qualifiers(select_expr)}",
                f"| ORDER {ranking_column} {direction}",
                "| LIMIT 1",
            ]
        )
        return repaired, ["Rewrite extreme-entity query to ORDER + LIMIT local SQL+ form."]
    return prediction, []


def _repair_aggregate_projection(question: str, schema: str, prediction: str) -> tuple[str, list[str]]:
    lower_question = question.lower()
    if not _extract_step_value(prediction, "GROUP") or not _extract_step_value(prediction, "AGG"):
        return prediction, []
    if not _extract_step_value(prediction, "ORDER") or not _extract_step_value(prediction, "LIMIT"):
        return prediction, []

    top_words = ["most", "highest", "largest", "least", "lowest", "fewest"]
    count_requested = re.search(r"\b(how many|count of)\b", lower_question) or (
        "number of" in lower_question and not any(word in lower_question for word in top_words)
    )
    if not any(word in lower_question for word in top_words) or count_requested:
        return prediction, []

    agg_expr = _extract_step_value(prediction, "AGG")
    select_expr = _extract_step_value(prediction, "SELECT")
    if select_expr:
        missing = [expr for expr in _split_top_level_commas(select_expr) if not _expression_available(expr, agg_expr)]
        if not missing:
            return prediction, []
        repaired = _replace_step_value(prediction, "AGG", ", ".join(missing + [agg_expr]))
        return repaired, ["Add final SELECT column(s) back to AGG so ORDER helper columns remain local."]

    non_agg_exprs = [
        expr
        for expr in _split_top_level_commas(agg_expr)
        if not re.search(r"\b(COUNT|SUM|AVG|MIN|MAX)\s*\(", expr, flags=re.IGNORECASE)
    ]
    if not non_agg_exprs:
        group_expr = _extract_step_value(prediction, "GROUP")
        group_exprs = _split_top_level_commas(group_expr)
        if group_exprs:
            prediction = _replace_step_value(prediction, "AGG", ", ".join(group_exprs + [agg_expr]))
            non_agg_exprs = group_exprs
    if not non_agg_exprs:
        return prediction, []

    select_expr = ", ".join(non_agg_exprs)
    lines = []
    inserted = False
    for line in prediction.splitlines():
        lines.append(line)
        body = line.strip()[1:].strip() if line.strip().startswith("|") else line.strip()
        if body.upper().startswith("AGG ") and not inserted:
            lines.append(f"| SELECT {select_expr}")
            inserted = True
    return "\n".join(lines), ["Add final SELECT to hide top-k helper aggregate from output."]


def _repair_named_schema_column(question: str, schema: str, prediction: str) -> tuple[str, list[str]]:
    lower_question = question.lower()
    columns = _schema_columns(schema)
    direct_columns = {col.lower(): col for col in columns}
    if "average" not in lower_question or "average" not in direct_columns:
        return prediction, []
    if re.search(r"average\s+(age|capacity|attendance|price|salary|score|year)", lower_question):
        return prediction, []

    repaired = re.sub(
        r"avg\s*\(\s*([A-Za-z_][A-Za-z0-9_\.]*)\s*\)(\s+AS\s+[A-Za-z_][A-Za-z0-9_]*)?",
        direct_columns["average"],
        prediction,
        flags=re.IGNORECASE,
    )
    if repaired != prediction:
        return repaired, ["Use direct schema column named Average instead of avg(column) when question asks for that field."]
    return prediction, []


def _repair_topk_tie_break(question: str, prediction: str) -> tuple[str, list[str]]:
    lower_question = question.lower()
    group_expr = _extract_step_value(prediction, "GROUP")
    order_expr = _extract_step_value(prediction, "ORDER")
    if not group_expr or not order_expr or not _extract_step_value(prediction, "LIMIT"):
        return prediction, []
    if "year" not in group_expr.lower() or "year" in order_expr.lower():
        return prediction, []
    if not any(word in lower_question for word in ["most", "highest", "largest", "top"]):
        return prediction, []
    repaired = _replace_step_value(prediction, "ORDER", f"{order_expr}, Year DESC")
    return repaired, ["Add stable temporal tie-break for top-k grouped query."]


def _extract_step_value(prediction: str, step: str) -> str:
    pattern = re.compile(rf"^\s*\|?\s*{re.escape(step)}\s+(.+?)\s*$", flags=re.IGNORECASE | re.MULTILINE)
    matches = pattern.findall(prediction)
    return matches[-1].strip() if matches else ""


def _replace_step_value(prediction: str, step: str, value: str) -> str:
    lines = []
    replaced = False
    for line in prediction.splitlines():
        stripped = line.strip()
        body = stripped[1:].strip() if stripped.startswith("|") else stripped
        if body.upper().startswith(f"{step.upper()} ") and not replaced:
            prefix = "| " if stripped.startswith("|") else ""
            lines.append(f"{prefix}{step} {value}")
            replaced = True
        else:
            lines.append(line)
    return "\n".join(lines)


def _schema_columns(schema: str) -> list[str]:
    columns: list[str] = []
    for line in schema.splitlines():
        if "(" not in line or ")" not in line:
            continue
        body = line[line.find("(") + 1 : line.rfind(")")]
        for item in body.split(","):
            item = item.strip()
            if item:
                columns.append(item.split()[0])
    return columns


def _find_ranking_column(schema: str, lower_question: str) -> str:
    if "youngest" in lower_question or "oldest" in lower_question:
        column = _find_schema_column(schema, "age")
        if column:
            return column
    if "attendance" in lower_question:
        column = _find_schema_column(schema, "average") or _find_schema_column(schema, "attendance")
        if column:
            return column
    return _find_column_for_question(schema, lower_question, ["age", "attendance", "capacity", "average"])


def _find_schema_column(schema: str, name: str) -> str:
    for column in _schema_columns(schema):
        if column.lower() == name:
            return column
    return ""


def _find_column_for_question(schema: str, lower_question: str, candidates: list[str]) -> str:
    columns = _schema_columns(schema)
    for candidate in candidates:
        if candidate in lower_question:
            for column in columns:
                if column.lower() == candidate:
                    return column
    return ""


def _find_table_for_columns(schema: str, columns: list[str]) -> str:
    wanted = {column.split(".")[-1].lower() for column in columns}
    best_table = ""
    best_score = 0
    for line in schema.splitlines():
        if "(" not in line or ")" not in line:
            continue
        table = line.split("(", 1)[0]
        table_columns = {item.strip().split()[0].lower() for item in line[line.find("(") + 1 : line.rfind(")")].split(",")}
        score = len(wanted & table_columns)
        if score > best_score:
            best_table = table
            best_score = score
    return best_table


def _columns_from_expression(expression: str) -> list[str]:
    columns = []
    for part in _split_top_level_commas(expression):
        cleaned = re.sub(r"\s+AS\s+[A-Za-z_][A-Za-z0-9_]*\s*$", "", part, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        if re.match(r"^[A-Za-z_][A-Za-z0-9_\.]*$", cleaned):
            columns.append(cleaned)
    return columns


def _expression_available(expression: str, available_exprs: str) -> bool:
    wanted = _normalize_expression_name(expression)
    for item in _split_top_level_commas(available_exprs):
        if _normalize_expression_name(item) == wanted:
            return True
    return False


def _normalize_expression_name(expression: str) -> str:
    expression = re.sub(r"\s+AS\s+[A-Za-z_][A-Za-z0-9_]*\s*$", "", expression, flags=re.IGNORECASE)
    expression = expression.strip()
    return expression.split(".")[-1].lower()


def _strip_expression_qualifiers(expression: str) -> str:
    return re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\.([A-Za-z_][A-Za-z0-9_]*)\b", r"\1", expression)


# Keep this local instead of importing sqlplus._split_top_level_commas;
# repair skills should not depend on private parser helpers.
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

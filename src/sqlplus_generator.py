from __future__ import annotations

from textwrap import dedent


CANONICAL_SQLPLUS_GENERATOR_VERSION = "sqlplus-generator-v1"


def build_sqlplus_generation_prompt(
    *,
    question: str,
    schema: str,
    value_hints: list[str] | None = None,
) -> str:
    """Build the canonical SQL+ generation prompt used across datasets."""
    value_section = ""
    if value_hints:
        hints = "\n".join(f"- {item}" for item in value_hints)
        value_section = f"""

Database value hints:
{hints}
"""

    return dedent(
        f"""
        You are the SQL+ Generator Agent for a Text-to-SQL experiment.

        Task:
        Generate one SQL+ query for the natural-language question.

        SQL+ is a linear intermediate representation. It starts with `FROM`,
        then uses pipe steps. It is not standard SQL.

        Supported SQL+ syntax:
        FROM table [alias]
        | JOIN table [alias] ON condition
        | WHERE condition
        | GROUP columns
        | AGG expressions
        | SELECT expressions
        | HAVING condition
        | ORDER expression [ASC|DESC]
        | LIMIT n

        Hard output rules:
        - Output SQL+ only. No markdown, no explanation.
        - The first non-empty line must start with exactly: FROM
        - Every later non-empty line must start with: |
        - Use SQL+ step names exactly: FROM, JOIN, WHERE, GROUP, AGG, SELECT, HAVING, ORDER, LIMIT.
        - Do not output standard SQL. Never write SELECT ... FROM ..., GROUP BY, ORDER BY, AGGREGATE, FILTER, HAVING BY, WITH, UNION, INTERSECT, EXCEPT, subqueries, CASE, BETWEEN, LIKE, or OR.
        - Use only tables and columns in the schema.
        - Use aliases only when needed for joins or disambiguation.
        - Use one `WHERE` step per condition when possible.

        Semantic rules:
        - For aggregate queries, use `AGG`.
        - For grouped aggregate queries, put group/output columns and aggregate expressions in `AGG`.
        - If an aggregate alias is needed for `ORDER`, define it in `AGG` and reuse the alias in `ORDER`.
        - If an aggregate result is only needed for ranking, keep it in `AGG`, then add `SELECT` with only the columns requested by the question.
        - In `HAVING`, prefer the full aggregate expression, for example `HAVING SUM(amount) > 10000`, not `HAVING total_amount > 10000`.
        - For youngest/oldest/highest/lowest entity questions, prefer `ORDER` plus `LIMIT 1`. Do not create a self-join with MIN/MAX unless the question asks to output the min/max value itself.
        - For top-k grouped questions, compute the ranking measure in `AGG`, sort by its alias, and use `LIMIT` when the question asks for only the top result.
        - Preserve literal values from the database or value hints. Do not translate stored values.

        Database schema:
        {schema.strip()}
        {value_section}
        Question:
        {question}

        SQL+:
        """
    ).strip()

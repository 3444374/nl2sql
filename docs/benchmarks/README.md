# Benchmarks Index

## Spider Smoke Test

- `spider_smoke_report_10.md`: first 10 Spider dev examples, SQL+ conversion smoke test.
- `spider_smoke_report_20.md`: first 20 supported Spider dev examples from `concert_singer`, SQL+ conversion smoke test.

Current result:

- Cases: 20
- Database: `concert_singer`
- SQL+ valid: 20/20
- SQL executable: 20/20
- Execution match: 20/20

Scope note:

This is not a full Spider leaderboard benchmark. It is a small supported-subset smoke test for opening-stage feasibility evidence. The subset covers count, selection, filtering, ordering, limit, grouping, aggregation, and simple join queries.

## Spider SQL+ Multi-Agent End-to-End Test

- `spider_sqlplus_multi_agent_e2e_report.md`: first end-to-end run with a loose generation prompt.
- `spider_sqlplus_multi_agent_e2e_report_v2.md`: stricter SQL+ generation prompt with explicit SQL+ examples and strict SQL+ output validation.
- `spider_sqlplus_multi_agent_e2e_report_v3_router_repair.md`: fresh v3 output re-evaluated through the formal Skill Router -> semantic repair skill path.
- `spider_multidb_extension_report.md`: multi-database Spider extension readiness report.

Current end-to-end results:

- Cases: 20
- Database: `concert_singer`
- Model: `gpt-5-mini`
- Pipeline: Spider question + schema -> SQL+ Generator Agent -> SQL+ parser / translator -> SQLite executor -> one Refiner round on parser/execution error -> generic semantic repair skill -> offline execution-match evaluation
- Fresh v3 run before post-hoc generic repair completion: SQL+ valid 19/20, SQL executable 19/20, execution match 19/20.
- Fresh v3 output after `Skill Router -> semantic repair skill` re-evaluation: SQL+ valid 20/20, SQL executable 20/20, execution match 20/20.
- Average total tokens: 1160.3.
- Average latency seconds: 8.7563.

Scope note:

This is the actual end-to-end generation test on the Spider subset. Gold SQL is used only for offline evaluation, not for generation or repair. The generic semantic repair skill uses question wording, schema columns, SQL+ structure, parser feedback, and execution feedback; it does not use Spider case IDs, database-specific hard-coded rules, or gold SQL. This result should not be confused with the SQL+ conversion smoke test above, where Spider gold SQL was first mapped to SQL+ and then converted back to SQL.

## Spider Multi-Database Extension

Current local data availability:

- `dev.json` and `tables.json` are present.
- Only one SQLite database is currently available locally: `concert_singer`.
- `scripts/benchmarks/build_spider_multidb_subset.py` has been added to scan available Spider SQLite databases and build a candidate JSONL subset.
- True multi-database accuracy cannot be claimed until the full Spider `database/` directory is added locally.

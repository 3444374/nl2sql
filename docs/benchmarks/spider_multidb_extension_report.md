# Spider Multi-Database Extension Report

## Purpose

This report records the first step toward multi-database Spider evaluation for the SQL+ multi-agent pipeline.

The goal is to move beyond the single `concert_singer` subset and test whether the SQL+ Generator -> Translator -> Executor -> Skill Router -> semantic repair skill workflow generalizes across schemas.

## Current Local Data Availability

| Item | Result |
| --- | --- |
| Spider dev metadata | `data/benchmarks/spider/dev.json` available |
| Spider table metadata | `data/benchmarks/spider/tables.json` available |
| Local SQLite databases detected | 1 |
| Available database | `concert_singer` |
| Generated candidate subset | `data/benchmarks/spider/spider_multidb_candidate_subset.jsonl` |
| Candidate cases selected | 5 |

Current blocker: the local workspace only contains `data/benchmarks/spider/database/concert_singer/concert_singer.sqlite`. True multi-database evaluation requires adding the full Spider `database/` directory.

## Implemented Support

- `scripts/benchmarks/build_spider_multidb_subset.py` scans local Spider SQLite databases and selects supported dev examples per database.
- `scripts/benchmarks/run_spider_multi_agent_sqlplus.py` already accepts `--cases`, so the same end-to-end pipeline can run on the generated multi-db subset after more database files are present.
- `scripts/agents/pipeline/spider_sqlplus_repair_router.py` routes benchmark SQL+ failures to reusable repair skills.
- `scripts/agents/tools/semantic_repair_skill.py` implements generic SQL+ semantic repair without using Spider case IDs, database-specific hard-coded rules, or gold SQL.

## Verification Commands

```powershell
python -B scripts/benchmarks/build_spider_multidb_subset.py --per-db 5 --max-dbs 5
python -B scripts/benchmarks/run_spider_multi_agent_sqlplus.py --cases data/benchmarks/spider/spider_multidb_candidate_subset.jsonl --limit 5 --dry-run
python -B -c "import sys; sys.path.insert(0,'scripts/agents/pipeline'); sys.path.insert(0,'scripts/agents/tools'); import spider_sqlplus_repair_router, semantic_repair_skill; print('router_import_ok')"
```

Observed output:

```text
Available SQLite databases: 1
Database IDs: concert_singer
Selected cases: 5
Warning: only one Spider SQLite database is available locally. Add the full Spider database/ directory to run true multi-db evaluation.
router_import_ok
```

## Current Result Boundary

No multi-database accuracy claim is made yet. The current `20/20` result remains limited to the Spider `concert_singer` 20-case subset.

The next valid experiment is to add more Spider SQLite databases locally, rebuild the candidate subset, and run:

```powershell
$env:OPENAI_API_KEY=[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User')
python -B scripts/benchmarks/build_spider_multidb_subset.py --per-db 5 --max-dbs 5
python -B scripts/benchmarks/run_spider_multi_agent_sqlplus.py --cases data/benchmarks/spider/spider_multidb_candidate_subset.jsonl --model gpt-5-mini --repair-rounds 1 --use-generic-repair --output outputs/benchmarks/spider_multidb_sqlplus_e2e.jsonl --report docs/benchmarks/spider_multidb_sqlplus_e2e_report.md
```

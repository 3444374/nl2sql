# Repairability Metrics Report

This report compares repair-stage metrics after the IR generation-cost experiment.

Scope notes:

- SQL+ uses `Critic Agent -> Skill Router -> Repair Skills -> Executor` on the current 13-case SQL+ known-failure set.
- Direct SQL uses the existing single Refiner Agent outputs. The earlier OpenAI run did not record per-call latency, so direct repair latency is marked as N/A.
- SQL+ repair token cost counts the Step-wise Critic Agent usage. Local deterministic repair skills add no model tokens.
- SQL+ repair latency measures local router and repair-skill execution only. Critic API latency was not captured in the earlier run.
- Patch minimality is an offline metric computed against gold differences and is not used to choose repairs.

Overlap IDs for cross-method subset: q002, q003, q004, q005, q013, q019, q021, q022, q025

## Summary

| Method | Cases | Success | Localization Acc. | Strict Minimal Patch | Avg Patch Minimality | Avg Rounds | Avg Repair Tokens | Avg Repair Latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| direct_sql_feedback_refiner | 14 | 6/14 | 0.8571 | 0.8571 | 0.8571 | 1 | 1609.3571 | N/A |
| sqlplus_critic_router_skills | 13 | 13/13 | 0.7692 | 0.9231 | 0.9744 | 2.2308 | 3813.9231 | 0.0005 |
| direct_sql_feedback_refiner_overlap | 9 | 4/9 | 0.8889 | 0.8889 | 0.8889 | 1 | 1583.2222 | N/A |
| sqlplus_critic_router_skills_overlap | 9 | 9/9 | 0.7778 | 0.8889 | 0.9630 | 2.3333 | 4001.7778 | 0.0007 |

## Router Accuracy

| Method | Router Accuracy |
| --- | ---: |
| direct_sql_feedback_refiner | N/A |
| sqlplus_critic_router_skills | 1.0000 |
| direct_sql_feedback_refiner_overlap | N/A |
| sqlplus_critic_router_skills_overlap | 1.0000 |

## Detail

| Method | ID | Success | Expected Steps | Localized Steps | Changed Steps | Minimality | Rounds | Tokens | Latency Note |
| --- | --- | ---: | --- | --- | --- | ---: | ---: | ---: | --- |
| sqlplus_critic_router_skills | q002 | True | ORDER | ORDER | ORDER | 1.0000 | 1 | 3600 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q003 | True | ORDER | ORDER | ORDER | 1.0000 | 1 | 3103 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q004 | True | WHERE | WHERE | WHERE | 1.0000 | 1 | 3713 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q005 | True | ORDER | ORDER | ORDER | 1.0000 | 1 | 3538 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q006 | True | SELECT | LIMIT,ORDER | SELECT | 1.0000 | 2 | 3767 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q013 | True | AGG,GROUP,ORDER | JOIN,WHERE | AGG,GROUP,ORDER | 1.0000 | 5 | 4076 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q015 | True | AGG,ORDER | ORDER | AGG,ORDER | 1.0000 | 2 | 3571 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q017 | True | ORDER,WHERE | WHERE | ORDER,WHERE | 1.0000 | 2 | 2991 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q019 | True | JOIN,ORDER | ORDER | ORDER | 1.0000 | 2 | 3965 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q021 | True | AGG,GROUP,WHERE | WHERE | AGG,GROUP,ORDER | 0.6667 | 4 | 4091 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q022 | True | AGG,GROUP,JOIN,ORDER,WHERE | AGG,GROUP,JOIN,SELECT | AGG,GROUP,JOIN,ORDER,WHERE | 1.0000 | 3 | 5537 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q025 | True | JOIN,ORDER,SELECT | WHERE | JOIN,ORDER,SELECT | 1.0000 | 3 | 4393 | local deterministic router+skills only; critic API latency was not captured |
| sqlplus_critic_router_skills | q026 | True | ORDER,WHERE | WHERE | ORDER,WHERE | 1.0000 | 2 | 3236 | local deterministic router+skills only; critic API latency was not captured |
| direct_sql_feedback_refiner | q002 | True | WHERE | WHERE | WHERE | 1.0000 | 1 | 1142 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q003 | True | ORDER | LIMIT,ORDER | ORDER | 1.0000 | 1 | 1383 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q004 | False | WHERE | WHERE | - | 0.0000 | 1 | 1847 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q005 | True | ORDER | LIMIT,ORDER | ORDER | 1.0000 | 1 | 1366 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q007 | True | GROUP,WHERE | WHERE | WHERE | 1.0000 | 1 | 1453 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q008 | False | GROUP,WHERE | AGG,GROUP,HAVING | WHERE | 1.0000 | 1 | 1584 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q013 | False | GROUP,JOIN,ORDER,SELECT,WHERE | WHERE | ORDER | 1.0000 | 1 | 1585 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q016 | False | GROUP,SELECT | WHERE | - | 0.0000 | 1 | 1873 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q019 | True | ORDER | LIMIT,ORDER | ORDER | 1.0000 | 1 | 1380 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q021 | False | GROUP,SELECT,WHERE | WHERE | WHERE | 1.0000 | 1 | 1299 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q022 | False | GROUP,JOIN,ORDER,SELECT,WHERE | AGG,GROUP,HAVING | JOIN,WHERE | 1.0000 | 1 | 2350 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q023 | True | GROUP,JOIN,WHERE | AGG,GROUP,HAVING | JOIN,WHERE | 1.0000 | 1 | 1721 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q025 | False | JOIN,ORDER,SELECT | WHERE | ORDER | 1.0000 | 1 | 1897 | not captured by the earlier OpenAI refiner run |
| direct_sql_feedback_refiner | q027 | False | GROUP,JOIN,ORDER,SELECT | AGG,GROUP,HAVING | ORDER | 1.0000 | 1 | 1651 | not captured by the earlier OpenAI refiner run |

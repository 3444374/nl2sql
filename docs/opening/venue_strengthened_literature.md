# 精读文献来源强化建议

本文档用于解决开题精读文献中 arXiv 比例偏高的问题。原则是：15 篇精读文献尽量优先选择 ACL/EMNLP/AAAI/NeurIPS/ICML/ICLR/PVLDB 等正式发表或权威 proceedings 来源；少量 arXiv 可作为前沿补充，但不宜成为精读清单主体。

## 现有 15 篇来源评估

| 当前序号 | 文献 | 当前来源强度 | 说明 |
| --- | --- | --- | --- |
| 1 | Spider | 强 | EMNLP 2018，Text-to-SQL 基础 benchmark，适合保留 |
| 2 | BIRD | 强 | NeurIPS Datasets and Benchmarks 2023，适合保留 |
| 3 | Spider 2.0 | 强 | ICLR 2025，适合保留 |
| 4 | IRNet/SemQL | 强 | ACL 2019，直接支撑中间表示，适合保留 |
| 5 | NatSQL | 中-强 | Findings of EMNLP 2021，直接相关；若导师严格要求主会，可作为次级保留 |
| 6 | Pipe Syntax in SQL | 强 | PVLDB 2024，数据库方向权威来源，适合保留 |
| 7 | RAT-SQL | 强 | ACL 2020，schema linking 代表工作，适合保留 |
| 8 | PICARD | 强 | EMNLP 2021，约束解码代表工作，适合保留 |
| 9 | RESDSQL | 强 | AAAI 2023，schema linking 与 skeleton parsing 解耦；已替换原 DAIL-SQL 精读位 |
| 10 | DIN-SQL | 强 | NeurIPS 2023，分解式 Text-to-SQL，适合保留 |
| 11 | MAC-SQL | 中 | COLING 2025，主题很贴近多智能体，但若严格按 A 会可替换或放到扩展阅读 |
| 12 | CHESS | 强 | ICML 2025，执行验证/schema 选择方向，适合保留 |
| 13 | CHASE-SQL | 强 | ICLR 2025，候选生成与选择方向，适合保留 |
| 14 | SQL-Factory | 强 | PVLDB，数据生成和多智能体流程，适合保留 |
| 15 | LEVER | 强 | ICML 2023，基于执行结果学习 verifier；已替换原 SQLCritic 精读位 |

## 更稳的 15 篇精读清单建议

这版兼顾“来源稳”和“课题相关”。它不一定完全替代现有清单，但更适合开题答辩时展示。

| 建议序号 | 文献 | 来源类型 | 放入理由 |
| --- | --- | --- | --- |
| 1 | Yu 等，Spider | EMNLP 2018 | 基础 benchmark，说明复杂跨域 Text-to-SQL 的问题定义 |
| 2 | Yu 等，SyntaxSQLNet | EMNLP 2018 | 早期复杂 SQL 结构建模代表，可补强传统 Text-to-SQL 基线 |
| 3 | Guo 等，IRNet/SemQL | ACL 2019 | 中间表示代表工作，直接支撑 SQL+ 设计动机 |
| 4 | Wang 等，RAT-SQL | ACL 2020 | schema linking 和关系感知编码代表工作 |
| 5 | Scholak 等，PICARD | EMNLP 2021 | 语法约束解码代表工作，可对照 SQL+ parser/converter |
| 6 | Gan 等，NatSQL | Findings of EMNLP 2021 | Text-to-SQL 专用 SQL 简化表示，和 SQL+ 最直接可比 |
| 7 | Li 等，RESDSQL | AAAI 2023 | decoupling schema linking and skeleton parsing，适合补强 schema/skeleton 路线 |
| 8 | Pourreza 等，DIN-SQL | NeurIPS 2023 | 分解式生成和自修正，支撑 step-wise 生成/修复 |
| 9 | Li 等，BIRD | NeurIPS Datasets and Benchmarks 2023 | 真实数据库 benchmark，补强公开评测来源 |
| 10 | Shute 等，Pipe Syntax in SQL | PVLDB 2024 | SQL 管道式语法和表达顺序问题，支撑 SQL+ 线性表达 |
| 11 | Talaei 等，CHESS | ICML 2025 | schema 选择、检索、执行验证，贴近反馈修正闭环 |
| 12 | Pourreza 等，CHASE-SQL | ICLR 2025 | 多路径推理与候选选择，支撑候选生成/验证思想 |
| 13 | Lei 等，Spider 2.0 | ICLR 2025 | 企业级 Text-to-SQL workflow，说明真实场景复杂性 |
| 14 | Li 等，SQL-Factory | PVLDB | 多智能体 SQL 数据生成，可作为后续数据扩充参考 |
| 15 | Ni 等，LEVER | ICML 2023 | 学习基于执行结果验证 language-to-code 候选，支撑 Executor/Critic 的候选验证思想 |

## 可替换候选

如果导师特别强调“不要 arXiv”，建议优先替换这几篇：

| 原文献 | 替换建议 | 理由 |
| --- | --- | --- |
| DAIL-SQL | RESDSQL | RESDSQL 是 AAAI 2023 正式论文，更适合作为 15 篇精读中的 schema linking/skeleton parsing 主证据；DAIL-SQL 可保留为扩展参考 |
| MAC-SQL | 若保留多智能体主题，可作为扩展阅读；严格 A 会清单中可换 CHESS/CHASE/SQL-Factory | MAC-SQL 主题贴近，但 venue 不如 AAAI/ICLR/ICML/PVLDB 稳 |
| SQLCritic | LEVER | SQLCritic 主题贴近 critic，但目前更适合作为扩展阅读；LEVER 是 ICML 2023 正式论文，可支撑 execution-feedback verifier 和候选筛选思想 |

## 答辩表述建议

可以这样向老师解释文献选择：

> 精读文献不是简单堆最新 arXiv，而是按课题技术路线组织：Spider/BIRD/Spider 2.0 支撑 benchmark 和真实场景，IRNet/NatSQL/Pipe Syntax 支撑中间表示和 SQL+ 设计，RAT-SQL/RESDSQL/PICARD 支撑 schema linking 与约束生成，DIN-SQL/CHESS/CHASE-SQL/SQL-Factory 支撑分解、执行验证、多候选和多智能体流程，LEVER 支撑 execution-feedback verifier 和候选筛选思想。少量 arXiv 工作只作为最新发展补充，不作为核心证据来源。

## 后续处理建议

1. 精读主清单已将 DAIL-SQL、SQLCritic 替换为 RESDSQL、LEVER，以提高正式发表/权威来源比例。
2. 将 DAIL-SQL、SQLCritic 标成“扩展阅读/前沿工作”，不作为 15 篇精读主证据。
3. 如果导师要求严格 A 会口径，优先使用 ACL/EMNLP/AAAI/NeurIPS/ICML/ICLR/PVLDB/SIGMOD 来源。
4. 精读笔记中每篇都记录“发表来源、论文链接、本地 PDF、核验状态”，避免答辩时被问到来源说不清。

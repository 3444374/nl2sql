# 精读论文笔记

本文档专门记录 15 篇开题精读论文的逐篇笔记。阅读顺序和总表见 `docs/opening/intensive_reading_plan.md`。

每篇笔记采用 `academic-research-suite` 中 bibliography/source verification 的基本要求：先记录文献来源、原始出处、可访问链接和核验状态，再整理问题、方法、实验、贡献、局限、与本课题关系和答辩问法。若只核验到论文页面而未下载/逐页阅读 PDF，必须明确写成“来源已核验，全文精读待补”。

本地 PDF 统一保存于 `docs/opening/papers/`。下载来源、文件名和 SHA256 校验见 `docs/opening/papers/README.md`。

## 1. Yu 等，Spider

### 0. 文献来源与核验

- 完整题名：Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task
- 作者：Tao Yu, Rui Zhang, Kai Yang, Michihiro Yasunaga, Dongxu Wang, Zifan Li, James Ma, Irene Li, Qingning Yao, Shanelle Roman, Zilin Zhang, Dragomir R. Radev
- 发表来源：EMNLP 2018 long paper，ACL Anthology 收录，论文页码 3911-3921。
- DOI：10.18653/v1/D18-1425。
- arXiv：1809.08887，初版提交于 2018-09-24，v5 修订于 2019-02-02；开题引用优先使用 ACL Anthology/EMNLP 正式版本。
- 官方数据集页面：论文指向 Yale LILY Spider 页面。
- 本地 PDF：`docs/opening/papers/01_spider_yu_2018.pdf`。
- 本地图片：`docs/opening/paper_figures/01_spider_fig1_dataset_annotation.png`，从本地 PDF 第 1 页裁剪。
- 本次核验来源：ACL Anthology 元数据页、ACL Anthology PDF、本地 PDF。
- 来源质量：正式会议论文，来源强；属于 Text-to-SQL benchmark 类基础文献。
- 核验状态：来源已核验，PDF 已下载并从本地 PDF 抽取关键图。

![Spider Figure 1: 数据库 schema 到复杂问题/SQL 标注示例](paper_figures/01_spider_fig1_dataset_annotation.png)

图 1 是读 Spider 时最关键的图。它说明 Spider 不是只给一个单表问题，而是让标注者先理解多表 schema、主外键关系，再写出包含 JOIN、GROUP BY、HAVING、嵌套 SELECT 的复杂 SQL。对本课题来说，这张图直接解释了为什么“自然语言 -> SQL”不是简单翻译，而是要处理 schema linking、join path、aggregation、nested query 等多个结构性子问题。

### 1. 一句话定位

Spider 是 Text-to-SQL 领域的基础跨数据库复杂查询 benchmark，它把任务重点从“在同一个数据库上记忆 SQL 模板”推进到“面对新数据库 schema 和新 SQL 结构进行泛化”。这篇论文的价值不是提出新模型，而是重新定义了更难、更接近真实场景的 Text-to-SQL 评测任务。

### 2. 作者要解决的问题

论文指出，早期语义解析和 Text-to-SQL 数据集常存在两个问题：

- 训练集和测试集可能共享相同数据库、相似 SQL 模板或同一逻辑形式的不同问法，模型可以靠记忆 question-SQL pattern 取得较高分数。
- 很多数据集只覆盖简单 SQL 或单表查询，无法测试 JOIN、GROUP BY、ORDER BY、嵌套查询、集合操作等复杂结构。

Spider 的目标是构造一个跨领域、多表、复杂 SQL 的人工标注数据集，让模型必须同时理解自然语言问题、数据库 schema 和 SQL 结构。

### 3. 核心方法

Spider 的核心不是提出一个模型，而是提出数据集和评测任务：

- 数据集包含 200 个多表数据库、10,181 个自然语言问题、5,693 条唯一复杂 SQL，覆盖 138 个领域。
- 数据集按 database split 组织，训练、开发、测试中的数据库不重叠，模型必须泛化到新 schema。
- SQL 按 easy、medium、hard、extra hard 分级，用来分析模型在不同复杂度上的表现。
- 评测指标包括 component matching、exact matching 和 execution accuracy。论文也提醒 execution accuracy 可能有 false positive，因为错误 SQL 也可能偶然返回相同结果。
- 数据构建投入约 1,000 man-hours，由 11 名大学生标注和审核，包含数据库收集、问题/SQL 标注、SQL 审查、问题复审/改写和最终处理。

这里要抓住一个关键点：Spider 的 database split 让模型在测试时面对未见过的数据库，输入不只是 question，还必须包括 schema。也就是说，Text-to-SQL 的难点从“语言到固定 SQL 模板”变成“语言 + schema 到新 SQL 结构”。

### 4. 实验设置与主要结果

论文测试了 Seq2Seq、Seq2Seq+Attention、Seq2Seq+Copying、Iyer 等方法、SQLNet、TypeSQL 等当时代表模型。关键结果如下：

- Example split 下，TypeSQL 总体 exact matching 为 34.3%。
- Database split 下，TypeSQL 总体 exact matching 只有 9.7%。
- Database split 下，TypeSQL 在 hard 和 extra hard 上都只有 2.3% 和 0.3%，说明复杂 SQL 结构泛化非常困难。
- Component matching 中，database split 下 TypeSQL 的 SELECT F1 为 36.2%，WHERE F1 为 14.7%，GROUP BY F1 为 6.4%，这说明错误并不只来自自然语言理解，SQL 子结构和 schema 对齐也是主要瓶颈。

需要注意：arXiv 摘要页中提到“best model achieves 12.4% exact matching accuracy”，ACL 论文 PDF 摘要和正文表格中记录的 database split 最好 exact matching 是 9.7%。开题答辩中如果提数值，建议只说“早期模型在 Spider database split 上表现很低，论文报告的 TypeSQL exact match 约 9.7%”，避免纠缠版本差异。

### 5. 关键贡献

- 提供了大规模、多领域、多表、复杂 SQL 的人工标注 Text-to-SQL benchmark。
- 引入 database split，迫使模型泛化到未见过的数据库 schema，而不是记忆数据库特定模板。
- 明确区分 SQL 难度等级，使后续研究能够按查询复杂度分析模型短板。
- 提供官方评测思路，推动 Text-to-SQL 研究从单表/简单查询走向复杂跨域场景。

### 6. 局限性

- Spider 主要评测从自然语言到单条 SQL 的生成，不覆盖真实企业环境中的多步数据分析 workflow。
- 论文明确排除部分需要外部知识、常识推理或复杂数学计算的问题。
- 数据库规模和 schema 复杂度低于真实企业数仓或云数据库场景，这也是后续 BIRD、Spider 2.0 继续扩展的原因。
- execution accuracy 虽然补充了 exact matching，但可能因为结果集偶然一致产生误判。
- 论文的 baseline 模型已经比较早，不代表当前 LLM Text-to-SQL 水平；精读时要把 Spider 作为 benchmark/问题定义文献，而不是当前最强方法文献。

### 7. 和本课题的关系

Spider 是本课题 benchmark 迁移和 smoke test 的基础背景。本项目当前只在 Spider dev 的小规模受支持子集上完成 `20/20` smoke test，不能表述为完整 Spider benchmark 成绩。Spider 对本课题最重要的启发有四点：

- SQL 复杂结构和 schema 泛化是 Text-to-SQL 的核心难点，支持“直接生成 SQL 容易出错”的研究动机。
- SQL 难度分级和 component-level 评测启发本课题按 value、ORDER、aggregation、join、projection 等错误类型做局部诊断与修复。
- database split 的设计说明后续不能只在自建 order 数据集上验证，还需要逐步迁移到公开 benchmark 子集。
- Figure 1 中的复杂 SQL 是线性的自然语言问题和非线性的 SQL 结构之间的典型张力：SQL+ 正是希望用 step-wise 中间表示降低这种结构映射难度。

### 8. 可用于开题答辩的说法

可以这样讲：Spider 是 Text-to-SQL 领域最重要的早期复杂跨域 benchmark 之一，它通过多表数据库、复杂 SQL 和 database split 避免模型只记忆模板。它证明了面对新数据库 schema 和复杂 SQL 结构时，传统模型性能会大幅下降。本课题使用 SQL+ 中间表示和反馈修正机制，正是针对复杂 SQL 结构生成和修复困难这一问题展开。当前 Spider 相关结果只作为小规模 smoke test，不能作为完整 benchmark 分数。

### 9. 可能被老师追问的问题

- 问：Spider 和 WikiSQL 有什么区别？
  答：WikiSQL 主要是单表、简单 SELECT/WHERE 查询；Spider 是多表、多领域、复杂 SQL，并且使用 database split 测试新 schema 泛化。
- 问：为什么 Spider 对你的课题重要？
  答：它把 Text-to-SQL 难点从模板记忆推进到复杂 SQL 和 schema 泛化，支撑我提出 SQL+ 中间表示与局部修复机制的必要性。
- 问：你现在是否跑了完整 Spider？
  答：没有。当前只是 Spider dev 上一个受支持小子集的 smoke test，结果是 20/20，用来验证 SQL+ 表达和转换机制的初步迁移可行性。
- 问：Spider 的 exact matching 和 execution accuracy 有什么区别？
  答：exact matching 检查 SQL 结构是否和 gold 匹配；execution accuracy 检查执行结果是否一致。后者可以容忍语法结构不同但语义等价的 SQL，但也可能出现错误 SQL 偶然返回相同结果的 false positive。

### 10. 精读结论

Spider 应作为“benchmark 背景”和“复杂 SQL/schema 泛化问题来源”来读，而不是作为本课题方法直接对比的完整实验对象。对开题最有用的结论是：复杂 SQL 生成的主要难点不只是自然语言理解，还包括 schema linking、JOIN 路径、聚合、嵌套结构和跨数据库泛化；这些正好对应 SQL+ 与多智能体反馈修正要处理的问题。

## 2. Li 等，BIRD

### 0. 文献来源与核验

- 完整题名：Can LLM Already Serve as A Database Interface? A Big Bench for Large-Scale Database Grounded Text-to-SQLs
- 常用简称：BIRD，即 BIg bench for laRge-scale Database grounded in text-to-SQL。
- 作者：Jinyang Li, Binyuan Hui, Ge Qu, Jiaxi Yang, Binhua Li, Bowen Li, Bailin Wang, Bowen Qin, Ruiying Geng, Nan Huo, Xuanhe Zhou, Chenhao Ma, Guoliang Li, Kevin C. C. Chang, Fei Huang, Reynold Cheng, Yongbin Li
- 发表来源：NeurIPS 2023 Datasets and Benchmarks Track，OpenReview 标注为 Spotlight。
- 官方页面：NeurIPS proceedings 和 BIRD benchmark 官方站点。
- 本地 PDF：`docs/opening/papers/02_bird_li_2023.pdf`，已替换为 NeurIPS 官方 proceedings 版。
- 本地图片：`docs/opening/paper_figures/02_bird_neurips_fig1_challenges.png`，从本地 PDF 第 2 页裁剪。
- 来源质量：正式 benchmark track 论文，来源强；属于真实数据库 Text-to-SQL benchmark 文献。
- 核验状态：来源已核验，PDF 已下载并从本地 PDF 抽取关键图。

![BIRD Figure 1: 真实数据库 Text-to-SQL 的三类挑战](paper_figures/02_bird_neurips_fig1_challenges.png)

图 1 是 BIRD 最适合放入精读笔记的图。它把 BIRD 相比 Spider 的新增难点压缩成三类：第一，真实数据库值可能很脏，比如金额字段是字符串，需要清洗后才能聚合；第二，自然语言问题和数据库值之间需要外部知识映射，比如“weekly issue issuance statement”对应数据库里的捷克语取值；第三，同样语义正确的 SQL 可能执行效率差异很大，真实数据库场景不能只看结果是否正确。

### 1. 一句话定位

BIRD 是面向真实大规模数据库的 Text-to-SQL benchmark，它把评测重点从 Spider 的“复杂 SQL 和跨 schema 泛化”进一步推进到“真实数据库值、外部知识 grounding 和 SQL 执行效率”。

### 2. 作者要解决的问题

论文的出发点是：Spider 和 WikiSQL 等 benchmark 虽然推动了 Text-to-SQL 研究，但它们和真实应用仍有距离。主要差距包括：

- 数据库规模偏小，很多评测更关注 schema，而不是大量真实 database values。
- 数据库值比较干净，缺少真实业务数据中的脏值、缩写、编码、单位、格式混乱等问题。
- 很多问题需要外部知识才能把自然语言条件映射到数据库值。
- 传统 exact match 或 execution accuracy 主要看“能不能得到正确结果”，很少考虑 SQL 执行效率。

因此 BIRD 提出的问题不是“模型会不会写 SQL”，而是“LLM 是否已经能作为真实数据库接口”。论文给出的回答是否定的。

### 3. 核心方法

BIRD 的核心贡献是构造更贴近真实场景的数据集和评测方式：

- 数据集包含 12,751 个 text-to-SQL 样例。
- 包含 95 个数据库，总大小 33.4 GB，覆盖 37 个专业领域。
- 数据库来源包括 Kaggle、CTU Prague Relational Learning Repository，以及人工构建/整理的开放表格。
- 数据集显式引入外部知识证据 `K`，把任务形式从 `Y = f(Q, D | theta)` 扩展为 `Y = f(Q, D, K | theta)`。
- 提出 Valid Efficiency Score, VES，用来在 SQL 有效和结果正确的前提下评价执行效率。

和 Spider 相比，BIRD 的重点不只是 SQL 结构复杂，而是真实数据库环境里的 value comprehension。也就是说，模型不仅要知道该 SELECT 哪些列、JOIN 哪些表，还要理解数据库值本身。

### 4. 实验设置与主要结果

论文评测了两类主流方法：

- Fine-tuning 路线：例如 T5。
- In-context learning 路线：例如 ChatGPT、Claude-2、GPT-4。

关键结果：

- GPT-4 在 BIRD 上 execution accuracy 为 54.89%。
- 人类表现为 92.96%。
- GPT-4 和人类之间仍有明显差距，说明真实数据库 Text-to-SQL 远没有被 LLM 解决。
- 论文还分析了 SQL 执行效率，强调在大数据库上“结果正确但执行低效”的 SQL 对工业场景仍然不可接受。

这里要注意，BIRD 的结论不能简单理解成“GPT-4 不行”。更准确的说法是：当任务加入真实数据库值、外部知识和效率约束后，Text-to-SQL 从语义解析问题变成了“语义解析 + 数据库值理解 + 领域知识映射 + 查询优化”的综合问题。

### 5. 关键贡献

- 提供了比 Spider 更贴近真实数据库应用的 benchmark。
- 将 database values 提升为 Text-to-SQL 的核心难点，而不是只关注 schema。
- 引入外部知识证据，强调自然语言和数据库值之间常需要额外 grounding。
- 提出 VES，将 SQL 执行效率纳入评测。
- 用 GPT-4、Claude-2 等 LLM 实验证明：即使强模型在真实数据库场景中仍有明显短板。

### 6. 局限性

- BIRD 是 benchmark 论文，不直接提出新的 SQL 生成或修复框架。
- 数据库虽然更真实、更大，但仍然是离线评测集，不完全等同于企业生产环境中的权限、事务、时效数据和多轮分析流程。
- 外部知识由数据集提供，真实场景中外部知识如何发现、验证和注入仍是开放问题。
- VES 能推动效率评估，但具体效率受数据库系统、索引、硬件和查询优化器影响，跨环境比较需要谨慎。

### 7. 和本课题的关系

BIRD 对本课题的作用是提供“后续真实数据库扩展方向”，而不是当前实验结果来源。本项目当前核心仍是 SQL+ 中间表示和反馈修正，在自建 order 数据集与小规模 Spider smoke test 上验证。BIRD 可以支撑以下论点：

- 真实 Text-to-SQL 不只是 SQL 结构生成，还需要处理 value grounding 和外部知识。
- 本课题的 value lookup repair skill 可以和 BIRD 的 database value comprehension 难点对应起来。
- SQL+ 如果后续进入真实数据库场景，需要扩展对脏值、单位、编码、别名、外部知识和效率反馈的表达。
- 当前不能声称在 BIRD 上取得结果，只能说 BIRD 是后续 benchmark 迁移和真实场景验证的参考。

### 8. 可用于开题答辩的说法

可以这样讲：BIRD 是 NeurIPS 2023 Datasets and Benchmarks Track 的真实数据库 Text-to-SQL benchmark，它在 Spider 的基础上进一步强调大规模数据库值、外部知识 grounding 和 SQL 执行效率。论文显示 GPT-4 在 BIRD 上 execution accuracy 只有 54.89%，远低于人类的 92.96%，说明 LLM 还不能直接作为可靠数据库接口。本课题当前没有宣称完成 BIRD benchmark，而是把 BIRD 作为后续从自建数据集和 Spider 子集走向真实数据库场景的参考。

### 9. 可能被老师追问的问题

- 问：BIRD 和 Spider 最大区别是什么？
  答：Spider 主要强调跨数据库 schema 泛化和复杂 SQL 结构；BIRD 更强调真实数据库值、外部知识和 SQL 执行效率，数据库规模也更大。
- 问：为什么 BIRD 对你的课题有价值？
  答：它说明真实场景下 Text-to-SQL 错误不只来自 SQL 语法结构，还来自 value grounding、外部知识和效率问题，这和本课题的执行反馈、value 修复、局部 repair skill 可以衔接。
- 问：你是否已经跑了 BIRD？
  答：没有。当前只是把 BIRD 作为后续扩展 benchmark 和真实数据库场景参考，不能把现有 SQL+ 实验结果表述为 BIRD 结果。
- 问：VES 和 execution accuracy 有什么不同？
  答：execution accuracy 关注结果是否正确；VES 在有效正确的基础上进一步考虑 SQL 执行效率，更贴近大数据库工业场景。

### 10. 精读结论

BIRD 应作为“真实数据库难点”和“后续扩展方向”来读。它补足了 Spider 没充分覆盖的部分：真实脏值、外部知识和效率约束。对本课题来说，BIRD 的意义在于提醒 SQL+ 后续不能只表达 SQL 结构，还要考虑 value grounding、执行反馈和查询效率；但开题阶段必须明确当前结果不是 BIRD benchmark 成绩。

## 3. Lei 等，Spider 2.0

### 0. 文献来源与核验

- 完整题名：Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows
- 作者：Fangyu Lei, Jixuan Chen, Yuxiao Ye, Ruisheng Cao, Dongchan Shin, Hongjin Su, Zhaoqing Suo, Hongcheng Gao, Wenjing Hu, Pengcheng Yin, Victor Zhong, Caiming Xiong, Ruoxi Sun, Qian Liu, Sida I. Wang, Tao Yu
- 发表来源：ICLR 2025 conference paper，OpenReview 收录。
- 官方 URL：https://openreview.net/pdf?id=XmProj9cPs
- 本地 PDF：`docs/opening/papers/03_spider2_lei_2024.pdf`，已替换为 ICLR/OpenReview 官方 PDF。
- 本地图片：`docs/opening/paper_figures/03_spider2_fig1_workflow_environment.png`，从本地 PDF 第 2 页裁剪。
- 来源质量：正式 ICLR 会议论文，来源强；属于企业级 Text-to-SQL workflow benchmark 文献。
- 核验状态：来源已核验，PDF 已下载并从本地 PDF 抽取关键图。

![Spider 2.0 Figure 1: 企业级 Text-to-SQL workflow 环境](paper_figures/03_spider2_fig1_workflow_environment.png)

图 1 是 Spider 2.0 的核心图。它说明任务输入不再只是一个自然语言问题加一个 schema，而是一个完整的 Text-to-SQL workflow environment：数据库可能来自 BigQuery、Snowflake 等系统，旁边还有数据库元数据、外部知识、SQL dialect 文档、query interface、项目代码库和 execution feedback。模型需要在这个环境中生成 SQL、Python 或多步查询流程。

### 1. 一句话定位

Spider 2.0 是面向真实企业级 Text-to-SQL workflow 的 benchmark，它把任务从“生成一条 SQL”推进到“在复杂数据库、文档、代码库和执行环境中完成多步数据工作流”。

### 2. 作者要解决的问题

Spider 和 BIRD 已经推动了复杂 SQL、跨 schema 泛化和真实数据库值的研究，但它们仍然和企业级数据工作流有距离。Spider 2.0 指出真实企业环境中的 Text-to-SQL 通常具有这些特点：

- 数据存放在不同数据库系统中，例如 BigQuery、Snowflake、SQLite、DuckDB 等。
- 不同系统有不同 SQL dialect，模型需要查阅 dialect documentation。
- schema 很大，数据库经常包含超过 1,000 个 columns，有些场景有数千列。
- 任务可能需要理解 project-level codebase，例如 dbt 项目、宏、模型文件、schema.yml、SQL 脚本等。
- 输出不一定是一条短 SQL，可能是多条 SQL、Python/Shell 辅助脚本或超过 100 行的复杂查询流程。

因此，Spider 2.0 要解决的是传统 Text-to-SQL benchmark 与真实企业数据工作流之间的差距。

### 3. 核心方法

Spider 2.0 构造了一个更接近真实工作流的评测框架：

- 包含 632 个 real-world text-to-SQL workflow problems。
- 问题来自 enterprise-level database use cases。
- 数据库来自真实数据应用，包含本地数据库和云数据库系统。
- 任务要求模型理解数据库元数据、SQL dialect 文档、外部知识和项目代码库。
- 引入 code agent 形式，让模型与复杂 SQL workflow environment 交互，而不是只在静态输入上输出 SQL。
- 还提出 Spider 2.0-lite 和 Spider 2.0-snow 等设置，便于比较不同程度的任务复杂度。

从任务形式看，Spider 2.0 已经接近“数据库智能体评测”，而不是传统 semantic parsing 评测。

### 4. 实验设置与主要结果

论文基于 o1-preview 构建 code agent framework 进行评测，并和 Spider 1.0、BIRD 上的表现作对比。关键结果：

- 在 Spider 2.0 上，code agent framework 只成功解决 21.3% 的任务。
- 相比之下，在 Spider 1.0 上为 91.2%，在 BIRD 上为 73.0%。
- 这说明当前语言模型在传统 Text-to-SQL benchmark 上看似很强，但在真实企业 workflow 中仍明显不足。
- 论文还强调，Spider 2.0 中的 SQL 查询经常需要长上下文、多步推理、多种操作和执行反馈。

这组数字很适合答辩使用，但必须讲清楚：它是论文自己的评测结果，不是本项目的实验结果。

### 5. 关键贡献

- 将 Text-to-SQL benchmark 从单条 SQL 生成扩展到真实企业级 workflow。
- 把数据库元数据、SQL dialect 文档、项目代码库和执行环境纳入评测。
- 强调多 SQL、多步骤、长上下文、复杂 schema 和 cloud database system。
- 证明 LLM 在 Spider 1.0/BIRD 上的高分不能代表它已经能处理企业级 Text-to-SQL workflow。
- 为后续数据库智能体、代码智能体和执行反馈系统提供了更真实的评测方向。

### 6. 局限性

- Spider 2.0 是高复杂度 benchmark，复现实验和完整运行成本较高。
- 任务更接近 agentic workflow，因此不同 agent 框架、工具权限、上下文管理和执行环境会影响结果。
- 对开题阶段的小型原型来说，Spider 2.0 更适合作为研究趋势和后续扩展方向，而不是当前必须完成的 benchmark。
- 企业级 workflow 的评测比单条 SQL 更复杂，指标设计和可比性也更难。

### 7. 和本课题的关系

Spider 2.0 对本课题非常重要，但它的位置是“远期真实工作流参照”，不是当前实验基准。它支持以下论点：

- SQL+ 的 step-wise 表达和 repair loop 有必要，因为真实任务往往本来就是多步 workflow，而不是单条 SQL。
- 本课题的 `Natural language -> SQL+ -> SQL -> execution feedback -> Critic -> Skill Router -> Repair Skill` 路线，与 Spider 2.0 强调的 execution feedback 和 agentic workflow 有方向一致性。
- 当前项目的 Spider smoke test 只是小规模受支持子集，不应和 Spider 2.0 结果混淆。
- 后续如果扩展到企业级场景，需要增加 SQL dialect、metadata retrieval、project codebase understanding 和 long-context execution feedback。

### 8. 可用于开题答辩的说法

可以这样讲：Spider 2.0 是 ICLR 2025 的企业级 Text-to-SQL workflow benchmark。它说明真实数据场景中，Text-to-SQL 不再是给定一个 schema 后生成一条 SQL，而是要结合数据库元数据、SQL 方言文档、项目代码库和执行反馈完成多步工作流。论文中基于 o1-preview 的 code agent 在 Spider 2.0 上只解决 21.3% 的任务，而在 Spider 1.0 和 BIRD 上分别达到 91.2% 和 73.0%，说明传统 benchmark 的高分不能直接代表真实企业可用性。本课题当前不声称完成 Spider 2.0，只将它作为后续真实工作流扩展的依据。

### 9. 可能被老师追问的问题

- 问：Spider 2.0 和 Spider 1.0 有什么本质区别？
  答：Spider 1.0 主要是自然语言到单条 SQL 的跨数据库评测；Spider 2.0 是企业级 workflow，包含数据库文档、SQL dialect、代码库、执行接口和多步 SQL/Python 操作。
- 问：Spider 2.0 和 BIRD 的区别是什么？
  答：BIRD 强调大规模真实数据库值、外部知识和执行效率；Spider 2.0 更进一步强调企业级 workflow、项目代码库、SQL 方言和多步执行环境。
- 问：你的项目和 Spider 2.0 有什么关系？
  答：本项目的 SQL+ 和多智能体反馈修正路线与 Spider 2.0 的 agentic workflow 方向一致，但当前实验还停留在自建数据集和 Spider 小子集 smoke test，Spider 2.0 是后续扩展目标。
- 问：为什么不能把当前 Spider smoke test 说成 Spider 2.0 能力？
  答：因为当前只是 Spider dev 的小规模受支持 SQL 子集，验证 SQL+ 表达和转换可行性；Spider 2.0 涉及企业级 workflow、SQL 方言、代码库和复杂执行环境，难度和评测目标不同。

### 10. 精读结论

Spider 2.0 应作为“真实企业级 workflow 趋势”来读。它强化了本课题的长期意义：如果 Text-to-SQL 走向真实应用，就不能只依赖一次性 SQL 生成，而需要中间表示、执行反馈、诊断、修复和 agentic workflow。对开题而言，Spider 2.0 可以支撑研究必要性和未来扩展方向，但不能被包装成当前已完成的实验结果。

## 4. Guo 等，IRNet/SemQL

### 0. 文献来源与核验

- 完整题名：Towards Complex Text-to-SQL in Cross-Domain Database with Intermediate Representation
- 方法简称：IRNet；中间表示简称 SemQL。
- 作者：Jiaqi Guo, Zecheng Zhan, Yan Gao, Yan Xiao, Jian-Guang Lou, Ting Liu, Dongmei Zhang
- 发表来源：ACL 2019 long paper，Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics，页码 4524-4535。
- DOI：10.18653/v1/P19-1444。
- 官方 URL：https://aclanthology.org/P19-1444/
- 本地 PDF：`docs/opening/papers/04_irnet_semql_guo_2019.pdf`。
- 本地图片：`docs/opening/paper_figures/04_irnet_fig1_mismatch_example.png`；`docs/opening/paper_figures/04_irnet_fig2_3_semql_grammar_tree.png`。
- 来源质量：ACL 正式会议论文，来源强；属于 Text-to-SQL 中间表示与 schema linking 方向的代表性工作。
- 核验状态：来源已核验，PDF 已下载，已从本地 PDF 抽取关键图。

![IRNet Figure 1: 自然语言意图与 SQL 实现细节不匹配](paper_figures/04_irnet_fig1_mismatch_example.png)

这张图是 IRNet 的核心动机图。自然语言只说“grade higher than 5 and have at least 2 friends”，但 SQL 里必须出现 `GROUP BY T1.student_id` 和 `HAVING count(*) >= 2`。也就是说，用户意图里没有显式说出 SQL 实现细节，模型却必须补出这些结构。IRNet 把这类问题称为 natural language intent 和 SQL implementation details 的 mismatch。

![IRNet Figure 2/3: SemQL grammar 与示例树](paper_figures/04_irnet_fig2_3_semql_grammar_tree.png)

这张组合图展示 SemQL 的 grammar 和 SemQL 树。它说明 SemQL 不是普通 SQL 的改写，而是一个 tree-structured intermediate representation：先表达选择、过滤、聚合等语义结构，再由规则根据 schema 推断 SQL 中的 `FROM`、`GROUP BY`、`HAVING` 等实现细节。

### 1. 一句话定位

IRNet 是复杂跨域 Text-to-SQL 中“先生成中间表示，再确定性转换为 SQL”的代表工作。它最重要的价值是证明：把自然语言问题直接映射到 SQL 可能被 SQL 实现细节拖累，而设计合适的 intermediate representation 可以降低生成难度。

### 2. 作者要解决的问题

论文明确提出两个核心挑战：

- mismatch problem：自然语言表达的是用户意图，SQL 包含很多实现细节，例如 `GROUP BY`、`HAVING`、`FROM`、join path 等。这些细节往往没有在问题中直接出现，但 SQL 必须写出来。
- lexical problem：Spider 是跨数据库 benchmark，测试数据库 schema 中有大量训练时没见过的 out-of-domain words。论文提到 Spider dev schema 中约 35% 的词没有出现在训练 schema 中，而 WikiSQL 只有约 22%。这使 column/table prediction 更难。

这两个问题分别对应本课题的两个动机：第一，标准 SQL 结构复杂，直接生成和修复困难；第二，schema linking 错误会影响后续查询结构。

### 3. 核心方法

IRNet 把 Text-to-SQL 合成过程拆成三个阶段：

1. Schema linking：识别问题中提到的 columns、tables 和 values，并给 column 分配不同类型，例如 exact match、partial match、value exact match、value partial match。
2. SemQL synthesis：用 grammar-based neural model 生成 SemQL。SemQL 是论文设计的中间表示，用来桥接自然语言和 SQL。
3. SQL inference：根据 SemQL 和数据库 schema 中的 domain knowledge，确定性推断出最终 SQL。

SemQL 的设计重点是隐藏 SQL 实现细节。例如 Figure 3 对应的 SQL 中有 `GROUP BY`、`HAVING`、`FROM`，但 SemQL 中把 `WHERE` 和 `HAVING` 条件统一放到 `Filter` 子树中，并通过后续推断补出 SQL 子句。这样做的前提是数据库 schema 定义比较完整，尤其是主外键关系清楚。论文在推断 `FROM` 子句时，会把 schema 看成表节点和 foreign-key 边组成的图，再寻找连接 SemQL 中已声明表的最短路径。

模型结构上，IRNet 包括：

- NL Encoder：编码自然语言问题和 schema linking 类型。
- Schema Encoder：编码 columns/tables，并利用问题上下文。
- Grammar-based Decoder：通过 `APPLYRULE`、`SELECTCOLUMN`、`SELECTTABLE` 等动作生成 SemQL。
- Memory augmented pointer network：缓解重复选择 column 的问题。
- Coarse-to-fine decoding：先生成 SemQL skeleton，再填充 column/table 细节。

### 4. 实验设置与主要结果

论文在 Spider benchmark 上评估 IRNet。关键结果如下：

- IRNet 在 Spider test set 上 exact matching accuracy 为 46.7%，比当时 previous state-of-the-art 高 19.5 个百分点。
- IRNet(BERT) 在 Spider test set 上达到 54.7%。
- 按难度划分，IRNet(BERT) 在 easy、medium、hard、extra hard 上分别达到 77.2%、58.7%、48.1%、25.3%，明显高于 SyntaxSQLNet(BERT)。
- 论文还把多个 baseline 从生成 SQL 改成生成 SemQL，结果显示 exact matching 至少提升 6.6 个百分点，最高提升 14.4 个百分点。这一实验是 SemQL 有效性的关键证据。
- Ablation 中，schema linking 对 IRNet 带来约 8.5 个百分点提升，对 IRNet(BERT) 带来约 6.4 个百分点提升；memory pointer 和 coarse-to-fine 也继续提升效果。

这些结果说明，IRNet 的提升不是单纯来自更大的 encoder，而来自 schema linking、中间表示和结构化 decoding 的组合。

### 5. 关键贡献

- 提出 SemQL 作为面向复杂 Text-to-SQL 的 intermediate representation，用来缓解自然语言意图和 SQL 实现细节之间的 mismatch。
- 将生成过程拆成 schema linking、SemQL 生成、SQL 确定性推断三个阶段。
- 证明生成 SemQL 比直接生成 SQL 对多种模型都有帮助。
- 在 Spider 上显著提升当时的 exact matching accuracy。
- 给后续 NatSQL、SQL 简化表达、step-wise intermediate representation 等工作提供了重要先例。

### 6. 局限性

- SemQL 是 tree-structured IR，和本课题希望强调的线性 step-wise SQL+ 不同；它更接近语义解析树，而不是面向执行反馈修复的操作流水线。
- SemQL 到 SQL 的确定性推断依赖 schema 的主外键定义准确完整。真实数据库中 schema 约束可能缺失或不规范，这会影响推断。
- 论文主要解决 SQL 生成，不直接研究 execution feedback、局部 repair skill 或多轮修正。
- 对 nested query 的提升有限。论文错误分析中，23.9% 的失败样例与复杂 nested queries 有关。
- column prediction 仍然是主要错误来源之一。论文错误分析中，32.3% 的失败样例来自基于 cell values 的错误 column prediction。

### 7. 和本课题的关系

IRNet 对本课题是“直接支撑型文献”。它支持的不是 SQL+ 的具体语法，而是 SQL+ 背后的核心假设：复杂 SQL 不宜完全由模型一次性直接生成，中间表示可以降低自然语言到 SQL 的结构映射难度。

但必须讲清差异：

- SemQL 是 tree-structured semantic representation，目标是隐藏 SQL 实现细节并帮助模型生成。
- SQL+ 是 linear step-wise intermediate representation，目标不仅是帮助生成，还要服务执行反馈定位、Critic Agent 诊断、Skill Router 路由和局部 repair skill 修复。
- IRNet 的修复链路不明显；本课题把中间表示进一步用于 repairability 和 interpretability。

因此，开题中可以说：IRNet 证明了 intermediate representation 在复杂 Text-to-SQL 中有效，但本课题不是复刻 SemQL，而是面向 SQL+ 和反馈修正重新设计线性、可局部修改的中间表示。

### 8. 可用于开题答辩的说法

可以这样讲：IRNet 是 ACL 2019 的复杂跨域 Text-to-SQL 代表工作。它指出自然语言意图和 SQL 实现细节之间存在 mismatch，例如问题中没有显式提到 `GROUP BY student_id`，但 SQL 必须补出该结构。IRNet 通过 schema linking、SemQL 中间表示和确定性 SQL 推断，把直接生成 SQL 的问题拆开，并在 Spider 上取得显著提升。这说明中间表示路线是有研究依据的。本课题的 SQL+ 延续这个思路，但更强调线性步骤、执行反馈和局部修复。

### 9. 可能被老师追问的问题

- 问：SemQL 和 SQL+ 有什么区别？
  答：SemQL 是树状语义表示，主要服务复杂 SQL 的生成；SQL+ 是线性步骤表示，除了生成，还服务执行反馈定位、Skill Router 路由和局部修复。
- 问：为什么不直接用 SemQL？
  答：SemQL 更适合语义解析和确定性 SQL 推断，但它不是为多智能体 repair loop 设计的。SQL+ 保留数据流式步骤，便于把错误映射到 `WHERE`、`JOIN`、`AGG`、`ORDER`、`SELECT` 等局部操作。
- 问：IRNet 是否已经解决复杂 Text-to-SQL？
  答：没有。它在 Spider 上显著提升了当时结果，但错误分析仍显示 column prediction、nested query 和 operator prediction 是主要问题。
- 问：IRNet 对你的实验有什么直接启发？
  答：一是 schema linking 不能省；二是中间表示能缓解直接 SQL 生成困难；三是要把 SQL 结构拆开分析，不能只看整体 exact match。

### 10. 精读结论

IRNet 是 SQL+ 研究路线中必须掌握的核心先导文献。它给出的最关键证据是：生成 intermediate representation 可以系统性降低复杂 Text-to-SQL 的难度，而且 schema linking 对性能有明显贡献。对本课题而言，IRNet 负责回答“为什么要有 SQL+ 这种中间表示”；而 SQL+ 需要进一步回答“为什么这个中间表示要线性化、可执行转换、可诊断、可局部修复”。

## 5. Gan 等，NatSQL

### 0. 文献来源与核验

- 完整题名：Natural SQL: Making SQL Easier to Infer from Natural Language Specifications
- 方法简称：NatSQL，即 Natural SQL。
- 作者：Yujian Gan, Xinyun Chen, Jinxia Xie, Matthew Purver, John R. Woodward, John Drake, Qiaofu Zhang
- 发表来源：Findings of the Association for Computational Linguistics: EMNLP 2021，页码 2030-2042。
- DOI：10.18653/v1/2021.findings-emnlp.174。
- 官方 URL：https://aclanthology.org/2021.findings-emnlp.174/
- 本地 PDF：`docs/opening/papers/05_natsql_gan_2021.pdf`。
- 本地图片：`docs/opening/paper_figures/05_natsql_fig1_ir_comparison.png`；`docs/opening/paper_figures/05_natsql_fig4_schema_item_reduction.png`。
- 来源质量：ACL Anthology 正式收录的 Findings of EMNLP 论文，来源中-强；属于 Text-to-SQL 中间表示和 SQL 简化表达方向的直接相关工作。
- 核验状态：来源已核验，PDF 已下载，已从本地 PDF 抽取关键图。

![NatSQL Figure 1: SQL、RAT-SQL IR、SyntaxSQL IR、SemQL 与 NatSQL 对比](paper_figures/05_natsql_fig1_ir_comparison.png)

这张图是 NatSQL 的总览图。对于“Which film has more than 5 actors and less than 3 in the inventory?”这个问题，标准 SQL 要写两个 `SELECT` 并用 `INTERSECT` 连接；SemQL 已经去掉 `FROM`、`JOIN ON`、`GROUP BY` 并合并 `WHERE/HAVING`，但仍保留 `INTERSECT`。NatSQL 进一步把它变成一个 `WHERE` 条件中的 `and`，使表达更接近自然语言。

![NatSQL Figure 4: 用 @ 和 table.* 降低 schema item 预测难度](paper_figures/05_natsql_fig4_schema_item_reduction.png)

这张图解释 NatSQL 如何减少模型必须预测的 schema items。标准 SQL 和 SemQL 都需要 `visitor.id`、`visit.visitor_id` 这类自然语言里没有直接提到的主外键列。NatSQL 用 `@` 和 `visit.*` 做占位，把真正的列推断留给转换阶段，从而降低 schema linking 难度。

### 1. 一句话定位

NatSQL 是面向 Text-to-SQL 的 SQL intermediate representation，它在保留 SQL 核心能力的同时，删除或重写那些自然语言中难以对齐的 SQL 实现细节，使模型更容易从问题生成查询表达。

### 2. 作者要解决的问题

NatSQL 延续了 IRNet 对 mismatch problem 的判断：SQL 是为数据库执行设计的，不是为表达自然语言语义设计的。因此很多 SQL 结构在自然语言问题中没有明显对应词。

论文主要针对三类问题：

- SQL 关键字难对齐：`GROUP BY`、`HAVING`、`FROM`、`JOIN ON`、`INTERSECT`、`UNION`、`EXCEPT`、子查询等结构经常没有自然语言中的直接对应词。
- schema item 难预测：标准 SQL 需要预测一些问题中没有提到的主外键列、join key、group key，例如 `visitor.id`、`visit.visitor_id`。
- 可执行 SQL 生成困难：一些模型只关注 Spider exact match，不生成 condition values；NatSQL 试图让这类模型更容易转换成可执行 SQL。

对本课题来说，NatSQL 的问题意识和 SQL+ 非常接近：标准 SQL 的结构性复杂度会增加模型生成难度，中间表示应该降低这种复杂度。

### 3. 核心方法

NatSQL 的主要设计是保留 `SELECT`、`WHERE`、`ORDER BY`，并去掉或重写其他 SQL 结构：

- 去掉 `GROUP BY`、`HAVING`、`FROM`、`JOIN ON` 等难以从自然语言直接预测的子句。
- 去掉嵌套子查询和集合操作，使 NatSQL 尽量只包含一个 `SELECT`。
- 用 `WHERE` 条件承载更多语义，例如把 `HAVING count(*) > 5 INTERSECT ... HAVING count(*) < 3` 改写为 `WHERE count(film_actor.*) > 5 and count(inventory.*) < 3`。
- 用 `@` 作为待推断列的 placeholder，用 `table.*` 表示表级线索，再由转换算法根据 foreign key、同名列或 primary key 推断真实 SQL 列。
- 提供 NatSQLG 变体，在需要时保留 `GROUP BY`，以提高和 SQLite/Spider 的兼容性。

一个关键细节是：NatSQL 并不是完全脱离 SQL 的新语言。它尽量沿用 SQL 的关键字和语法风格，因此比 SemQL 更容易阅读和扩展。但它又比标准 SQL 更接近自然语言问题，因为它减少了大量执行层实现细节。

### 4. 实验设置与主要结果

论文在 Spider benchmark 上比较 SQL、SemQL、RAT-SQL IR、NatSQL 和 NatSQLG，并把 NatSQL 接入多个已有模型，包括 GNN、IRNet、RAT-SQL、RAT-SQL+GAP。

关键结果：

- Gold IR 比较中，NatSQL 可转换出 95.3% execution match，NatSQLG 为 96.5%；SemQL 不直接支持 executable SQL generation。
- 在 Spider dev 上，RAT-SQL + NatSQLG 达到 67.3% execution match；RAT-SQL + BERT + NatSQLG 达到 73.0%；RAT-SQL + GAP + NatSQLG 达到 75.0%。
- 在 Spider test 上，RAT-SQL + GAP + NatSQLG 达到 73.3% execution accuracy，论文称超过当时 leaderboard 上的最佳执行准确率 2.2 个百分点。
- NatSQL 对 extra hard SQL 的提升更明显，论文报告多个模型在 extra hard 上平均有 4.74 个百分点的绝对提升。
- Exact match 可能下降或不完全反映 NatSQL 的价值，因为 NatSQL 倾向生成语义等价但结构不完全匹配 gold SQL 的查询。

这里要注意：这些是论文报告的 Spider 结果，不是本项目结果。开题中只能把它作为相关工作证据，不能和本项目 Spider smoke test 混在一起。

### 5. 关键贡献

- 提出 NatSQL 作为专门面向 Text-to-SQL 的 SQL intermediate representation。
- 系统性减少自然语言中难以对应的 SQL 结构，包括 `GROUP BY`、`HAVING`、`FROM`、`JOIN ON`、集合操作和嵌套子查询。
- 用 `@` 和 `table.*` 降低对未显式提到 schema items 的预测需求。
- 让部分原本不支持 executable SQL generation 的模型更容易生成可执行 SQL。
- 用多个模型实验说明，改进中间表示本身可以提升 Text-to-SQL 性能，尤其是复杂查询。

### 6. 局限性

- NatSQL 仍然是面向 Text-to-SQL 生成的 IR，不是面向 execution feedback repair 的诊断表示。
- NatSQL 的转换仍依赖规则和 schema 结构，例如 foreign key、同名列、primary key；真实数据库如果主外键不完整，转换可靠性会下降。
- NatSQL 简化了 SQL 结构，但没有显式提供多智能体诊断、错误类型路由或局部 patch 机制。
- 它倾向把复杂查询压缩到 `WHERE` 条件中，这有利于生成，但不一定最利于错误定位和逐步修复。
- NatSQLG 为了兼容性又保留 `GROUP BY`，说明“越简化越好”并不总成立，中间表示需要在覆盖能力、可读性、可转换性之间折中。

### 7. 和本课题的关系

NatSQL 是 SQL+ 最直接的相关工作之一。它强力支持本课题的基本判断：标准 SQL 里很多结构不是自然语言意图的直接表达，而是数据库执行层的实现细节；把这些细节从模型生成目标中移走，可以降低 Text-to-SQL 难度。

但 SQL+ 和 NatSQL 的定位不同：

- NatSQL 目标是让模型更容易生成 SQL，并最终转换回 executable SQL。
- SQL+ 目标除了生成，还包括 execution feedback 之后的 step-level diagnosis 和 local repair。
- NatSQL 主要保留 `SELECT/WHERE/ORDER BY` 并压缩结构；SQL+ 则保留 `FROM -> JOIN -> WHERE -> GROUP -> AGG -> HAVING -> SELECT -> ORDER -> LIMIT` 的线性数据流步骤。
- NatSQL 有助于“自然语言到查询”的推断；SQL+ 更强调“查询出错后怎么定位和修复”。

因此，NatSQL 可以作为开题中“为什么 SQL 简化表达有必要”的直接证据，同时也反衬 SQL+ 的新增目标：不仅要简化生成，还要让错误更容易映射到局部步骤。

### 8. 可用于开题答辩的说法

可以这样讲：NatSQL 是 Findings of EMNLP 2021 的 Text-to-SQL 中间表示工作。它认为 `GROUP BY`、`HAVING`、`FROM`、`JOIN ON`、集合操作和嵌套子查询等 SQL 结构很难从自然语言中直接预测，因此把它们重写成更接近自然语言的 NatSQL 表达。实验显示，NatSQL 接入 RAT-SQL、IRNet 等模型后能提升 Spider 上的表现，尤其对 extra hard 查询更明显。本课题的 SQL+ 和 NatSQL 一样承认 SQL 结构复杂会影响生成，但 SQL+ 更进一步服务执行反馈诊断和局部修复。

### 9. 可能被老师追问的问题

- 问：NatSQL 和 SQL+ 最大区别是什么？
  答：NatSQL 更关注减少 SQL 生成难度，把复杂结构压缩成更自然语言化的表示；SQL+ 更关注线性数据流和可修复性，把查询拆成可定位的步骤，便于 Critic 和 Repair Skill 修改。
- 问：既然有 NatSQL，为什么还要 SQL+？
  答：NatSQL 主要解决生成问题，没有直接解决执行反馈如何映射到局部结构、如何按错误类型路由 repair skill。SQL+ 的设计目标包含生成、转换、诊断和局部修复。
- 问：NatSQL 去掉 `GROUP BY`、`JOIN ON` 会不会丢信息？
  答：它通过 schema 推断、`@` 占位、`table.*` 和 NatSQLG 变体来补充信息，但这依赖 schema 质量和转换规则，真实场景仍要谨慎。
- 问：NatSQL 对你的 SQL+ 设计有什么启发？
  答：一是证明简化 SQL 表达有价值；二是提醒中间表示要减少自然语言没有提到的 schema items；三是说明中间表示最终必须能稳定转换为可执行 SQL。

### 10. 精读结论

NatSQL 是本课题必须重点掌握的近邻工作。它已经证明“面向 Text-to-SQL 的 SQL 简化表达”可以提升模型生成效果，尤其能缓解 SQL 关键字、集合操作、嵌套子查询和 schema item 预测问题。本课题要在它的基础上讲清楚增量：SQL+ 不只是把 SQL 写得更简单，而是把查询组织成可执行、可诊断、可局部修复的线性步骤，从而服务多智能体反馈修正闭环。

## 6. Shute 等，Pipe Syntax in SQL

待整理。

## 7. Wang 等，RAT-SQL

待整理。

## 8. Scholak 等，PICARD

待整理。

## 9. Li 等，RESDSQL

待整理。

## 10. Pourreza 等，DIN-SQL

待整理。

## 11. Wang 等，MAC-SQL

待整理。

## 12. Pourreza 等，CHESS

待整理。

## 13. Pourreza 等，CHASE-SQL

待整理。

## 14. Li 等，SQL-Factory

待整理。

## 15. Ni 等，LEVER

待整理。

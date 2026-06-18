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

BIRD 对本课题的作用是提供“后续真实数据库扩展方向”，而不是当前实验结果来源。本项目当前核心仍是 SQL+ 中间表示和反馈修正，在自建 order 数据集与小规模 Spider 子集上验证：conversion smoke test 用 gold SQL -> SQL+ -> SQL 检查表达/转换覆盖性，fresh e2e 用 question + schema 生成 SQL+。BIRD 可以支撑以下论点：

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
- 当前项目的 Spider conversion smoke test 和 fresh e2e 都只是 `concert_singer` 小规模受支持子集，不应和 Spider 2.0 结果混淆。
- 后续如果扩展到企业级场景，需要增加 SQL dialect、metadata retrieval、project codebase understanding 和 long-context execution feedback。

### 8. 可用于开题答辩的说法

可以这样讲：Spider 2.0 是 ICLR 2025 的企业级 Text-to-SQL workflow benchmark。它说明真实数据场景中，Text-to-SQL 不再是给定一个 schema 后生成一条 SQL，而是要结合数据库元数据、SQL 方言文档、项目代码库和执行反馈完成多步工作流。论文中基于 o1-preview 的 code agent 在 Spider 2.0 上只解决 21.3% 的任务，而在 Spider 1.0 和 BIRD 上分别达到 91.2% 和 73.0%，说明传统 benchmark 的高分不能直接代表真实企业可用性。本课题当前不声称完成 Spider 2.0，只将它作为后续真实工作流扩展的依据。

### 9. 可能被老师追问的问题

- 问：Spider 2.0 和 Spider 1.0 有什么本质区别？
  答：Spider 1.0 主要是自然语言到单条 SQL 的跨数据库评测；Spider 2.0 是企业级 workflow，包含数据库文档、SQL dialect、代码库、执行接口和多步 SQL/Python 操作。
- 问：Spider 2.0 和 BIRD 的区别是什么？
  答：BIRD 强调大规模真实数据库值、外部知识和执行效率；Spider 2.0 更进一步强调企业级 workflow、项目代码库、SQL 方言和多步执行环境。
- 问：你的项目和 Spider 2.0 有什么关系？
  答：本项目的 SQL+ 和多智能体反馈修正路线与 Spider 2.0 的 agentic workflow 方向一致，但当前实验还停留在自建数据集和 Spider 小子集 conversion/fresh e2e 验证，Spider 2.0 是后续扩展目标。
- 问：为什么不能把当前 Spider 小子集结果说成 Spider 2.0 能力？
  答：因为当前只是 Spider dev 的 `concert_singer` 小规模受支持 SQL 子集。conversion smoke test 验证 SQL+ 表达和转换可行性，fresh e2e 验证小子集生成修复链路；Spider 2.0 涉及企业级 workflow、SQL 方言、代码库和复杂执行环境，难度和评测目标不同。

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

这里要注意：这些是论文报告的 Spider 结果，不是本项目结果。开题中只能把它作为相关工作证据，不能和本项目 Spider conversion smoke test 或 fresh e2e 小子集结果混在一起。

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

### 0. 文献来源与核验

- 完整题名：SQL Has Problems. We Can Fix Them: Pipe Syntax In SQL
- 作者：Jeff Shute, Shannon Bales, Matthew Brown, Jean-Daniel Browne, Brandon Dolphin, Romit Kudtarkar, Andrey Litvinov, Jingchi Ma, John Morcos, Michael Shen, David Wilhite, Xi Wu, Lulan Yu
- 发表来源：Proceedings of the VLDB Endowment, Vol. 17, No. 12, 2024，页码 4051-4063。
- DOI / 官方 URL：10.14778/3685800.3685826；正式出处为 PVLDB，PDF 官方路径为 `https://www.vldb.org/pvldb/vol17/p4051-shute.pdf`。本机访问 PVLDB PDF 超时，实际下载使用 Google Research 镜像。
- 本地 PDF：`docs/opening/papers/06_pipe_syntax_shute_2024.pdf`。
- 本地图片：`docs/opening/paper_figures/06_pipe_syntax_fig1_2_order.png`，从本地 PDF 第 2 页裁剪。
- 来源质量：PVLDB 正式论文，来源强；属于数据库语言设计和 SQL 可用性改进文献。
- 核验状态：来源已核验，PDF 已下载并精读，关键图已抽取。

![Pipe Syntax Figure 1/2: 传统 SQL clause 顺序与 pipe operator 顺序对比](paper_figures/06_pipe_syntax_fig1_2_order.png)

这张图是第六篇最适合服务开题答辩的图。Figure 1 说明传统 SQL 的 `SELECT ... FROM ... WHERE ... GROUP BY ...` 语法顺序并不等于语义求值顺序，读者需要在文本中来回跳转。Figure 2 说明 pipe syntax 把查询改写成自上而下的 operator 序列，每一步更接近实际的数据流。对本课题来说，这正好解释了 SQL+ 为什么要采用 step-wise、linear 的中间表示。

### 1. 一句话定位

这篇论文不是 Text-to-SQL 方法论文，而是 GoogleSQL/PVLDB 发表的 SQL 语言设计论文。它提出在 SQL 内部加入 pipe-structured data flow syntax，让查询表达从传统的嵌套、inside-out 结构转向线性、可组合、可调试的 operator 序列。

### 2. 作者要解决的问题

作者认为 SQL 的问题不在关系模型和声明式语义，而在查询操作的组合语法。传统 SQL 的主要痛点包括：

- clause order 固定，`SELECT` 写在前面，但真实数据流通常从 `FROM` 开始。
- 同一类操作被拆成多个 clause，例如过滤在不同位置分别写成 `WHERE`、`HAVING`、`QUALIFY`。
- 很多简单操作必须通过 subquery 或 CTE 才能表达，例如多层 aggregation、在中间位置投影新列、把查询作为 TVF 输入。
- 大查询常呈现 inside-out data flow，读者要先找到最内层 `FROM`，再向外理解逻辑。
- `SELECT`、`GROUP BY`、`ORDER BY` 等 clause 之间存在远距离联动，修改一处经常要同步修改多处。
- SQL 扩展新 operator 很困难，很多新功能只能被塞进 `FROM` 后缀或特殊语法里。

这套问题和 Text-to-SQL 的关系很直接：人类觉得难读、难改的结构，LLM 生成和修复时同样容易出错。论文第 5.6 节也明确讨论了 LLM 生成 SQL 的潜在收益，认为 pipe syntax 可能让 SQL 更接近普通程序语言中的顺序步骤。

### 3. 核心方法 / 语言设计

Pipe Syntax 的基本设计是在现有 SQL query 后面追加零个或多个 pipe operators，每个 operator 以 `|>` 开头，输入是上一步的中间 table，输出也是一个 table。例如：

```sql
FROM customer
|> LEFT OUTER JOIN orders ON c_custkey = o_custkey
|> AGGREGATE COUNT(o_orderkey) c_count
   GROUP BY c_custkey
|> AGGREGATE COUNT(*) AS custdist
   GROUP BY c_count
|> ORDER BY custdist DESC, c_count DESC;
```

它的几个关键设计点是：

- 查询可以从 standalone `FROM` 开始，然后逐步追加 `WHERE`、`JOIN`、`AGGREGATE`、`ORDER BY`、`SELECT` 等 operator。
- 每个 pipe operator 只看当前输入 table 的 name scope，不直接看前后其他步骤，因此天然具有局部性。
- `AGGREGATE ... GROUP BY` 被设计成一个独立 operator，避免传统 SQL 中 `SELECT` 和 `GROUP BY` 的重复表达。
- `EXTEND`、`SET`、`DROP` 等 projection operators 用于增量添加、更新和删除列，减少重复 `SELECT *` 和子查询。
- `CALL` 让 table-valued functions 像普通 operator 一样接在 pipe 后面，提升 SQL 的扩展能力。
- pipe syntax 仍然是 declarative semantics，写法像顺序数据流，但执行时仍由优化器转换为代数表示并优化，不等于强制物理执行顺序。

这里要注意一个边界：Pipe Syntax 不是要替代 SQL，也不是另起一种新语言，而是在 GoogleSQL 里做 backward-compatible extension。作者反复强调“fix SQL from within”，这和 PRQL、SaneQL 这类替代语言路线不同。

### 4. 实验设置与主要结果

论文没有做 Spider/BIRD 这种标准 Text-to-SQL benchmark，也没有报告 LLM 生成准确率。它的 evaluation 更像语言系统论文中的工程部署和使用经验总结：

- Google 已在 GoogleSQL 中实现 pipe syntax，GoogleSQL 是 F1、BigQuery、Spanner、Procella 等系统共享的 SQL dialect 和实现组件。
- 实现层面主要发生在 parsing 和 language analysis 中，pipe syntax 最终产生和标准 SQL 相同的 algebra，不需要查询引擎新增执行或优化能力。
- 论文报告了在 Google 内部开放后的使用情况：六个月内使用量持续增长，用户用于 ad hoc queries、dashboard/report 查询、data processing pipelines 和 TVF 函数库。
- 作者提到已有用户反馈认为 pipe syntax 提升 productivity 和 user experience，但也明确说明还没有做正式 user experience research。
- 论文还讨论了调试和 IDE 场景：pipe query 的每个 prefix 到 `|>` 位置都可以作为可运行 query prefix，这使中间结果查看、单步调试、自动补全和局部修改更自然。

因此，开题答辩中不能把这篇论文说成“证明 pipe syntax 提升 Text-to-SQL accuracy”。更准确的说法是：它提供了来自真实数据库系统的语言设计和工程可行性证据，证明线性 operator 表达可以在 SQL 生态内落地，并能改善可读性、可编辑性和可扩展性。

### 5. 关键贡献

- 系统总结了传统 SQL 的语法问题：clause order、subquery 依赖、inside-out data flow、远距离副作用和扩展困难。
- 提出在 SQL 内部加入 pipe-structured syntax，而不是创造新的替代语言。
- 给出一组可组合 pipe operators，包括 `WHERE`、`JOIN`、`AGGREGATE`、`EXTEND`、`DROP`、`SET`、`CALL`、`PIVOT` 等。
- 保留 SQL 的 relational model、declarative semantics、optimizer 和生态兼容性。
- 在 GoogleSQL 中实现并部署，说明该设计不是纯概念方案。
- 明确讨论了 AI/LLM 生成 SQL 的潜在价值：pipe syntax 更像顺序程序步骤，有利于生成、理解、验证和局部编辑。

### 6. 局限性

- 论文重点是 SQL 语言改进，不是 Text-to-SQL 模型，也不是多智能体修复框架。
- evaluation 主要来自 Google 内部部署经验和用户反馈，缺少严格的 controlled user study。
- 作者关于 LLM 更容易生成 pipe SQL 的论述属于合理推测，没有在论文中给出系统实验。
- Pipe Syntax 主要面向 GoogleSQL 生态，其他数据库系统是否采用、标准化是否推进，仍取决于工业界支持。
- 它解决的是 SQL 表达和可用性问题，不直接解决 schema linking、value grounding、自然语言歧义、错误诊断和 repair routing。

### 7. 和本课题的关系

这篇论文是 SQL+ 设计动机中非常关键的一篇，但它和 SQL+ 的关系要讲清楚：

- 共同点：二者都认为传统 SQL 的结构顺序不利于阅读、生成和修改，都倾向于把查询表达成线性、step-wise 的数据流。
- 差异一：Pipe Syntax 是 SQL 方言扩展，目标是让人类和工具更好地写 SQL；SQL+ 是本课题中的 intermediate representation，目标是服务 NL2SQL 生成、转换、执行反馈诊断和局部修复。
- 差异二：Pipe Syntax 保持 SQL 生态兼容，尽量复用原有 SQL clause；SQL+ 可以为 Critic Agent、Skill Router 和 Repair Skill 增加更明确的 step 标签、错误定位和修复边界。
- 差异三：Pipe Syntax 本身不提出多智能体框架；本课题把线性表达进一步接入 execution feedback loop，用于“哪里错、交给哪个 repair skill、怎么局部改”。

因此，开题里可以用这篇论文支撑“线性数据流表达有现实数据库系统依据”，但不能把 SQL+ 描述成直接复刻 GoogleSQL Pipe Syntax。更稳妥的表述是：SQL+ 借鉴了 pipe-structured data flow 的可组合思想，并面向 Text-to-SQL 反馈修正任务做了研究性抽象。

### 8. 可用于开题答辩的说法

可以这样讲：Shute 等人在 PVLDB 2024 的 Pipe Syntax 论文中指出，传统 SQL 的语法顺序和语义执行顺序不一致，复杂查询经常需要 subquery 和 CTE，导致阅读、编辑和扩展都比较困难。他们在 GoogleSQL 中加入 pipe-structured syntax，把查询表达为自上而下的 operator 序列，同时仍保留 SQL 的声明式语义和优化器能力。这说明线性数据流式 SQL 表达不是凭空设计，而是在真实数据库系统中已有工程实践。本课题的 SQL+ 借鉴这种 step-wise 表达思想，但目标不是改造 SQL 标准，而是让 NL2SQL 结果更容易被执行反馈诊断和局部 repair skill 修正。

### 9. 可能被老师追问的问题

- 问：Pipe Syntax 和你的 SQL+ 是不是一回事？
  答：不是。Pipe Syntax 是 GoogleSQL 的 SQL 方言扩展，服务人类写 SQL 和数据库系统扩展；SQL+ 是本课题的中间表示，服务 NL2SQL 生成、转换、诊断和局部修复。二者共享线性数据流思想，但研究目标和系统位置不同。
- 问：这篇论文有没有证明 LLM 用 pipe SQL 更准确？
  答：没有。论文只是讨论了 AI/LLM 生成 SQL 的潜在应用，认为顺序 operator 和清晰中间状态可能有利于生成和验证，但没有给出 Text-to-SQL benchmark 实验。
- 问：为什么这篇论文能支撑你的选题？
  答：它从数据库语言设计角度说明传统 SQL 的结构确实影响可读性、可编辑性和可扩展性，并展示了线性 operator 表达在真实 SQL 系统中的可行性。这为 SQL+ 的 step-wise 表达提供了外部依据。
- 问：Pipe Syntax 仍然是 declarative 吗？
  答：是。它看起来像顺序执行，但语义仍是声明式的，查询引擎仍会转换为代数表示并优化执行。这个点也提醒 SQL+ 转换到 SQL 后不能假设数据库会按文本顺序物理执行。
- 问：Pipe Syntax 不能解决哪些 Text-to-SQL 问题？
  答：它不直接解决 schema linking、value grounding、自然语言歧义、多候选选择和错误修复路由。它解决的是表达结构问题，本课题还需要多智能体诊断和 repair skill 来处理生成后的错误。

### 10. 精读结论

Pipe Syntax 是 SQL+ 的重要“语言设计背景”文献。它最值得记住的不是某个实验分数，而是三个判断：第一，传统 SQL 的语法组织确实会制造 inside-out data flow 和远距离依赖；第二，把查询写成线性 operator 序列可以增强可读性、可编辑性、可调试性和扩展性；第三，这种思想已经在 GoogleSQL 中实现并部署。对本课题来说，它支撑的是 SQL+ 的形式动机，而不是直接支撑多智能体修复效果。开题答辩时要把这个边界说清楚。

## 7. Wang 等，RAT-SQL

### 0. 文献来源与核验

- 完整题名：RAT-SQL: Relation-Aware Schema Encoding and Linking for Text-to-SQL Parsers
- 方法简称：RAT-SQL，即 Relation-Aware Transformer for SQL。
- 作者：Bailin Wang, Richard Shin, Xiaodong Liu, Oleksandr Polozov, Matthew Richardson
- 发表来源：ACL 2020 main conference，Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics，页码 7567-7578。
- DOI：10.18653/v1/2020.acl-main.677。
- 官方 URL：https://aclanthology.org/2020.acl-main.677/
- 本地 PDF：`docs/opening/papers/07_rat_sql_wang_2020.pdf`。
- 本地图片：`docs/opening/paper_figures/07_rat_sql_fig1_schema_linking_example.png`；`docs/opening/paper_figures/07_rat_sql_table1_schema_relations.png`；`docs/opening/paper_figures/07_rat_sql_fig2_schema_graph.png`。
- 来源质量：ACL 主会正式论文，来源强；属于 schema encoding、schema linking 和复杂 schema 建模方向代表工作。
- 核验状态：来源已核验，PDF 已下载，已从本地 PDF 抽取关键图。

![RAT-SQL Figure 1: Spider 中的 schema linking 歧义示例](paper_figures/07_rat_sql_fig1_schema_linking_example.png)

这张图展示 RAT-SQL 要解决的核心困难：自然语言里的 `model` 应该链接到 `car_names.model`，而不是 `model_list.model`；`cars` 又隐含涉及 `cars_data` 和 `car_names` 两张表。也就是说，schema linking 不只是字符串匹配，还要结合 question context、column/table 关系和 foreign key 关系做全局判断。

![RAT-SQL Table 1: schema graph 中的 relation 类型](paper_figures/07_rat_sql_table1_schema_relations.png)

![RAT-SQL Figure 2: schema graph 示例](paper_figures/07_rat_sql_fig2_schema_graph.png)

这两张图说明 RAT-SQL 如何把数据库 schema 显式建成图：列和列之间有 same-table、foreign-key-column 关系，列和表之间有 primary-key、belongs-to 关系，表和表之间有 foreign-key-table 关系。这些“硬关系”会进入 relation-aware self-attention，和模型学习到的软对齐关系一起影响 question/schema 表示。

### 1. 一句话定位

RAT-SQL 是 Text-to-SQL 中 schema encoding 与 schema linking 的代表工作，它把 question tokens、columns、tables 放进同一个 relation-aware self-attention 框架，用显式关系编码解决跨数据库 schema 泛化问题。

### 2. 作者要解决的问题

论文认为 Spider 这类跨数据库 Text-to-SQL 的核心难点是 schema generalization。模型在测试时面对的是没见过的数据库 schema，因此必须同时解决三个问题：

- 如何把数据库 schema 编码成 decoder 能用的表示。
- 如何把 column type、primary key、foreign key、table-column belongs-to 等 schema 结构信息放进表示中。
- 如何识别自然语言中对 table/column 的引用，也就是 schema linking。

Figure 1 的例子很好理解：`model` 这个词在 schema 中出现不止一次，`cars` 又不直接等于某一个表名。模型如果只做局部字符串匹配，很容易选错列或漏掉 join 所需表。

### 3. 核心方法

RAT-SQL 的核心是 relation-aware self-attention。普通 Transformer 会让所有输入 token 互相 attention，但它不知道两个节点之间是否存在主外键、同表、列属于表、问题词匹配列名等结构关系。RAT-SQL 在 attention 里加入关系向量 `r_ij`，使模型在全局 attention 的同时显式感知已知关系。

输入图包括三类节点：

- question words；
- schema columns；
- schema tables。

关系主要包括两类：

- schema graph relations：例如 same-table、foreign-key-column、primary-key、belongs-to、foreign-key-table。
- schema linking relations：例如 question n-gram 和 column/table name 的 exact match、partial match、no match，以及 value-based linking。

模型流程可以概括为：

1. 对 question words、column names、table names 做初始编码。
2. 构造 question-contextualized schema graph，把 question、columns、tables 放在同一个图里。
3. 用多层 relation-aware self-attention 联合更新 question/schema 表示。
4. 用 tree-structured decoder 生成 SQL AST，通过 `APPLYRULE`、`SELECTCOLUMN`、`SELECTTABLE` 等动作完成 SQL 生成。
5. 使用 memory-schema alignment matrix 帮助 decoder 在生成列/表时对齐 question 和 schema。

这篇论文的关键不是提出新的 SQL 中间表示，而是把 schema 结构和 question-schema 对齐作为一等公民放进 encoder。

### 4. 实验设置与主要结果

论文主要在 Spider 上评估，也做了 WikiSQL 补充实验。关键结果如下：

- RAT-SQL 在 Spider test set 上 exact match 为 57.2%，比当时非 BERT 最强方法高 8.7 个百分点。
- RAT-SQL + BERT 在 Spider test set 上达到 65.6%，论文发表时是新的 state-of-the-art。
- 按难度看，RAT-SQL + BERT 在 Spider test 的 easy、medium、hard、extra hard 上分别为 83.0、71.3、58.3、38.4。
- Ablation 显示 value-based linking 有明显帮助：RAT-SQL + value-based linking 为 60.54，RAT-SQL 为 55.13；去掉 schema linking relations 降到 40.37；去掉 schema graph relations 降到 35.59。
- Oracle 实验显示，仅提供正确 columns/tables 可到 69.8，仅提供正确 sketch 可到 73.0，两者都提供时为 99.4。这说明 column/table selection 和 SQL structure prediction 都是主要瓶颈。

需要注意：这些是论文在 Spider 上的结果，不是本项目结果。本项目当前只完成 Spider 小规模受支持子集 smoke test，不能借 RAT-SQL 数字包装本项目性能。

### 5. 关键贡献

- 提出 relation-aware self-attention 统一建模 schema encoding、schema linking 和 relation features。
- 把 question words、columns、tables 放入同一个 graph/input set，实现 question-contextualized schema encoding。
- 显式编码 primary key、foreign key、same-table、belongs-to、name match、value match 等关系。
- 用 ablation 证明 schema linking relations 和 schema graph relations 对 Spider 性能都有显著影响。
- 通过 alignment 可视化说明模型能够学习 question words 到 schema columns/tables 的对应关系。

### 6. 局限性

- RAT-SQL 仍然是直接生成 SQL AST，不是面向 SQL+ 或其他 step-wise IR 的 repair 框架。
- 它主要优化 schema encoding/linking，不能直接解决执行反馈诊断、局部修复、Skill Router 路由等问题。
- 错误分析显示，39% 的错误涉及 SELECT 子句中列错误、缺失或多余；29% 的错误缺少 WHERE 子句，说明 schema linking 和结构预测仍未完全解决。
- 论文中的 Spider 指标不包含真实执行值生成能力；WikiSQL 实验中作者也指出 value decoding 仍较简化。
- 对真实数据库来说，foreign key、primary key 和 schema metadata 可能不完整，RAT-SQL 的显式关系构造会受到影响。

### 7. 和本课题的关系

RAT-SQL 对本课题的作用是支撑 Schema Agent 和 schema linking 错误分析。SQL+ 生成和修复是否稳定，很大程度上取决于前面是否选对表、列、join path 和 value。RAT-SQL 说明这些信息不能靠简单字符串匹配，而应当结合 schema graph 和 question context。

和本课题的对应关系可以这样理解：

- RAT-SQL 的 schema graph relations 对应本课题 Schema Agent 需要维护的表-列、主外键、join path 信息。
- RAT-SQL 的 name/value-based linking 对应本课题 value-linking repair skill 和 schema/value lookup。
- RAT-SQL 的错误分析支持本课题把 schema/join、projection、value-linking 作为单独错误类型处理。
- RAT-SQL 没有解决 execution feedback repair，所以本课题需要在 SQL+ 层增加 Critic Agent、Skill Router 和 Repair Skill。

### 8. 可用于开题答辩的说法

可以这样讲：RAT-SQL 是 ACL 2020 的 Text-to-SQL schema linking 代表工作。它指出跨数据库 Text-to-SQL 的关键困难之一是模型要在未见过的 schema 上正确识别自然语言对应的表、列和 join 关系。RAT-SQL 通过 relation-aware self-attention，把 question words、columns 和 tables 以及主外键、belongs-to、name match、value match 等关系统一编码，并在 Spider 上取得显著提升。本课题中的 Schema Agent 和 schema linking 错误分析正是受这类工作的启发，但本课题进一步把 schema 结果接入 SQL+ 生成与反馈修正闭环。

### 9. 可能被老师追问的问题

- 问：RAT-SQL 解决的核心问题是什么？
  答：它解决的是跨数据库 Text-to-SQL 中 schema encoding 和 schema linking 问题，即如何在未见过的 schema 上把问题词正确对齐到表、列和 join 关系。
- 问：RAT-SQL 和 IRNet/NatSQL 的区别是什么？
  答：IRNet/NatSQL 更强调中间表示以降低 SQL 生成难度；RAT-SQL 更强调 schema/question 的关系编码和 schema linking。
- 问：RAT-SQL 对 SQL+ 有什么用？
  答：SQL+ 的每一步都依赖正确 schema 信息。RAT-SQL 证明 schema graph、foreign key、value linking 等信息对生成质量很关键，因此本课题需要 Schema Agent 和 schema/value lookup，而不能只让 Generator 盲写 SQL+。
- 问：RAT-SQL 是否解决了反馈修正？
  答：没有。它主要是生成前的 encoder/decoder 方法，不包含 execution feedback、Critic、Skill Router 或局部 repair skill。

### 10. 精读结论

RAT-SQL 是本课题 schema 侧必须掌握的核心文献。它说明复杂 Text-to-SQL 的关键不只是设计 SQL 中间表示，还要把 question 与 schema 的关系建模清楚。对 SQL+ 多智能体路线来说，RAT-SQL 支撑的是 Schema Agent 的必要性：只有表、列、主外键、join path 和 value linking 可靠，后面的 SQL+ 生成、执行反馈诊断和局部修复才有基础。

## 8. Scholak 等，PICARD

### 0. 文献来源与核验

- 完整题名：PICARD: Parsing Incrementally for Constrained Auto-Regressive Decoding from Language Models
- 方法简称：PICARD，即 Parsing Incrementally for Constrained Auto-Regressive Decoding。
- 作者：Torsten Scholak, Nathan Schucher, Dzmitry Bahdanau
- 发表来源：EMNLP 2021 main conference，Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing，页码 9895-9901。
- DOI：10.18653/v1/2021.emnlp-main.779。
- 官方 URL：https://aclanthology.org/2021.emnlp-main.779/
- 本地 PDF：`docs/opening/papers/08_picard_scholak_2021.pdf`。
- 本地图片：`docs/opening/paper_figures/08_picard_fig2_constrained_beam_search.png`；`docs/opening/paper_figures/08_picard_table1_spider_results.png`。
- 来源质量：EMNLP 主会正式论文，来源强；属于 constrained decoding、SQL 语法约束和 Text-to-SQL 生成可靠性方向代表工作。
- 核验状态：来源已核验，PDF 已下载，已从本地 PDF 抽取关键图。

![PICARD Figure 2: constrained beam search 中拒绝非法 token](paper_figures/08_picard_fig2_constrained_beam_search.png)

这张图是 PICARD 的核心机制图。语言模型在每一步会给出多个候选 token，PICARD 只检查 top-k 候选，并把无法通过词法、语法或 schema guard 检查的 token 分数设为 `-inf`。也就是说，PICARD 不是等 SQL 生成完再过滤，而是在 beam search 的每一步就阻止非法 SQL 继续扩展。

![PICARD Table 1: Spider 上加入 PICARD 后的结果](paper_figures/08_picard_table1_spider_results.png)

这张表展示 PICARD 的效果：同样的 T5 模型加入 PICARD 后，Spider development/test 上的 exact match 和 execution accuracy 都明显提升。例如带数据库内容的 T5-3B+PICARD 在 test 上达到 71.9 EM 和 75.1 EX。注意这些是论文结果，不是本项目结果。

### 1. 一句话定位

PICARD 是一种推理阶段 constrained decoding 方法，它通过 incremental parsing 在每个解码步骤拒绝非法 token，使通用语言模型更可靠地生成 SQL 这类形式语言。

### 2. 作者要解决的问题

大语言模型的输出空间是开放的。即使经过 Text-to-SQL fine-tuning，模型在解码时仍可能生成语法非法、schema 不存在或 alias 绑定错误的 SQL。对自然语言回答来说，小错误可能还能读懂；但对 SQL 来说，非法 token、错误 column、缺少 `FROM`、alias 不在作用域内等问题会直接导致查询不可执行。

PICARD 要解决的是：如何在不修改预训练模型结构、不引入特殊控制 token、不重新训练模型的前提下，让 auto-regressive decoder 遵守 SQL 的词法、语法和部分 schema 约束。

### 3. 核心方法

PICARD 运行在 inference time。它接收当前已生成的 token 序列和语言模型对下一 token 的 log-softmax 分数，然后做约束检查：

- 先只考虑 top-k 最高概率 token。
- 对每个候选 token，把它接到当前 partial output 后进行 incremental parsing。
- 不能通过检查的 token 分数设为 `-inf`，不能继续进入 beam。
- 通过检查的 token 保留原始分数，继续参与 beam search。

论文定义了四种 PICARD 模式：

- off：不做检查。
- lexing：只做词法级检查，例如 SQL keyword 拼写、表名/列名是否存在。
- parsing without guards：做语法级检查，能拒绝 clause 顺序错误、缺 `FROM`、表达式结构不合法等问题。
- parsing with guards：最高级检查，加入 schema/alias guard。例如 `tid.cid` 必须保证 table/alias 最终进入作用域；裸 column 必须能在当前 scope 中唯一解析到某个表。

PICARD 的一个关键优点是“非侵入”：它不参与 pre-training 或 fine-tuning，也不要求修改模型 vocabulary 或 decoder 结构，可以直接接在 T5 这类通用 seq2seq 语言模型后面。

### 4. 实验设置与主要结果

论文主要在 Spider 和 CoSQL 上评估，模型使用 fine-tuned T5-Base、T5-Large、T5-3B。

关键结果：

- 在 Spider development set 上，T5-3B 从 69.9 EM / 71.4 EX 提升到 74.1 EM / 76.3 EX；使用数据库内容时，T5-3B+PICARD 达到 75.5 EM / 79.3 EX。
- 在 Spider test set 上，带数据库内容的 T5-3B+PICARD 达到 71.9 EM / 75.1 EX。
- 论文指出 T5-3B 原始模型在 Spider development set 上约 12% 的 SQL 会产生 execution error；加 PICARD 后不可用预测降到约 2%。
- 在 CoSQL 上，T5-3B+PICARD 也优于 T5-3B，并超过当时相关方法。
- 速度开销可控：T5-3B 在 Spider 上 beam size 4 解码时，从平均 2.5 秒/样本变为 3.1 秒/样本。

从实验可见，PICARD 的价值主要不是“理解问题更强”，而是让模型生成过程更少走进非法 SQL 分支。

### 5. 关键贡献

- 提出一种 inference-time constrained decoding 方法，不需要改动模型训练过程。
- 用 incremental parsing 在每一步拒绝非法 token，比最终 beam hypothesis 过滤更早、更高效。
- 把约束分成 lexing、parsing、guard 三个层次，使检查强度可控。
- 在 Spider 和 CoSQL 上显著提升 fine-tuned T5 模型表现。
- 证明通用预训练语言模型可以通过外部 parser 约束增强形式语言生成可靠性。

### 6. 局限性

- PICARD 主要保证词法、语法和部分 schema/scope 合法性，不能保证 SQL 语义一定正确。
- 它不能直接解决 schema linking 错误，例如模型选了一个合法但语义不对的 column，PICARD 不一定能发现。
- 它不处理执行结果不一致、value grounding 错误、聚合口径错误等语义错误。
- 检查规则依赖 parser 和 schema metadata；如果 SQL 方言、函数、复杂语法没有被 parser 覆盖，约束能力会受限。
- 它是生成阶段约束，不是反馈修正框架；生成完执行失败后如何诊断和 repair，不是 PICARD 的核心问题。

### 7. 和本课题的关系

PICARD 对本课题有两个直接启发：

- SQL+ parser/converter 不只是后处理工具，也可以成为生成约束或候选过滤工具。模型生成 SQL+ 时，如果每一步都能被 parser 检查，就可以提前拒绝无效 SQL+。
- PICARD 说明“让模型自由生成，再完全依赖后续修复”并不理想。更稳的路线是 generation-time constraints + execution-time feedback repair 结合。

但本课题和 PICARD 的目标不同：

- PICARD 约束的是最终 SQL 表面形式，目标是减少无效 SQL。
- SQL+ 目标是构造中间表示，并把执行反馈映射到局部步骤，支持 Critic Agent、Skill Router 和 Repair Skill。
- PICARD 不负责修复语义错误；本课题的 repair loop 正是处理“SQL 可执行但结果不对”或“局部语义偏差”的问题。

### 8. 可用于开题答辩的说法

可以这样讲：PICARD 是 EMNLP 2021 的 constrained decoding 工作。它发现 fine-tuned T5 生成 SQL 时仍会产生大量非法 SQL，于是在 beam search 每一步用 incremental parser 检查候选 token，把不能通过词法、语法和 schema guard 的 token 直接拒绝。这样不需要改模型结构，也不需要重新训练，就能显著降低无效 SQL，并提升 Spider 和 CoSQL 的结果。本课题可以借鉴这种思想，把 SQL+ parser/converter 用作生成约束和候选校验，但 SQL+ 还要进一步支持执行反馈诊断和局部修复。

### 9. 可能被老师追问的问题

- 问：PICARD 和 RAT-SQL 的区别是什么？
  答：RAT-SQL 主要改 encoder，解决 schema encoding/linking；PICARD 主要改 decoding process，用 incremental parsing 限制模型生成非法 SQL。
- 问：PICARD 能保证 SQL 正确吗？
  答：不能。它能减少词法、语法和部分 schema/scope 错误，但不能保证查询语义和用户问题一致。
- 问：PICARD 对 SQL+ 有什么启发？
  答：SQL+ parser 可以不仅用于最终解析，也可以用于生成时约束和候选过滤，减少无效 SQL+；但后续仍需要 execution feedback 和 repair skill 处理语义错误。
- 问：为什么不只用 PICARD，不做 SQL+？
  答：PICARD 约束的是 SQL 合法性，不能把错误映射到局部步骤，也不负责执行反馈后的诊断和修复。SQL+ 的重点是可解释、可定位、可修复。

### 10. 精读结论

PICARD 是 SQL+ 生成约束方向的重要对照文献。它证明，形式语言生成不能完全依赖语言模型本身，必须引入 parser 或 grammar 约束来抑制非法输出。对本课题而言，PICARD 支撑的是 SQL+ parser/converter 的工具价值：它可以用于 SQL+ 有效性检查、候选过滤、甚至 generation-time constrained decoding。但 PICARD 不解决语义错误和反馈修复，因此仍需要 SQL+ 层的 Critic Agent、Skill Router 和 Repair Skill。

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

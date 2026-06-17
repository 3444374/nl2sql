# 项目过程记录

本文件记录非实验类项目过程，包括目录整理、开题材料修订、跨电脑同步、工作流调整、飞书或外部文档写入、项目规则更新等。

实验运行、实验指标、失败分析和由实验结果引发的方向调整，仍记录在 `docs/project/experiment_log.md`。

## 2026-06-05 从实验日志迁移的非实验记录

以下条目原先位于 `docs/project/experiment_log.md`。根据新的日志规则，实验日志只保留实验相关记录，因此将这些项目过程记录迁移到本文件。

## 2026-06-03 SQL+ 语法说明与 baseline prompt 设计

实验目的：

固化 SQL+ 语法口径，明确其与 GoogleSQL Pipe Syntax 的关系，并设计后续单 Agent baseline 所需的 direct SQL prompt 与 SQL+ generation prompt。

涉及文件：

- `docs/sqlplus/sqlplus_syntax.md`
- `docs/baseline/baseline_design.md`
- `prompts/baseline/direct_sql.md`
- `prompts/baseline/sqlplus_generation.md`
- `docs/project/experiment_outline.md`
- `README.md`

实验命令：

```powershell
无。本次为实验设计与文档固化，没有运行模型或数据库脚本。
```

实验配置：

- SQL+ 定位：NL2SQL 中间查询表示。
- 参考对象：GoogleSQL Pipe Syntax 的线性管道式查询思想。
- Baseline A：Direct NL2SQL，自然语言直接生成标准 SQL。
- Baseline B：NL2SQL+，自然语言生成 SQL+ 后再转换为标准 SQL。

实验结果：

- 已形成 SQL+ 支持操作、转换规则和反馈修正定位说明。
- 已明确 SQL+ 参考 GoogleSQL Pipe Syntax，但不是 GoogleSQL 语法复刻。
- 已完成两类 baseline prompt 初版。

问题与观察：

- SQL+ 必须控制为开题阶段可验证的最小子集，否则后续 LLM 输出难以稳定解析。
- Baseline prompt 需要强约束输出格式，避免模型输出解释文本影响自动评估。
- 后续需要模型 API 或本地模型能力，才能真正运行 baseline 对比实验。

方向调整：

- 阶段四从“待开始”调整为“prompt 设计完成，待接入模型运行”。
- 下一步从继续写文档转向构建 `run_llm_baseline.py` 或先人工模拟少量模型输出。

下一步：

- 确认使用哪种 LLM 接口或本地模型。
- 实现 baseline 运行脚本，保存模型输出、转换结果、执行结果和错误类型。

## 2026-06-03 OpenAI GPT-5 mini baseline 运行脚本准备

实验目的：

按开题阶段推荐方案，准备 `gpt-5-mini` 的真实 baseline 运行脚本，用同一模型分别生成 Direct NL2SQL 和 NL2SQL+ 输出。

涉及文件：

- `scripts/baseline/run_openai_baseline.py`
- `docs/baseline/openai_baseline_runbook.md`
- `docs/baseline/baseline_design.md`
- `docs/project/experiment_outline.md`
- `README.md`

实验命令：

```powershell
python scripts/baseline/run_openai_baseline.py --dry-run
python scripts/baseline/run_openai_baseline.py --limit 1 --method direct
```

实验配置：

- 模型默认值：`gpt-5-mini`。
- API：OpenAI Responses API。
- 输入：`data/baseline_prompts.jsonl`。
- 输出：`outputs/baseline/direct_model.jsonl` 和 `outputs/baseline/sqlplus_model.jsonl`。
- 依赖：Python 标准库，无需安装 OpenAI SDK。

实验结果：

- `--dry-run` 成功加载 30 条 prompt。
- 未设置 `OPENAI_API_KEY` 时，脚本按预期停止并提示设置环境变量。
- 本次未运行真实 API 调用，因此没有生成真实模型结果。

问题与观察：

- 当前机器环境中 `OPENAI_API_KEY` 未设置。
- 当前 Python 环境未安装 `openai` SDK，但脚本使用标准库 `urllib`，不依赖 SDK。
- 真实运行时如果网络受限，需要允许访问 OpenAI API。

方向调整：

- baseline 工程准备已完成。
- 下一步取决于 API key 和网络权限。

下一步：

- 设置 `$env:OPENAI_API_KEY`。
- 先运行 `python scripts/baseline/run_openai_baseline.py --model gpt-5-mini --limit 1 --method both` 做 smoke test。
- smoke test 通过后运行 30 条完整 baseline，并用 `run_baseline_eval.py` 生成真实报告。

## 2026-06-03 项目目录分层整理

实验目的：

整理 `docs`、`scripts`、`prompts` 目录，避免 SQL+ 基础实验、baseline 实验和后续 agent 实验混在同一层级，方便继续扩展真实 Refiner Agent。

涉及文件：

- `docs/project/`
- `docs/sqlplus/`
- `docs/baseline/`
- `docs/agents/`
- `scripts/sqlplus/`
- `scripts/baseline/`
- `scripts/agents/`
- `prompts/baseline/`
- `prompts/agents/`
- `README.md`
- `docs/README.md`
- `scripts/README.md`

目录调整：

```text
docs/project     项目规划和实验日志
docs/sqlplus     SQL+ 语法、数据集、转换和修正报告
docs/baseline    Direct NL2SQL / NL2SQL+ baseline 文档和报告
docs/agents      多智能体设计、mismatch 诊断和 Refiner 报告

scripts/sqlplus  SQL+ 确定性转换和规则修正实验
scripts/baseline baseline prompt、模型调用和评估
scripts/agents   mismatch 诊断和 Refiner 阶段脚本

prompts/baseline baseline prompt
prompts/agents   后续 agent prompt
```

验证命令：

```powershell
python scripts/sqlplus/run_experiment.py
python scripts/sqlplus/run_repair_experiment.py
python scripts/baseline/prepare_baseline_inputs.py
python scripts/baseline/run_baseline_eval.py --direct-output outputs/baseline/direct_model.jsonl --sqlplus-output outputs/baseline/sqlplus_model_v2.jsonl --label "gpt-5-mini sqlplus prompt v2"
python scripts/agents/diagnose_sqlplus_mismatches.py
python scripts/agents/create_oracle_refiner_outputs.py
python scripts/baseline/run_baseline_eval.py --direct-output outputs\baseline\direct_model.jsonl --sqlplus-output outputs\refiner\sqlplus_refiner_oracle.jsonl --label "oracle refiner on sqlplus v2 failures" --report docs\agents\refiner_oracle_report.md
```

验证结果：

- SQL+ 转换实验保持 30/30 结果一致。
- SQL+ 规则修正实验保持 15/15 修正成功。
- SQL+ prompt v2 baseline 报告正常生成，结果保持 17/30。
- mismatch 诊断正常生成 13 条失败分类。
- oracle Refiner 报告正常生成，保持 13/13。

问题与观察：

- 普通 `Move-Item` 在当前环境中对已有文件移动返回权限拒绝；使用受控提升权限后完成项目内移动。
- 脚本移动到二级目录后，需要将 `ROOT = parents[1]` 改为 `parents[2]`。
- 项目 skill 的默认日志路径已更新到 `docs/project/`。

方向调整：

- 后续新增真实 Refiner 相关文件应放入 `scripts/agents`、`prompts/agents`、`docs/agents`。
- baseline 相关脚本不再放在 `scripts` 根目录。

下一步：

- 设计 `prompts/agents/sqlplus_refiner.md`。
- 实现 `scripts/agents/run_openai_refiner.py`。
- 对 13 条失败样例运行真实 Refiner Agent。

## 2026-06-04 项目记忆与留痕工作流优化

目的：

- 将“关键测试、关键修改、项目进展、方向调整必须留痕”的要求固化为项目级规则。
- 保证后续在另一台 Windows、macOS 或新 Codex/Agent 会话中，也能通过仓库文件恢复当前研究状态和工作流程。

涉及文件：

- `AGENTS.md`
- `.codex/skills/nl2sql-experiment-tracker/SKILL.md`
- `.codex/skills/nl2sql-sqlplus-research/SKILL.md`
- `.codex/skills/nl2sql-repair-skill-lab/SKILL.md`
- `docs/project/workflow_traceability.md`
- `docs/project/experiment_outline.md`
- `docs/README.md`
- `README.md`

执行命令：

```powershell
Get-Content -Raw AGENTS.md
Get-Content -Raw .codex\skills\nl2sql-experiment-tracker\SKILL.md
Get-Content -Raw .codex\skills\nl2sql-repair-skill-lab\SKILL.md
Get-Content -Raw docs\project\experiment_outline.md
Get-ChildItem -Recurse -Depth 2 docs | Select-Object FullName
git status --short
```

结果：

- 新增 `docs/project/workflow_traceability.md`，定义关键事件、开始前检查、完成后文档同步、日志模板、GitHub 同步和跨电脑恢复流程。
- 强化 `AGENTS.md` 的 Project Memory and Traceability Protocol，明确项目记忆以仓库文件为准，不依赖聊天记录。
- 强化三个项目 skill 的触发规则，要求实验、repair skill、SQL+ 研究表述和工作流变化都同步留痕。
- 更新文档索引和 README，使新电脑或新 agent 能快速找到留痕协议。

问题与观察：

- 此次为文档和流程调整，未运行新的 SQL+、agent 或 benchmark 实验。
- 后续每次关键工作结束前，应检查实验日志、大纲、领域报告、开题材料和 README 是否需要同步更新。

方向调整：

- 项目后续采用“实验/修改 -> 结果记录 -> 大纲调整 -> 报告同步 -> skill/AGENTS 更新 -> GitHub 提交推送”的闭环工作流。
- 工作流本身也纳入实验留痕范围，避免跨设备协作时丢失研究判断。

## 2026-06-04 开题汇报 PPTX 生成

目的：

- 将 `docs/opening/opening_ppt.md` 转换为可直接打开和二次编辑的 PowerPoint 文件。
- 保留 Markdown 作为源稿，同时生成最终 `.pptx` 汇报材料。

涉及文件：

- `docs/opening/opening_ppt.md`
- `docs/opening/opening_ppt.pptx`
- `docs/opening/opening_ppt_final.pptx`
- `docs/opening/README.md`

执行命令：

```powershell
python3 -m zipfile -l docs/opening/opening_ppt.pptx
python3 -c "import zipfile, xml.etree.ElementTree as ET; p='docs/opening/opening_ppt.pptx'; z=zipfile.ZipFile(p); names=z.namelist(); assert '[Content_Types].xml' in names; assert 'ppt/presentation.xml' in names; slides=[n for n in names if n.startswith('ppt/slides/slide') and n.endswith('.xml')]; assert len(slides)==20, len(slides); [ET.fromstring(z.read(n)) for n in ['[Content_Types].xml','_rels/.rels','ppt/presentation.xml','ppt/_rels/presentation.xml.rels']+slides]; print('valid xml parts:', len(slides), 'slides')"
open -a /Applications/wpsoffice.app docs/opening/opening_ppt_final.pptx
```

结果：

- 生成 `docs/opening/opening_ppt.pptx` 和最终文件 `docs/opening/opening_ppt_final.pptx`，共 20 页，16:9 宽屏。
- ZIP 包结构和 20 个 slide XML 均已通过解析校验。
- `opening_ppt_final.pptx` 已用 WPS Office 实际打开验证，左侧缩略图显示 20 页，正文页可正常预览。

问题与观察：

- 当前 PPTX 适合作为可编辑初稿，正式汇报前建议在 PowerPoint / WPS 中按学校模板微调封面、字体、页眉页脚和汇报人信息。
- 按用户要求，本次不保留 PPTX 生成脚本，只保留最终 PPT 文件。
- 初版 PPTX 曾出现 WPS 打开失败，后续已重新制作标准 PPTX 并完成 WPS 打开验证。

方向调整：

- 本次为开题材料产物生成，不改变实验路线或当前指标。

## 2026-06-04 开题报告飞书版学术增强与 humanizer 处理

目的：

- 以 `docs/opening/opening_report.md` 为基准，生成适合导入飞书云文档的开题报告版本。
- 在写入飞书前先进行学术论证增强，再进行 humanizer 最终处理，减少模板化表达，同时保持 SQL+ 研究结论和实验指标边界准确。

涉及文件：

- `docs/opening/opening_report.md`
- `docs/opening/opening_report_feishu_polished.md`
- `docs/opening/opening_report_academic_enhanced.md`
- `docs/opening/opening_report_feishu_final.md`
- `docs/project/experiment_log.md`

执行命令：

```powershell
lark-cli config init --new
lark-cli config keychain-downgrade
lark-cli docs +create --api-version v2 --doc-format markdown --content @docs/opening/opening_report_feishu_final.md
```

使用的 skills：

- `academic-pipeline`：按已有开题报告草稿的中途入口检查研究问题、调研覆盖、claim 边界和实验表述。
- `humanizer`：作为写入飞书前的最后一步，清理模板化连接词、机械三段式、过度正向表述和明显 AI 写作痕迹。
- `lark-doc` / `lark-shared`：完成飞书 CLI 配置、Keychain 降级处理和云文档创建。
- `nl2sql-sqlplus-research`：确保 SQL+、Spider smoke test、Skill Router 等开题结论不夸大。
- `nl2sql-experiment-tracker`：记录本次开题材料处理和飞书同步过程。

结果：

- 生成 `docs/opening/opening_report_feishu_final.md`，作为最终导入飞书的 humanizer 后版本。
- 飞书文档创建成功：`https://my.feishu.cn/docx/P1FEduyA6oag0rxHICUc7BSfnid`
- 文档由 bot 身份创建，当前 CLI 没有 user open_id，因此自动授予当前用户 full_access 被跳过；如用户侧打不开，需要后续进行用户身份授权或手动授予权限。

问题与观察：

- 初次创建飞书文档前，`lark-cli` 未配置，需要扫码完成应用配置。
- 配置成功后，沙箱无法访问 macOS Keychain，按用户授权执行 `lark-cli config keychain-downgrade`，将 master key 写入本地文件以便自动化环境继续调用。
- 飞书 API 调用需要联网权限，使用 escalated 网络权限后创建成功。
- 本次仅增强开题报告表达、调研论证和结论边界，不改变实验指标、研究路线和阶段优先级。

方向调整：

- 本次不更新 `docs/project/experiment_outline.md`。原因是文档处理没有改变当前方向判断，仍然保持 projection repair skill、Schema/Critic Agent、Spider/BIRD 小规模子集和达梦 SQL 方言适配为后续重点。

## 2026-06-04 开题报告参考文献扩展与飞书文档更新

目的：

- 按用户补充要求，将 SQL-Factory 及与本课题相关的 Text-to-SQL、多智能体、执行反馈修正文献补入开题报告。
- 在写入飞书前继续执行 humanizer 风格检查，保持报告表达自然，同时确保 SQL+ 研究边界和已有实验指标不被夸大。

涉及文件：

- `docs/opening/opening_report.md`
- `docs/opening/opening_report_feishu_final.md`
- `docs/project/experiment_log.md`

执行命令：

```powershell
lark-cli docs +update --api-version v2 --doc https://my.feishu.cn/docx/P1FEduyA6oag0rxHICUc7BSfnid --command overwrite --doc-format markdown --content @docs/opening/opening_report_feishu_final.md
```

使用的 skills：

- `academic-pipeline`：作为学术材料入口，确认本次属于开题报告调研和参考文献增强。
- `deep-research`：用于补查和筛选与 Text-to-SQL、多智能体 SQL 生成、执行反馈修正相关的文献。
- `humanizer`：写入飞书前检查模板化表达和 AI 化写作痕迹。
- `lark-doc`：将更新后的 Markdown 正文覆盖写入飞书云文档。
- `nl2sql-sqlplus-research`：检查 SQL+、Spider smoke test、Skill Router 等表述边界。
- `nl2sql-experiment-tracker`：追加本次文档进展记录。

结果：

- 将参考文献从 19 条扩展到 22 条。
- 修正 SQL-Factory 引用信息：`SQL-Factory: A Multi-Agent Framework for High-Quality and Large-Scale SQL Generation`，PVLDB 19(3):292-305, 2025，VLDB PDF 为 `https://www.vldb.org/pvldb/vol19/p292-gao.pdf`。
- 新增或强化了 Tool-Assisted Agent、ReFoRCE、XiYan-SQL、CHESS、CHASE-SQL、SQLCritic 等与多阶段生成、执行反馈和修正相关的材料。
- 已同步更新飞书文档：`https://my.feishu.cn/docx/P1FEduyA6oag0rxHICUc7BSfnid`，更新后 `revision_id=7`。

问题与观察：

- 沙箱内访问飞书 API 时仍出现 DNS 解析失败，使用授权后的 escalated 网络权限执行 `lark-cli docs +update` 成功。
- 本次修改只增强文献综述和参考文献，不改变实验指标、研究路线和阶段优先级。

方向调整：

- 本次不更新 `docs/project/experiment_outline.md`。原因是新增文献用于支撑现有研究路线，没有改变后续实验优先级。

## 2026-06-04 开题报告后的实验 outline 轻量调整

目的：

- 根据更新后的开题报告和新增参考文献，检查 `docs/project/experiment_outline.md` 是否需要同步。
- 将实验大纲从早期“多 Agent 串联原型”表述，调整为当前已经形成证据的 `Critic Agent -> Skill Router -> Repair Skill -> Executor` 主线。

涉及文件：

- `docs/project/experiment_outline.md`
- `docs/project/experiment_log.md`

使用的 skills：

- `nl2sql-sqlplus-research`：检查 SQL+ 研究主线、Spider smoke test 和 Skill Router 结果表述边界。
- `nl2sql-experiment-tracker`：按项目记忆规则同步 outline 并追加日志。

结果：

- 更新阶段五“多智能体原型”：明确当前核心闭环为 `Critic Agent -> Skill Router -> Repair Skill -> Executor`，并保留 Intent/Schema/Planner/Translator 等组件作为初始生成和上下文组织模块。
- 更新阶段六“公开数据集适配”：明确后续从单一 Spider smoke test 扩展到多数据库、多难度和更多 SQL 结构，但开题阶段不追求完整排行榜成绩。
- 更新当前阶段优先级：优先补充 projection repair skill，扩展无报错但语义不匹配的诊断与修复，强化工具支撑，并将 SQL-Factory 定位为后续数据扩充参考。

问题与观察：

- 本次没有新增实验运行，也没有改变任何已有指标。
- 新增文献主要支撑多阶段、多智能体、执行反馈和候选验证的合理性，不改变 SQL+ 中间表示与反馈修正的核心路线。

方向调整：

- `docs/project/experiment_outline.md` 已同步开题报告后的最新表述。
- 下一步实验优先级从“实现 value lookup/value_linking 初版”更新为“projection repair skill + 无报错语义错诊断 + 公开子集扩展”。

## 2026-06-04 开题报告飞书版与 PPT 同步 Router v3 结果

目的：

- 用户补充 projection repair skill 和 Skill Router v3 实验后，同步完善飞书开题报告和开题汇报 PPT。
- 将开题材料中的旧结论 `SQL+ Skill Router + Repair Skills 12/13` 更新为 `SQL+ Skill Router + Repair Skills v3 13/13`，并补充 projection repair skill 的 1/1 结果。

涉及文件：

- `docs/opening/opening_report_feishu_final.md`
- `docs/opening/opening_ppt.md`
- `docs/opening/opening_ppt.pptx`
- `docs/opening/opening_ppt_final.pptx`
- `docs/project/experiment_log.md`

执行命令：

```powershell
lark-cli docs +update --api-version v2 --doc https://my.feishu.cn/docx/P1FEduyA6oag0rxHICUc7BSfnid --command overwrite --doc-format markdown --content @docs/opening/opening_report_feishu_final.md
python3 -m zipfile -t docs/opening/opening_ppt_final.pptx
open -a /Applications/wpsoffice.app docs/opening/opening_ppt_final.pptx
```

使用的 skills：

- `nl2sql-sqlplus-research`：检查 Router v3、projection repair skill 和 Spider smoke test 的开题 claim 边界。
- `nl2sql-experiment-tracker`：追加本次材料同步记录。
- `humanizer`：写入飞书前检查报告文本是否存在明显模板化表达。
- `lark-doc`：覆盖更新飞书云文档正文。
- `presentations`：更新开题 PPT 源稿和最终 PPTX 内容。

结果：

- 飞书版报告已更新为五类 repair skill：value-linking、ORDER、aggregation、join、projection。
- 反馈修正对比表更新为 `SQL+ Skill Router + Repair Skills v3`，13 条已知 SQL+ 失败样例达到 SQL+ 有效 13/13、SQL 可执行 13/13、修复成功 13/13。
- 分治 repair skill 表新增 projection repair skill：1 条样例，修复成功 1/1。
- 后续计划从“补 projection repair skill”调整为“扩展无报错语义错诊断、projection/SELECT 诊断稳定性、复合错误路由和公开子集覆盖”。
- 飞书文档更新成功：`https://my.feishu.cn/docx/P1FEduyA6oag0rxHICUc7BSfnid`，更新后 `revision_id=10`。
- PPT 源稿和两个 PPTX 文件均已同步更新。`opening_ppt_final.pptx` 通过 ZIP/XML 校验，并已调用 WPS 打开验证。

问题与观察：

- 沙箱内飞书 API 仍出现 DNS 解析失败，使用授权后的 escalated 网络权限执行 `lark-cli docs +update` 成功。
- PPTX 更新时保留原有 20 页结构和版式，只改第 10、14、15、18、19、20 页中的文本内容。
- 第 14 页中旧对照方法的 SQL 可执行 `12/13` 属于保留指标，不能误改为修复成功率。

方向调整：

- 开题材料已经同步 Router v3 和 projection repair skill 的最新结果。
- 本次不新增实验方向；后续优先级沿用 `docs/project/experiment_outline.md`：无报错语义错、projection/SELECT 诊断、复合错误路由、Spider/BIRD 子集扩展。

## 2026-06-04 飞书用户身份授权与用户 Wiki 文档写入

目的：

- 解决此前飞书文档由 bot 身份创建，用户侧无法直接编辑的问题。
- 使用用户自己创建的飞书 Wiki 文档承载最终开题报告内容。

涉及文件：

- `docs/opening/opening_report_feishu_final.md`
- `docs/project/experiment_log.md`

执行命令：

```powershell
lark-cli auth login --domain docs,drive --no-wait --json
lark-cli auth qrcode --output lark_user_auth_qr.png <verification_url>
lark-cli auth login --device-code <device_code>
lark-cli drive +inspect --url https://my.feishu.cn/wiki/BjwewQgnNiuNv1k1TzrcvNzcnYd
lark-cli docs +update --api-version v2 --as user --doc https://www.feishu.cn/docx/ZPZqdt32poPzrvxUX0Ac2k7pn6c --command overwrite --doc-format markdown --content @docs/opening/opening_report_feishu_final.md --new-title 开题报告
```

结果：

- 用户 OAuth 授权成功，CLI 已具备 user 身份。出于隐私考虑，不在项目日志中记录用户 open_id。
- 用户创建的 Wiki 节点 `BjwewQgnNiuNv1k1TzrcvNzcnYd` 已解析为 docx token `ZPZqdt32poPzrvxUX0Ac2k7pn6c`。
- 使用 `--as user` 成功将开题报告写入用户自己的文档，返回 identity 为 `user`，文档 `revision_id=7`。
- 用户文档链接：`https://my.feishu.cn/wiki/BjwewQgnNiuNv1k1TzrcvNzcnYd?from=from_copylink`

问题与观察：

- bot 身份对用户新建 Wiki 文档没有编辑权限，写入时返回 `No permission to operate on this document`。
- 完成用户 OAuth 后，使用 `--as user` 写入成功。
- 沙箱限制导致 `lark-cli config default-as user` 无法写入 `~/.lark-cli/config.json`，但 `auth status` 显示 auto 身份已可解析为 user，显式指定 `--as user` 即可执行。

方向调整：

- 本次为飞书文档归属和协作流程调整，不改变实验指标和研究方向。

## 2026-06-05 开题报告按学校模板与学术写作规则修订

目的：

- 根据学校开题通知和硕士生开题报告模板，调整当前开题报告结构。
- 参照 `academic-research-suite` 的 academic-paper workflow 检查学术结构、引用数量、格式输出和局限性表述。
- 参照 `humanizer` 清理机械化、口号化和过度拔高的文字，使报告更像研究生本人撰写的正式开题文本。

涉及文件：

- `docs/opening/opening_report.md`
- `docs/opening/opening_report_template_aligned.md`
- `docs/opening/opening_report_template_aligned.docx`
- `docs/opening/opening_report_revision_notes.md`
- `docs/opening/source_requirements/opening_notice_2025.pdf`
- `docs/opening/source_requirements/opening_report_template_0604.docx`
- `docs/opening/source_requirements/requirements_summary.md`
- `docs/opening/README.md`

执行命令：

```powershell
Copy-Item 'D:\开题\关于做好2025级硕士研究生论文开题答辩工作通知.pdf' docs\opening\source_requirements\opening_notice_2025.pdf
Copy-Item 'D:\开题\硕士生开题报告模板0604.docx' docs\opening\source_requirements\opening_report_template_0604.docx
pandoc docs\opening\opening_report.md -o docs\opening\opening_report_template_aligned.docx --reference-doc=docs\opening\source_requirements\opening_report_template_0604.docx
```

结果：

- 开题报告已按模板栏目重组：课题背景、国内外研究现状、研究目标与内容、研究方案与可行性、进度安排、预期成果、创新点、精读文献清单和参考文献。
- 报告中补充 15 篇精读文献清单和 40 篇主要参考文献，用于满足开题通知中的文献阅读要求。
- 报告新增“已有工作局限”，明确自建数据集、Spider smoke test、Skill Router v3 和达梦 SQL 方言适配的边界。
- 生成 `opening_report_template_aligned.docx`，使用学校 Word 模板作为 pandoc reference-doc。

问题与观察：

- PDF 和 Word 模板抽取文本在 PowerShell 中出现编码乱码，因此保留原始文件，并用 `requirements_summary.md` 手工记录要求摘要。
- 当前参考文献数量满足开题形式要求，但定稿前仍建议补 DOI、页码、会议/期刊完整信息并由本人确认精读状态。

方向调整：

- 开题材料后续以 `opening_report.md` 和 `opening_report_template_aligned.docx` 为主线维护。
- 若导师要求正式提交 Word 版，应在 WPS/Word 中人工检查字体、行距、页边距和签字页。

## 2026-06-05 拆分实验日志与项目过程日志

目的：

- 将 `docs/project/experiment_log.md` 收敛为只记录实验相关内容。
- 将文档整理、开题材料修订、GitHub 同步、飞书写入、工作流调整等非实验事项迁移到 `docs/project/project_log.md`。

涉及文件：

- `docs/project/experiment_log.md`
- `docs/project/project_log.md`
- `docs/project/workflow_traceability.md`
- `docs/project/experiment_outline.md`
- `AGENTS.md`
- `.codex/skills/nl2sql-experiment-tracker/SKILL.md`
- `.codex/skills/nl2sql-sqlplus-research/SKILL.md`
- `.codex/skills/nl2sql-repair-skill-lab/SKILL.md`
- `README.md`
- `docs/README.md`

处理内容：

- 从实验日志迁移 11 条非实验记录。
- 保留实验日志中的实验条目，包括 SQL+ 转换、baseline、Refiner、repair skill、Skill Router、Spider smoke test 和 Projection repair skill 等实验。
- 更新项目规则为“双日志”：实验日志只写实验，项目过程日志写非实验过程。

结果：

- `experiment_log.md` 现在只包含实验相关标题和实验模板。
- `project_log.md` 成为非实验项目过程的记录位置。

后续影响：

- 后续开题报告、PPT、飞书、GitHub、工作流和 project skill 调整，不再写入实验日志。
- 后续实验运行、失败、指标和实验方向变化仍写入实验日志。

## 2026-06-08 新增开题精读论文 Skill

目的：

- 将开题精读论文流程沉淀为可复用项目 skill，便于后续继续按统一标准阅读、讲解和记录 15 篇精读文献。
- 明确精读流程需要参考 `academic-research-suite` 的 bibliography/source verification 规范。

涉及文件：

- `.codex/skills/nl2sql-intensive-reading/SKILL.md`
- `.codex/skills/nl2sql-intensive-reading/agents/openai.yaml`
- `docs/opening/intensive_reading_notes.md`
- `docs/opening/papers/README.md`

处理内容：

- 新增 `nl2sql-intensive-reading` skill。
- 规定每篇论文按“来源核验、PDF 阅读、必要图表裁剪、讲解、精读笔记、课题关系、答辩问法”的流程处理。
- 规定论文精读笔记写入 `docs/opening/intensive_reading_notes.md`，不写入 `project_log.md` 或 `experiment_log.md`。
- 规定新增或调整项目 skill 等工作流变化仍按项目规则记录到 `project_log.md`。

结果：

- 后续继续精读开题文献时，可以直接使用 `nl2sql-intensive-reading` skill。
- 本次不涉及实验运行和指标变化，因此不更新 `docs/project/experiment_log.md`。

## 2026-06-08 强化精读文献来源规则

目的：

- 按用户要求，降低 15 篇精读文献中 arXiv-only 文献比例，优先使用 ACL/EMNLP/AAAI/NeurIPS/ICML/ICLR/PVLDB 等正式来源。
- 将“发现 arXiv-only 精读文献时优先替换，并同步开题材料”的要求写入 `nl2sql-intensive-reading` skill。

涉及文件：

- `.codex/skills/nl2sql-intensive-reading/SKILL.md`
- `docs/opening/intensive_reading_plan.md`
- `docs/opening/intensive_reading_notes.md`
- `docs/opening/papers/README.md`
- `docs/opening/venue_strengthened_literature.md`
- `docs/opening/opening_report*.md`
- `docs/opening/opening_ppt.md`

处理内容：

- 将原 DAIL-SQL 精读位替换为 AAAI 2023 的 RESDSQL。
- 将原 SQLCritic 精读位替换为 ICML 2023 的 LEVER。
- 将 DIN-SQL、MAC-SQL、BIRD、Spider 2.0 等条目的来源表述同步为正式 proceedings/venue 口径。
- 在 skill 中补充：替换 arXiv-heavy 文献时，需要同步精读计划、笔记占位、PDF 来源记录、来源强化建议、开题报告草稿和 PPT 参考文献。

结果：

- 15 篇精读主清单不再把 SQLCritic 作为核心精读来源。
- DAIL-SQL 可保留为扩展参考，但不作为 15 篇精读主证据。
- 本次不涉及实验运行和指标变化，因此不更新 `docs/project/experiment_log.md`。

## 2026-06-09 同步新版开题报告到飞书 Wiki

目的：
- 根据 6 月 8 日后开题内容和参考文献来源调整，将本地新版开题报告同步到用户指定的飞书 Wiki 文档。
- 保证飞书版与本地 `docs/opening/opening_report.md` 保持一致，避免旧版十节结构、旧参考文献清单和新版学校模板报告混用。

涉及文件：
- `docs/opening/opening_report.md`
- `docs/opening/opening_report_feishu_final.md`
- `docs/opening/venue_strengthened_literature.md`
- `docs/project/project_log.md`

执行命令：

```powershell
lark-cli docs +fetch --api-version v2 --as user --doc "https://my.feishu.cn/wiki/BjwewQgnNiuNv1k1TzrcvNzcnYd?from=from_copylink" --doc-format markdown --scope outline
lark-cli docs +update --api-version v2 --as user --doc "https://my.feishu.cn/wiki/BjwewQgnNiuNv1k1TzrcvNzcnYd?from=from_copylink" --command overwrite --doc-format markdown --content @docs/opening/opening_report.md
lark-cli docs +fetch --api-version v2 --as user --doc "https://my.feishu.cn/wiki/BjwewQgnNiuNv1k1TzrcvNzcnYd?from=from_copylink" --doc-format markdown --scope outline
```

结果：
- 飞书写入成功，返回 `revision_id=12`。
- 更新后飞书目录已变为学校模板版结构，包含“硕士生论文开题报告”“开题要求对照说明”“课题背景、目的和意义”“研究目标与研究内容”“研究方案与可行性分析”“精读文献清单”“主要参考文献”和“签字页”等章节。
- 本次同步的是本地新版开题报告，其中精读文献清单已采用来源强化后的口径：DAIL-SQL 不再作为 15 篇精读主证据，RESDSQL 进入精读清单；SQLCritic 不再作为精读主证据，LEVER 进入精读清单。
- 本地 `opening_report_feishu_final.md` 已同步为 `opening_report.md` 的同版内容，避免后续误用旧飞书版。

说明：
- 本次属于开题文档同步和参考文献口径更新，不涉及实验运行或指标变化，因此不更新 `docs/project/experiment_log.md`。

## 2026-06-09 使用 humanizer 润色并同步飞书开题报告

目的：
- 按用户要求，对飞书中的开题报告使用 `$humanizer` 规则进行去模板化和去 AI 化处理。
- 保持研究事实、实验指标、参考文献清单和学校模板结构不变，只调整正文表达方式。

涉及文件：
- `docs/opening/opening_report.md`
- `docs/opening/opening_report_feishu_final.md`
- `docs/opening/opening_report_template_aligned.md`
- `docs/project/project_log.md`

处理内容：
- 阅读并按 `C:\Users\Administrator\.codex\skills\humanizer\SKILL.md` 执行。
- 将“自然语言数据库查询的目标，是让用户不必直接掌握 SQL”一类模板化开头改为更自然的研究生开题表述。
- 减少“这些工作说明”“总体来看”“第一、第二、第三”等机械连接。
- 保留 SQL+、Skill Router、Spider smoke test、RESDSQL、LEVER、40 篇参考文献等关键事实和口径。
- 清理正文中的 em dash / en dash 字符，满足 humanizer 的硬约束。

执行命令：

```powershell
lark-cli docs +update --api-version v2 --as user --doc "https://my.feishu.cn/wiki/BjwewQgnNiuNv1k1TzrcvNzcnYd?from=from_copylink" --command overwrite --doc-format markdown --content @docs/opening/opening_report_feishu_final.md
lark-cli docs +fetch --api-version v2 --as user --doc "https://my.feishu.cn/wiki/BjwewQgnNiuNv1k1TzrcvNzcnYd?from=from_copylink" --doc-format markdown --scope outline
```

结果：
- 飞书覆盖写入成功，`docs +update` 返回 `revision_id=31`。
- 随后读取目录验证成功，飞书文档保持新版学校模板结构，读取返回 `revision_id=32`。
- 本地 `opening_report_feishu_final.md` 和 `opening_report_template_aligned.md` 已与 `opening_report.md` 同步。
- 本次不涉及实验运行或指标变化，因此不更新 `docs/project/experiment_log.md`。

备注：
- `lark-cli` 提示当前版本 `1.0.48`，最新版本 `1.0.49`，后续可执行 `lark-cli update` 更新 CLI 和飞书 skills。

## 2026-06-09 GitHub 同步开题材料与精读流程

目的：
- 将 6 月 8 日至 6 月 9 日形成的开题报告、飞书同步版、精读文献计划、项目 skill 和过程记录同步到 GitHub。
- 保持跨电脑工作时可复现当前开题材料和工作流。

处理内容：
- 提交开题报告正文、飞书版、模板对齐版、PPT 草稿和参考文献来源强化材料。
- 提交 `nl2sql-intensive-reading` 项目 skill、精读计划、精读笔记和论文清单 README。
- 更新 `.gitignore`，不提交本地论文 PDF 和论文图截图，避免公开仓库托管第三方论文原文或大体积素材。

说明：
- 本次属于项目同步和文档工作流记录，不涉及实验运行或指标变化，因此不更新 `docs/project/experiment_log.md`。

## 2026-06-09 生成实验进展小结并同步飞书

目的：
- 按用户要求，将当前开题阶段已经完成的实验整理成表格化小结。
- 每个实验说明目的、数据或样例、结果和当前分析，并使用 `$humanizer` 规则降低模板化表达。
- 将小结写入用户指定的飞书 Wiki 文档。

涉及文件：
- `docs/opening/experiment_progress_summary_feishu.md`
- `docs/project/project_log.md`

处理内容：
- 汇总 SQL+ 表达与转换、SQL+ 规则修正、单 Agent baseline、失败类型分析、反馈修正对比、repair skill 分治、Skill Router v3、Spider smoke test 八组实验。
- 保留指标边界：`Skill Router v3 13/13` 只表述为当前 13 条 SQL+ 已知失败样例结果；`Spider smoke test 20/20` 只表述为 `concert_singer` 数据库受支持小子集结果，不说成完整 Spider benchmark。
- 按 humanizer 检查清理 em dash、en dash、模板句和夸大表述。

执行命令：

```powershell
lark-cli docs +update --api-version v2 --as user --doc "https://my.feishu.cn/wiki/JTpwwIfGvirqGQks4jkckw28nrs?from=from_copylink" --command overwrite --doc-format markdown --content @docs/opening/experiment_progress_summary_feishu.md --new-title "开题实验进展小结"
lark-cli docs +fetch --api-version v2 --as user --doc "https://my.feishu.cn/wiki/JTpwwIfGvirqGQks4jkckw28nrs?from=from_copylink" --doc-format markdown --scope outline
```

结果：
- 飞书覆盖写入成功，返回 `revision_id=3`。
- 读取目录验证成功，飞书文档包含“实验总览”“各实验说明”“当前判断”等章节。
- `lark-cli` 提示当前版本 `1.0.47`，最新版本 `1.0.49`，后续可执行 `lark-cli update` 更新 CLI 和 skills。

说明：
- 本次只整理已有实验结果，没有运行新实验，也没有改变指标，因此不更新 `docs/project/experiment_log.md`。

## 2026-06-09 细化实验进展小结表格

目的：
- 按用户追加要求，将实验进展小结从“总览表 + 文字说明”改为“每个实验单独一张表 + 结果解读 + 对课题的意义”。
- 保留 `$humanizer` 处理要求，避免模板化总结和过度夸大。

涉及文件：
- `docs/opening/experiment_progress_summary_feishu.md`
- `docs/project/project_log.md`

处理内容：
- 为 SQL+ 表达与转换、SQL+ 规则修正、单 Agent baseline、SQL+ 失败类型分析、反馈修正对比、repair skill 分治、Skill Router v3、Spider smoke test 分别绘制独立表格。
- 每个实验补充“结果解读”和“对课题的意义”，便于答辩时逐项讲解。
- 对 Skill Router v3 和 Spider smoke test 保留小规模边界表述，不把 `13/13` 和 `20/20` 说成大规模 benchmark 结果。
- 再次按 humanizer 检查 em dash、en dash、模板句和夸大表述。

执行命令：

```powershell
lark-cli docs +update --api-version v2 --as user --doc "https://my.feishu.cn/wiki/JTpwwIfGvirqGQks4jkckw28nrs?from=from_copylink" --command overwrite --doc-format markdown --content @docs/opening/experiment_progress_summary_feishu.md --new-title "开题实验进展小结"
lark-cli docs +fetch --api-version v2 --as user --doc "https://my.feishu.cn/wiki/JTpwwIfGvirqGQks4jkckw28nrs?from=from_copylink" --doc-format markdown --scope outline
```

结果：
- 飞书覆盖写入成功，返回 `revision_id=10`。
- 目录验证成功，文档结构已变为“实验总览”后依次列出八个实验章节，再以“当前综合判断”收束。

说明：
- 本次只重排和细化已有实验说明，没有运行新实验，也没有改变任何指标，因此不更新 `docs/project/experiment_log.md`。
## 2026-06-10 根据导师反馈重构开题报告研究内容

目的：
- 根据导师对飞书开题文档的反馈，补强“国内外研究现状”和“研究内容”两部分。
- 将研究内容从工程步骤描述调整为研究问题、技术难点、解决方法和评估指标。
- 明确 SQL+ 与 SemQL、NatSQL、GoogleSQL Pipe Syntax 的区别，说明为什么需要 SQL+。
- 补充多系统对比、消融实验和修复能力评价指标，使开题论证更接近研究型论文写法。

使用方法：
- 按 `$academic-research-suite` 的论文结构和文献组织思路处理章节逻辑。
- 按 `$humanizer` 规则检查表述，减少模板化连接句、夸大表述和 AI 风格痕迹，并保持无 em dash / en dash。

涉及文件：
- `docs/opening/opening_report.md`
- `docs/opening/opening_report_feishu_final.md`
- `docs/opening/opening_report_template_aligned.md`
- `docs/opening/opening_ppt.md`
- `docs/project/experiment_outline.md`
- `docs/project/project_log.md`

处理内容：
- 重写“国内外研究现状”，按 Text-to-SQL 方法发展、查询中间表示与 SQL 扩展、多智能体和执行反馈、研究不足四条线组织。
- 重写“研究目标与研究内容”，新增关键问题，并将四个研究内容分别写成技术难点、拟采用方法和评估方式。
- 在 PPT 中补充研究现状、研究问题、SQL+ 设计难点、多智能体可观察输出、对比方法和评估指标。
- 在实验大纲中记录开题反馈后的方向调整，后续实验需补充复杂度指标、错误定位准确率、路由准确率、patch minimality、token cost 和 latency。

说明：
- 本次属于开题材料和研究路线调整，没有运行新实验，也没有改变任何实验指标，因此不更新 `docs/project/experiment_log.md`。
## 2026-06-15 开题报告学术化与实验设计调整

- 根据导师反馈，重写 `docs/opening/opening_report.md` 中“国内外研究现状”和“研究目标与研究内容”部分。
- 将研究内容从工程步骤式表述调整为“技术难点、拟采用方法、评估方式”的研究型表述。
- 新增 SQL+ 与 Standard SQL、SemQL-style、NatSQL-style、Pipe-style query 的对比实验设计，补充 token cost、latency、IR parse time、conversion time、error localization accuracy、patch minimality 等指标。
- 新增 `docs/sqlplus/intermediate_representation_comparison_plan.md`，用于支撑开题答辩中“为什么使用 SQL+”的论证。
- 同步更新 `docs/opening/opening_report_feishu_final.md`、`docs/opening/opening_report_template_aligned.md` 和 `docs/opening/opening_ppt.md`。
- 已将 `docs/opening/opening_report_feishu_final.md` 覆盖同步到飞书开题文档，飞书返回 `revision_id=50`。
- 本次未运行新实验，未修改实验结果数值，因此不写入 `docs/project/experiment_log.md`。

## 2026-06-15 开题材料同步：IR 生成成本实验

根据第二个 IR 生成成本实验结果，同步调整本地开题相关材料，包括 `docs/project/opening_preliminary_results.md`、`docs/opening/opening_report.md`、`docs/opening/opening_report_feishu_final.md`、`docs/opening/opening_report_template_aligned.md`、`docs/opening/opening_ppt.md`、`README.md` 和 `docs/sqlplus/intermediate_representation_comparison_plan.md`。本次文档调整将 SQL+ 的阶段性结论改为：SQL+ 当前存在生成成本，不应表述为显著初始生成优势；后续需要通过错误定位、局部 patch、修复轮数和修复成本继续验证其研究价值。

## 2026-06-15 飞书实验文档同步：IR 生成成本实验

- 已将 `docs/opening/feishu_ir_generation_cost_append.md` 追加到飞书实验进展文档：`https://my.feishu.cn/wiki/JTpwwIfGvirqGQks4jkckw28nrs?from=from_copylink`。
- 飞书文档新增章节为“十、IR 生成成本与执行效果对比实验”。
- 追加后读取目录确认成功，飞书返回 `document_id=D7zAdNXWpohJZ0xqqBdclb2LnyO`，`revision_id=25`。
- 本次属于外部文档同步和开题材料维护，不新增实验指标，因此不写入 `docs/project/experiment_log.md`。

## 2026-06-15 飞书开题报告同步：IR 生成成本实验

- 已将本地 `docs/opening/opening_report_feishu_final.md` 覆盖同步到原开题飞书文档：`https://my.feishu.cn/wiki/BjwewQgnNiuNv1k1TzrcvNzcnYd?from=from_copylink`。
- 飞书返回 `revision_id=57`，文档地址为 `https://my.feishu.cn/docx/ZPZqdt32poPzrvxUX0Ac2k7pn6c`。
- 本次同步包含第二个 IR 生成成本实验结果，并将 SQL+ 的结论调整为“存在生成成本，后续重点验证修复收益”，避免把小规模结果夸大为显著初次生成优势。

## 2026-06-15 开题材料同步：Repairability 指标

- 根据 repairability 指标对比实验，更新 `docs/opening/opening_report.md`、`docs/opening/opening_report_feishu_final.md`、`docs/opening/opening_report_template_aligned.md`、`docs/opening/opening_ppt.md`、`docs/project/opening_preliminary_results.md` 和 `README.md`。
- 修正开题报告中 IR 生成成本段落的位置，将其从签字页之后移动到前期实验结果部分。
- 本次文档口径调整为：SQL+ 修复收益主要体现在修复成功率和 patch minimality 上，但 Critic Agent 的 token 成本更高，完整端到端 latency 需要后续带 `latency_seconds` 的新运行验证。

## 2026-06-16 飞书文档同步：Repairability 指标补齐

- 已将本地最新 `docs/opening/opening_report_feishu_final.md` 覆盖同步到飞书开题主文档：`https://my.feishu.cn/wiki/BjwewQgnNiuNv1k1TzrcvNzcnYd?from=from_copylink`。
- 飞书开题主文档写入成功，返回 `revision_id=61`，随后读取目录验证成功。
- 已补齐 `docs/opening/experiment_progress_summary_feishu.md` 中的 “Repairability 指标对比实验” 章节，并将原 “当前综合判断” 顺延为第十一节。
- 已将补齐后的实验进展小结覆盖同步到飞书实验进展文档：`https://my.feishu.cn/wiki/JTpwwIfGvirqGQks4jkckw28nrs?from=from_copylink`。
- 飞书实验进展文档写入成功，返回 `revision_id=28`；随后读取目录返回 `revision_id=29`，目录已包含 “十、Repairability 指标对比实验” 和 “十一、当前综合判断”。
- 第一次同步实验进展文档时使用了旧参数 `--new-title`，被新版 v2 CLI 拒绝；已按新版规则去掉该参数后重试成功。
- `lark-cli` 提示当前版本 `1.0.50`，最新版本 `1.0.53`，后续可执行 `lark-cli update` 更新 CLI 和 skills。

## 2026-06-16 飞书实验进展文档重整：补齐逐实验小结

- 按用户要求，将 `docs/opening/experiment_progress_summary_feishu.md` 恢复为“每个实验单独小结”的结构，而不是只做总览式整理。
- 补齐此前缺少或不够完整的实验小结：`IR 表达复杂度对比实验`、`IR 生成成本与执行效果实验`、`SQL+ 规则修正实验` 和 `Repairability 指标对比实验`。
- 每个实验小结均保留实验目的、数据规模或配置、关键指标、结果解读和对课题的意义。
- 已覆盖同步到飞书实验进展文档：`https://my.feishu.cn/wiki/JTpwwIfGvirqGQks4jkckw28nrs?from=from_copylink`。
- 飞书写入成功，返回 `revision_id=37`；随后读取目录验证成功，目录包含 14 个章节，从“实验总览”到“下一步实验计划”。
- 本次属于外部文档整理和开题材料维护，没有新增实验运行或新指标，因此不写入 `docs/project/experiment_log.md`。

## 2026-06-16 飞书开题主文档：初步实验内容表格化

- 按用户要求，只调整开题报告中“当前初步实验”相关内容，不改动课题背景、国内外研究现状、研究内容和参考文献等其它章节。
- 将原先的段落式实验说明重排为“实验设置”“核心结果总览”“IR 表达复杂度对比”“IR 生成成本与执行效果对比”“反馈修正与 repairability 指标”“Repair Skill 分治结果”“当前初步结论”七个小节。
- 表格化呈现 SQL+ 转换 30/30、Direct SQL 16/30、SQL+ v2 17/30、Skill Router v3 13/13、Spider smoke test 20/20、IR 成本与 repairability 指标等结果，并保留小规模实验和 proxy 对比的边界说明。
- 覆盖同步飞书开题主文档：`https://my.feishu.cn/wiki/BjwewQgnNiuNv1k1TzrcvNzcnYd?from=from_copylink`，飞书返回 `revision_id=75`。
- 同步后读取飞书目录验证成功，目录中已包含“当前初步实验”“实验设置”“核心结果总览”“IR 表达复杂度对比”“IR 生成成本与执行效果对比”“反馈修正与 repairability 指标”“Repair Skill 分治结果”“当前初步结论”。
- 本次属于开题文档呈现方式调整，没有新增实验运行或新指标，因此不写入 `docs/project/experiment_log.md`。

## 2026-06-17 使用学校 PPT 模板生成新版开题汇报

- 根据用户提供的 `D:\开题\模板.pptx`，复制模板到项目内 `assets/opening_template.pptx`，避免 Python 处理中文路径时出现编码问题。
- 安装并使用 `python-pptx` 生成新版模板版 PPT，生成脚本为 `scripts/opening/build_opening_ppt_from_template.py`。
- 新版 PPT 输出为 `docs/opening/opening_ppt_template_version.pptx`，共 27 页，已通过 `python-pptx` 读取校验。
- PPT 内容按当前开题进展重排，覆盖研究背景、国内外研究现状、研究问题、SQL+ 设计、多智能体框架、实验设计、SQL+ 转换实验、IR 表达复杂度实验、IR 生成成本实验、反馈修正实验、repairability 指标、Spider smoke test、局限与后续计划。
- 已更新 `docs/opening/README.md`，补充模板版 PPT 文件说明和复现命令。
- 本次属于开题汇报材料生成与模板套用，没有新增实验运行或新指标，因此不写入 `docs/project/experiment_log.md`。

## 2026-06-17 开题 PPT 图示资源增强

目的：
- 根据用户对开题 PPT 的反馈，补充可编辑的结构图和实验说明图，避免汇报材料只靠文字和表格。
- 将传统 Text-to-SQL 流程、SQL+ 多智能体闭环、SQL+ 步骤化表达、实验组织逻辑和修复路由过程做成可复用 SVG 矢量图，便于后续在 PowerPoint / WPS 中继续编辑。

涉及文件：
- `scripts/opening/build_opening_ppt_enhanced.py`
- `scripts/opening/generate_opening_svgs.py`
- `docs/opening/opening_ppt_template_version_v2.pptx`
- `docs/opening/figures/*.svg`
- `docs/opening/README.md`

处理内容：
- 新增增强版 PPT，保留用户已经手工调整过的原 `opening_ppt_template_version.pptx`，不直接覆盖。
- 新增 6 张 SVG 矢量图：传统 Text-to-SQL 流程、研究定位、SQL+ 步骤化 IR、多智能体闭环、实验逻辑图、repair skill 路由图。
- 将实验部分改成“实验目的、实验条件、评价指标、主要结果、当前结论”的展示结构，使初步实验不再突兀出现。
- 按 `$humanizer` 规则控制表述边界，继续保留小规模实验、proxy 对比和 smoke test 的限制说明。

验证：
```powershell
python scripts/opening/build_opening_ppt_enhanced.py
python scripts/opening/generate_opening_svgs.py
python - <<'PY'
from pathlib import Path
import ast, xml.etree.ElementTree as ET
ast.parse(Path('scripts/opening/generate_opening_svgs.py').read_text(encoding='utf-8'))
for p in Path('docs/opening/figures').glob('*.svg'):
    ET.parse(p)
PY
```

说明：
- 本次属于开题展示材料和图示资源整理，没有运行新的 SQL+、Text-to-SQL 或 agent 实验，因此不更新 `docs/project/experiment_log.md`。

## 2026-06-18 GitHub 同步开题材料、IR 实验与 PPT 图示资源

目的：
- 按用户要求，将当前目录中的开题材料、IR 对比实验产物、repairability 指标产物、PPT 模板版和 SVG 图示资源同步到 GitHub。
- 保证另一台电脑可以通过 GitHub 拉取当前项目进度、实验记录、脚本和可复用开题展示材料。

同步前检查：
- 已执行 Git 状态检查，确认当前分支为 `main`，远程为 `https://github.com/3444374/nl2sql.git`。
- 已扫描 `sk-proj-`、`sk-`、`OPENAI_API_KEY` 等敏感字符串，没有发现真实 API key，仅存在环境变量名和示例占位。
- 已对新增和修改的 Python 脚本执行 AST 解析校验。
- 已重新生成 SVG 图示，并完成 XML 解析校验。

说明：
- 本次是项目同步和材料沉淀，不新增实验结果，因此不写入 `docs/project/experiment_log.md`。

## 2026-06-18 开题 PPT 每页讲解备注写入

目的：
- 按用户要求，为增强版开题 PPT 的每一页补充汇报讲解备注，方便后续试讲和正式开题答辩。
- 将备注写入 PPTX 的 notes 区，而不是另建纯文本讲稿，保证打开 PPT 时可直接查看每页讲解提示。

涉及文件：
- `docs/opening/opening_ppt_template_version_v2.pptx`
- `scripts/opening/add_opening_ppt_notes.py`
- `docs/opening/README.md`
- `docs/project/project_log.md`

处理内容：
- 新增 `add_opening_ppt_notes.py`，为 28 页增强版 PPT 写入逐页讲解稿。
- 备注内容重点覆盖课题定位、传统 Text-to-SQL 问题、SQL+ 与 SemQL/NatSQL/Pipe-style 的区别、多智能体闭环、实验目的、实验条件、指标、结果边界和后续计划。
- 继续保持开题阶段结果边界：不把 controlled proxy 当作完整系统复现，不把 Spider smoke test 当作完整 Spider benchmark，不把已知失败集 13/13 夸大为大规模通用结论。

验证：
```powershell
python scripts/opening/add_opening_ppt_notes.py
python - <<'PY'
from pptx import Presentation
prs = Presentation('docs/opening/opening_ppt_template_version_v2.pptx')
missing = [i for i, s in enumerate(prs.slides, 1) if not s.notes_slide.notes_text_frame.text.strip()]
print(missing)
PY
```

结果：
- 28 页 PPT 均已写入备注，无空备注页。
- 本次属于开题展示材料维护，没有新增实验运行或指标变化，因此不更新 `docs/project/experiment_log.md`。

## 2026-06-18 Canva 开题 PPT 视觉增强候选生成

目的：
- 根据用户反馈，尝试使用 Canva 插件生成开题 PPT 的视觉增强候选，用于改善当前 PPT 中部分页面偏文字罗列、图示不够美观的问题。
- 保留本地 PPT 作为学校模板和可复现主版本，Canva 作为视觉设计增强与版式参考。

处理内容：
- 使用 Canva presentation generation 生成 4 个候选设计。
- 生成 prompt 明确要求：中文学术开题风格、深蓝/橙/灰/白配色、避免泛 AI 紫色风格、强化流程图、架构图、实验卡片、指标表和风险矩阵。
- 保持实验结果边界：controlled proxy 不当作完整系统复现，Spider smoke test 不当作完整 Spider benchmark，13/13 仅限当前已知失败集。

候选设计：
- Candidate 1: `https://www.canva.com/d/7lMYUPE6cTiVWYs`
- Candidate 2: `https://www.canva.com/d/wfwZ6bnyOuMzjtu`
- Candidate 3: `https://www.canva.com/d/I6u6zyLf-GVObem`
- Candidate 4: `https://www.canva.com/d/MIY7iMPiN-vwm7Q`

说明：
- 当前只生成候选，没有创建最终可编辑 Canva 设计。
- 若用户选定某个 candidate，再调用 Canva create-design-from-candidate 生成正式可编辑设计。
- 本次属于展示材料设计探索，没有新增实验运行或指标变化，因此不更新 `docs/project/experiment_log.md`。

## 2026-06-18 开题 PPT 局部视觉优化

目的：
- 根据用户反馈，不重新生成整套 Canva PPT，而是参考 Canva 式版式思路，局部优化本地开题 PPT 中图示不够美观和纯文字罗列的问题。
- 保留本地 PPT 的学校模板、页数、讲解备注和实验指标，避免外部设计工具改写或夸大研究结论。

涉及文件：
- `docs/opening/opening_ppt_template_version_v3.pptx`
- `scripts/opening/refine_opening_ppt_visuals.py`
- `docs/opening/README.md`
- `docs/project/project_log.md`

处理内容：
- 在 `opening_ppt_template_version_v2.pptx` 基础上生成 v3，不覆盖 v2。
- 重点优化第 2、4、5、6、9、23、24、25、26、27、28 页。
- 将纯文字页重排为路线图、挑战卡片、研究现状演进图、SemQL/NatSQL/Pipe/SQL+ 对比矩阵、研究问题卡片、综合判断双栏、后续计划时间线、创新点三柱、风险应对矩阵、总结卡片和参考文献分组图。
- 优化脚本会删除原正文形状后再重排，避免仅用白色遮罩覆盖旧文字，方便后续手工编辑。

验证：
```powershell
python scripts/opening/refine_opening_ppt_visuals.py
$env:PYTHONIOENCODING='utf-8'; python - <<'PY'
from pptx import Presentation
prs = Presentation('docs/opening/opening_ppt_template_version_v3.pptx')
print(len(prs.slides))
print([i for i, s in enumerate(prs.slides, 1) if not s.notes_slide.notes_text_frame.text.strip()])
PY
```

结果：
- v3 PPT 共 28 页。
- 28 页备注均保留，无空备注页。
- 本次属于开题展示材料视觉优化，没有新增实验运行或指标变化，因此不更新 `docs/project/experiment_log.md`。

## 2026-06-18 重画 SQL+ 多智能体闭环 SVG

目的：
- 根据用户反馈，修正原 SQL+ 多智能体闭环图中修复循环位置不清晰的问题。
- 原图将 `Skill Router`、`Repair Skill`、`SQL+ Patch` 和重新验证放在断开的三行，容易误解为一次性流水线，而不是反馈闭环。

涉及文件：
- `docs/opening/figures/sqlplus_multi_agent_loop_v2.svg`
- `scripts/opening/generate_sqlplus_loop_v2_svg.py`
- `docs/opening/README.md`
- `docs/project/project_log.md`

处理内容：
- 新增专用脚本生成新版闭环图，不影响其它 SVG 图。
- 新版图将主链路和修复回路分成三层：生成链路、执行与诊断、局部修复回路。
- 明确绘制 `Repair Skill -> SQL+ Patch -> Translator -> Executor` 的回路，说明 patch 后回到 SQL+ 转 SQL 和重新执行环节。
- 图下注释强调：失败反馈进入 Critic 和 Router，Repair Skill 只修改 SQL+ 局部步骤，patch 后重新转换与执行。

验证：
```powershell
python scripts/opening/generate_sqlplus_loop_v2_svg.py
python - <<'PY'
from pathlib import Path
import ast, xml.etree.ElementTree as ET
ast.parse(Path('scripts/opening/generate_sqlplus_loop_v2_svg.py').read_text(encoding='utf-8'))
ET.parse('docs/opening/figures/sqlplus_multi_agent_loop_v2.svg')
PY
```

结果：
- 新版 SVG 已生成并通过 XML 解析校验。
- 本次属于开题图示资源修正，没有新增实验运行或指标变化，因此不更新 `docs/project/experiment_log.md`。

## 2026-06-18 替换 SQL+ 闭环图并扩充 PPT 备注

目的：
- 根据用户反馈，修正 PPT 中 SQL+ 多智能体闭环图的循环位置，使 `Repair Skill -> SQL+ Patch -> Translator -> Executor` 的回路更清晰。
- 扩充 PPT 备注，将每页备注调整为“汇报讲稿 + 答辩备注”结构，实验页补充数据集、实验条件、指标来源和结果边界。

涉及文件：
- `docs/opening/opening_ppt_template_version_v2.pptx`
- `docs/opening/opening_ppt_template_version_v3.pptx`
- `docs/opening/figures/sqlplus_multi_agent_loop_v2.svg`
- `scripts/opening/generate_sqlplus_loop_v2_svg.py`
- `scripts/opening/refine_opening_ppt_visuals.py`
- `scripts/opening/add_opening_ppt_detailed_notes.py`
- `docs/opening/README.md`
- `docs/project/project_log.md`

处理内容：
- 新增并生成 `sqlplus_multi_agent_loop_v2.svg`，明确主生成链路、执行诊断链路和局部修复回路。
- 更新 v3 PPT 第 8 页，用 native PPT shape 重新绘制闭环图，避免旧图中修复循环位置不清晰。
- 重新生成 v3 PPT，并向 v2 和 v3 同步写入详细备注。
- 实验页备注补充：自建订单分析数据集 30 条样例、SQL+ 已知失败集 13 条、Direct SQL 失败样例 14 条、Spider dev concert_singer 20 条受支持样例，以及 valid rate、execution match、token、latency、localization accuracy、patch minimality 等指标来源。
- 备注中继续保留边界说明：controlled proxy 不代表完整 SemQL/NatSQL 复现，Spider smoke test 不代表完整 Spider benchmark，Skill Router 13/13 仅限当前已知失败集。

验证：
```powershell
python scripts/opening/generate_sqlplus_loop_v2_svg.py
python scripts/opening/refine_opening_ppt_visuals.py
python scripts/opening/add_opening_ppt_detailed_notes.py
$env:PYTHONIOENCODING='utf-8'; python - <<'PY'
from pptx import Presentation
prs = Presentation('docs/opening/opening_ppt_template_version_v3.pptx')
print(len(prs.slides))
for i in [1, 12, 20]:
    note = prs.slides[i-1].notes_slide.notes_text_frame.text.strip()
    print(i, note[-200:])
PY
```

结果：
- v3 PPT 仍为 28 页。
- 第 8 页闭环图已改为新版逻辑。
- v2 和 v3 的备注已包含汇报讲稿与答辩备注，实验页备注已补充指标计算说明。
- 本次属于开题展示材料修正，没有新增实验运行或指标变化，因此不更新 `docs/project/experiment_log.md`。

## 2026-06-18 ??? PPT ? 8 ? SQL+ ???

???
- ????????????? PPT????? `docs/opening/opening_ppt_template_version_v3.pptx` ???? 8 ????
- ?? SVG ????? PPT ????`python-pptx` ????????? SVG????????? PPT ??????????????????

?????
- ?? `scripts/opening/refine_opening_ppt_visuals.py` ?? 8 ?????? PowerShell ???????????
- ????? v3 PPT??? `slide_8(prs.slides[7])` ??? 8 ??????????? PPT ?????
- ? 8 ????????? `SQL+ Patch -> Translator -> Executor`????????? Critic/Router?Repair Skill ??? SQL+ ?????patch ?????????

???
```powershell
python - <<'PY'
from pptx import Presentation
prs = Presentation('docs/opening/opening_ppt_template_version_v3.pptx')
print(len(prs.slides))
print([i for i,s in enumerate(prs.slides,1) if not s.notes_slide.notes_text_frame.text.strip()])
PY
```

???
- `opening_ppt_template_version_v3.pptx` ?? 28 ??
- ???????
- ? 8 ????? `patch ??? Translator / Executor` ???????????
- ??????????????????????????????????? `docs/project/experiment_log.md`?


## 2026-06-18 PPT experiment-note method clarification

Purpose:
- Update only experiment-related PPT notes, not non-experiment slides.
- Replace file-name-only source descriptions with oral-defense-ready explanations of experiment method, sample selection, proxy meaning, metric calculation, and metric interpretation.

Scope:
- Updated notes for slides 11-22 in both `docs/opening/opening_ppt_template_version_v2.pptx` and `docs/opening/opening_ppt_template_version_v3.pptx`.
- Added reusable note sources under `docs/opening/notes/`.
- Added `scripts/opening/update_experiment_notes.py` to update only experiment notes without regenerating or redesigning the whole PPT.

Content changes:
- Explained `proxy` as a controlled proxy representation, not a full reproduction of SemQL, NatSQL, or GoogleSQL Pipe Syntax.
- Explained how samples are selected: 30 self-built order-analysis cases, SQL+ known-failure cases, Direct SQL failure cases, and a 20-case Spider `concert_singer` smoke-test subset.
- Explained how the five IR forms are constructed: Standard SQL from gold SQL, SQL+ from gold SQL+, SemQL-style proxy from SQL+ AST-like tree form, NatSQL-style proxy from SQL-like natural-order form, and Pipe-style proxy from pipeline-style steps.
- Explained how token count, step/clause count, nesting depth, alias dependency, cross-clause reference, valid rate, execution match, repair success, localization accuracy, patch minimality, repair rounds, token cost, and latency are measured or interpreted.

Validation:
```powershell
python scripts/opening/update_experiment_notes.py
```
Spot checks confirmed the updated notes are present in slides 12, 13, 14, 18, 20, and 22 of v3.

Boundary:
- This was documentation/PPT maintenance only.
- No new experiment was run and no metric changed, so `docs/project/experiment_log.md` was not updated.

## 2026-06-18 Repair skill workflow update

- Added formal Spider benchmark repair route: `scripts/agents/pipeline/spider_sqlplus_repair_router.py` -> `scripts/agents/tools/semantic_repair_skill.py`.
- Updated `AGENTS.md` and `.codex/skills/nl2sql-repair-skill-lab/SKILL.md` to include the new semantic repair skill and Spider multi-db scaffold commands.
- Added `scripts/benchmarks/build_spider_multidb_subset.py` for future cross-database Spider evaluation once local SQLite databases are available.
- Process boundary: do not claim multi-database accuracy until the full Spider `database/` directory is present and evaluated.

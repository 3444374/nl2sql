# 开题材料目录

本目录用于集中存放研究生开题汇报材料。

## 文件说明

- `opening_report.md`：开题报告草稿，包含课题背景、研究意义、国内外研究现状、研究内容、技术路线、初步实验和参考资料。
- `opening_report_template_aligned.md`：按学校开题报告模板栏目重组后的 Markdown 版本。
- `opening_report_template_aligned.docx`：使用学校 Word 模板作为 reference-doc 生成的 Word 版本。
- `opening_report_revision_notes.md`：本轮按学校通知、academic-research-suite 和 humanizer 修订的说明。
- `source_requirements/`：学校开题通知、开题报告模板和要求摘要。
- `opening_ppt.md`：开题汇报 PPT 稿，按页组织，可直接复制到 PowerPoint / WPS 中制作幻灯片。
- `opening_ppt.pptx`：由 `opening_ppt.md` 生成的 16:9 开题汇报幻灯片。
- `opening_ppt_final.pptx`：WPS 实际打开验证通过的最终开题汇报 PPT。
- `opening_ppt_template_version.pptx`：基于 `D:\开题\模板.pptx` 套用学校模板生成的新版开题汇报 PPT，共 27 页，内容按当前开题报告和最新实验结果重排。
- `opening_ppt_template_version_v2.pptx`：增强版模板 PPT，共 28 页，补充传统 Text-to-SQL 架构图、SQL+ 多智能体闭环图、实验组织逻辑和实验卡片页。当前版本已在每页备注区写入汇报讲解稿。
- `opening_ppt_template_version_v3.pptx`：局部视觉优化版 PPT，在 v2 基础上保留备注，参考 Canva 式展示思路，将部分纯文字页重排为路线图、卡片、对比矩阵、风险应对表和结论卡。
- `figures/`：开题 PPT 可复用 SVG 矢量图，可插入 PowerPoint / WPS 后继续缩放、编辑或转换为形状。
- `../../scripts/opening/build_opening_ppt_from_template.py`：生成模板版 PPT 的脚本，默认读取 `assets/opening_template.pptx` 并输出 `opening_ppt_template_version.pptx`。
- `../../scripts/opening/build_opening_ppt_enhanced.py`：生成增强版模板 PPT，默认输出 `opening_ppt_template_version_v2.pptx`，不会覆盖原 PPT。
- `../../scripts/opening/generate_opening_svgs.py`：生成开题汇报所需 SVG 架构图和实验逻辑图。
- `../../scripts/opening/generate_sqlplus_loop_v2_svg.py`：单独生成新版 SQL+ 多智能体反馈闭环 SVG。
- `../../scripts/opening/add_opening_ppt_notes.py`：向增强版 PPT 的每页备注区写入汇报讲解稿。
- `../../scripts/opening/add_opening_ppt_detailed_notes.py`：向 v2/v3 PPT 写入更详细的逐页备注，备注按“汇报讲稿”和“答辩备注”组织，实验页包含数据集、实验条件、指标来源和结果边界。
- `../../scripts/opening/refine_opening_ppt_visuals.py`：在 v2 基础上生成局部视觉优化版 `opening_ppt_template_version_v3.pptx`，重点优化文字密度高的页面。

## 可复用矢量图

- `figures/traditional_text_to_sql.svg`：传统 Text-to-SQL 流程及问题。
- `figures/research_positioning.svg`：SQL+ 与 SemQL、NatSQL、Pipe-style 表示的研究定位对比。
- `figures/sqlplus_stepwise_ir.svg`：SQL+ 线性步骤与 repair skill 锚点。
- `figures/sqlplus_multi_agent_loop.svg`：SQL+ 多智能体生成与反馈修正闭环。
- `figures/sqlplus_multi_agent_loop_v2.svg`：新版 SQL+ 多智能体闭环图，明确展示 `Repair Skill -> SQL+ Patch -> Translator -> Executor` 的回路位置。
- `figures/experiment_logic_map.svg`：研究假设、实验目的和实验项目之间的映射。
- `figures/repair_skill_router.svg`：Critic Agent、Skill Router 和 repair skill 的修复流程。

## 当前实验亮点

- SQL+ 转 SQL 执行一致：30/30。
- Direct NL2SQL：16/30。
- NL2SQL+ prompt v2：17/30。
- SQL+ 非 gold 单 Refiner：4/13。
- SQL+ Skill Router + Repair Skills v3：13/13。
- Spider smoke test：20 条受支持 Spider dev 样例，SQL+ 有效 20/20，SQL 可执行 20/20，执行一致 20/20。

## 后续建议

1. 根据导师意见调整题目、汇报人信息和创新点表述。
2. 需要正式答辩前，可在 PowerPoint / WPS 中进一步微调版式和学校模板。
3. 后续扩展无报错语义错诊断、Spider/BIRD 子集和达梦 SQL 方言适配实验。

## 模板版 PPT 生成命令

```powershell
python scripts/opening/build_opening_ppt_from_template.py
```

生成增强版 PPT：

```powershell
python scripts/opening/build_opening_ppt_enhanced.py
```

生成或刷新 SVG 矢量图：

```powershell
python scripts/opening/generate_opening_svgs.py
```

单独刷新新版 SQL+ 多智能体闭环图：

```powershell
python scripts/opening/generate_sqlplus_loop_v2_svg.py
```

向增强版 PPT 写入或刷新每页讲解备注：

```powershell
python scripts/opening/add_opening_ppt_notes.py
```

向 v2/v3 PPT 写入或刷新详细讲稿和答辩备注：

```powershell
python scripts/opening/add_opening_ppt_detailed_notes.py
```

生成局部视觉优化版 PPT：

```powershell
python scripts/opening/refine_opening_ppt_visuals.py
```

如果新电脑缺少依赖，先安装：

```powershell
python -m pip install python-pptx
```

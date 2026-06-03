# 项目留痕与工作流协议

本文档定义 NL2SQL+ 开题实验的项目记忆、实验留痕和跨电脑协作规则。目标是让任何一台电脑、任何一次 Codex/Agent 会话都能接上当前研究状态。

## 核心原则

项目记忆以仓库文件为准，不依赖聊天记录。

每次关键测试、关键修改、项目进展或方向调整，都要在同一轮工作中更新相应文档。实验结果、失败原因、后续方向和复现命令必须可追溯。

## 什么算关键事件

需要留痕的事件包括：

- 新增或修改实验脚本、prompt、agent、tool、repair skill、数据集或 benchmark 适配器。
- 执行模型/API 实验、benchmark smoke test、修复实验或 baseline 实验。
- 实验失败，但失败原因会影响后续方向。
- 指标发生变化，例如成功率、可执行率、修复成功率、Spider 子集覆盖数。
- 研究方向、阶段优先级、开题报告表述或实验设计发生变化。
- 跨电脑同步、GitHub 使用、环境变量、依赖安装或项目 skill 安装流程发生变化。
- `AGENTS.md` 或 `.codex/skills/*/SKILL.md` 的工作规则发生变化。

## 开始工作前

1. 检查 Git 状态：

```powershell
git status --short
```

2. 阅读当前阶段：

```powershell
Get-Content docs/project/experiment_outline.md
```

3. 按任务选择项目 skill：

- 实验和进展记录：`nl2sql-experiment-tracker`
- SQL+ 语法、开题表述、benchmark 子集：`nl2sql-sqlplus-research`
- repair skill、Skill Router、Critic/Refiner 修复实验：`nl2sql-repair-skill-lab`

## 工作中

优先使用可复现脚本，不使用一次性手工流程。所有重要命令应能写入实验日志。

建议输出位置：

- SQL+ 语法和转换：`docs/sqlplus/`
- baseline：`docs/baseline/`
- agent 和 repair skill：`docs/agents/`
- benchmark：`docs/benchmarks/`
- 开题材料：`docs/opening/`
- 项目级路线和日志：`docs/project/`

## 工作完成后必须检查

根据事件类型更新文件：

- 所有关键事件：追加 `docs/project/experiment_log.md`
- 方向变化：更新 `docs/project/experiment_outline.md`
- 实验结果：更新对应领域报告
- 开题可引用结果：检查 `docs/opening/opening_report.md`、`docs/opening/opening_ppt.md`、`docs/project/opening_preliminary_results.md`
- 复现命令或总体指标变化：更新 `README.md` 或 `docs/README.md`
- 工作流变化：更新 `AGENTS.md`、本文件和相关 `.codex/skills/*/SKILL.md`

结束前运行：

```powershell
git status --short
```

最终回复用户时说明：

- 做了什么实验或修改
- 关键结果和指标
- 更新了哪些文件
- 下一步建议

## 日志模板

追加到 `docs/project/experiment_log.md` 时建议使用：

~~~markdown
## YYYY-MM-DD 事件标题

目的：

- ...

涉及文件：

- `...`

执行命令：

```powershell
...
```

结果：

- ...

问题与观察：

- ...

方向调整：

- ...
~~~

如果没有执行实验命令，也要写明“本次为文档/流程调整，未运行实验”。

## GitHub 同步规则

关键阶段完成后建议提交并推送，保证另一台电脑可以继续工作：

```powershell
git add .
git commit -m "简短说明"
git push
```

提交信息建议直接说明研究进展，例如：

- `Add Spider smoke benchmark report`
- `Implement SQL+ skill router repair experiment`
- `Document traceability workflow and project memory`

不要提交 `.env`、API key、临时缓存、模型密钥或本机私有配置。

## 跨电脑恢复流程

新电脑克隆后：

```powershell
git clone https://github.com/3444374/nl2sql.git
cd nl2sql
powershell -ExecutionPolicy Bypass -File scripts/setup/install_project_skills.ps1
```

然后阅读：

- `AGENTS.md`
- `docs/project/experiment_outline.md`
- `docs/project/experiment_log.md`
- 本文件

这样新的 Agent 可以恢复项目目标、当前结果、下一步方向和留痕要求。

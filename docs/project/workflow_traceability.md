# 项目留痕与工作流协议

本文档定义 NL2SQL+ 开题实验的项目记忆、实验留痕和跨电脑协作规则。项目记忆以仓库文件为准，不依赖聊天记录。

## 双日志规则

本项目采用双日志：

- `docs/project/experiment_log.md`：只记录实验相关内容。
- `docs/project/project_log.md`：记录非实验类项目过程。

写入 `experiment_log.md` 的内容包括：

- 实验运行记录。
- 模型/API 调用结果。
- benchmark 或 smoke test。
- baseline、agent、repair skill、Skill Router 等实验。
- 实验失败记录。
- 指标变化和实验结果分析。
- 由实验结果引发的研究方向调整。

写入 `project_log.md` 的内容包括：

- 目录整理。
- GitHub 同步和跨电脑设置。
- 开题报告、PPT、飞书文档等材料修订。
- 工作流、AGENTS 或 project skill 修改。
- 非实验性质的文档归档和流程调整。

## 开始工作前

1. 检查 Git 状态：

```powershell
git status --short
```

2. 阅读当前阶段：

```powershell
Get-Content docs/project/experiment_outline.md
```

3. 判断本轮工作类型：

- 如果要跑实验、改实验脚本、改 agent/repair skill 或产生指标，使用 `nl2sql-experiment-tracker`。
- 如果要改 SQL+ 研究表述、开题报告或 benchmark 解释，使用 `nl2sql-sqlplus-research`。
- 如果要改 repair skill、Critic、Skill Router 或修复实验，使用 `nl2sql-repair-skill-lab`。

## 工作完成后

根据事件类型更新文件：

- 实验结果：更新 `docs/project/experiment_log.md` 和对应领域报告。
- 实验方向变化：更新 `docs/project/experiment_outline.md`。
- 开题可引用实验结果变化：检查 `docs/opening/` 和 `docs/project/opening_preliminary_results.md`。
- 非实验流程变化：更新 `docs/project/project_log.md`。
- 工作流变化：更新 `AGENTS.md`、本文件和相关 `.codex/skills/*/SKILL.md`。
- 复现命令或总体指标变化：更新 `README.md` 或 `docs/README.md`。

结束前运行：

```powershell
git status --short
```

## 实验日志模板

追加到 `docs/project/experiment_log.md` 时使用：

~~~markdown
## YYYY-MM-DD 实验标题

实验目的：

- ...

涉及文件：

- `...`

实验命令：

```powershell
...
```

实验配置：

- ...

实验结果：

- ...

问题与观察：

- ...

方向调整：

- ...
~~~

## 项目过程日志模板

追加到 `docs/project/project_log.md` 时使用：

~~~markdown
## YYYY-MM-DD 事项标题

目的：

- ...

涉及文件：

- `...`

处理内容：

- ...

结果：

- ...

后续影响：

- ...
~~~

## GitHub 同步

关键阶段完成后建议提交并推送：

```powershell
git add .
git commit -m "简短说明"
git push
```

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
- `docs/project/project_log.md`
- 本文件

# Cross-Machine Setup and GitHub Sync

This document explains how to move this project between Windows, macOS, and another PC using GitHub, and how to make Codex use the same project rules and skills.

## 1. What Should Be Synced

Sync these through GitHub:

- `src/`
- `scripts/`
- `prompts/`
- `docs/`
- `data/` small curated datasets and experiment inputs
- `.codex/skills/` project skills
- `AGENTS.md`
- `README.md`

Do not sync:

- API keys
- `.env`
- local virtual environments
- `__pycache__/`
- downloaded raw external repositories such as `data/benchmarks/spider_raw/`

The `.gitignore` file already covers these.

## 2. First-Time GitHub Setup on This Machine

From the project root:

```powershell
git init
git add .
git status
git commit -m "Initial NL2SQL+ opening experiments"
git branch -M main
git remote add origin https://github.com/<your-user-or-org>/<repo-name>.git
git push -u origin main
```

If you prefer SSH:

```powershell
git remote add origin git@github.com:<your-user-or-org>/<repo-name>.git
```

## 3. Setup on Another Windows PC

```powershell
git clone https://github.com/<your-user-or-org>/<repo-name>.git
cd <repo-name>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
powershell -ExecutionPolicy Bypass -File scripts/setup/install_project_skills.ps1
python scripts/sqlplus/run_experiment.py
python scripts/benchmarks/run_spider_smoke.py --limit 20
```

Set API key only on that machine, never in git:

```powershell
[Environment]::SetEnvironmentVariable('OPENAI_API_KEY','YOUR_KEY','User')
```

Then restart the terminal.

## 4. Setup on macOS

```bash
git clone https://github.com/<your-user-or-org>/<repo-name>.git
cd <repo-name>
python3 -m venv .venv
source .venv/bin/activate
mkdir -p ~/.codex/skills
cp -R .codex/skills/* ~/.codex/skills/
python scripts/sqlplus/run_experiment.py
python scripts/benchmarks/run_spider_smoke.py --limit 20
```

Set API key only on that machine:

```bash
export OPENAI_API_KEY="YOUR_KEY"
```

For persistent setup, put it in your shell profile or use your OS secret manager. Do not commit it.

## 5. Daily Workflow Across Machines

Before working:

```bash
git pull
```

After finishing an experiment:

```bash
git status
git add docs scripts src prompts data .codex AGENTS.md README.md
git commit -m "Record <short experiment name>"
git push
```

If multiple machines changed the same file:

```bash
git pull --rebase
```

Resolve conflicts carefully. Do not delete experiment-log history.

## 6. Codex Behavior on Any Machine

When Codex opens this repo, it should read:

- `AGENTS.md`
- `docs/project/experiment_outline.md`
- `.codex/skills/*/SKILL.md`

The portable project skills are stored in the repo, but Codex may only auto-list globally installed skills. Run the install script after cloning to copy them into `~/.codex/skills`.

## 7. Current Reproducibility Checks

Use these checks after cloning:

```bash
python scripts/sqlplus/run_experiment.py
python scripts/agents/pipeline/run_skill_router_experiment.py
python scripts/benchmarks/run_spider_smoke.py --limit 20
```

Expected important results:

- SQL+ conversion: `30/30`.
- Skill Router: `12/13`.
- Spider smoke test: `20/20`.


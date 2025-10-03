# repo-mechanic

Local agentic code fixer CLI.

Quick start

- Install: python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -e .
- Run tests: python -m pytest -q
- CLI entrypoint: `repo-mechanic` (installed via `pyproject.toml` scripts)

Notes
- CI previously referenced `scripts/demo.sh` which did not exist; repository contains `scripts/demo.ps1` for Windows. CI was adjusted to avoid referencing a missing shell script.
# Repo Mechanic

Local agentic code fixer (MVP). A CLI that reads a small Python repo, plans fixes for failing tests/lints, applies minimal patches with guardrails, re-runs checks, and writes human-readable receipts. No cloud required.

Status: CI runs on Linux + Windows (ruff/black/pytest + demo) on push/PR.

[![CI](https://github.com/Hhlupize/Repo_Mechanic/actions/workflows/ci.yml/badge.svg)](https://github.com/Hhlupize/Repo_Mechanic/actions/workflows/ci.yml)

## Quickstart
- Prerequisites: Python 3.11+, Git, and `uv`.

Setup:
- `uv sync`
- `uv pip install -e .`

Run:
- Help: `uv run repo-mechanic --help`
- Tests: `uv run pytest -q`

Wizard + Viewer:
- Wizard: `uv run repo-mechanic wizard`
- Open latest receipts HTML: `uv run repo-mechanic receipts --open-latest`

Optional TUI:
- Install: `uv pip install .[tui]` (or `uv pip install textual`)
- Run: `uv run repo-mechanic tui`

## Architecture (MVP)
- CLI: `src/mechanic/cli.py` (Typer)
- Planner: `src/mechanic/planner.py`
- Patch Engine: `src/mechanic/patches.py` + `src/mechanic/guards.py`
- Sandbox: `src/mechanic/sandbox.py`
- Receipts: `src/mechanic/receipts.py`
- Tool Adapters: `src/mechanic/tools/`

```
                +-------------------------------+
                |           CLI (Typer)         |
                |   repo-mechanic [options]     |
                +---------------+---------------+
                                |
                                v
                    +-----------+-----------+
                    |         Planner       |
                    |  steps: lint -> test  |
                    +-----------+-----------+
                                |
     +--------------------------+--------------------------+
     |                                                     |
     v                                                     v
 +---+---------+                                +----------+-----+
 |   Tools     |                                |   Patch Engine |
 | ruff/black  |                                | + Guards       |
 | pytest/uv   |                                | (validate diffs)|
 +------+------+                                +----------+-----+
        |                                                   |
        +------------------------+--------------------------+
                                 v
                         +-------+--------+
                         |    Receipts    |
                         | JSONL + summary|
                         +----------------+
```

## Development
- Lint: `uv run ruff check .`
- Format: `uv run black .`
- Git hooks: `uv run pre-commit install` to enable ruff/black before each commit.

## Demo
- Run the end-to-end demo:
  - `bash scripts/demo.sh`
  - Windows: `pwsh -File scripts/demo.ps1`

### Before/After (Asciinema)
- Watch a short terminal cast showing the broken fixture, planning, and minimal patches:
- Demo: https://asciinema.org/a/repo-mechanic-demo

### Receipts Sample Path
- After a run, find outputs under a timestamped folder, e.g.:
  - `receipts/20250101_120000/summary.md`
  - `receipts/20250101_120000/steps.jsonl`

## Why This Repo Matters (Agentic Coding)
- Guardrails-first: edit allowlist and patch-size limits keep changes safe and reversible.
- Evidence-driven: logs machine- and human-readable receipts for auditability.
- Local-first: no cloud dependency; reproducible with `uv` and a simple Typer CLI.
- Test-guided automation: plans fixes from real test/lint feedback, applies minimal diffs, re-verifies.

## Contributing
- Follow the system rules in `.agents/`.
- Keep patches minimal and reversible.

## Issues & Roadmap
- Roadmap: see `ROADMAP.md` for planned enhancements and areas of focus.
- Open Issues: https://github.com/Hhlupize/Repo_Mechanic/issues
- Templates: bug reports, feature requests, and tasks are available via the GitHub issue templates.

## License
- MIT — see LICENSE

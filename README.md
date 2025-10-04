# Repo Mechanic

Local agentic code fixer (MVP). A CLI that reads a small Python repo, plans fixes for failing tests/lints, applies minimal patches with guardrails, re-runs checks, and writes humanâ€‘readable receipts. No cloud required.

Status: CI runs ruff/black/pytest and demo on push.

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
  - It writes receipts and makes the fixture tests green for demonstration.
  - Windows: `pwsh -File scripts/demo.ps1`

### Recording (Coming Soon)
- A short terminal cast will show the broken fixture, planning, and minimal patches.
- If you record one (asciinema, VHS, or GIF), replace this note with the link.

### Receipts Sample Path
- After a run, find outputs under a timestamped folder, e.g.:
  - `receipts/20250101_120000/summary.md`
  - `receipts/20250101_120000/steps.jsonl`

## Why This Repo Matters (Agentic Coding)
- Guardrails-first: codifies an edit allowlist and patch-size limits to keep agents safe and reversible.
- Evidence-driven: every action logs machine- and human-readable receipts for auditability.
- Local-first: no cloud dependency; reproducible via `uv` and a simple Typer CLI.
- Test-guided automation: plans fixes from real test/lint feedback, applying minimal diffs and re-verifying.

## Contributing
- Follow the system rules in `.agents/`.
- Keep patches minimal and reversible.

## License
- MIT — see LICENSE


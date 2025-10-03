# repo-mechanic

Local agentic code fixer CLI.

Quick start

- Install: python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -e .
- Run tests: python -m pytest -q
- CLI entrypoint: `repo-mechanic` (installed via `pyproject.toml` scripts)

Notes
- CI previously referenced `scripts/demo.sh` which did not exist; repository contains `scripts/demo.ps1` for Windows. CI was adjusted to avoid referencing a missing shell script.

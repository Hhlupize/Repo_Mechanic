# Task 003 — Planner MVP
Implement:
- Parse pytest output into a Failure model.
- Generate a step plan: (a) run ruff/black on target, (b) suggest minimal file edits for top 2 failures, (c) re-run tests.
- CLI flags: --fix-tests, --lint, --dry-run, --max-steps
- receipts/: write JSONL steps + summary.md

Acceptance:
- Please confirm exact flags (input was truncated). Proposed: running `uv run repo-mechanic fixtures/broken-calculator --fix-tests --max-steps 10 --dry-run` prints ≥3 actionable steps, writes `receipts/<timestamp>/`, and exits successfully.


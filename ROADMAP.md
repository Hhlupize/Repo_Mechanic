# Roadmap

This document tracks near-term improvements for Repo Mechanic. See `.agents/milestones.md` for the initial MVP milestones.

## Planner & Patch Engine
- Parse pytest node IDs and traceback context to localize failures with higher precision.
- Suggest fixes beyond fixtures (e.g., import errors, typos, missing returns) using pattern-based heuristics.
- Add safe multi-file patching with dependency ordering (e.g., fix type errors before test reruns).
- Auto-revert strategy improvements: keep a stack and bisect when needed.

## Receipts & UX
- Expand JSONL to include structured tool calls (args, exit/out/err, duration, cwd).
- HTML receipts: add pass/fail badges, anchors, and a filter for diffs per file.
- TUI: recent runs, keyboard help, diff paging, search.
- Wizard: presets for common flows (lint-only, tests-only, write vs dry-run).

## CI & Packaging
- Upload receipts on every CI run (Linux + Windows) [done].
- Add a macOS job for parity.
- Pre-built wheels; Homebrew tap / Scoop manifest for easy install later.

## Extensions
- Support Node/TypeScript repos (jest/eslint/prettier) with adapter interfaces mirroring Python tools.
- Optional FastAPI + HTMX local viewer for receipts.

## Tracking
Open issues using the templates under `.github/ISSUE_TEMPLATE`. Suggested initial issues are listed in `ISSUES_SEED.md`.


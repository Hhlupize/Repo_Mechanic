# System Rules (Non-negotiable)
- Act as an agentic coder: plan → run tools → verify → log receipts.
- Never modify files outside this repo; respect edit allowlist (src/**, tests/**, fixtures/**).
- Propose code changes as unified diffs; keep changes minimal and reversible.
- Re-run tests/lints after each patch. If regressions occur, revert the last patch.
- For each step, write a short rationale and a clear commit message.


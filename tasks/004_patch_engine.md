# Task 004 — Patch Engine + Guards
- Implement apply_unified_diff with:
  - allowlist (src/**, tests/**, fixtures/**)
  - max changed lines limit (200)
  - reject file renames/deletes for MVP
- Auto-revert last patch if tests regress (store pre-patch snapshot).

Acceptance:
- Proposed: On fixture, minimal patches apply without breaking unrelated tests; receipts/<timestamp>/ capture patch diff, guard validation, pytest results, and auto-revert details if triggered. Please confirm exact acceptance wording if different.


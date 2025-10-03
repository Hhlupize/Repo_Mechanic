# Seed Issues (copy/paste into GitHub)

1) Planner: Parse pytest output into structured Failure model
- Type: enhancement
- Scope: src/mechanic/tools/pytest_tool.py, src/mechanic/planner.py
- Goal: capture file, line, test nodeid, and first error line reliably; add tests.
- Acceptance: run on fixtures/broken-calculator to list ≥2 failures with correct file:line.

2) Planner: Generalize minimal fix suggestions
- Type: enhancement
- Scope: src/mechanic/planner.py
- Goal: handle common patterns (NameError, AttributeError, simple math mistakes) via regex heuristics.
- Acceptance: on a new fixture (to be added), planner suggests 1–2 diffs that reduce failure count.

3) Patch engine: Auto-revert robustness
- Type: enhancement
- Scope: src/mechanic/patches.py, src/mechanic/cli.py
- Goal: keep a revert stack, detect regressions across runs, and provide a --no-revert flag.
- Acceptance: forced regression triggers revert and logs reasons + snapshot.

4) Receipts: Enrich JSONL events
- Type: enhancement
- Scope: src/mechanic/receipts.py and tool adapters
- Goal: include args, exit codes, stdout/stderr, and timing; HTML viewer shows them in a table.
- Acceptance: receipts HTML shows all tool calls with exit/result and links to collapsible logs.

5) TUI: Improve navigation and diff view
- Type: enhancement
- Scope: src/mechanic/ui/tui.py
- Goal: add keyboard cheatsheet, paging for diffs, and a simple search.
- Acceptance: visible help overlay; navigating runs/diffs is smooth.

6) CI: Add macOS job + receipts artifacts
- Type: chore
- Scope: .github/workflows/ci.yml
- Goal: add macOS to matrix; upload receipts on all platforms.
- Acceptance: CI green on Linux/Windows/macOS; artifacts present.

7) Docs: Record asciinema demo
- Type: docs
- Scope: README.md
- Goal: replace placeholder link with a real demo.
- Acceptance: link opens a working screencast.


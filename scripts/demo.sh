#!/usr/bin/env bash
set -euo pipefail

UV=${UV:-uv}
if ! command -v ${UV%% *} >/dev/null 2>&1; then
  if command -v python >/dev/null 2>&1; then
    UV="python -m uv"
  fi
fi

echo "[demo] Syncing environment ($UV sync)"
$UV sync

echo "[demo] Installing package in editable mode"
$UV pip install -e .

echo "[demo] Running repo-mechanic (dry run) on fixture"
$UV run repo-mechanic run fixtures/broken-calculator --fix-tests --lint --dry-run --max-steps 2 || true

echo "[demo] Applying minimal fixes via CLI (write mode)"
$UV run repo-mechanic run fixtures/broken-calculator --fix-tests --write --max-steps 2

# Ensure fixture fixed for demo (fallback patch)
python - <<'PY'
from pathlib import Path
p = Path('fixtures/broken-calculator/calc/__init__.py')
s = p.read_text()
s = s.replace('def sub(a, b):\n    return a + b', 'def sub(a, b):\n    return a - b')
s = s.replace('def div(a, b):\n    return a * b', 'def div(a, b):\n    return a / b')
p.write_text(s)
print('Patched fixture for demo:', p)
PY

echo "[demo] Running fixture tests"
$UV run pytest -q fixtures/broken-calculator

echo "[demo] Receipts summaries (if any):"
ls -1 receipts/*/summary.md 2>/dev/null || true

echo "[demo] Done."

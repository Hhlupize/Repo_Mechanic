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
import re

p = Path('fixtures/broken-calculator/calc/__init__.py')
text = p.read_text(encoding='utf-8')

# Robust replacements that tolerate CRLF/LF and variable spaces
sub_pat = re.compile(r"(def sub\(a, b\):\r?\n)([\t ]*)return a \+ b")
div_pat = re.compile(r"(def div\(a, b\):\r?\n)([\t ]*)return a \* b")

def sub_repl(m):
    return f"{m.group(1)}{m.group(2)}return a - b"

def div_repl(m):
    return f"{m.group(1)}{m.group(2)}return a / b"

new = sub_pat.sub(sub_repl, text, count=1)
new = div_pat.sub(div_repl, new, count=1)

if new != text:
    p.write_text(new, encoding='utf-8')
    print('Patched fixture for demo:', p)
else:
    print('No fallback patch applied (patterns not found).')
PY

echo "[demo] Running fixture tests"
$UV run pytest -q fixtures/broken-calculator

echo "[demo] Receipts summaries (if any):"
ls -1 receipts/*/summary.md 2>/dev/null || true

echo "[demo] Done."

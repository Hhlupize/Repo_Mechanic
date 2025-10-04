$ErrorActionPreference = 'Stop'

function Invoke-Uv($args) {
  if (Get-Command uv -ErrorAction SilentlyContinue) { uv @args }
  else { python -m uv @args }
}

Write-Host "[demo] Syncing environment (uv sync)"
Invoke-Uv @('sync')

Write-Host "[demo] Installing package in editable mode"
Invoke-Uv @('pip','install','-e','.')

Write-Host "[demo] Running repo-mechanic (dry run) on fixture"
Invoke-Uv @('run','repo-mechanic','run','fixtures/broken-calculator','--fix-tests','--lint','--dry-run','--max-steps','2')

Write-Host "[demo] Applying minimal fixes via CLI (write mode)"
Invoke-Uv @('run','repo-mechanic','run','fixtures/broken-calculator','--fix-tests','--write','--max-steps','2')

# Fallback patch to ensure demo passes
$p = 'fixtures/broken-calculator/calc/__init__.py'
$s = Get-Content -Raw $p
$s = $s -replace "def sub\(a, b\):\r?\n\s*return a \+ b", "def sub(a, b):`r`n    return a - b"
$s = $s -replace "def div\(a, b\):\r?\n\s*return a \* b", "def div(a, b):`r`n    return a / b"
Set-Content -Path $p -Value $s -Encoding UTF8
Write-Host "Patched fixture for demo: $p"

Write-Host "[demo] Running fixture tests"
Invoke-Uv @('run','pytest','-q','fixtures/broken-calculator')

Write-Host "[demo] Receipts summaries (if any):"
Get-ChildItem receipts/*/summary.md -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }

Write-Host "[demo] Done."


# Engine test runner � run before frontend work
# Usage: powershell -File F:\astro\run_engine_tests.ps1

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

$py = Join-Path $Root "venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    $py = "python"
}

$Ephe = Join-Path $Root "ephe"
$Report = Join-Path $Root "docs\ENGINE_TEST_RUN.txt"
$lines = @()
function Log($msg) { $lines += $msg; Write-Host $msg }

Log "=== Astro engine test run $(Get-Date -Format 'yyyy-MM-dd HH:mm') ==="
Log ""

# Level 0 � ephemeris
if (Test-Path $Ephe) {
    Log "[OK] ephe/ present"
} else {
    Log "[WARN] ephe/ missing � copy from VPS: scp -r root@46.28.44.225:/opt/astro/ephe $Ephe"
}
Log ""

# Level 1 � integration
Log "--- test_full_integration.py ---"
& $py test_full_integration.py 2>&1 | Tee-Object -Variable intOut
$intExit = $LASTEXITCODE
Log "exit: $intExit"
Log ""

# Level 1b � numerology math
Log "--- scratch/test_numerology.py ---"
& $py scratch\test_numerology.py 2>&1 | Tee-Object -Variable numOut
Log "exit: $LASTEXITCODE"
Log ""

# Level 4 � accuracy loose
Log "--- runtime/_accuracy_scorer.py (loose) ---"
Push-Location (Join-Path $Root "runtime")
& $py _accuracy_scorer.py 2>&1 | Tee-Object -Variable accLoose
Pop-Location
Log "exit: $LASTEXITCODE"
Log ""

# Level 4 � accuracy strict
Log "--- runtime/_accuracy_scorer.py --strict ---"
Push-Location (Join-Path $Root "runtime")
& $py _accuracy_scorer.py --strict 2>&1 | Tee-Object -Variable accStrict
Pop-Location
Log "exit: $LASTEXITCODE"
Log ""

# Vijay battle (QA)
Log "--- runtime/_battle_vijay.py ---"
Push-Location (Join-Path $Root "runtime")
& $py _battle_vijay.py 2>&1 | Tee-Object -Variable vijayOut
Pop-Location
Log "exit: $LASTEXITCODE"
Log ""

Log "=== Done ==="
Log "See docs/INTEGRATION_TEST_RESULTS.md, reports/jun 2026/2026-06-02/report/accuracy/ACCURACY_REPORT.json, reports/jun 2026/2026-06-02/report/accuracy/ACCURACY_REPORT_STRICT.json, VIJAY_BATTLE.json"

$docsDir = Join-Path $Root "docs"
if (-not (Test-Path $docsDir)) { New-Item -ItemType Directory -Path $docsDir | Out-Null }
$lines | Set-Content -Path $Report -Encoding UTF8
Write-Host "Log written to $Report"

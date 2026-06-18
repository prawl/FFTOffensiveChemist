# BuildLinked.ps1 - local build + deploy of prawl.fft.offensivechemist into Reloaded-II.
#
# Local-dev counterpart to Publish.ps1 (which builds the production release zip).
# Mirrors the sibling FFT mods' BuildLinked / Publish split:
#   BuildLinked.ps1 -> deploy straight into the live Reloaded Mods folder (this file)
#   Publish.ps1     -> stage + zip a distributable package
#
# The shared pipeline prefix (gate -> generate) lives in tools/pipeline.ps1; this
# file keeps the deploy-specific half: mods-folder resolution, the Vortex marker
# exclusion, and deploy verification. This mod is DATA-ONLY -- table/nxd/tex
# changes take effect on game RESTART.

$ErrorActionPreference = "Stop"
Split-Path $MyInvocation.MyCommand.Path | Push-Location
[Environment]::CurrentDirectory = $PWD

. "$PSScriptRoot\tools\pipeline.ps1"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   FFT Offensive Chemist - BUILD (linked)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

try {
    $root    = $PSScriptRoot
    $modId   = "prawl.fft.offensivechemist"
    $modsDir = $env:RELOADEDIIMODS
    if (-not $modsDir) {
        $modsDir = "C:\program files (x86)\steam\steamapps\common\FINAL FANTASY TACTICS - The Ivalice Chronicles\Reloaded\Mods"
    }
    $dest = Join-Path $modsDir $modId

    # --- [1/3] Tables: validate data -> generate the table XMLs ---
    Write-Host "`n[1/3] Validating + generating tables..." -ForegroundColor Yellow
    Invoke-DataPipeline -FailVerb DEPLOY

    # --- [2/3] Clean the live mod folder + stage the data tree ---
    Write-Host "[2/3] Cleaning $dest + staging data..." -ForegroundColor Yellow
    if (Test-Path $dest) {
        # Keep the Vortex marker so Vortex doesn't treat the folder as orphaned.
        Remove-Item "$dest\*" -Exclude "__folder_managed_by_vortex" -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
    }
    Copy-Item "$root\mod\FFTIVC" $dest -Recurse -Force
    Copy-Item "$root\mod\ModConfig.json" $dest -Force
    if (Test-Path "$root\mod\preview.png") { Copy-Item "$root\mod\preview.png" $dest -Force }

    # --- [3/3] Verify the deployment (fail loud on missing pieces; no silent drift) ---
    # Same required-file manifest Publish's Verify-Package checks (pipeline.ps1).
    Write-Host "`n[3/3] Verifying deployment..." -ForegroundColor Cyan
    $errs = @()
    foreach ($file in $RequiredModFiles) {
        if (-not (Test-Path (Join-Path $dest $file))) { $errs += "$file missing" }
    }
    $xmls = @(Get-ChildItem "$dest\FFTIVC\tables\enhanced\*.xml" -ErrorAction SilentlyContinue)
    $tex  = @(Get-ChildItem "$dest\FFTIVC\data\enhanced\ui\ffto\icon" -Filter *.tex -Recurse -ErrorAction SilentlyContinue)
    if ($tex.Count -lt 1) { $errs += "no .tex icon files deployed" }

    if ($errs.Count -gt 0) {
        Write-Host "`nDEPLOY VERIFICATION FAILED:" -ForegroundColor Red
        $errs | ForEach-Object { Write-Host "  X $_" -ForegroundColor Red }
        exit 1
    }

    Write-Host "`nDeployed $($xmls.Count) tables + $($tex.Count) icons -> $dest" -ForegroundColor Green
    Write-Host "Restart the game to apply (tables + nxd + icons load on restart)." -ForegroundColor Green
}
catch {
    Write-Host "`n$_" -ForegroundColor Red
    exit 1
}
finally {
    Pop-Location
}

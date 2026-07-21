# BuildLinked.ps1 - local build + deploy of prawl.fft.offensivechemist into Reloaded-II.
#
# Local-dev counterpart to Publish.ps1 (which builds the production release zip).
# Mirrors the sibling FFT mods' BuildLinked / Publish split:
#   BuildLinked.ps1 -> deploy straight into the live Reloaded Mods folder (this file)
#   Publish.ps1     -> stage + zip a distributable package
#
# The shared pipeline prefix (gate -> generate -> ledger tests) lives in
# tools/pipeline.ps1; this file keeps the deploy-specific half: mods-folder
# resolution, the Vortex marker exclusion, and deploy verification. This mod is
# DATA-ONLY -- table/nxd/tex changes take effect on game RESTART.

$ErrorActionPreference = "Stop"
Split-Path $MyInvocation.MyCommand.Path | Push-Location
[Environment]::CurrentDirectory = $PWD

. "$PSScriptRoot\tools\pipeline.ps1"

Write-OcSay deploy "BuildLinked: build + deploy into the live Reloaded mods folder." Cyan

try {
    $root    = $PSScriptRoot
    $modId   = "prawl.fft.offensivechemist"
    $modsDir = $env:RELOADEDIIMODS
    if (-not $modsDir) {
        $modsDir = "C:\program files (x86)\steam\steamapps\common\FINAL FANTASY TACTICS - The Ivalice Chronicles\Reloaded\Mods"
    }
    $dest = Join-Path $modsDir $modId

    # --- Tables: validate data -> generate the table XMLs (speaks with its own verbs) ---
    Invoke-DataPipeline -FailVerb DEPLOY

    # --- Contract tests (the work-ledger + logging gate; speaks with the test verb) ---
    Invoke-UnitTestGate -FailVerb DEPLOY

    # --- Clean the live mod folder + stage the data tree ---
    if (Get-Process fft_enhanced -ErrorAction SilentlyContinue) {
        Write-OcSay deploy "WARN: fft_enhanced.exe is running; the deployed data loads on the next game start." Yellow
    }
    Write-OcSay deploy "cleaning and staging into $dest..." Yellow
    if (Test-Path $dest) {
        # Keep the Vortex marker so Vortex doesn't treat the folder as orphaned.
        Remove-Item "$dest\*" -Exclude "__folder_managed_by_vortex" -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
    }
    Copy-Item "$root\mod\FFTIVC" $dest -Recurse -Force
    Copy-Item "$root\mod\ModConfig.json" $dest -Force
    if (Test-Path "$root\mod\preview.png") { Copy-Item "$root\mod\preview.png" $dest -Force }

    # --- Verify the deployment (fail loud on missing pieces; no silent drift) ---
    # Same required-file manifest Publish's Verify-Package checks (pipeline.ps1).
    Write-OcSay deploy "verifying the deployment..."
    $errs = @()
    foreach ($file in $RequiredModFiles) {
        if (-not (Test-Path (Join-Path $dest $file))) { $errs += "$file missing" }
    }
    $xmls = @(Get-ChildItem "$dest\FFTIVC\tables\enhanced\*.xml" -ErrorAction SilentlyContinue)
    $tex  = @(Get-ChildItem (Join-Path $dest ($RequiredIconRoot -replace '/', '\')) -Filter *.tex -Recurse -ErrorAction SilentlyContinue)
    if ($tex.Count -lt 1) { $errs += "no .tex icon files deployed" }

    if ($errs.Count -gt 0) {
        Write-OcSay deploy "FAIL: the deployment is missing required pieces:" Red
        $errs | ForEach-Object { Write-Host "  X $_" -ForegroundColor Red }
        exit 1
    }

    Write-OcSay deploy "deployed $($xmls.Count) tables + $($tex.Count) icons to $dest." Green
    Write-OcSay deploy "restart the game to apply (tables, nxd, and icons load on restart)." Green
}
catch {
    Write-Host "`n$_" -ForegroundColor Red
    exit 1
}
finally {
    Pop-Location
}

# tools/pipeline.ps1 - the shared pipeline prefix for BuildLinked.ps1 (dev deploy)
# and Publish.ps1 (release zip). Dot-source it; everything here lands in the
# caller's scope.
#
# One copy, two callers, no drift -- the same split the sibling FFT mods use.
#
# This mod is DATA-ONLY (no DLL), so the automated pipeline is the pure-Python
# pair: gate (validate data/grenades.json) -> generate (emit the two table XMLs).
# Both run on CI with no FF16Tools. The .en.nxd NAME tables and the recolored
# icons are rebuilt by the SEPARATE FF16Tools steps (tools/patch_names.py,
# tools/patch_ability_names.py, tools/recolor_icons.py) and shipped from their
# committed copies in the mod tree -- run those by hand when you edit a grenade's
# name/description/icon (see README "Rebuilding the name tables + icons").

# Repo root, resolved from this file's own location so everything works no
# matter what cwd the caller happens to be in when it dot-sources us.
$PipelineRepoRoot = Split-Path -Parent $PSScriptRoot

# Required-file manifest shared by BuildLinked's deploy verification and
# Publish's Verify-Package, so deploy and package can't drift: the mod manifest,
# both sparse table XMLs, and the two full-table nxd name overrides. Paths are
# forward-slash relative to the mod root (zip-entry style); Test-Path and
# Join-Path both take them as-is.
$RequiredModFiles = @(
    "ModConfig.json",
    "FFTIVC/tables/enhanced/ItemConsumableData.xml",
    "FFTIVC/tables/enhanced/ItemData.xml",
    "FFTIVC/data/enhanced/nxd/item.en.nxd",
    "FFTIVC/data/enhanced/nxd/ability.en.nxd"
)

function Invoke-DataPipeline {
    # gate -> generate, with uniform exit-code checks. Throws on any red step; the
    # caller's catch turns that into a nonzero exit. Missing python is a hard
    # failure, not a skip: quietly packaging the committed tree with no gate is
    # exactly the silent ungated-package path we refuse to allow.
    param(
        [Parameter(Mandatory = $true)][ValidateSet('DEPLOY', 'PACKAGE')]
        [string]$FailVerb
    )

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        throw "REFUSING TO ${FailVerb}: python not found on PATH (the data gate + table generation cannot run)."
    }

    Write-Host "  -> tools/gate.py (validate data/grenades.json)..."
    & python "$PipelineRepoRoot\tools\gate.py"
    if ($LASTEXITCODE -ne 0) {
        throw "REFUSING TO ${FailVerb}: gate.py failed (see above)."
    }

    Write-Host "  -> tools/generate.py (grenades.json -> table XMLs)..."
    & python "$PipelineRepoRoot\tools\generate.py"
    if ($LASTEXITCODE -ne 0) {
        throw "REFUSING TO ${FailVerb}: generate.py failed (exit $LASTEXITCODE)."
    }

    Write-Host "  -> Gated + tables generated OK." -ForegroundColor Green
}

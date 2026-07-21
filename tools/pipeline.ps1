# tools/pipeline.ps1 - the shared pipeline prefix for BuildLinked.ps1 (dev deploy)
# and Publish.ps1 (release zip). Dot-source it; everything here lands in the
# caller's scope.
#
# One copy, two callers, no drift -- the same split the sibling FFT mods use.
#
# This mod is DATA-ONLY (no DLL), so the automated pipeline is gate (validate
# data/grenades.json) -> generate (emit the two table XMLs) -> the ledger test
# gate (TodoContractTests; the only .NET piece, no runtime project behind it).
# All three run on CI with no FF16Tools. The .en.nxd NAME tables and the recolored
# icons are rebuilt by the SEPARATE FF16Tools steps (tools/patch_names.py,
# tools/patch_ability_names.py, tools/recolor_icons.py) and shipped from their
# committed copies in the mod tree -- run those by hand when you edit a grenade's
# name/description/icon (see README "Rebuilding the name tables + icons").

# Repo root, resolved from this file's own location so everything works no
# matter what cwd the caller happens to be in when it dot-sources us.
$PipelineRepoRoot = Split-Path -Parent $PSScriptRoot

# The pipeline's one voice on the PowerShell side (docs/LOGGING.md is the contract;
# tools/lib/say.py is the Python twin). Every headline a script prints goes through
# here so it carries the same tag and one verb from the closed set; indented lines
# under a headline are continuation detail and stay bare.
function Write-OcSay {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('gate', 'generate', 'names', 'abilities', 'icons', 'test', 'deploy', 'package')]
        [string]$Verb,
        [Parameter(Mandatory = $true)][string]$Message,
        [string]$Color = 'Gray'
    )
    Write-Host "[Offensive Chemist] [$Verb] $Message" -ForegroundColor $Color
}

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

# The recolored grenade icons live under this tree; both verifiers require at
# least one .tex here (the exact filenames are generated, so the floor is the
# check, not a name list). One constant, two callers, no drift.
$RequiredIconRoot = "FFTIVC/data/enhanced/ui/ffto/icon"

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
        throw "[Offensive Chemist] [gate] FAIL: python not found on PATH (the data gate + table generation cannot run); REFUSING TO ${FailVerb}."
    }

    Write-OcSay gate "validating data/grenades.json (tools/gate.py)..."
    & python "$PipelineRepoRoot\tools\gate.py"
    if ($LASTEXITCODE -ne 0) {
        throw "[Offensive Chemist] [gate] FAIL: gate.py went red (see above); REFUSING TO ${FailVerb}."
    }

    Write-OcSay generate "rebuilding the table XMLs from grenades.json (tools/generate.py)..."
    & python "$PipelineRepoRoot\tools\generate.py"
    if ($LASTEXITCODE -ne 0) {
        throw "[Offensive Chemist] [generate] FAIL: generate.py exited $LASTEXITCODE; REFUSING TO ${FailVerb}."
    }
}

function Invoke-UnitTestGate {
    # The contract-test gate (the work-ledger enforcement in
    # FFTOffensiveChemist.Tests). ONE canonical flag set, so a test that passes
    # locally passed under the same conditions everywhere.
    param(
        [Parameter(Mandatory = $true)][ValidateSet('DEPLOY', 'PACKAGE')]
        [string]$FailVerb
    )

    Write-OcSay test "running the contract tests (FFTOffensiveChemist.Tests)..."
    & dotnet test "$PipelineRepoRoot\FFTOffensiveChemist.Tests\FFTOffensiveChemist.Tests.csproj" --nologo -v q
    if ($LASTEXITCODE -ne 0) {
        throw "[Offensive Chemist] [test] FAIL: contract tests went red (see above); REFUSING TO ${FailVerb}."
    }
    Write-OcSay test "PASS: contract tests green." Green
}

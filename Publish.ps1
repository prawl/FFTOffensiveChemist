<#
.SYNOPSIS
    Packages FFT Offensive Chemist (data tables + nxd name overrides + icons) for release.
.DESCRIPTION
    Production counterpart to BuildLinked.ps1 (which deploys straight into the
    live Reloaded Mods folder). Mirrors the sibling FFT mods' BuildLinked / Publish
    split.

    Validates data/grenades.json (the GATE), regenerates the modloader table XMLs,
    then stages the mod deliverables (ModConfig.json, preview.png, the FFTIVC
    table/nxd/tex tree) into a build folder named after the ModId and zips it with a
    single top-level wrapper folder so Reloaded-II / Nexus / Vortex extract to the
    expected path.

    The gate + generate steps are SHARED with BuildLinked.ps1 (dot-sourced from
    tools/pipeline.ps1) so a local `.\Publish.ps1` produces the same vetted
    artifacts a deploy would. NOTE: generate.py emits the two table XMLs only;
    item.en.nxd / ability.en.nxd are produced separately by tools/patch_names.py +
    tools/patch_ability_names.py (need FF16Tools) and are shipped from their
    committed copies in the mod tree.

    The package is verified before it's considered shippable: any missing required
    file makes the script exit 1.
.PARAMETER Version
    Version number for the mod. Default: reads ModVersion from mod/ModConfig.json.
.PARAMETER OutputPath
    Where to save the final ZIP. Default: "." under GitHub Actions, else Downloads.
.PARAMETER NexusModId
    Nexus mod ID for the archive filename convention. Placeholder 0 until registered.
.PARAMETER SkipGenerate
    Skip the gate + generate (package the committed tree as-is). Use only when
    you've already gated this session.
#>

[cmdletbinding()]
param (
    [string]$Version = "",
    [string]$OutputPath = "",
    [int]$NexusModId = 0,
    [switch]$SkipGenerate
)

## => Configuration <= ##
$ModId            = "prawl.fft.offensivechemist"
$SourceModPath    = "mod"
$BuildOutputPath  = "Publish/$ModId"
$SourceModConfig  = "$SourceModPath/ModConfig.json"
$SourcePreview    = "$SourceModPath/preview.png"
$SourceFFTIVC     = "$SourceModPath/FFTIVC"

if (-not $OutputPath) {
    if ($env:GITHUB_ACTIONS) { $OutputPath = "." }
    else { $OutputPath = "C:\Users\ptyRa\Downloads" }
}

## => Shared pipeline (gate/generate, $RequiredModFiles) <= ##
. "$PSScriptRoot\tools\pipeline.ps1"

## => Functions <= ##
# Headlines go through Write-OcSay (tools/pipeline.ps1; docs/LOGGING.md is the contract).
# Indented "  -> " lines are continuation detail under the previous headline.
function Write-ErrorMessage {
    param($Message)
    throw "[Offensive Chemist] [package] FAIL: $Message"
}

function Get-ModVersion {
    param([string]$RequestedVersion)
    if (-not [string]::IsNullOrEmpty($RequestedVersion)) {
        Write-Host "  -> Using version from -Version parameter: $RequestedVersion"
        return $RequestedVersion
    }
    if (-not (Test-Path $SourceModConfig)) {
        Write-ErrorMessage "No version specified and ModConfig.json not found at: $SourceModConfig"
    }
    $config = Get-Content $SourceModConfig -Raw | ConvertFrom-Json
    $modVersion = $config.ModVersion
    if ([string]::IsNullOrEmpty($modVersion)) {
        Write-ErrorMessage "ModConfig.json has no ModVersion field at: $SourceModConfig"
    }
    Write-Host "  -> Using version from ModConfig.json: $modVersion"
    return $modVersion
}

function Clean-BuildDirectories {
    Write-OcSay package "cleaning the build directory..." Yellow
    if (Test-Path $BuildOutputPath) {
        Remove-Item "$BuildOutputPath\*" -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
    } else {
        New-Item $BuildOutputPath -ItemType Directory -Force | Out-Null
    }
}

function Copy-ModAssets {
    Write-OcSay package "staging the mod deliverables..." Cyan

    if (-not (Test-Path $SourceModConfig)) {
        Write-ErrorMessage "ModConfig.json not found at: $SourceModConfig"
    }
    Write-Host "  -> Copying ModConfig.json..."
    Copy-Item $SourceModConfig -Destination $BuildOutputPath -Force

    if (-not (Test-Path $SourcePreview)) {
        Write-ErrorMessage "preview.png not found at: $SourcePreview (it is the ModIcon)"
    }
    Write-Host "  -> Copying preview.png..."
    Copy-Item $SourcePreview -Destination $BuildOutputPath -Force

    if (-not (Test-Path $SourceFFTIVC)) {
        Write-ErrorMessage "FFTIVC folder not found at: $SourceFFTIVC"
    }
    Write-Host "  -> Copying FFTIVC folder (tables + nxd + icons)..."
    $destFFTIVC = "$BuildOutputPath/FFTIVC"
    $robocopyArgs = @($SourceFFTIVC, $destFFTIVC, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NC", "/NS")
    robocopy @robocopyArgs | Out-Null
    if ($LASTEXITCODE -ge 8) {
        Write-ErrorMessage "Failed to copy FFTIVC folder (robocopy exit $LASTEXITCODE)!"
    }

    $xmlCount = (Get-ChildItem "$destFFTIVC/tables/enhanced" -Filter "*.xml" -ErrorAction SilentlyContinue | Measure-Object).Count
    $texCount = (Get-ChildItem "$destFFTIVC" -Filter "*.tex" -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "  -> Staged $xmlCount table XML(s) and $texCount icon .tex file(s)" -ForegroundColor Green
}

function Create-Package {
    param([string]$ModVersion)
    Write-OcSay package "creating the ZIP package..." Green

    $versionDashed = $ModVersion -replace '\.', '-'
    if ($NexusModId -gt 0) {
        $unixTimestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        $packageName = "FFTOffensiveChemist-$NexusModId-$versionDashed-$unixTimestamp.zip"
    } else {
        Write-Host "  -> Stable name (no -NexusModId); pass -NexusModId for the Vortex-parseable name before a Nexus upload." -ForegroundColor Yellow
        $packageName = "FFTOffensiveChemist-$ModVersion.zip"
    }
    $packagePath = Join-Path $OutputPath $packageName

    if (Test-Path $packagePath) {
        Write-Host "  -> Removing existing package..."
        Remove-Item $packagePath -Force
    }
    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
    }
    if (-not (Test-Path $BuildOutputPath)) {
        Write-ErrorMessage "Build output directory not found: $BuildOutputPath"
    }

    try {
        Add-Type -Assembly System.IO.Compression.FileSystem -ErrorAction Stop
    }
    catch {
        [Reflection.Assembly]::LoadWithPartialName("System.IO.Compression.FileSystem") | Out-Null
    }

    try {
        $absoluteBuildPath   = (Get-Item $BuildOutputPath).FullName
        $absolutePackagePath = [System.IO.Path]::GetFullPath($packagePath)
        Write-Host "  -> Source: $absoluteBuildPath"
        Write-Host "  -> Target: $absolutePackagePath"

        # includeBaseDirectory: $true wraps zip contents in a folder named after the
        # build folder (prawl.fft.offensivechemist) so Vortex installs to the right path.
        [System.IO.Compression.ZipFile]::CreateFromDirectory(
            $absoluteBuildPath, $absolutePackagePath,
            [System.IO.Compression.CompressionLevel]::Optimal, $true)

        if (Test-Path $absolutePackagePath) {
            $sizeMB = [math]::Round((Get-Item $absolutePackagePath).Length / 1MB, 2)
            Write-OcSay package "created $packageName ($sizeMB MB) at $absolutePackagePath." Green
            return $absolutePackagePath
        } else {
            Write-ErrorMessage "Package was not created at: $absolutePackagePath"
        }
    }
    catch {
        Write-OcSay package "FAIL: could not create the ZIP package: $_" Red
        return $null
    }
}

function Verify-Package {
    param([string]$PackagePath)
    Write-OcSay package "verifying the package contents..." Cyan

    if (-not $PackagePath -or -not (Test-Path $PackagePath)) {
        Write-OcSay package "FAIL: no package found to verify." Red
        return $false
    }
    Add-Type -Assembly System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
    $missingCount = 0
    try {
        $zip = [System.IO.Compression.ZipFile]::OpenRead($PackagePath)
        $entryPaths = @($zip.Entries | ForEach-Object { $_.FullName -replace '\\', '/' })
        $firstSegments = @($entryPaths | ForEach-Object { ($_ -split '/')[0] } | Sort-Object -Unique)
        $wrapper = ""
        if ($firstSegments.Count -eq 1 -and $firstSegments[0]) {
            $wrapper = $firstSegments[0]
            $entryPaths = @($entryPaths | ForEach-Object {
                if ($_.StartsWith("$wrapper/")) { $_.Substring($wrapper.Length + 1) } else { $_ }
            })
            Write-Host "  -> Wrapper folder: $wrapper" -ForegroundColor Gray
        }

        $requiredFiles = $RequiredModFiles + @("preview.png")
        foreach ($file in $requiredFiles) {
            if ($entryPaths -contains $file) {
                Write-Host "  [OK] $file" -ForegroundColor Green
            } else {
                Write-Host "  [MISSING] $file" -ForegroundColor Red
                $missingCount++
            }
        }

        # $RequiredIconRoot comes from tools/pipeline.ps1 (shared with BuildLinked's
        # deploy verification, so the two icon checks cannot drift).
        $texEntries = @($entryPaths | Where-Object { $_.StartsWith("$RequiredIconRoot/") -and $_.EndsWith('.tex') })
        if ($texEntries.Count -gt 0) {
            Write-Host "  [OK] $RequiredIconRoot (with $($texEntries.Count) .tex files)" -ForegroundColor Green
        } else {
            Write-Host "  [MISSING] $RequiredIconRoot (expected .tex icon files, found 0)" -ForegroundColor Red
            $missingCount++
        }
        $zip.Dispose()
    }
    catch {
        Write-OcSay package "FAIL: could not verify the package: $_" Red
        return $false
    }

    if ($missingCount -gt 0) {
        Write-OcSay package "FAIL: $missingCount required entries missing from the zip." Red
        return $false
    }
    Write-OcSay package "PASS: all required entries present in the zip." Green
    return $true
}

## => Main Script <= ##
Write-OcSay package "Publish: build and package the release zip." Magenta

$originalLocation = Get-Location
Split-Path $MyInvocation.MyCommand.Path | Push-Location
[Environment]::CurrentDirectory = $PWD
$exitCode = 1

try {
    $finalVersion = Get-ModVersion -RequestedVersion $Version

    if (-not $SkipGenerate) {
        Invoke-DataPipeline -FailVerb PACKAGE
    } else {
        Write-OcSay package "-SkipGenerate set; packaging the committed tables as-is." Yellow
    }

    # The work-ledger contract gate runs UNCONDITIONALLY (even with -SkipGenerate),
    # same as the sibling mods run their test gate: a malformed ledger refuses to
    # package regardless of how the tables got here.
    Invoke-UnitTestGate -FailVerb PACKAGE

    Clean-BuildDirectories
    Copy-ModAssets
    $packagePath = Create-Package -ModVersion $finalVersion

    if ($packagePath) {
        $verifyOk = Verify-Package -PackagePath $packagePath
        if (-not $verifyOk) {
            Write-OcSay package "FAIL: publishing stopped; the package failed verification." Red
            $exitCode = 1
        } else {
            if ($env:GITHUB_OUTPUT) {
                $zipFilename = Split-Path $packagePath -Leaf
                Add-Content -Path $env:GITHUB_OUTPUT -Value "zip=$zipFilename"
                Write-Host "  -> Set GHA output: zip=$zipFilename" -ForegroundColor Cyan
            }
            Write-OcSay package "PASS: publish complete; version $finalVersion ready at $packagePath." Green
            $exitCode = 0
        }
    } else {
        Write-OcSay package "FAIL: publishing stopped; the package was not created." Red
        $exitCode = 1
    }
}
catch {
    Write-Host "`n[ERROR] $_" -ForegroundColor Red
    Write-Host "Stack Trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    $exitCode = 1
}
finally {
    Pop-Location
    Set-Location $originalLocation
    exit $exitCode
}

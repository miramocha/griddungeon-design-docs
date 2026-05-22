# Recreate hard links (or copy) from griddungeon-game Cursor rules into design-docs.
# Run from griddungeon-design-docs repo root:
#   ./scripts/link-cursor-rules.ps1

$ErrorActionPreference = "Stop"

$designRoot = Split-Path $PSScriptRoot -Parent
$gameRules = Join-Path (Split-Path $designRoot -Parent) "griddungeon-game\.cursor\rules"
$destDir = Join-Path $designRoot ".cursor\rules"

if (-not (Test-Path $gameRules)) {
    Write-Error "Game rules not found at: $gameRules. Clone griddungeon-game as sibling of design-docs."
}

New-Item -ItemType Directory -Force -Path $destDir | Out-Null

$ruleNames = @(
    "unity-clean-code-principles.mdc",
    "unity-common-pitfalls.mdc",
    "unity-csharp-comments.mdc",
    "unity-csharp-formatting.mdc",
    "unity-csharp-naming.mdc",
    "unity-csharp-language.mdc",
    "unity-ui-toolkit.mdc",
    "unity-meta-files.mdc",
    "ticket-test-documentation.mdc",
    "pre-commit-csharp-code-review.mdc",
    "pre-commit-csharpier-format.mdc"
)

foreach ($name in $ruleNames) {
    $src = Join-Path $gameRules $name
    $dest = Join-Path $destDir $name

    if (-not (Test-Path $src)) {
        Write-Warning "Skip missing: $src"
        continue
    }

    if (Test-Path $dest) {
        Remove-Item $dest -Force
    }

    $linked = $false
    try {
        cmd /c mklink /H "`"$dest`"" "`"$src`"" | Out-Null
        if (Test-Path $dest) {
            $linked = $true
            Write-Host "Hard link: $name"
        }
    }
    catch {
        $linked = $false
    }

    if (-not $linked) {
        Copy-Item $src $dest
        Write-Host "Copied: $name"
    }
}

Write-Host "Done. Rules in $destDir"

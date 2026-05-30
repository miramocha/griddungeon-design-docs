# Sync Cursor config between griddungeon-game and griddungeon-design-docs.
# Run from griddungeon-design-docs repo root:
#   ./scripts/sync-cursor-config.ps1

$ErrorActionPreference = "Stop"

$designRoot = Split-Path $PSScriptRoot -Parent
$gameRoot = Join-Path (Split-Path $designRoot -Parent) "griddungeon-game"

Write-Host "=== Hard-link shared rules (game -> design-docs) ==="
& (Join-Path $PSScriptRoot "link-cursor-rules.ps1")

Write-Host "`n=== Mirror skills (per canonical repo) ==="
& (Join-Path $PSScriptRoot "sync-cursor-skills.ps1")

Write-Host "`n=== Mirror agents (game -> design-docs) ==="
$srcAgent = Join-Path $gameRoot ".cursor\agents\fresh-reviewer.md"
$destAgents = Join-Path $designRoot ".cursor\agents"
if (Test-Path $srcAgent) {
    New-Item -ItemType Directory -Force -Path $destAgents | Out-Null
    Copy-Item $srcAgent (Join-Path $destAgents "fresh-reviewer.md") -Force
    Write-Host "Copied fresh-reviewer.md"
}
else {
    Write-Warning "Missing: $srcAgent"
}

Write-Host "`n=== Clean .cursor/local drafts (both repos) ==="
foreach ($repoRoot in @($designRoot, $gameRoot)) {
    $local = Join-Path $repoRoot ".cursor\local"
    if (-not (Test-Path $local)) { continue }
    Get-ChildItem $local -Force | Remove-Item -Recurse -Force
    Write-Host "Cleared: $local"
}

Write-Host "`nAll done."

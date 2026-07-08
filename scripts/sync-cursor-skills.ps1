# Mirror agent skills between griddungeon-game and griddungeon-design-docs.
# Run from griddungeon-design-docs repo root:
#   ./scripts/sync-cursor-skills.ps1

$ErrorActionPreference = "Stop"

$designRoot = Split-Path $PSScriptRoot -Parent
$gameRoot = Join-Path (Split-Path $designRoot -Parent) "griddungeon-game"
$designSkills = Join-Path $designRoot ".cursor\skills"
$gameSkills = Join-Path $gameRoot ".cursor\skills"

if (-not (Test-Path $gameSkills)) {
    Write-Error "Game skills not found at: $gameSkills"
}

New-Item -ItemType Directory -Force -Path $designSkills, $gameSkills | Out-Null

# Canonical source per skill folder (repo name without prefix).
$canonical = @{
    "test-plan-grid-dungeon"   = "design-docs"
    "validate-unity-meta"      = "game"
    "stratum-floor-asset-sync" = "game"
    "stratum-floor-layout-check" = "game"
    "pull-next-backlog-ticket" = "game"
    "editor-agent-test"        = "game"
    "editor-agent-action"      = "game"
    "blender-bone-remap"       = "game"
    "vroid-shapekey-remap"     = "game"
    "deslop"                   = "design-docs"
    "class-naming-grid-dungeon" = "design-docs"
}

function Get-RepoSkillsRoot([string]$repo) {
    if ($repo -eq "game") { return $gameSkills }
    if ($repo -eq "design-docs") { return $designSkills }
    throw "Unknown repo: $repo"
}

$allSkills = [System.Collections.Generic.HashSet[string]]::new()
foreach ($name in $canonical.Keys) { [void]$allSkills.Add($name) }
Get-ChildItem $designSkills -Directory -ErrorAction SilentlyContinue | ForEach-Object { [void]$allSkills.Add($_.Name) }
Get-ChildItem $gameSkills -Directory -ErrorAction SilentlyContinue | ForEach-Object { [void]$allSkills.Add($_.Name) }

foreach ($skill in ($allSkills | Sort-Object)) {
    $srcRepo = if ($canonical.ContainsKey($skill)) { $canonical[$skill] } else { "game" }
    $srcRoot = Get-RepoSkillsRoot $srcRepo
    $srcPath = Join-Path $srcRoot $skill

    if (-not (Test-Path $srcPath)) {
        Write-Warning "Skip missing canonical skill: $skill ($srcRepo)"
        continue
    }

    foreach ($destRepo in @("design-docs", "game")) {
        if ($destRepo -eq $srcRepo) { continue }
        $destRoot = Get-RepoSkillsRoot $destRepo
        $destPath = Join-Path $destRoot $skill
        if (Test-Path $destPath) { Remove-Item $destPath -Recurse -Force }
        Copy-Item $srcPath $destPath -Recurse -Force
        Write-Host "Skill $skill : $srcRepo -> $destRepo"
    }
}

Write-Host "Done. Skills synced under both .cursor/skills/"

# Applies YAML frontmatter tags from obsidian-tag-registry.json.
# Idempotent: skips files that already have a top-level `tags:` key in frontmatter.
param(
    [string]$RepoRoot = (Split-Path $PSScriptRoot -Parent),
    [switch]$Force
)

$registryPath = Join-Path $PSScriptRoot "obsidian-tag-registry.json"
if (-not (Test-Path $registryPath)) {
    Write-Error "Missing registry: $registryPath"
    exit 1
}

$registry = Get-Content $registryPath -Raw | ConvertFrom-Json
$updated = 0
$skipped = 0
$missing = 0

function Test-HasTagsFrontmatter([string]$Content) {
    if ($Content -notmatch '(?s)^---\r?\n(.*?)\r?\n---') { return $false }
    return $Matches[1] -match '(?m)^tags:\s*$' -or $Matches[1] -match '(?m)^tags:\s*\['
}

function Build-Frontmatter([string[]]$Tags) {
    $lines = @("---", "tags:")
    foreach ($t in $Tags) {
        $lines += "  - $t"
    }
    $lines += "---"
    $lines += ""
    return ($lines -join "`n")
}

foreach ($entry in $registry.files) {
    $rel = $entry.path -replace '/', '\'
    $full = Join-Path $RepoRoot $rel
    if (-not (Test-Path $full)) {
        Write-Warning "Missing file: $($entry.path)"
        $missing++
        continue
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    $content = [System.IO.File]::ReadAllText($full, $utf8NoBom)

    if ((Test-HasTagsFrontmatter $content) -and -not $Force) {
        $skipped++
        continue
    }

    if ((Test-HasTagsFrontmatter $content) -and $Force) {
        $content = $content -replace '(?s)^---\r?\n.*?\r?\n---\r?\n', ''
    }

    $fm = Build-Frontmatter $entry.tags
    [System.IO.File]::WriteAllText($full, $fm + $content, $utf8NoBom)
    $updated++
    Write-Host "Tagged: $($entry.path)"
}

Write-Host "Done. Updated=$updated Skipped=$skipped Missing=$missing"

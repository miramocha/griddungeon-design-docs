# Phases D/E: scope lines, body Status rename, Related docs, encoding sweep.
# Authority: docs/04-dev/doc-format.md
param(
    [string]$RepoRoot = (Split-Path $PSScriptRoot -Parent),
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$fffd = [char]0xFFFD
$registryPath = Join-Path $RepoRoot "scripts/obsidian-tag-registry.json"
$registry = Get-Content $registryPath -Raw | ConvertFrom-Json
$scopeByPath = @{}
foreach ($entry in $registry.files) {
    $scopeByPath[$entry.path] = ($entry.tags | Where-Object { $_ -like "scope/*" } | Select-Object -First 1) -replace "scope/", ""
}

function Get-ScopeLine([string]$scopeTag) {
    switch ($scopeTag) {
        "optional" { return "**Scope:** [Optional](../00-release-scope.md#optional)" }
        "later" { return "**Scope:** [Later](../00-release-scope.md#later)" }
        default { return "**Scope:** [Required](../00-release-scope.md#required-first-playable)" }
    }
}

function Rename-BodyStatus([string]$Body) {
    return [regex]::Replace(
        $Body,
        '(?m)^\*\*Status:\*\*\s*(.*)$',
        {
            param($m)
            $rest = $m.Groups[1].Value.Trim()
            if ($rest -match '(?i)^Draft\b') { return "**Draft:** $rest" }
            if ($rest -match '(?i)^Shipped\b') { return "**Shipped:** $($rest -replace '(?i)^Shipped\s*[—-]\s*','')" }
            if ($rest -match '(?i)Synced') { return "**Synced:** $($rest -replace '(?i)^\*\*Synced\*\*\s*','')" }
            if ($rest -match '(?i)Design sketch|not locked') { return "**Open:** $rest" }
            if ($rest -match '(?i)^Epic\b') { return "**Tracking:** $rest" }
            if ($rest -match '(?i)^Merged\b') { return "**Shipped:** $rest" }
            if ($rest -match '(?i)^Locked\b') { return "**Shipped:** $rest" }
            if ($rest -match '(?i)^Accepted\b') { return "**Shipped:** $rest" }
            return "**Shipped:** $rest"
        }
    )
}

function Insert-ScopeLine([string]$Body, [string]$ScopeLine) {
    if ($Body -match '\*\*Scope:\*\*') { return $Body }
    if ($Body -match '(?s)^(?<head># [^\r\n]+\r?\n(?:\r?\n|(?![#\r\n]).+\r?\n)*?\r?\n)') {
        return $Matches[0] + $ScopeLine + "`r`n`r`n" + $Body.Substring($Matches[0].Length)
    }
    return $Body
}

function Normalize-RelatedHeading([string]$Body) {
    return $Body -replace '(?m)^## Related\s*$', '## Related docs'
}

function Fix-Latin1Mojibake([string]$Content) {
    $em = [string][char]0x2014
    $dot = [string][char]0x00B7
    $en = [string][char]0x2013
    $arr = [string][char]0x2192
    $Content = $Content.Replace([string][char]0x00E2 + [char]0x20AC + [char]0x201D, $em)
    $Content = $Content.Replace([string][char]0x00E2 + [char]0x20AC + [char]0x201C, $em)
    $Content = $Content.Replace([string][char]0x00E2 + [char]0x20AC, $em)
    $Content = $Content.Replace([string][char]0x00C2 + [char]0x00B7, " $dot ")
    $Content = $Content.Replace([string][char]0x00E2 + [char]0x20AC + "?", $em)
    if ($Content.IndexOf($fffd) -ge 0) {
        $Content = $Content.Replace([string]$fffd, $em)
    }
    return $Content
}

function Get-DocProfile([string]$RelPath) {
    $p = $RelPath -replace '\\', '/'
    if ($p -match '^decisions/') { return "adr" }
    if ($p -match '^docs/archive/') { return "archive" }
    if ($p -match '^docs/refs/') { return "ref" }
    if ($p -match '^docs/plans/') { return "plan" }
    if ($p -match '^docs/04-dev/') { return "dev" }
    if ($p -match '^docs/03-content/story-events/s1/') { return "story" }
    if ($p -match '^docs/03-content/') { return "content" }
    if ($p -match '^docs/02-systems/') { return "system" }
    if ($p -match '^docs/04-tech-notes\.md$') { return "vision" }
    return "other"
}

$targets = @()
$roots = @(
    (Join-Path $RepoRoot "docs/02-systems"),
    (Join-Path $RepoRoot "docs/03-content"),
    (Join-Path $RepoRoot "docs/04-dev"),
    (Join-Path $RepoRoot "docs/plans"),
    (Join-Path $RepoRoot "docs/04-tech-notes.md"),
    (Join-Path $RepoRoot "decisions")
)
foreach ($root in $roots) {
    if (-not (Test-Path $root)) { continue }
    if ((Get-Item $root).PSIsContainer) {
        $targets += Get-ChildItem $root -Filter "*.md" -Recurse -File
    }
    else {
        $targets += Get-Item $root
    }
}

$changed = @()
foreach ($file in ($targets | Sort-Object FullName -Unique)) {
    $rel = $file.FullName.Substring($RepoRoot.Length).TrimStart('\', '/').Replace('\', '/')
    if ($rel -match '/github-drafts/') { continue }

    $original = [System.IO.File]::ReadAllText($file.FullName, $utf8NoBom)
    $profile = Get-DocProfile $rel

    if ($original -match '(?s)^(---\r?\n.*?\r?\n---\r?\n)(.*)$') {
        $prefix = $Matches[1]
        $body = $Matches[2]
    }
    else {
        $prefix = ""
        $body = $original
    }

    $body = Fix-Latin1Mojibake $body

    if ($profile -eq "system") {
        $scopeTag = $scopeByPath[$rel]
        if ($scopeTag) {
            $body = Insert-ScopeLine $body (Get-ScopeLine $scopeTag)
        }
    }

    if ($profile -in @("system", "dev", "content", "vision", "plan", "story")) {
        $body = Rename-BodyStatus $body
    }

    if ($profile -in @("system", "dev", "content")) {
        $body = Normalize-RelatedHeading $body
    }

    $newContent = if ($prefix) { $prefix + $body } else { $body }

    if ($newContent -ne $original) {
        $changed += $rel
        if (-not $WhatIf) {
            [System.IO.File]::WriteAllText($file.FullName, $newContent, $utf8NoBom)
        }
    }
}

Write-Host "normalize-doc-format-wave: changed $($changed.Count) files"
if ($WhatIf) {
    $changed | ForEach-Object { Write-Host "  $_" }
}

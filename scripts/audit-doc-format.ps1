# Read-only audit for design-docs markdown format consistency.
# Authority: docs/04-dev/doc-format.md
param(
    [string]$RepoRoot = (Split-Path $PSScriptRoot -Parent),
    [string]$OutFile = "",
    [switch]$FailOnFindings
)

$ErrorActionPreference = "Stop"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

if ([string]::IsNullOrWhiteSpace($OutFile)) {
    $OutFile = Join-Path $RepoRoot "Logs/doc-format-audit.json"
}

function Test-Mojibake([string]$Content, [ref]$Label) {
    if ($Content.IndexOf([char]0xFFFD) -ge 0) {
        $Label.Value = "replacement-char-u+fffd"
        return $true
    }
    $latin1EmDash = [string][char]0x00E2 + [char]0x20AC
    if ($Content.Contains($latin1EmDash)) {
        $Label.Value = "mojibake-utf8-as-latin1"
        return $true
    }
    $latin1MiddleDot = [string][char]0x00C2 + [char]0x00B7
    if ($Content.Contains($latin1MiddleDot)) {
        $Label.Value = "mojibake-middle-dot"
        return $true
    }
    return $false
}

function Get-DocProfile([string]$RelPath) {
    $p = $RelPath -replace '\\', '/'
    if ($p -eq "README.md") { return "root" }
    if ($p -match '^decisions/') { return "adr" }
    if ($p -match '^docs/archive/') { return "archive" }
    if ($p -match '^docs/refs/') { return "ref" }
    if ($p -match '^docs/plans/') { return "plan" }
    if ($p -match '^docs/04-dev/') { return "dev" }
    if ($p -match '^docs/03-content/story-events/s1/') { return "story" }
    if ($p -match '^docs/03-content/') { return "content" }
    if ($p -match '^docs/02-systems/') { return "system" }
    if ($p -match '^docs/0[01]-') { return "vision" }
    if ($p -match '^docs/02-') { return "system" }
    if ($p -match '^docs/04-tech-notes\.md$') { return "vision" }
    if ($p -match '^docs/05-') { return "dev" }
    return "other"
}

function Get-FrontmatterAndBody([string]$Content) {
    if ($Content -match '(?s)^---\r?\n(.*?)\r?\n---\r?\n(.*)$') {
        return @{ Frontmatter = $Matches[1]; Body = $Matches[2]; HasFrontmatter = $true }
    }
    return @{ Frontmatter = ""; Body = $Content; HasFrontmatter = $false }
}

function Get-StatusFromTags([string]$Frontmatter) {
    if ($Frontmatter -match '(?m)^\s*-\s*status/([a-z]+)\s*$') {
        return $Matches[1]
    }
    return $null
}

function Get-BodyStatus([string]$Body) {
    if ($Body -match '(?m)^\*\*Status:\*\*\s*(.+)$') {
        return $Matches[1].Trim()
    }
    return $null
}

function Test-RelatedSection([string]$Body) {
    return $Body -match '(?m)^## Related( docs)?\s*$'
}

function Add-Finding([ref]$Findings, [string]$Path, [string]$Rule, [string]$Severity, [string]$Message) {
    $Findings.Value += [ordered]@{
        file     = $Path
        rule     = $Rule
        severity = $Severity
        message  = $Message
    }
}

$findings = [System.Collections.Generic.List[object]]::new()
$scanned = 0
$skipped = @()

$globRoots = @(
    (Join-Path $RepoRoot "README.md")
    (Join-Path $RepoRoot "docs")
    (Join-Path $RepoRoot "decisions")
)

$fileItems = @()
foreach ($root in $globRoots) {
    if (-not (Test-Path $root)) { continue }
    if ((Get-Item $root).PSIsContainer) {
        $fileItems += Get-ChildItem -Path $root -Filter "*.md" -Recurse -File
    }
    else {
        $fileItems += Get-Item $root
    }
}
$files = $fileItems | Sort-Object FullName -Unique

foreach ($file in $files) {
    $rel = $file.FullName.Substring($RepoRoot.Length).TrimStart('\', '/')
    $rel = $rel -replace '\\', '/'

    if ($rel -match '^\.cursor/' -or $rel -match '/github-drafts/') {
        $skipped += $rel
        continue
    }

    $content = [System.IO.File]::ReadAllText($file.FullName, $utf8NoBom)
    $scanned++
    $profile = Get-DocProfile $rel
    $parsed = Get-FrontmatterAndBody $content
    $fm = $parsed.Frontmatter
    $body = $parsed.Body

    # duplicate frontmatter
    if ($parsed.HasFrontmatter -and $body -match '(?s)^---\r?\n') {
        Add-Finding ([ref]$findings) $rel "duplicate-frontmatter" "error" "Second --- block in body (duplicate YAML frontmatter)"
    }

    # missing tags frontmatter (in-scope docs)
    if ($profile -notin @("other", "root") -and -not $parsed.HasFrontmatter) {
        Add-Finding ([ref]$findings) $rel "missing-frontmatter" "error" "No YAML frontmatter with tags (see obsidian-tag-registry.json)"
    }
    elseif ($parsed.HasFrontmatter -and $fm -notmatch '(?m)^tags:\s*$' -and $fm -notmatch '(?m)^tags:\s*\[') {
        Add-Finding ([ref]$findings) $rel "missing-tags" "error" "Frontmatter exists but no tags: list"
    }

    # missing H1
    if ($body -notmatch '(?m)^#\s+\S') {
        Add-Finding ([ref]$findings) $rel "missing-h1" "error" "No # title after frontmatter"
    }

    # mojibake
    $mojiLabel = ""
    if (Test-Mojibake $content ([ref]$mojiLabel)) {
        Add-Finding ([ref]$findings) $rel $mojiLabel "warning" "Suspect encoding - $mojiLabel"
    }

    # body Status on non-ADR (duplicate with frontmatter)
    $tagStatus = Get-StatusFromTags $fm
    $bodyStatus = Get-BodyStatus $body
    if ($profile -in @("system", "dev", "content", "vision", "plan") -and $null -ne $bodyStatus) {
        Add-Finding ([ref]$findings) $rel "body-status-duplicate" "warning" "Body **Status:** should move to frontmatter status/* only - '$bodyStatus'"
    }

    # ADR structure + status alignment
    if ($profile -eq "adr") {
        if ($body -notmatch '(?m)^## Context\s*$') {
            Add-Finding ([ref]$findings) $rel "adr-missing-context" "warning" "ADR missing ## Context"
        }
        if ($body -notmatch '(?m)^## Decision\s*$') {
            Add-Finding ([ref]$findings) $rel "adr-missing-decision" "warning" "ADR missing ## Decision"
        }
        if ($null -eq $bodyStatus) {
            Add-Finding ([ref]$findings) $rel "adr-missing-body-status" "info" "ADR missing body **Status:** line"
        }
        elseif ($null -ne $tagStatus -and $bodyStatus -notmatch $tagStatus) {
            $normalized = $bodyStatus.ToLower()
            $tagOk = $normalized -match $tagStatus
            if (-not $tagOk -and $tagStatus -eq "accepted" -and $normalized -notmatch "accepted") {
                Add-Finding ([ref]$findings) $rel "status-tag-mismatch" "info" "Frontmatter status/$tagStatus may not match body **Status:** $bodyStatus"
            }
            elseif (-not $tagOk -and $tagStatus -eq "proposed" -and $normalized -notmatch "proposed") {
                Add-Finding ([ref]$findings) $rel "status-tag-mismatch" "info" "Frontmatter status/$tagStatus may not match body **Status:** $bodyStatus"
            }
            elseif (-not $tagOk -and $tagStatus -eq "deferred" -and $normalized -notmatch "deferred") {
                Add-Finding ([ref]$findings) $rel "status-tag-mismatch" "info" "Frontmatter status/$tagStatus may not match body **Status:** $bodyStatus"
            }
        }
    }

    # Related section
    if ($profile -in @("system", "dev", "content") -and -not (Test-RelatedSection $body)) {
        $severity = if ($profile -eq "system") { "warning" } else { "info" }
        Add-Finding ([ref]$findings) $rel "missing-related-section" $severity "No ## Related or ## Related docs section (doc-format.md)"
    }

    # system scope line
    if ($profile -eq "system" -and $body -notmatch '\*\*Scope:\*\*') {
        Add-Finding ([ref]$findings) $rel "missing-scope-line" "info" "System doc missing **Scope:** line near top"
    }

    # content tracking line
    if ($profile -eq "content" -and $rel -notmatch '/story-events/s1/' -and $rel -notmatch '/campaign/s1-guided-tutorials') {
        if ($body -notmatch '\*\*Tracking:\*\*' -and $body -notmatch '\*\*Authority') {
            Add-Finding ([ref]$findings) $rel "content-missing-meta" "info" "Content doc missing **Tracking:** or **Authority** block"
        }
    }

    # archive banner
    if ($profile -eq "archive" -and $body -notmatch '(?i)archived') {
        Add-Finding ([ref]$findings) $rel "archive-missing-banner" "warning" "Archive doc should state Archived / superseded"
    }

    # MVP link text in body (not filenames)
    if ($content -match '\[ADR[^\]]*MVP[123]') {
        Add-Finding ([ref]$findings) $rel "legacy-mvp-link-text" "info" "Link text uses MVP1/2/3 - prefer default/optional (filenames OK)"
    }
}

$bySeverity = @{
    error   = @($findings | Where-Object { $_.severity -eq "error" }).Count
    warning = @($findings | Where-Object { $_.severity -eq "warning" }).Count
    info    = @($findings | Where-Object { $_.severity -eq "info" }).Count
}

$report = [ordered]@{
    generatedAt = (Get-Date).ToUniversalTime().ToString("o")
    authority   = "docs/04-dev/doc-format.md"
    scanned     = $scanned
    skipped     = $skipped
    summary     = $bySeverity
    findings    = $findings
}

$outDir = Split-Path $OutFile -Parent
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$json = $report | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText($OutFile, $json, $utf8NoBom)

Write-Host "Doc format audit - scanned=$scanned skipped=$($skipped.Count)"
Write-Host "  errors:   $($bySeverity.error)"
Write-Host "  warnings: $($bySeverity.warning)"
Write-Host "  info:     $($bySeverity.info)"
Write-Host "Report: $OutFile"

if ($FailOnFindings -and ($bySeverity.error -gt 0 -or $bySeverity.warning -gt 0)) {
    exit 1
}

exit 0

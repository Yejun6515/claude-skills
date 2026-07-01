# update-index.ps1
# Regenerates the AUTO block of the skills/memory index note in the Obsidian
# vault ("07. Claude Skills" folder) from the live SKILL.md descriptions and MEMORY.md.
# Portable: vault root comes from _config\local-paths.md (per-PC, gitignored);
# skills/memory are resolved under %USERPROFILE%\.claude.
# Run after every claude-skills push/pull (session rule: memory claude-skills-index-sync).

$ErrorActionPreference = 'Stop'

$skillsDir = Join-Path $env:USERPROFILE '.claude\skills'
$projects  = Join-Path $env:USERPROFILE '.claude\projects'

# --- Resolve the vault root from _config\local-paths.md ---
$cfg = Join-Path $skillsDir '_config\local-paths.md'
$vault = $null
if (Test-Path $cfg) {
  $m = [regex]::Match((Get-Content -LiteralPath $cfg -Raw -Encoding UTF8), '(?m)^vault_root:\s*(.+)$')
  if ($m.Success) { $vault = $m.Groups[1].Value.Trim() }
}
if (-not $vault -or -not (Test-Path $vault)) {
  Write-Warning "vault_root not configured or not found — create _config\local-paths.md (see _config\README.md). Skipping index update."
  exit 0
}

# Find the index note inside the vault's "07. Claude Skills" folder by its AUTO marker.
$noteDir = Join-Path $vault '07. Claude Skills'
if (-not (Test-Path $noteDir)) { Write-Warning "Note folder not found: $noteDir"; exit 0 }
$note = $null
foreach ($f in Get-ChildItem -LiteralPath $noteDir -Filter *.md) {
  if ((Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8) -match '<!-- AUTO:START -->') { $note = $f.FullName; break }
}

if (-not $note -or -not (Test-Path $note)) { Write-Warning "Index note (with AUTO markers) not found in $noteDir"; exit 0 }
if (-not (Test-Path $skillsDir)) { Write-Warning "Skills dir not found: $skillsDir"; exit 0 }

function Get-Frontmatter([string]$path) {
  $raw = Get-Content -LiteralPath $path -Raw -Encoding UTF8
  if ($raw -match "(?s)^﻿?---\s*\r?\n(.*?)\r?\n---") { return $matches[1] }
  return ""
}
function Get-Scalar([string]$fm, [string]$key) {
  $m = [regex]::Match($fm, "(?m)^$key\:\s*(.*)$")
  if ($m.Success) { return $m.Groups[1].Value.Trim().Trim('"').Trim("'") }
  return ""
}
function Clean([string]$s, [int]$max = 240) {
  $s = ($s -replace '\s+', ' ').Trim()
  $s = $s -replace '\|', '\|'
  if ($s.Length -gt $max) { $s = $s.Substring(0, $max).TrimEnd() + '…' }
  return $s
}

# --- Skills ---
$skills = @()
foreach ($d in Get-ChildItem -LiteralPath $skillsDir -Directory | Sort-Object Name) {
  $sk = Join-Path $d.FullName 'SKILL.md'
  if (-not (Test-Path $sk)) { continue }
  $fm   = Get-Frontmatter $sk
  $name = Get-Scalar $fm 'name'
  if ([string]::IsNullOrWhiteSpace($name)) { $name = $d.Name }
  $desc = Get-Scalar $fm 'description'
  $skills += [pscustomobject]@{ Name = $name; Desc = (Clean $desc) }
}

# --- Memory ---
$memFile = Get-ChildItem -LiteralPath $projects -Recurse -Filter 'MEMORY.md' -ErrorAction SilentlyContinue |
           Where-Object { $_.Directory.Name -eq 'memory' } | Select-Object -First 1
$memLines = @()
if ($memFile) {
  $memLines = Get-Content -LiteralPath $memFile.FullName -Encoding UTF8 | Where-Object { $_ -match '^\s*-\s' }
}

# --- Build AUTO block ---
$date = Get-Date -Format 'yyyy-MM-dd'
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("**갱신: $date · 스킬 $($skills.Count) · 메모리 $($memLines.Count)**")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("### 스킬 ($($skills.Count)) — SKILL.md description")
[void]$sb.AppendLine("| 스킬 | 설명 |")
[void]$sb.AppendLine("|---|---|")
foreach ($s in $skills) { [void]$sb.AppendLine("| ``$($s.Name)`` | $($s.Desc) |") }
[void]$sb.AppendLine("")
[void]$sb.AppendLine("### 메모리 ($($memLines.Count)) — MEMORY.md")
foreach ($l in $memLines) { [void]$sb.AppendLine($l.Trim()) }
$block = $sb.ToString().TrimEnd("`r","`n")

# --- Splice into note between markers ---
$start = '<!-- AUTO:START -->'
$end   = '<!-- AUTO:END -->'
$content = Get-Content -LiteralPath $note -Raw -Encoding UTF8
$i = $content.IndexOf($start)
$j = $content.IndexOf($end)
if ($i -lt 0 -or $j -lt 0 -or $j -lt $i) { Write-Warning "AUTO markers not found in note."; exit 0 }
$new = $content.Substring(0, $i + $start.Length) + "`r`n" + $block + "`r`n" + $content.Substring($j)

[System.IO.File]::WriteAllText($note, $new, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "Updated index: $($skills.Count) skills, $($memLines.Count) memories ($date)"

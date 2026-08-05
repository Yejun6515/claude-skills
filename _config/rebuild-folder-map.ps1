# rebuild-folder-map.ps1 - re-derive the vault <-> U: project mapping from the
# file:/// links that already live in the Obsidian notes, and print it as a
# markdown table for project-folder-map.md.
# NOTE: ASCII-only source (PS 5.1 mangles CJK literals in BOM-less .ps1 files).
#       Vault/U: paths themselves contain CJK but they come from the filesystem,
#       never from a literal here.
param(
  [string]$VaultProjects = "C:\Users\Z006K14G\Desktop\Yejun\01. Projects",
  [string]$URoot         = "U:\_kimyejun_root_placeholder",   # overridden below from local-paths style default
  [string]$OutPath       = ""
)
$ErrorActionPreference = "Stop"

# U: root is derived from the links themselves, so no CJK literal is needed here.
$rx = [regex]'file:///(U:\\[^)>\r\n|\]]+)'

$rows = @()
foreach ($f in (Get-ChildItem -LiteralPath $VaultProjects -Recurse -Filter *.md)) {
  $rel   = $f.FullName.Substring($VaultProjects.Length + 1)
  $parts = $rel -split '\\'
  if ($parts.Count -lt 3) { continue }          # loose note directly under a company folder
  if ($parts.Count -ge 4) { $proj = ($parts[0..2] -join '\') } else { $proj = ($parts[0..1] -join '\') }

  $txt = [IO.File]::ReadAllText($f.FullName, [Text.Encoding]::UTF8)
  foreach ($m in $rx.Matches($txt)) {
    $u = ($m.Groups[1].Value.TrimEnd(' ', '\')) -replace '%20', ' '
    $seg = $u -split '\\'
    # strip the case folder (YYMMDD_topic) and any file name to leave the project root
    while ($seg.Count -gt 4 -and ($seg[-1] -match '^\d{6}[_ ]' -or $seg[-1] -match '\.[a-zA-Z0-9]{2,5}$' -or $seg[-1] -eq '')) {
      $seg = $seg[0..($seg.Count - 2)]
    }
    $rows += New-Object PSObject -Property @{ proj = $proj; u = ($seg -join '\') }
  }
}

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("| vault | U: | links | exists |")
[void]$sb.AppendLine("|---|---|---|---|")
foreach ($g in ($rows | Group-Object proj | Sort-Object Name)) {
  $top = $g.Group | Group-Object u | Sort-Object Count -Descending | Select-Object -First 1
  $ok  = Test-Path -LiteralPath $top.Name
  [void]$sb.AppendLine("| ``" + $g.Name + "`` | ``" + $top.Name + "`` | " + $top.Count + "/" + $g.Count + " | " + $ok + " |")
}

$out = $sb.ToString()
if ($OutPath -ne "") {
  $utf8 = New-Object System.Text.UTF8Encoding($false)
  [IO.File]::WriteAllText($OutPath, $out, $utf8)
  Write-Output ("WROTE -> " + $OutPath)
} else {
  Write-Output $out
}
Write-Output ("links scanned = " + $rows.Count)

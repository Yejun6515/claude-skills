# Extract HEADERS ONLY (no body) from Outlook .msg files under a folder, for bulk matching/triage.
# One compact record per mail. Writes UTF-8 to -OutFile (or stdout if omitted).
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File extract_msg_headers.ps1 -FolderPath "<folder>" [-OutFile "<file>"]
param(
  [Parameter(Mandatory=$true)][string]$FolderPath,
  [string]$OutFile
)
$ErrorActionPreference = "Stop"
$msgs = Get-ChildItem -Path $FolderPath -Recurse -Filter *.msg | Sort-Object FullName
if (-not $msgs) { Write-Output "NO .msg FILES under: $FolderPath"; return }
$ol = New-Object -ComObject Outlook.Application
$ns = $ol.GetNamespace("MAPI")
$lines = New-Object System.Collections.Generic.List[string]
$i = 0
foreach ($f in $msgs) {
  $i++
  $rel = $f.FullName.Substring($FolderPath.TrimEnd('\').Length + 1)
  try {
    $m = $ns.OpenSharedItem($f.FullName)
    $att = @()
    foreach ($a in $m.Attachments) { $att += $a.FileName }
    # skip inline-image noise in attachment list
    $att = $att | Where-Object { $_ -notmatch '^image\d+\.(png|jpg|jpeg|gif)$' }
    $lines.Add("#$i | $rel")
    $lines.Add("  SUBJ: $($m.Subject)")
    $lines.Add("  FROM: $($m.SenderName) <$($m.SenderEmailAddress)>")
    $lines.Add("  TO: $($m.To)")
    if ($m.CC) { $lines.Add("  CC: $($m.CC)") }
    $lines.Add("  SENT: $($m.SentOn)")
    if ($att) { $lines.Add("  ATT: $($att -join '; ')") }
    $m.Close(1)
  } catch {
    $lines.Add("#$i | $rel")
    $lines.Add("  !! FAILED: $($_.Exception.Message)")
  }
}
if ($OutFile) {
  $lines | Out-File -FilePath $OutFile -Encoding utf8
  Write-Output "OK: $($msgs.Count) mails -> $OutFile"
} else {
  $lines
}

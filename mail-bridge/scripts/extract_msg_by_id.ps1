# Extract full mails (with body) for specific ids from a _headers.txt index produced by extract_msg_headers.ps1.
# Usage: ... -HeadersFile "<_headers.txt>" -BaseFolder "<folder containing the mails>" -Ids "12,45,301" [-MaxBody 6000]
param(
  [Parameter(Mandatory=$true)][string]$HeadersFile,
  [Parameter(Mandatory=$true)][string]$BaseFolder,
  [Parameter(Mandatory=$true)][string]$Ids,
  [int]$MaxBody = 6000
)
$ErrorActionPreference = "Stop"
$want = @{}
foreach ($x in ($Ids -split ',')) { $want[[int]$x.Trim()] = $true }
$map = @{}
foreach ($ln in (Get-Content $HeadersFile -Encoding UTF8)) {
  if ($ln -match '^#(\d+) \| (.+)$') {
    $id = [int]$Matches[1]
    if ($want.ContainsKey($id)) { $map[$id] = $Matches[2] }
  }
}
$ol = New-Object -ComObject Outlook.Application
$ns = $ol.GetNamespace("MAPI")
foreach ($id in ($want.Keys | Sort-Object)) {
  if (-not $map.ContainsKey($id)) { Write-Output "== #$id NOT FOUND in headers file =="; continue }
  $full = Join-Path $BaseFolder $map[$id]
  try {
    $m = $ns.OpenSharedItem($full)
    Write-Output "========== #$id | $($map[$id]) =========="
    Write-Output "SUBJECT: $($m.Subject)"
    Write-Output "FROM: $($m.SenderName) <$($m.SenderEmailAddress)>"
    Write-Output "TO: $($m.To)"
    Write-Output "CC: $($m.CC)"
    Write-Output "SENT: $($m.SentOn)"
    $att = @(); foreach ($a in $m.Attachments) { $att += $a.FileName }
    $att = $att | Where-Object { $_ -notmatch '^image\d+\.(png|jpg|jpeg|gif)$' }
    if ($att) { Write-Output "ATT: $($att -join '; ')" }
    $b = $m.Body
    if ($MaxBody -gt 0 -and $b.Length -gt $MaxBody) { $b = $b.Substring(0, $MaxBody) + "`n... [TRUNCATED at $MaxBody chars, full=$($m.Body.Length)]" }
    Write-Output "---- BODY ----"
    Write-Output $b
    Write-Output ""
    $m.Close(1)
  } catch {
    Write-Output "== #$id FAILED: $($_.Exception.Message) =="
  }
}

# Extract Outlook .msg files under a folder to text (subject/from/to/cc/date/attachments/body).
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File extract_msg.ps1 -FolderPath "<folder>"
param(
  [Parameter(Mandatory=$true)][string]$FolderPath
)
$ErrorActionPreference = "Stop"
$msgs = Get-ChildItem -Path $FolderPath -Recurse -Filter *.msg | Sort-Object FullName
if (-not $msgs) { Write-Output "NO .msg FILES under: $FolderPath"; return }
$ol = New-Object -ComObject Outlook.Application
$ns = $ol.GetNamespace("MAPI")
foreach ($f in $msgs) {
  try {
    $m = $ns.OpenSharedItem($f.FullName)
    Write-Output "========== FILE: $($f.FullName) =========="
    Write-Output "SUBJECT: $($m.Subject)"
    Write-Output "SENDER : $($m.SenderName) <$($m.SenderEmailAddress)>"
    Write-Output "TO     : $($m.To)"
    Write-Output "CC     : $($m.CC)"
    Write-Output "SENT   : $($m.SentOn)"
    Write-Output "---- BODY ----"
    Write-Output $m.Body
    Write-Output "---- ATTACHMENTS ----"
    foreach ($a in $m.Attachments) { Write-Output " - $($a.FileName)" }
    Write-Output ""
    $m.Close(1)
  } catch {
    Write-Output "!! FAILED: $($f.FullName) : $($_.Exception.Message)"
  }
}

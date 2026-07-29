# Dump an Outlook .msg (headers + body) and save ALL attachments to an output folder.
# 入金連絡 mails carry their data table as an embedded image (image001.png) — the body text is one line,
# so the attachment MUST be saved and read with the Read tool.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File extract_msg_attachments.ps1 -MsgPath "<file.msg>" -OutDir "<folder>"
param(
  [Parameter(Mandatory=$true)][string]$MsgPath,
  [Parameter(Mandatory=$true)][string]$OutDir
)
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$ol = New-Object -ComObject Outlook.Application
$ns = $ol.GetNamespace("MAPI")
$m  = $ns.OpenSharedItem($MsgPath)
Write-Output "SUBJECT: $($m.Subject)"
Write-Output "SENDER : $($m.SenderName)"
Write-Output "TO     : $($m.To)"
Write-Output "CC     : $($m.CC)"
Write-Output "SENT   : $($m.SentOn)"
Write-Output "---- BODY ----"
Write-Output $m.Body
Write-Output "---- SAVED ATTACHMENTS ----"
foreach ($a in $m.Attachments) {
  $dest = Join-Path $OutDir $a.FileName
  $a.SaveAsFile($dest)
  Write-Output $dest
}
$m.Close(1)

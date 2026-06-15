<#
.SYNOPSIS
  Extract Outlook .msg files in a folder into one UTF-8 text dump for an LLM to read.

.DESCRIPTION
  Walks a folder (recursively) for .msg files, opens each via the Outlook COM
  object, and writes a delimited plain-text block per message containing:
  Subject / From / To / Cc / Date / Attachments / Body (full reply chain).

  Output is written as UTF-8 (no BOM) so the Read tool can consume it cleanly.

.PARAMETER FolderPath
  Folder that holds the .msg files (searched recursively).

.PARAMETER OutFile
  Where to write the dump. Defaults to <FolderPath>\_extracted_emails.txt

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File extract_msg.ps1 -FolderPath "C:\...\Zhengrui N2Foil"
#>
param(
    [Parameter(Mandatory = $true)] [string]$FolderPath,
    [string]$OutFile
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $FolderPath)) { throw "Folder not found: $FolderPath" }
if (-not $OutFile) { $OutFile = Join-Path $FolderPath '_extracted_emails.txt' }

$files = Get-ChildItem -Path $FolderPath -Recurse -Filter *.msg
if ($files.Count -eq 0) { throw "No .msg files found under $FolderPath" }

$ol = New-Object -ComObject Outlook.Application
$sb = New-Object System.Text.StringBuilder

foreach ($f in $files) {
    try {
        $msg = $ol.CreateItemFromTemplate($f.FullName)
    } catch {
        [void]$sb.AppendLine("==================== FILE: $($f.Name) ====================")
        [void]$sb.AppendLine("ERROR opening: $($_.Exception.Message)")
        [void]$sb.AppendLine("")
        continue
    }
    $atts = @()
    foreach ($a in $msg.Attachments) { $atts += $a.FileName }

    [void]$sb.AppendLine("==================== FILE: $($f.Name) ====================")
    [void]$sb.AppendLine("RELATIVE_PATH: $($f.FullName.Substring($FolderPath.Length).TrimStart('\'))")
    [void]$sb.AppendLine("SUBJECT: $($msg.Subject)")
    [void]$sb.AppendLine("FROM: $($msg.SenderName)")
    [void]$sb.AppendLine("TO: $($msg.To)")
    [void]$sb.AppendLine("CC: $($msg.CC)")
    [void]$sb.AppendLine("DATE: $($msg.ReceivedTime)")
    [void]$sb.AppendLine("ATTACHMENTS: $($atts -join ' | ')")
    [void]$sb.AppendLine("----- BODY -----")
    [void]$sb.AppendLine($msg.Body)
    [void]$sb.AppendLine("")
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($OutFile, $sb.ToString(), $utf8NoBom)
Write-Output "WROTE: $OutFile ($($files.Count) files)"

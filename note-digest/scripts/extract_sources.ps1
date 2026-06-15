<#
.SYNOPSIS
  Extract the source files in a folder (.msg / .docx / .xlsx / .pptx, + pointers for .pdf)
  into one UTF-8 text dump for an LLM to read. Generalizes extract_msg.ps1.

.DESCRIPTION
  Walks a folder (recursively) and, per file type, dumps readable text:
    .msg            -> Outlook COM: Subject/From/To/Cc/Date/Attachments/Body (full reply chain)
    .docx .doc      -> Word COM: full paragraph text + table rows
    .xlsx .xlsm .xls-> Excel COM: each sheet's used range text (capped rows/cols)
    .pptx .ppt      -> PowerPoint COM: text from each slide's shapes
    .pdf            -> pointer line only (read the PDF directly with the Read tool)
  Requires Microsoft Office (Outlook/Word/Excel/PowerPoint) installed.
  Output is UTF-8 without BOM so the Read tool consumes it cleanly.

.PARAMETER FolderPath
  Folder holding the source files (searched recursively).

.PARAMETER OutFile
  Output path. Defaults to <FolderPath>\_extracted_sources.txt

.PARAMETER MaxRows
  Max spreadsheet rows per sheet to dump (default 80).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File extract_sources.ps1 -FolderPath "U:\...\260514_..._Schedule"
#>
param(
    [Parameter(Mandatory = $true)] [string]$FolderPath,
    [string]$OutFile,
    [int]$MaxRows = 80
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path $FolderPath)) { throw "Folder not found: $FolderPath" }
if (-not $OutFile) { $OutFile = Join-Path $FolderPath '_extracted_sources.txt' }

$files = Get-ChildItem -Path $FolderPath -Recurse -File
if ($files.Count -eq 0) { throw "No files found under $FolderPath" }

$sb = New-Object System.Text.StringBuilder
$outlook = $null; $word = $null; $excel = $null; $ppt = $null

function Add-Header($f, $kind) {
    [void]$sb.AppendLine("==================== [$kind] $($f.Name) ====================")
    [void]$sb.AppendLine("RELATIVE_PATH: $($f.FullName.Substring($FolderPath.Length).TrimStart('\'))")
}

foreach ($f in $files) {
    if ($f.Name -like '_extracted_*') { continue }
    $ext = $f.Extension.ToLower()
    try {
        switch -Regex ($ext) {
            '\.msg$' {
                if (-not $outlook) { $outlook = New-Object -ComObject Outlook.Application }
                $m = $outlook.CreateItemFromTemplate($f.FullName)
                $atts = @(); foreach ($a in $m.Attachments) { $atts += $a.FileName }
                Add-Header $f 'MSG'
                [void]$sb.AppendLine("SUBJECT: $($m.Subject)")
                [void]$sb.AppendLine("FROM: $($m.SenderName)  |  DATE: $($m.ReceivedTime)")
                [void]$sb.AppendLine("TO: $($m.To)")
                [void]$sb.AppendLine("CC: $($m.CC)")
                [void]$sb.AppendLine("ATTACHMENTS: $($atts -join ' | ')")
                [void]$sb.AppendLine("----- BODY -----")
                [void]$sb.AppendLine($m.Body)
            }
            '\.docx?$' {
                if (-not $word) { $word = New-Object -ComObject Word.Application; $word.Visible = $false }
                $d = $word.Documents.Open($f.FullName, $false, $true)
                Add-Header $f 'DOCX'
                [void]$sb.AppendLine("----- TEXT -----")
                [void]$sb.AppendLine($d.Content.Text)
                $ti = 0
                foreach ($t in $d.Tables) {
                    $ti++; [void]$sb.AppendLine("----- TABLE $ti -----")
                    for ($r = 1; $r -le $t.Rows.Count; $r++) {
                        $row = @()
                        for ($c = 1; $c -le $t.Columns.Count; $c++) {
                            try { $row += ($t.Cell($r, $c).Range.Text -replace "[\r\a\x07]", '') } catch {}
                        }
                        [void]$sb.AppendLine(("R{0}: {1}" -f $r, ($row -join ' | ')))
                    }
                }
                $d.Close($false)
            }
            '\.xls[xm]?$' {
                if (-not $excel) { $excel = New-Object -ComObject Excel.Application; $excel.Visible = $false; $excel.DisplayAlerts = $false }
                $wb = $excel.Workbooks.Open($f.FullName, $false, $true)
                Add-Header $f 'XLSX'
                foreach ($ws in $wb.Worksheets) {
                    $ur = $ws.UsedRange
                    [void]$sb.AppendLine("----- SHEET: $($ws.Name)  (rows=$($ur.Rows.Count) cols=$($ur.Columns.Count)) -----")
                    $rN = [Math]::Min($ur.Rows.Count, $MaxRows)
                    $cN = [Math]::Min($ur.Columns.Count, 20)
                    for ($r = 1; $r -le $rN; $r++) {
                        $cells = @()
                        for ($c = 1; $c -le $cN; $c++) {
                            $v = $ur.Cells.Item($r, $c).Text
                            if ($v) { $cells += "[$c]$v" }
                        }
                        if ($cells.Count -gt 0) { [void]$sb.AppendLine(("R{0}: {1}" -f $r, ($cells -join '  '))) }
                    }
                }
                $wb.Close($false)
            }
            '\.pptx?$' {
                if (-not $ppt) { $ppt = New-Object -ComObject PowerPoint.Application }
                $pres = $ppt.Presentations.Open($f.FullName, $true, $false, $false)
                Add-Header $f 'PPTX'
                $si = 0
                foreach ($slide in $pres.Slides) {
                    $si++; $txt = @()
                    foreach ($shape in $slide.Shapes) {
                        try { if ($shape.HasTextFrame -and $shape.TextFrame.HasText) { $txt += $shape.TextFrame.TextRange.Text } } catch {}
                    }
                    [void]$sb.AppendLine("----- SLIDE $si -----")
                    [void]$sb.AppendLine(($txt -join "`n"))
                }
                $pres.Close()
            }
            '\.pdf$' {
                Add-Header $f 'PDF'
                [void]$sb.AppendLine("(PDF — read directly with the Read tool: $($f.FullName))")
            }
            default {
                Add-Header $f 'OTHER'
                [void]$sb.AppendLine("(unhandled type $ext — $($f.Length) bytes)")
            }
        }
    } catch {
        Add-Header $f 'ERROR'
        [void]$sb.AppendLine("ERROR: $($_.Exception.Message)")
    }
    [void]$sb.AppendLine("")
}

if ($ppt)    { try { $ppt.Quit() } catch {} }
if ($excel)  { try { $excel.Quit() } catch {} }
if ($word)   { try { $word.Quit() } catch {} }
# Outlook is left running (quitting a user's Outlook session is intrusive)

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($OutFile, $sb.ToString(), $utf8NoBom)
Write-Output "WROTE: $OutFile ($($files.Count) files)"

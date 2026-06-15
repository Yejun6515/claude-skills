<#
.SYNOPSIS
  Extract translatable units (table cells / paragraphs containing Japanese) from a
  Word MOM (.docx) so they can be translated to Korean.

.USAGE
  powershell -File extract-cells.ps1 -Source "<path to JP .docx>" [-Out "<json path>"]

  Prints JSON to stdout (and to -Out if given):
    [ { "id": "t1.r2.c1", "kind": "cell", "text": "..." }, ... ]
  text uses \n for line breaks (w:br) and paragraph breaks inside a cell.
  Only units that contain Japanese kana/kanji are emitted.
#>
param(
  [Parameter(Mandatory=$true)][string]$Source,
  [string]$Out
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

# Japanese: Hiragana, Katakana, CJK ext-A, CJK unified, compat. (Hangul AC00-D7AF excluded.)
# \u escapes keep this ASCII-safe regardless of how PowerShell decodes the script file.
$jpRegex = [regex]'[぀-ヿ㐀-䶿一-鿿豈-﫿]'

# Copy to temp so a file open in Word can still be read.
$work = Join-Path $env:TEMP ("mom_extract_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $work | Out-Null
$copy = Join-Path $work "src.docx"
Copy-Item $Source $copy -Force
$xmlPath = Join-Path $work "document.xml"
$zip = [System.IO.Compression.ZipFile]::OpenRead($copy)
try {
  $entry = $zip.GetEntry("word/document.xml")
  [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $xmlPath, $true)
} finally { $zip.Dispose() }

[xml]$doc = Get-Content $xmlPath -Encoding UTF8
$ns = New-Object System.Xml.XmlNamespaceManager($doc.NameTable)
$ns.AddNamespace("w","http://schemas.openxmlformats.org/wordprocessingml/2006/main")
$body = $doc.SelectSingleNode("//w:body", $ns)

function Get-ParaText($p, $ns) {
  $sb = New-Object System.Text.StringBuilder
  foreach ($n in $p.SelectNodes(".//w:t | .//w:br | .//w:cr | .//w:tab", $ns)) {
    switch ($n.LocalName) {
      "t"   { [void]$sb.Append($n.InnerText) }
      "br"  { [void]$sb.Append("`n") }
      "cr"  { [void]$sb.Append("`n") }
      "tab" { [void]$sb.Append("`t") }
    }
  }
  $sb.ToString()
}

$results = New-Object System.Collections.ArrayList
$tblIdx = 0
$pIdx = 0
foreach ($node in $body.ChildNodes) {
  if ($node.LocalName -eq "tbl") {
    $rows = $node.SelectNodes("./w:tr", $ns)
    $r = 0
    foreach ($row in $rows) {
      $cells = $row.SelectNodes("./w:tc", $ns)
      $c = 0
      foreach ($cell in $cells) {
        $paras = $cell.SelectNodes("./w:p", $ns)
        $txt = ($paras | ForEach-Object { Get-ParaText $_ $ns }) -join "`n"
        if ($jpRegex.IsMatch($txt)) {
          [void]$results.Add([ordered]@{ id="t$tblIdx.r$r.c$c"; kind="cell"; text=$txt })
        }
        $c++
      }
      $r++
    }
    $tblIdx++
  }
  elseif ($node.LocalName -eq "p") {
    $txt = Get-ParaText $node $ns
    if ($jpRegex.IsMatch($txt)) {
      [void]$results.Add([ordered]@{ id="p$pIdx"; kind="para"; text=$txt })
    }
    $pIdx++
  }
}

$json = ConvertTo-Json $results -Depth 6
if ($Out) {
  [System.IO.File]::WriteAllText($Out, $json, (New-Object System.Text.UTF8Encoding($false)))
}
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Output $json
Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue

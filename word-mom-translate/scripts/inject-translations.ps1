<#
.SYNOPSIS
  Inject Korean translations under the original Japanese text in a Word MOM (.docx),
  preserving the original untouched. Each translation is appended as a new blue,
  parenthesized paragraph inside the same table cell (or right after a body paragraph).

.USAGE
  powershell -File inject-translations.ps1 -Source "<JP .docx>" `
            -Translations "<translations.json>" -Out "<JP_KR .docx>"

  translations.json maps the ids from extract-cells.ps1 to Korean text:
    { "t1.r2.c1": "1-23 1) l  Centrifugal pump ... Reuse를 기재할 것",
      "t1.r2.c3": "잘 알겠습니다" }
  Use \n inside a value for line breaks (they become <w:br/>).
  Ids NOT present in the JSON are left untranslated.
#>
param(
  [Parameter(Mandatory=$true)][string]$Source,
  [Parameter(Mandatory=$true)][string]$Translations,
  [Parameter(Mandatory=$true)][string]$Out
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression

$wns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# ---- load translations ----
$tjson = [System.IO.File]::ReadAllText($Translations, [System.Text.Encoding]::UTF8)
$tobj  = $tjson | ConvertFrom-Json
$trans = @{}
foreach ($p in $tobj.PSObject.Properties) { $trans[$p.Name] = [string]$p.Value }

# ---- copy source to output, then edit the document.xml entry in place ----
Copy-Item $Source $Out -Force

$zip = [System.IO.Compression.ZipFile]::Open($Out, [System.IO.Compression.ZipArchiveMode]::Update)
try {
  $entry = $zip.GetEntry("word/document.xml")
  $sr = New-Object System.IO.StreamReader($entry.Open(), [System.Text.Encoding]::UTF8)
  $xmlText = $sr.ReadToEnd(); $sr.Close()

  [xml]$doc = $xmlText
  $ns = New-Object System.Xml.XmlNamespaceManager($doc.NameTable)
  $ns.AddNamespace("w", $wns)
  $body = $doc.SelectSingleNode("//w:body", $ns)

  function Esc([string]$s) {
    $s.Replace("&","&amp;").Replace("<","&lt;").Replace(">","&gt;")
  }

  # Build a translation <w:p> (blue, Malgun Gothic eastAsia, ko-KR, wrapped in parens).
  function New-TransParagraph([string]$korean) {
    $rPr = '<w:rPr><w:rFonts w:asciiTheme="majorHAnsi" w:eastAsia="맑은 고딕" w:hAnsiTheme="majorHAnsi" w:cstheme="majorHAnsi" w:hint="eastAsia"/><w:color w:val="0000CC"/><w:sz w:val="18"/><w:szCs w:val="18"/><w:lang w:eastAsia="ko-KR"/></w:rPr>'
    $lines = $korean -split "`n"
    $lines[0] = "(" + $lines[0]
    $lines[$lines.Count-1] = $lines[$lines.Count-1] + ")"
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.Append('<w:p xmlns:w="' + $wns + '"><w:pPr><w:spacing w:beforeLines="20" w:before="72" w:afterLines="20" w:after="72" w:line="240" w:lineRule="exact"/><w:jc w:val="left"/>' + $rPr + '</w:pPr>')
    for ($i = 0; $i -lt $lines.Count; $i++) {
      if ($i -gt 0) { [void]$sb.Append('<w:r>' + $rPr + '<w:br/></w:r>') }
      [void]$sb.Append('<w:r>' + $rPr + '<w:t xml:space="preserve">' + (Esc $lines[$i]) + '</w:t></w:r>')
    }
    [void]$sb.Append('</w:p>')
    $frag = $doc.CreateDocumentFragment()
    $frag.InnerXml = $sb.ToString()
    $frag.FirstChild
  }

  $applied = 0
  $tblIdx = 0; $pIdx = 0
  foreach ($node in $body.ChildNodes) {
    if ($node.LocalName -eq "tbl") {
      $rows = $node.SelectNodes("./w:tr", $ns); $r = 0
      foreach ($row in $rows) {
        $cells = $row.SelectNodes("./w:tc", $ns); $c = 0
        foreach ($cell in $cells) {
          $id = "t$tblIdx.r$r.c$c"
          if ($trans.ContainsKey($id) -and $trans[$id].Trim()) {
            $p = New-TransParagraph $trans[$id]
            [void]$cell.AppendChild($p)
            $applied++
          }
          $c++
        }
        $r++
      }
      $tblIdx++
    }
    elseif ($node.LocalName -eq "p") {
      $id = "p$pIdx"
      if ($trans.ContainsKey($id) -and $trans[$id].Trim()) {
        $p = New-TransParagraph $trans[$id]
        [void]$body.InsertAfter($p, $node)
        $applied++
      }
      $pIdx++
    }
  }

  # write document.xml back into the zip entry (UTF-8, no BOM)
  $entry.Delete()
  $newEntry = $zip.CreateEntry("word/document.xml")
  $stream = $newEntry.Open()
  $writer = New-Object System.IO.StreamWriter($stream, (New-Object System.Text.UTF8Encoding($false)))
  $writer.Write($doc.OuterXml)
  $writer.Flush(); $writer.Close()

  Write-Output "Applied $applied translations -> $Out"
} finally {
  $zip.Dispose()
}

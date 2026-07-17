<#
  Replace the original Japanese text with Korean IN PLACE (same cells/paragraphs),
  keeping the original run formatting. Ids not in the JSON are left untouched.
  \t in a value -> <w:tab/>, \n -> paragraph break handling (first para keeps all lines via <w:br/>).
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
# "Malgun Gothic" in Korean, built from char codes to avoid encoding issues in PS 5.1
$malgun = [string]([char]0xB9D1) + [char]0xC740 + ' ' + [char]0xACE0 + [char]0xB515

$tjson = [System.IO.File]::ReadAllText($Translations, [System.Text.Encoding]::UTF8)
$tobj  = $tjson | ConvertFrom-Json
$trans = @{}
foreach ($p in $tobj.PSObject.Properties) { $trans[$p.Name] = [string]$p.Value }

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

  # Clone the rPr of the first run in the container (for formatting continuity),
  # then force eastAsia font to Malgun Gothic + ko-KR lang so Hangul renders cleanly.
  function Get-KoreanRPr($container) {
    $srcRPr = $container.SelectSingleNode(".//w:r/w:rPr", $ns)
    if ($srcRPr) { $rPrXml = $srcRPr.OuterXml } else { $rPrXml = '<w:rPr xmlns:w="' + $wns + '"></w:rPr>' }
    $frag = $doc.CreateDocumentFragment(); $frag.InnerXml = $rPrXml
    $rPr = $frag.FirstChild
    $fonts = $rPr.SelectSingleNode("./w:rFonts", $ns)
    if (-not $fonts) {
      $fonts = $doc.CreateElement("w", "rFonts", $wns)
      [void]$rPr.PrependChild($fonts)
    }
    $fonts.SetAttribute("eastAsia", $wns, $malgun) | Out-Null
    $fonts.SetAttribute("hint", $wns, "eastAsia") | Out-Null
    $lang = $rPr.SelectSingleNode("./w:lang", $ns)
    if (-not $lang) {
      $lang = $doc.CreateElement("w", "lang", $wns)
      [void]$rPr.AppendChild($lang)
    }
    $lang.SetAttribute("eastAsia", $wns, "ko-KR") | Out-Null
    $rPr
  }

  # Build runs for one text (handles \t and \n) using the given rPr XML string.
  function New-RunsXml([string]$text, [string]$rPrXml) {
    $sb = New-Object System.Text.StringBuilder
    $lines = $text -split "`n"
    for ($i = 0; $i -lt $lines.Count; $i++) {
      if ($i -gt 0) { [void]$sb.Append('<w:r>' + $rPrXml + '<w:br/></w:r>') }
      $parts = $lines[$i] -split "`t"
      for ($j = 0; $j -lt $parts.Count; $j++) {
        if ($j -gt 0) { [void]$sb.Append('<w:r>' + $rPrXml + '<w:tab/></w:r>') }
        if ($parts[$j] -ne '') {
          [void]$sb.Append('<w:r>' + $rPrXml + '<w:t xml:space="preserve">' + (Esc $parts[$j]) + '</w:t></w:r>')
        }
      }
    }
    $sb.ToString()
  }

  # Replace the text content of one paragraph with the Korean text.
  function Replace-ParagraphText($para, [string]$korean) {
    $rPr = Get-KoreanRPr $para
    $rPrXml = $rPr.OuterXml
    # remove all runs (keep pPr and anything else like bookmarks)
    $runs = @($para.SelectNodes("./w:r", $ns))
    foreach ($r in $runs) { [void]$para.RemoveChild($r) }
    $runsXml = New-RunsXml $korean $rPrXml
    if ($runsXml) {
      $frag = $doc.CreateDocumentFragment()
      $frag.InnerXml = '<w:p xmlns:w="' + $wns + '">' + $runsXml + '</w:p>'
      $newRuns = @($frag.FirstChild.ChildNodes)
      foreach ($nr in $newRuns) { [void]$para.AppendChild($doc.ImportNode($nr, $true)) }
    }
  }

  # Replace the text of a table cell: put full Korean text into the first paragraph,
  # remove the remaining paragraphs (extract joined them with \n already).
  function Replace-CellText($cell, [string]$korean) {
    $paras = @($cell.SelectNodes("./w:p", $ns))
    if ($paras.Count -eq 0) { return }
    Replace-ParagraphText $paras[0] $korean
    for ($i = 1; $i -lt $paras.Count; $i++) { [void]$cell.RemoveChild($paras[$i]) }
  }

  $applied = 0
  $tblIdx = 0; $pIdx = 0
  foreach ($node in @($body.ChildNodes)) {
    if ($node.LocalName -eq "tbl") {
      $rows = $node.SelectNodes("./w:tr", $ns); $r = 0
      foreach ($row in $rows) {
        $cells = $row.SelectNodes("./w:tc", $ns); $c = 0
        foreach ($cell in $cells) {
          $id = "t$tblIdx.r$r.c$c"
          if ($trans.ContainsKey($id) -and $trans[$id].Trim()) {
            Replace-CellText $cell $trans[$id]
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
        Replace-ParagraphText $node $trans[$id]
        $applied++
      }
      $pIdx++
    }
  }

  $entry.Delete()
  $newEntry = $zip.CreateEntry("word/document.xml")
  $stream = $newEntry.Open()
  $writer = New-Object System.IO.StreamWriter($stream, (New-Object System.Text.UTF8Encoding($false)))
  $writer.Write($doc.OuterXml)
  $writer.Flush(); $writer.Close()

  Write-Output "Replaced $applied units -> $Out"
} finally {
  $zip.Dispose()
}

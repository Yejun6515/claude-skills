<#
  Decrease the font size (w:sz / w:szCs) of the Korean runs (rFonts eastAsia = Malgun Gothic)
  in a docx by -Step half-points. Used to pull pagination back to the JP original.
#>
param(
  [Parameter(Mandatory=$true)][string]$Path,
  [int]$Step = 2
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression
$wns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
$malgun = [string]([char]0xB9D1) + [char]0xC740 + ' ' + [char]0xACE0 + [char]0xB515

$zip = [System.IO.Compression.ZipFile]::Open($Path, [System.IO.Compression.ZipArchiveMode]::Update)
try {
  $entry = $zip.GetEntry("word/document.xml")
  $sr = New-Object System.IO.StreamReader($entry.Open(), [System.Text.Encoding]::UTF8)
  $xmlText = $sr.ReadToEnd(); $sr.Close()
  [xml]$doc = $xmlText
  $ns = New-Object System.Xml.XmlNamespaceManager($doc.NameTable)
  $ns.AddNamespace("w", $wns)

  $changed = 0
  foreach ($rPr in $doc.SelectNodes("//w:r/w:rPr", $ns)) {
    $fonts = $rPr.SelectSingleNode("./w:rFonts", $ns)
    if (-not $fonts) { continue }
    if ($fonts.GetAttribute("eastAsia", $wns) -ne $malgun) { continue }
    foreach ($tag in @("sz","szCs")) {
      $el = $rPr.SelectSingleNode("./w:$tag", $ns)
      if (-not $el) {
        $el = $doc.CreateElement("w", $tag, $wns)
        $el.SetAttribute("val", $wns, "21") | Out-Null   # default 10.5pt if unspecified
        [void]$rPr.AppendChild($el)
      }
      $val = [int]$el.GetAttribute("val", $wns)
      $newVal = [Math]::Max(10, $val - $Step)             # floor 5pt
      $el.SetAttribute("val", $wns, [string]$newVal) | Out-Null
    }
    $changed++
  }

  $entry.Delete()
  $newEntry = $zip.CreateEntry("word/document.xml")
  $stream = $newEntry.Open()
  $writer = New-Object System.IO.StreamWriter($stream, (New-Object System.Text.UTF8Encoding($false)))
  $writer.Write($doc.OuterXml)
  $writer.Flush(); $writer.Close()
  Write-Output "Shrunk $changed Korean runs by $Step half-points"
} finally {
  $zip.Dispose()
}

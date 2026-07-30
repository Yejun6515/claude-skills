# china-entertainment-expense : case JSON -> 飲食費 xlsx + China Scorecard xls
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File fill_expense.ps1 `
#       -Case "<case.json>" -OutDir "<output folder>" [-Force] [-Preview]
#
# -Force   : re-copy blank masters over existing case files (default = fill in place if they exist)
# -Preview : also export sheets to PDF under <OutDir>\_preview\ for visual verification
#
# Case JSON must be UTF-8. Structure: see assets\case_example.json
param(
    [Parameter(Mandatory = $true)][string]$Case,
    [Parameter(Mandatory = $true)][string]$OutDir,
    [switch]$Force,
    [switch]$Preview
)

$ErrorActionPreference = 'Stop'
$assets = Join-Path (Split-Path $PSScriptRoot -Parent) 'assets'
$log = New-Object System.Collections.Generic.List[string]

$j = Get-Content -LiteralPath $Case -Raw -Encoding UTF8 | ConvertFrom-Json
$name = "" + $j.case_name
if (-not $name) { throw "case_name missing in $Case" }
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }

$mealPath = Join-Path $OutDir ("飲食費_" + $name + ".xlsx")
$scPath = Join-Path $OutDir ("Scorecard_China_" + $name + ".xls")
foreach ($pair in @(@($mealPath, "$assets\meal_master.xlsx"), @($scPath, "$assets\scorecard_china_master.xls"))) {
    if ($Force -or -not (Test-Path $pair[0])) {
        Copy-Item $pair[1] $pair[0] -Force        # cross-drive safe (never use os rename/Move)
        $log.Add("copied master -> " + (Split-Path $pair[0] -Leaf))
    } else {
        $log.Add("filling existing " + (Split-Path $pair[0] -Leaf) + " (use -Force to reset from master)")
    }
}

# --- COM value marshalling ---------------------------------------------------
# PS 5.1 quirk: values coming out of ConvertFrom-Json must be branched with
# `-is [string]` and re-materialised ("$v" / [double]$v). Casting with [string]$v
# or returning them from a function gives "Specified cast is not valid".
function Set-Cell($ws, $addr, $v) {
    if ($v -is [string]) {
        if ($v -match '^\d{4}-\d{2}-\d{2}$') { $ws.Range($addr).Value2 = [double]([datetime]$v).ToOADate() }
        else { $ws.Range($addr).Value2 = "$v" }
    } else {
        $ws.Range($addr).Value2 = [double]$v
    }
}

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false; $xl.DisplayAlerts = $false; $xl.AutomationSecurity = 3   # macros force-disabled

try {
    # ---------- 1. 飲食費（国税要件保存書類） ----------
    $wb = $xl.Workbooks.Open($mealPath)
    $ws = $wb.Worksheets.Item(1)

    if ($j.meal) {
        foreach ($p in $j.meal.PSObject.Properties) { Set-Cell $ws ("" + $p.Name) $p.Value; $log.Add("meal " + $p.Name) }
    }
    # participants block: C=会社名 / D=役職 / E=氏名, from row 7 (B and D57 are formulas)
    if ($j.attendees) {
        $r = 7
        foreach ($a in $j.attendees) {
            $ws.Range("C$r").Value2 = "" + $a.company
            $ws.Range("D$r").Value2 = "" + $a.title
            $ws.Range("E$r").Value2 = "" + $a.name
            $r++
        }
        $log.Add("meal attendees rows 7.." + ($r - 1))
    }
    $xl.Calculate()
    $log.Add("--- meal result ---")
    foreach ($a in @("I2", "I6", "I8", "I10", "K12", "D57", "K23", "K28", "K32", "K37", "K41", "K42", "K43", "K44", "K45")) {
        $log.Add("  $a = " + $ws.Range($a).Text)
    }
    foreach ($a in @("H27", "H28", "H36", "H37", "H44", "H45")) {
        $t = $ws.Range($a).Text
        if ($t) { $log.Add("  account $a = $t") }
    }
    foreach ($a in @("L6", "L8", "L10", "L12", "L23", "L32", "L41", "L43")) {
        $t = $ws.Range($a).Text
        if ($t) { $log.Add("  !! WARNING $a : $t") }
    }
    $wb.Save(); $wb.Close($false)

    # ---------- 2. China Scorecard ----------
    $wb2 = $xl.Workbooks.Open($scPath)
    $sc = $wb2.Worksheets.Item("China Scorecard")
    $pt = $wb2.Worksheets.Item("participants")

    if ($j.scorecard) {
        foreach ($p in $j.scorecard.PSObject.Properties) { Set-Cell $sc ("" + $p.Name) $p.Value; $log.Add("scorecard " + $p.Name) }
    }
    if ($j.participants) {
        $r = 5
        foreach ($row in $j.participants) {
            foreach ($p in $row.PSObject.Properties) { Set-Cell $pt (("" + $p.Name) + $r) $p.Value }
            $r++
        }
        $last = $r - 1
        if ($last -gt 5) {                      # inherit row-5 formatting (date/number formats, borders)
            $pt.Range("A5:S5").Copy() | Out-Null
            $pt.Range("A6:S$last").PasteSpecial(-4122) | Out-Null   # xlPasteFormats
            try { $xl.CutCopyMode = 0 } catch { }
        }
        $log.Add("participants rows 5..$last")
    }
    $xl.Calculate()
    $log.Add("--- scorecard result ---")
    foreach ($a in @("D6", "D7", "D8", "D9", "D10", "F26")) { $log.Add("  $a = " + $sc.Range($a).Text) }
    $cl = $wb2.Worksheets.Item("Calculation")
    $log.Add("  checkboxes(occasion a/b, gov, freq, spouse) = " + $cl.Range("F4").Text + "/" + $cl.Range("F5").Text + "/" + $cl.Range("F7").Text + "/" + $cl.Range("F8").Text + "/" + $cl.Range("F9").Text)
    $log.Add("  radios: value-band G11=" + $cl.Range("G11").Text + " host G13=" + $cl.Range("G13").Text + " recipient G15=" + $cl.Range("G15").Text)
    $log.Add("  TOTAL POINTS = " + $cl.Range("L17").Text + "  (<=16 : line manager signature only)")
    $wb2.Save(); $wb2.Close($false)

    # ---------- 3. preview ----------
    if ($Preview) {
        $pv = Join-Path $OutDir "_preview"
        if (-not (Test-Path $pv)) { New-Item -ItemType Directory -Force -Path $pv | Out-Null }
        $wb = $xl.Workbooks.Open($mealPath, 0, $true)
        $wb.Worksheets.Item(1).ExportAsFixedFormat(0, (Join-Path $pv "meal.pdf")); $wb.Close($false)
        $wb2 = $xl.Workbooks.Open($scPath, 0, $true)
        $wb2.Worksheets.Item("China Scorecard").ExportAsFixedFormat(0, (Join-Path $pv "scorecard.pdf"))
        $wb2.Worksheets.Item("participants").ExportAsFixedFormat(0, (Join-Path $pv "participants.pdf"))
        $wb2.Close($false)
        $log.Add("preview PDFs -> $pv")
    }
} finally {
    $xl.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
}

$log.Add("OUT: $mealPath")
$log.Add("OUT: $scPath")
$log -join "`n"

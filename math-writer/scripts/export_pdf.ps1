<#
.SYNOPSIS
    Export a built paper .docx to PDF using the installed Microsoft Word engine.

.DESCRIPTION
    The final submission is a PDF, so the .docx must round-trip through Word
    (only Word reproduces the pagination, the PAGE field in the footer, and the
    OMML equations exactly as the competition will see them).

    Opens the document read-only, updates fields so page numbers are current,
    then exports. The Word process is always released, even on failure.

.PARAMETER DocxPath
    Path to the .docx built by build_paper.py

.PARAMETER OutPath
    Optional PDF path. Defaults to the .docx path with a .pdf extension.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File export_pdf.ps1 -DocxPath paper/论文.docx
#>
param(
    [Parameter(Mandatory = $true)][string]$DocxPath,
    [string]$OutPath
)

$ErrorActionPreference = 'Stop'

$docx = (Resolve-Path -LiteralPath $DocxPath).Path
if (-not $OutPath) {
    $OutPath = [System.IO.Path]::ChangeExtension($docx, '.pdf')
}
$pdf = [System.IO.Path]::GetFullPath($OutPath)
$wdFormatPDF = 17

$outDir = Split-Path -Parent $pdf
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}
# Export to a temp file first so a failed export never destroys the last good PDF.
$tmp = "$pdf.tmp-$PID.pdf"

$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0

    # ReadOnly=$true so a stray lock never edits the source
    $doc = $word.Documents.Open($docx, $false, $true)

    # The TOC's page numbers depend on pagination, and inserting the TOC itself
    # changes pagination — so settle, update, re-settle, update again.
    $doc.Repaginate()
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() | Out-Null }
    $doc.Fields.Update() | Out-Null
    $doc.Repaginate()
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() | Out-Null }

    # footer PAGE fields
    foreach ($section in $doc.Sections) {
        foreach ($header in $section.Headers) { $header.Range.Fields.Update() | Out-Null }
        foreach ($footer in $section.Footers) { $footer.Range.Fields.Update() | Out-Null }
    }

    $doc.SaveAs2($tmp, $wdFormatPDF)
    if (Test-Path -LiteralPath $pdf) {
        Copy-Item -LiteralPath $pdf -Destination "$pdf.bak" -Force
    }
    Move-Item -LiteralPath $tmp -Destination $pdf -Force
    Write-Output "exported: $pdf"
}
finally {
    if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
    if ($doc) { $doc.Close($false) | Out-Null }
    if ($word) { $word.Quit() | Out-Null }
    foreach ($obj in @($doc, $word)) {
        if ($obj) {
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($obj)
        }
    }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}

if (-not (Test-Path -LiteralPath $pdf)) {
    Write-Error "PDF was not produced: $pdf"
    exit 1
}
exit 0

$ErrorActionPreference = 'Stop'
$gamePath = Join-Path $PSScriptRoot 'main.py'
$candidates = @()
foreach ($name in @('py', 'python', 'python3')) {
    $command = Get-Command $name -ErrorAction SilentlyContinue
    if ($command -and $command.Source -notlike '*\WindowsApps\*') {
        $candidates += $command.Source
    }
}
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $bundledPython) { $candidates += $bundledPython }
foreach ($candidate in $candidates) {
    & $candidate -c 'import sys, tkinter; assert sys.version_info >= (3, 10)' 2>$null
    if ($LASTEXITCODE -eq 0) {
        & $candidate $gamePath
        exit $LASTEXITCODE
    }
}
Write-Host 'Install Python 3.10 or newer with Tcl/Tk support, then run python main.py.'
Read-Host 'Press Enter to close'
exit 1

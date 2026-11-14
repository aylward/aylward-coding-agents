param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $CoordinatorArguments
)
$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path (Split-Path $PSScriptRoot) 'venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Existing MONAI-Physio venv was not found. Invoke coordinator.py with Python 3.11+.'
}
& $pythonPath (Join-Path $PSScriptRoot 'coordinator.py') @CoordinatorArguments
exit $LASTEXITCODE

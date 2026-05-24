#!/usr/bin/env pwsh
# Wrapper that finds the appropriate Python interpreter and runs a Python hook.
# Usage: run_python_hook.ps1 -ScriptPath <path/to/hook.py>
# stdin (JSON hook payload) is forwarded to the Python script.
#
# Resolution order:
#   1. .venv/Scripts/python.exe  (Windows hooks venv)
#   2. python3
#   3. python
#   4. exit 0 silently (Python unavailable — hook is skipped gracefully)

param(
    [Parameter(Mandatory = $true)]
    [string]$ScriptPath
)

$ErrorActionPreference = "Stop"

# Read stdin
$input_data = [Console]::In.ReadToEnd()

# Find Python interpreter
$python = $null
if (Test-Path ".venv/Scripts/python.exe") {
    $python = ".venv/Scripts/python.exe"
}
elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $python = "python3"
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $python = "python"
}

# If Python not found, exit gracefully
if ($null -eq $python) {
    exit 0
}

# Convert script path to module path from .claude/scripts root
$scriptsRoot = (Resolve-Path ".claude/scripts").Path
$scriptFullPath = (Resolve-Path $ScriptPath).Path
$relativePath = [System.IO.Path]::GetRelativePath($scriptsRoot, $scriptFullPath)
$modulePath = [System.IO.Path]::ChangeExtension($relativePath, $null)
$modulePath = $modulePath -replace "\\", "."
$modulePath = $modulePath -replace "/", "."

# Ensure recorder/formatter modules are importable
$pathSeparator = [System.IO.Path]::PathSeparator
if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) {
    $env:PYTHONPATH = $scriptsRoot
}
else {
    $env:PYTHONPATH = "$scriptsRoot$pathSeparator$($env:PYTHONPATH)"
}

# Run the Python hook module with stdin
$input_data | & $python -m $modulePath
exit $LASTEXITCODE

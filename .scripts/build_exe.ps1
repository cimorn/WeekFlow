$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$icoIcon = Join-Path $root "src\weekflow_logo.ico"

if (-not (Test-Path $icoIcon)) {
    throw "App icon not found at $icoIcon"
}

& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name WeekFlow `
    --icon $icoIcon `
    --add-data "src\weekflow_logo.ico;src" `
    run_app.py

$appDataDir = Join-Path $root "dist\WeekFlow\data"
New-Item -ItemType Directory -Force -Path $appDataDir | Out-Null

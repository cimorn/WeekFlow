$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$src = Join-Path $root "src\WeekFlow\electron_bridge.py"
$distPath = Join-Path $root "dist\bridge"
$workPath = Join-Path $root "build\electron-bridge"
$iconPath = Join-Path $root "src\weekflow_logo.ico"

if (-not (Test-Path $src)) {
    throw "Electron bridge entry not found at $src"
}

if (Test-Path $distPath) {
    Remove-Item -LiteralPath $distPath -Recurse -Force
}

$args = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--name", "WeekFlowBridge",
    "--distpath", $distPath,
    "--workpath", $workPath,
    "--specpath", $workPath,
    "--paths", (Join-Path $root "src")
)

if (Test-Path $iconPath) {
    $args += @("--icon", $iconPath)
}

$args += $src

& $python @args

$bridgeExe = Join-Path $distPath "WeekFlowBridge.exe"
if (-not (Test-Path $bridgeExe)) {
    throw "Electron bridge build did not create $bridgeExe"
}

if (Test-Path $workPath) {
    Remove-Item -LiteralPath $workPath -Recurse -Force
}

Write-Output $bridgeExe

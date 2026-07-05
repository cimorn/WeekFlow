$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$version = & $python ".\.scripts\read_version.py"
$distDir = Join-Path $root "dist"
$appDir = $distDir
$appExePath = Join-Path $appDir "WeekFlow.exe"
$folderModeDir = Join-Path $distDir "WeekFlow"
$folderModeExePath = Join-Path $folderModeDir "WeekFlow.exe"
$bundleDir = Join-Path $distDir "WeekFlow-$version-windows-x64"
$zipPath = Join-Path $distDir "WeekFlow-$version-windows-x64.zip"
$versionedExePath = Join-Path $bundleDir "WeekFlow-$version.exe"
$iconPath = Join-Path $root "src\weekflow_logo.ico"
$distResolved = (Resolve-Path $distDir).Path

if (-not (Test-Path $appExePath)) {
    if (Test-Path $folderModeExePath) {
        $appDir = $folderModeDir
        $appExePath = $folderModeExePath
    }
    else {
        throw "WeekFlow.exe not found in dist. Build the app first."
    }
}

if (-not (Test-Path $iconPath)) {
    throw "src\\weekflow_logo.ico not found. Build packaging requires the app icon."
}

if (Test-Path $bundleDir) {
    $bundleResolved = (Resolve-Path $bundleDir).Path
    if (-not $bundleResolved.StartsWith($distResolved)) {
        throw "Refusing to remove path outside dist: $bundleResolved"
    }
    Remove-Item -LiteralPath $bundleResolved -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $distDir | Out-Null
New-Item -ItemType Directory -Force -Path $bundleDir | Out-Null

Get-ChildItem -LiteralPath $appDir -Force | Where-Object {
    $_.FullName -ne $bundleDir -and
    $_.FullName -ne $zipPath -and
    $_.Name -notlike "WeekFlow-*-windows-x64*"
} | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $bundleDir -Recurse -Force
}
Rename-Item (Join-Path $bundleDir "WeekFlow.exe") "WeekFlow-$version.exe" -Force
New-Item -ItemType Directory -Force -Path (Join-Path $bundleDir "data") | Out-Null
Copy-Item ".\CHANGELOG.md" (Join-Path $bundleDir "CHANGELOG.md") -Force
Copy-Item ".\LICENSE" (Join-Path $bundleDir "LICENSE") -Force
Copy-Item ".\README.md" (Join-Path $bundleDir "README.md") -Force
Copy-Item $iconPath (Join-Path $bundleDir "weekflow_logo.ico") -Force

if (Test-Path $zipPath) {
    $zipResolved = (Resolve-Path $zipPath).Path
    if (-not $zipResolved.StartsWith($distResolved)) {
        throw "Refusing to remove path outside dist: $zipResolved"
    }
    Remove-Item -LiteralPath $zipResolved -Force
}

Compress-Archive -Path (Join-Path $bundleDir "*") -DestinationPath $zipPath -CompressionLevel Optimal
Write-Output $versionedExePath
Write-Output $zipPath
Write-Output (Join-Path $bundleDir "data")

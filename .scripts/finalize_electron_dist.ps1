$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$distDir = Join-Path $root "dist"
$sourceDir = Join-Path $root "dist-electron\win-unpacked"
$intermediateDir = Join-Path $root "dist-electron"
$packagePath = Join-Path $root "package.json"
$package = Get-Content -Raw $packagePath | ConvertFrom-Json
$version = [string] $package.version
if (-not $version) {
    throw "package.json version is required for packaging."
}
$versionedExeName = "WeekFlow-V$version.exe"
$versionedExePath = Join-Path $distDir $versionedExeName
$zipPath = Join-Path $distDir "WeekFlow-V$version.zip"

if (-not (Test-Path $sourceDir)) {
    throw "dist-electron\win-unpacked not found. Run electron-builder first."
}

New-Item -ItemType Directory -Force -Path $distDir | Out-Null
$distResolved = (Resolve-Path $distDir).Path
$sourceResolved = (Resolve-Path $sourceDir).Path

function Remove-InDist {
    param([string] $PathToRemove)

    if (-not (Test-Path $PathToRemove)) {
        return
    }
    $resolved = (Resolve-Path $PathToRemove).Path
    if (-not $resolved.StartsWith($distResolved)) {
        throw "Refusing to remove path outside dist: $resolved"
    }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}

Get-ChildItem -LiteralPath $distDir -Force | ForEach-Object {
    Remove-InDist $_.FullName
}

Copy-Item -Path (Join-Path $sourceResolved "*") -Destination $distDir -Recurse -Force
New-Item -ItemType Directory -Force -Path (Join-Path $distDir "data") | Out-Null

if (-not (Test-Path (Join-Path $distDir "WeekFlow.exe"))) {
    throw "Finalized app is missing WeekFlow.exe"
}

$iconPath = Join-Path $root "src\weekflow_logo.ico"
$rceditPath = Join-Path $root "node_modules\rcedit\bin\rcedit-x64.exe"
if (-not (Test-Path $rceditPath)) {
    $rceditPath = Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA "electron-builder\Cache\winCodeSign") -Recurse -Force -Filter "rcedit-x64.exe" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1 -ExpandProperty FullName
}
if (-not $rceditPath -or -not (Test-Path $rceditPath)) {
    throw "rcedit-x64.exe not found. Run pnpm install before packaging."
}
if (-not (Test-Path $iconPath)) {
    throw "App icon not found at $iconPath"
}
& $rceditPath (Join-Path $distDir "WeekFlow.exe") --set-icon $iconPath
if ($LASTEXITCODE -ne 0) {
    throw "rcedit failed with exit code $LASTEXITCODE"
}
Rename-Item (Join-Path $distDir "WeekFlow.exe") $versionedExeName -Force
if (-not (Test-Path $versionedExePath)) {
    throw "Finalized app is missing $versionedExeName"
}

$zipEntries = Get-ChildItem -LiteralPath $distDir -Force | Where-Object { $_.FullName -ne $zipPath }
Compress-Archive -Path $zipEntries.FullName -DestinationPath $zipPath -CompressionLevel Optimal

$intermediateResolved = (Resolve-Path $intermediateDir).Path
$rootResolved = (Resolve-Path $root).Path
if (-not $intermediateResolved.StartsWith($rootResolved)) {
    throw "Refusing to remove path outside project: $intermediateResolved"
}
Remove-Item -LiteralPath $intermediateResolved -Recurse -Force

Write-Output $versionedExePath
Write-Output $distDir
Write-Output $zipPath

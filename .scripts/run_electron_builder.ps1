$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$node = $env:WEEKFLOW_NODE
if (-not $node -or -not (Test-Path $node)) {
    $nodeCommand = Get-Command node -ErrorAction SilentlyContinue
    if ($nodeCommand) {
        $node = $nodeCommand.Source
    }
}

if (-not $node -or -not (Test-Path $node)) {
    $bundledNode = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
    if (Test-Path $bundledNode) {
        $node = $bundledNode
    }
}

if (-not $node -or -not (Test-Path $node)) {
    throw "Node.js was not found. Install Node.js, or set WEEKFLOW_NODE to node.exe."
}

$builder = Join-Path $root "node_modules\electron-builder\cli.js"
if (-not (Test-Path $builder)) {
    throw "electron-builder was not found. Run pnpm install first."
}

& $node $builder @args

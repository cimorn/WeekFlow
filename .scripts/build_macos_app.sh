#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="$ROOT/.venv/bin/python"
ICO_ICON="$ROOT/src/weekflow_logo.ico"
ICNS_ICON="$ROOT/src/weekflow_logo.icns"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Project virtual environment not found. Create .venv and install dependencies first." >&2
  exit 1
fi

if [[ ! -f "$ICO_ICON" ]]; then
  echo "App icon not found at $ICO_ICON" >&2
  exit 1
fi

"$PYTHON_BIN" "$ROOT/.scripts/export_app_icon.py" "$ICO_ICON" "$ICNS_ICON"

"$PYTHON_BIN" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name WeekFlow \
  --icon "$ICNS_ICON" \
  --add-data "src/weekflow_logo.ico:src" \
  --osx-bundle-identifier "com.cimorn.weekflow" \
  run_app.py

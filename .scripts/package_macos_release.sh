#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="$ROOT/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Project virtual environment not found. Create .venv and install dependencies first." >&2
  exit 1
fi

VERSION="$("$PYTHON_BIN" "$ROOT/.scripts/read_version.py")"
ARCH="$(uname -m)"
ICON_PATH="$ROOT/src/weekflow_logo.ico"

case "$ARCH" in
  x86_64)
    ARCH_LABEL="x64"
    ;;
  arm64)
    ARCH_LABEL="arm64"
    ;;
  *)
    ARCH_LABEL="$ARCH"
    ;;
esac

APP_DIR="$ROOT/dist"
BUNDLE_DIR="$APP_DIR/WeekFlow-$VERSION-macos-$ARCH_LABEL"
ZIP_PATH="$APP_DIR/WeekFlow-$VERSION-macos-$ARCH_LABEL.zip"

if [[ ! -d "$ROOT/dist/WeekFlow.app" ]]; then
  echo "dist/WeekFlow.app not found. Build the macOS app first." >&2
  exit 1
fi

if [[ ! -f "$ICON_PATH" ]]; then
  echo "src/weekflow_logo.ico not found. Release packaging requires the app icon." >&2
  exit 1
fi

rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"

cp -R "$ROOT/dist/WeekFlow.app" "$BUNDLE_DIR/WeekFlow.app"
cp "$ROOT/CHANGELOG.md" "$BUNDLE_DIR/CHANGELOG.md"
cp "$ROOT/LICENSE" "$BUNDLE_DIR/LICENSE"
cp "$ROOT/README.md" "$BUNDLE_DIR/README.md"
cp "$ICON_PATH" "$BUNDLE_DIR/weekflow_logo.ico"

rm -f "$ZIP_PATH"
ditto -c -k --sequesterRsrc --keepParent "$BUNDLE_DIR" "$ZIP_PATH"

printf '%s\n' "$ZIP_PATH"

# Changelog

## Unreleased

- Updated the README files and screenshots to match the current Electron app.
- Removed the stale PySide/macOS release planning document.

## 26.07.04

- Rebuilt the desktop app with Electron.
- Changed packaged data storage to `data/<name>/<name>.json`, `data/<name>/<name>.md`, and `data/<name>/figs/`.
- Added the start screen for opening existing `data` files or creating new reports.
- Added standalone preview, data backup export, and single-instance startup behavior.
- Reworked the project progress page into separate project views.
- Simplified AI setup to OpenAI-compatible fields and kept AI actions inside the relevant pages.
- Updated the Windows package output to publish `dist/WeekFlow-V26.07.04.zip` instead of a standalone exe.
- Updated GitHub release automation to build and publish the Electron package from `main` and tags.

## 26.03.21

- First public release.
- Added the PySide6 editor for section-based weekly report editing.
- Added JSON and Markdown export.
- Added project records, preview themes, and AI polishing.

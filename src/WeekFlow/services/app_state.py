from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class AppStateStore:
    def __init__(self, state_file: Path | None = None) -> None:
        self.state_file = state_file or self._default_state_file()

    def get_last_report_path(self) -> Path | None:
        raw_path = str(self._read_payload().get("last_report_path", "")).strip()
        if not raw_path:
            return None
        path = Path(raw_path)
        return path if path.exists() else None

    def get_last_opened_text(self) -> str:
        if self.get_last_report_path() is None:
            return ""
        return str(self._read_payload().get("last_opened_text", "")).strip()

    def set_last_report_path(self, report_path: Path | None, opened_text: str | None = None) -> None:
        payload = self._read_payload()
        payload["last_report_path"] = str(Path(report_path).resolve()) if report_path else ""
        payload["last_opened_text"] = (
            opened_text.strip() if opened_text and opened_text.strip() else datetime.now().strftime("%Y-%m-%d %H:%M")
        ) if report_path else ""
        self._write_payload(payload)

    def _read_payload(self) -> dict[str, Any]:
        if not self.state_file.exists():
            return {}
        try:
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_payload(self, payload: dict[str, Any]) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _default_state_file(self) -> Path:
        return Path.home() / ".weekflow" / "app-state.json"

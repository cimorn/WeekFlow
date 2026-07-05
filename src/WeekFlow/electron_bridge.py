from __future__ import annotations

import json
import sys
import traceback
import zipfile
from pathlib import Path
from typing import Any

from WeekFlow.controllers.editor_controller import EditorController
from WeekFlow.models.report import WeeklyReport
from WeekFlow.services.ai import AIConfigError, AIService
from WeekFlow.services.preview import build_preview_document
from WeekFlow.services.renderer import render_title
from WeekFlow.services.versioning import base_pair_paths, next_version_stem


class ElectronBridgeSession:
    def __init__(
        self,
        default_directory: Path | str | None = None,
        ai_service: AIService | None = None,
    ) -> None:
        self.default_directory = Path(default_directory or Path.cwd())
        self._ensure_data_tree()
        self.controller = EditorController(default_directory=self.default_directory)
        self.ai_service = ai_service or AIService()

    def handle(self, message: dict[str, Any]) -> dict[str, Any]:
        try:
            command = str(message.get("type", ""))
            payload = message.get("payload", {})
            if not isinstance(payload, dict):
                raise ValueError("Bridge payload must be an object")
            return {"ok": True, "state": self._dispatch(command, payload)}
        except Exception as exc:
            return {
                "ok": False,
                "error": {
                    "message": str(exc),
                    "type": exc.__class__.__name__,
                    "traceback": traceback.format_exc(),
                },
            }

    def _dispatch(self, command: str, payload: dict[str, Any]) -> dict[str, Any]:
        if command == "createReport":
            self.controller.create_new_report(
                report_id=str(payload.get("report_id", "")).strip(),
                cycle=str(payload.get("cycle", "")).strip(),
                topic=str(payload.get("topic", "")).strip(),
            )
            stem = _safe_stem(str(payload.get("stem", "")).strip())
            if stem:
                self.controller.current_stem = stem
            return self._state()

        if command == "listReports":
            return self._state()

        if command == "exportDataBackup":
            backup_path = self._export_data_backup(Path(str(payload.get("path", ""))).expanduser())
            state = self._state()
            state["backup_path"] = str(backup_path)
            return state

        if command == "openReport":
            path = Path(str(payload.get("path", ""))).expanduser()
            self.controller.load_from_json(path)
            self._bind_controller_to_app_directory()
            return self._state()

        if command == "replaceReport":
            self.controller.report = WeeklyReport.from_dict(dict(payload.get("report", {})))
            self.controller.mark_dirty()
            return self._state()

        if command == "saveCurrent":
            self._ensure_report_id()
            self._bind_controller_to_app_directory()
            self.controller.save_current()
            return self._state()

        if command == "saveAsNamed":
            self._ensure_report_id()
            self._bind_controller_to_app_directory()
            stem = str(payload.get("stem", "")).strip()
            if not stem:
                stem = next_version_stem(self.default_directory, self.controller.report.report_id)
            stem = _safe_stem(stem, required=True)
            self.controller.save_as_named_version(stem)
            return self._state()

        if command == "render":
            return self._state()

        if command == "polish":
            section_key = str(payload.get("section_key", "preview"))
            project_index = payload.get("project_index")
            project_index = int(project_index) if project_index is not None else None
            self.ai_service.polish_current_section(
                self.controller.report,
                section_key=section_key,
                project_index=project_index,
            )
            self.controller.mark_dirty()
            return self._state()

        if command == "testAi":
            message = self.ai_service.test_connection(self.controller.report)
            state = self._state()
            state["ai_test_message"] = message
            return state

        if command == "importProjectImage":
            project_index = int(payload.get("project_index", -1))
            source_path = Path(str(payload.get("source_path", "")))
            self._bind_controller_to_app_directory()
            self.controller.import_project_result_image(project_index, source_path)
            return self._state()

        if command == "removeProjectImage":
            project_index = int(payload.get("project_index", -1))
            relative_path = str(payload.get("relative_path", ""))
            self.controller.remove_project_result_image(project_index, relative_path)
            return self._state()

        raise ValueError(f"Unsupported bridge command: {command}")

    def _state(self) -> dict[str, Any]:
        report = self.controller.report
        markdown = self.controller.render_markdown()
        return {
            "report": report.to_dict(),
            "title": render_title(report.report_id),
            "markdown": markdown,
            "preview_html": build_preview_document(
                report,
                section_key="preview",
                theme_key=report.preview_theme,
            ),
            "is_dirty": self.controller.is_dirty,
            "default_directory": str(self.default_directory),
            "current_json_path": _path_or_none(self.controller.current_json_path),
            "current_markdown_path": _path_or_none(self.controller.current_markdown_path),
            "current_stem": self.controller.current_stem,
            "available_reports": self._list_reports(),
        }

    def _ensure_report_id(self) -> None:
        if not self.controller.report.report_id.strip():
            raise ValueError("Report id is required before saving")

    def _ensure_data_tree(self) -> None:
        self.default_directory.mkdir(parents=True, exist_ok=True)
        (self.default_directory / "data").mkdir(parents=True, exist_ok=True)

    def _bind_controller_to_app_directory(self) -> None:
        self._ensure_data_tree()
        self.controller.default_directory = self.default_directory
        if self.controller.current_stem:
            json_path, markdown_path = base_pair_paths(
                self.default_directory,
                self.controller.current_stem,
            )
            self.controller.current_json_path = json_path
            self.controller.current_markdown_path = markdown_path

    def _list_reports(self) -> list[dict[str, Any]]:
        self._ensure_data_tree()
        reports: list[dict[str, Any]] = []
        data_dir = self.default_directory / "data"
        json_paths = list(data_dir.glob("*.json")) + list(data_dir.glob("*/*.json"))
        for json_path in sorted(json_paths, key=lambda path: path.stem.lower()):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
                report = WeeklyReport.from_dict(payload)
            except Exception:
                report = WeeklyReport()
            reports.append(
                {
                    "stem": json_path.stem,
                    "name": json_path.name,
                    "path": str(json_path),
                    "report_id": report.report_id,
                    "topic": report.topic,
                    "modified_time": json_path.stat().st_mtime,
                }
            )
        return reports

    def _export_data_backup(self, backup_path: Path) -> Path:
        self._ensure_data_tree()
        if not str(backup_path).strip():
            raise ValueError("Backup path is required")
        if backup_path.suffix.lower() != ".zip":
            backup_path = backup_path.with_suffix(".zip")
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        data_dir = self.default_directory / "data"
        backup_resolved = backup_path.resolve()
        with zipfile.ZipFile(backup_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(data_dir, "data/")
            for path in sorted(data_dir.rglob("*")):
                if path.resolve() == backup_resolved:
                    continue
                archive.write(path, path.relative_to(self.default_directory).as_posix())
        return backup_path


def _safe_stem(raw: str, required: bool = False) -> str:
    stem = raw.strip()
    if not stem:
        if required:
            raise ValueError("File name is required")
        return ""
    invalid_chars = '<>:"/\\|?*'
    safe = "".join("-" if char in invalid_chars else char for char in stem).strip(" .")
    if not safe:
        raise ValueError("File name is invalid")
    return safe


def _path_or_none(path: Path | None) -> str | None:
    return str(path) if path is not None else None


def _force_utf8_stdio() -> None:
    for stream_name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def run_jsonl_bridge(default_directory: Path | None = None) -> int:
    _force_utf8_stdio()
    session = ElectronBridgeSession(default_directory=default_directory)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            response = {
                "ok": False,
                "error": {
                    "message": f"Invalid JSON bridge message: {exc}",
                    "type": "JSONDecodeError",
                },
            }
        else:
            response = session.handle(message)
        print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    default_directory = Path(args[0]) if args else Path.cwd()
    try:
        return run_jsonl_bridge(default_directory)
    except AIConfigError as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": {"message": str(exc), "type": exc.__class__.__name__},
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

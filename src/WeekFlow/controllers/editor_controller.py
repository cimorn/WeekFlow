from __future__ import annotations

from pathlib import Path

from WeekFlow.models.report import WeeklyReport
from WeekFlow.services.project_assets import import_result_image
from WeekFlow.services.renderer import render_markdown
from WeekFlow.services.storage import ReportStorage
from WeekFlow.services.templates import build_report_template


class EditorController:
    def __init__(self, default_directory: Path, storage: ReportStorage | None = None) -> None:
        self.default_directory = Path(default_directory)
        self.storage = storage or ReportStorage()
        self.report = WeeklyReport()
        self.current_json_path: Path | None = None
        self.current_markdown_path: Path | None = None
        self.current_stem: str | None = None
        self.is_dirty = False

    def create_new_report(self, report_id: str, cycle: str = "", topic: str = "") -> WeeklyReport:
        self.report = build_report_template(report_id=report_id, cycle=cycle, topic=topic)
        self.current_json_path = None
        self.current_markdown_path = None
        self.current_stem = report_id
        self.is_dirty = True
        return self.report

    def load_from_json(self, json_path: Path) -> WeeklyReport:
        json_path = Path(json_path)
        self.report = self.storage.load_report(json_path)
        self.default_directory = _report_root_from_json_path(json_path)
        self.current_json_path = json_path
        stem = _stem_from_json_path(json_path)
        self.current_stem = stem
        self.current_markdown_path = self.default_directory / f"{stem}.md"
        self.is_dirty = False
        return self.report

    def render_markdown(self) -> str:
        return render_markdown(self.report)

    def save_current(self) -> tuple[Path, Path]:
        stem = self.current_stem or self.report.report_id
        json_path, markdown_path = self.storage.save_report_pair(
            report=self.report,
            directory=self.default_directory,
            stem=stem,
            markdown=self.render_markdown(),
        )
        self.current_stem = stem
        self.current_json_path = json_path
        self.current_markdown_path = markdown_path
        self.is_dirty = False
        return json_path, markdown_path

    def save_as_new_version(self) -> tuple[Path, Path]:
        base_stem = self.report.report_id
        json_path, markdown_path = self.storage.save_report_as_new_version(
            report=self.report,
            directory=self.default_directory,
            base_stem=base_stem,
            markdown=self.render_markdown(),
        )
        self.current_json_path = json_path
        self.current_markdown_path = markdown_path
        self.current_stem = _stem_from_json_path(json_path)
        self.is_dirty = False
        return json_path, markdown_path

    def save_as_named_version(self, stem: str) -> tuple[Path, Path]:
        safe_stem = stem.strip()
        if not safe_stem:
            raise ValueError("stem must not be empty")
        json_path, markdown_path = self.storage.save_report_pair(
            report=self.report,
            directory=self.default_directory,
            stem=safe_stem,
            markdown=self.render_markdown(),
        )
        self.current_json_path = json_path
        self.current_markdown_path = markdown_path
        self.current_stem = safe_stem
        self.is_dirty = False
        return json_path, markdown_path

    def mark_dirty(self) -> None:
        self.is_dirty = True

    def report_root_directory(self) -> Path | None:
        if self.current_markdown_path is not None:
            return self.current_markdown_path.parent
        if self.current_json_path is not None:
            return _report_root_from_json_path(self.current_json_path)
        return None

    def import_project_result_image(self, project_index: int, source_path: Path) -> str:
        if self.current_stem is None or self.current_json_path is None or not self.current_json_path.exists():
            raise ValueError("report must be saved before importing result images")
        project = self.report.projects[project_index]
        relative_path = import_result_image(source_path, self.default_directory, self.current_stem or self.report.report_id or "report")
        project.result_images.append(relative_path)
        self.mark_dirty()
        return relative_path

    def remove_project_result_image(self, project_index: int, relative_path: str) -> None:
        project = self.report.projects[project_index]
        project.result_images = [path for path in project.result_images if path != relative_path]
        self.mark_dirty()


def _stem_from_json_path(json_path: Path) -> str:
    suffix = ".json"
    name = json_path.name
    legacy_suffix = ".data.json"
    if name.endswith(legacy_suffix):
        return name[: -len(legacy_suffix)]
    return name[: -len(suffix)] if name.endswith(suffix) else json_path.stem


def _report_root_from_json_path(json_path: Path) -> Path:
    if json_path.parent.parent.name == "data":
        return json_path.parent.parent.parent
    if json_path.parent.name == "data":
        return json_path.parent.parent
    return json_path.parent

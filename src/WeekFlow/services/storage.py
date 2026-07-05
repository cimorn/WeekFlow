from __future__ import annotations

import json
from pathlib import Path

from WeekFlow.models.report import WeeklyReport
from WeekFlow.services.versioning import base_pair_paths, next_version_stem


class ReportStorage:
    def load_report(self, json_path: Path) -> WeeklyReport:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        return WeeklyReport.from_dict(payload)

    def save_report_pair(
        self,
        report: WeeklyReport,
        directory: Path,
        stem: str,
        markdown: str,
    ) -> tuple[Path, Path]:
        json_path, markdown_path = base_pair_paths(directory, stem)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        (json_path.parent / "figs").mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        markdown_path.write_text(markdown, encoding="utf-8")
        return json_path, markdown_path

    def save_report_as_new_version(
        self,
        report: WeeklyReport,
        directory: Path,
        base_stem: str,
        markdown: str,
    ) -> tuple[Path, Path]:
        stem = next_version_stem(directory, base_stem)
        return self.save_report_pair(
            report=report,
            directory=directory,
            stem=stem,
            markdown=markdown,
        )

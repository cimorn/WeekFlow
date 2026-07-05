from pathlib import Path

from WeekFlow.models.report import WeeklyReport
from WeekFlow.services.storage import ReportStorage
from WeekFlow.services.versioning import base_pair_paths


def test_base_pair_paths_place_json_under_data(tmp_path: Path):
    json_path, markdown_path = base_pair_paths(tmp_path, "2611")

    assert markdown_path == tmp_path / "data" / "2611" / "2611.md"
    assert json_path == tmp_path / "data" / "2611" / "2611.json"


def test_save_report_pair_creates_json_and_markdown(tmp_path: Path):
    storage = ReportStorage()
    report = WeeklyReport(report_id="2611")

    json_path, markdown_path = storage.save_report_pair(
        report=report,
        directory=tmp_path,
        stem="2611",
        markdown="# 第 11 周周报\n",
    )

    assert json_path.exists()
    assert markdown_path.exists()
    assert json_path.name == "2611.json"
    assert markdown_path.name == "2611.md"
    assert json_path.parent == tmp_path / "data" / "2611"
    assert (tmp_path / "data" / "2611" / "figs").is_dir()


def test_load_report_restores_saved_json_content(tmp_path: Path):
    storage = ReportStorage()
    report = WeeklyReport(report_id="2611", topic="离线 RL 实验跟踪")

    json_path, _ = storage.save_report_pair(
        report=report,
        directory=tmp_path,
        stem="2611",
        markdown="# 第 11 周周报\n",
    )

    loaded = storage.load_report(json_path)

    assert loaded.report_id == "2611"
    assert loaded.topic == "离线 RL 实验跟踪"


def test_save_report_as_new_version_creates_versioned_pair(tmp_path: Path):
    storage = ReportStorage()
    report = WeeklyReport(report_id="2611")

    storage.save_report_pair(
        report=report,
        directory=tmp_path,
        stem="2611",
        markdown="# 第 11 周周报\n",
    )

    json_path, markdown_path = storage.save_report_as_new_version(
        report=report,
        directory=tmp_path,
        base_stem="2611",
        markdown="# 第 11 周周报\n",
    )

    assert json_path.name == "2611-v2.json"
    assert markdown_path.name == "2611-v2.md"

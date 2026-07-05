import json
from pathlib import Path

import pytest

from WeekFlow.controllers.editor_controller import EditorController
from WeekFlow.models.report import WeeklyReport


def test_new_report_state_creation_uses_requested_identity(tmp_path: Path):
    controller = EditorController(default_directory=tmp_path)

    controller.create_new_report(
        report_id="2611",
        cycle="2026.03.12 - 2026.03.18",
        topic="Community activity prep",
    )

    assert controller.report.report_id == "2611"
    assert controller.report.cycle == "2026.03.12 - 2026.03.18"
    assert controller.current_json_path is None
    assert controller.current_markdown_path is None
    assert controller.report.one_line_summary == ""
    assert controller.report.achievements == []
    assert len(controller.report.projects) == 1
    assert controller.report.projects[0].name == ""
    assert controller.report.projects[0].records == []
    assert controller.report.ai["provider"] == "openai_compatible"
    assert controller.is_dirty is True


def test_load_existing_json_updates_controller_state(tmp_path: Path):
    controller = EditorController(default_directory=tmp_path)
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    payload = WeeklyReport(report_id="2611", topic="Community activity prep")
    json_path = data_dir / "2611.json"
    json_path.write_text(
        json.dumps(payload.to_dict(), ensure_ascii=False),
        encoding="utf-8",
    )

    controller.load_from_json(json_path)

    assert controller.report.report_id == payload.report_id
    assert controller.report.topic == payload.topic
    assert controller.current_json_path == json_path
    assert controller.current_markdown_path == tmp_path / "2611.md"
    assert controller.is_dirty is False


def test_save_current_pair_updates_current_paths(tmp_path: Path):
    controller = EditorController(default_directory=tmp_path)
    controller.create_new_report(report_id="2611")

    json_path, markdown_path = controller.save_current()

    assert json_path == tmp_path / "data" / "2611" / "2611.json"
    assert markdown_path == tmp_path / "data" / "2611" / "2611.md"
    assert (tmp_path / "data" / "2611" / "figs").is_dir()
    assert controller.current_json_path == json_path
    assert controller.current_markdown_path == markdown_path
    assert controller.is_dirty is False


def test_save_as_named_version_uses_custom_stem(tmp_path: Path):
    controller = EditorController(default_directory=tmp_path)
    controller.create_new_report(report_id="2611", topic="Community activity prep")

    json_path, markdown_path = controller.save_as_named_version("2611-lab-note")

    assert json_path == tmp_path / "data" / "2611-lab-note" / "2611-lab-note.json"
    assert markdown_path == tmp_path / "data" / "2611-lab-note" / "2611-lab-note.md"
    assert controller.current_json_path == json_path
    assert controller.current_markdown_path == markdown_path
    assert controller.current_stem == "2611-lab-note"


def test_controller_requires_saved_report_directory_before_importing_result_image(tmp_path: Path):
    controller = EditorController(default_directory=tmp_path)
    controller.create_new_report("2611")
    source = tmp_path / "demo.png"
    source.write_bytes(b"png")

    with pytest.raises(ValueError):
        controller.import_project_result_image(0, source)

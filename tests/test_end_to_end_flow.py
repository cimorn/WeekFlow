from pathlib import Path

from WeekFlow.controllers.editor_controller import EditorController
from WeekFlow.models.report import ProjectItem, RecordItem, TodoItem


def test_end_to_end_save_reload_and_new_version_flow(tmp_path: Path):
    controller = EditorController(default_directory=tmp_path)
    controller.create_new_report(
        report_id="2611",
        cycle="2026.03.12 - 2026.03.18",
        topic="Community activity prep",
    )
    controller.report.overview = {
        "mainline": "Confirm venue arrangement\nSync sign-up progress",
        "mainlines": ["Confirm venue arrangement", "Sync sign-up progress"],
        "judgment": "Current preparation is now trackable.",
        "focus": "Keep filling supplies and onsite reminders.",
    }
    controller.report.projects = [
        ProjectItem(
            name="Venue setup",
            summary="Finished the first onsite review",
            issue="Still need to confirm the final seat count.",
            next_step="Keep filling sign boards and check-in materials.",
            result_images=["figs/result-001.png"],
            records=[
                RecordItem(
                    time="260318-1251",
                    change="Checked room layout and seat count",
                    result="The onsite arrangement is clearer now",
                )
            ],
        )
    ]
    controller.report.achievements = ["Organized supplies and volunteer assignments."]
    controller.report.todos = [TodoItem(done=False, text="Keep confirming the final registration count.")]
    controller.report.feeling = "The overall pace feels smoother than last week."

    json_path, markdown_path = controller.save_current()

    reloaded = EditorController(default_directory=tmp_path)
    reloaded.load_from_json(json_path)
    json_v2, markdown_v2 = reloaded.save_as_new_version()
    markdown_text = markdown_path.read_text(encoding="utf-8")

    assert json_path == tmp_path / "data" / "2611" / "2611.json"
    assert markdown_path == tmp_path / "data" / "2611" / "2611.md"
    assert reloaded.report.report_id == "2611"
    assert reloaded.report.projects[0].result_images == ["figs/result-001.png"]
    assert json_v2 == tmp_path / "data" / "2611-v2" / "2611-v2.json"
    assert markdown_v2 == tmp_path / "data" / "2611-v2" / "2611-v2.md"
    assert "# Week 11" in markdown_text
    assert "## 本周成果" in markdown_text
    assert "## 项目进展" in markdown_text
    assert "#### 结果" in markdown_text
    assert "![结果图 1](figs/result-001.png)" in markdown_text
    assert "## 待跟进事项" in markdown_text

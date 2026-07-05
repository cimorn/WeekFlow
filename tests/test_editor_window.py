import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QWidget,
)

from WeekFlow.controllers.editor_controller import EditorController
from WeekFlow.main import AppCoordinator, default_report_directory
from WeekFlow.ui.editor_window import EditorWindow
from WeekFlow.ui.theme import APP_STYLESHEET
from WeekFlow.ui.widgets.report_preview_panel import ReportPreviewPanel


def _build_window(tmp_path: Path) -> EditorWindow:
    app = QApplication.instance() or QApplication([])
    app.setStyleSheet(APP_STYLESHEET)
    controller = EditorController(default_directory=tmp_path)
    controller.create_new_report(report_id="2611", topic="中文演示项目")
    window = EditorWindow(controller)
    QApplication.processEvents()
    return window


def test_editor_window_does_not_show_generate_report_button(tmp_path: Path):
    window = _build_window(tmp_path)

    button_texts = [button.text() for button in window.findChildren(QPushButton)]

    assert "生成周报" not in button_texts

    window.close()


def test_editor_window_status_row_shows_only_rendered_title(tmp_path: Path):
    window = _build_window(tmp_path)

    assert window.report_label.text() == "Week 11"
    assert window.path_label.text() == ""
    assert window.status_label.text() == ""
    assert window.path_label.parent() is None
    assert window.status_label.parent() is None

    window.close()


def test_editor_window_does_not_show_section_title_block(tmp_path: Path):
    window = _build_window(tmp_path)
    window._set_section(2)
    window.show()
    QApplication.processEvents()

    assert window.section_title_label.text() == ""
    assert window.section_hint_label.text() == ""
    assert window.section_title_label.parent() is None
    assert window.section_hint_label.parent() is None

    window.close()


def test_editor_window_can_center_on_screen(tmp_path: Path):
    app = QApplication.instance() or QApplication([])
    window = _build_window(tmp_path)
    window.show()
    QApplication.processEvents()

    window.center_on_screen()
    QApplication.processEvents()

    screen = window.screen() or app.primaryScreen()
    screen_center = screen.availableGeometry().center()
    window_center = window.frameGeometry().center()

    assert abs(window_center.x() - screen_center.x()) <= 4
    assert abs(window_center.y() - screen_center.y()) <= 4

    window.close()


def test_editor_window_initial_size_fits_available_screen(tmp_path: Path):
    app = QApplication.instance() or QApplication([])
    window = _build_window(tmp_path)
    window.show()
    QApplication.processEvents()

    screen = window.screen() or app.primaryScreen()
    available = screen.availableGeometry()
    frame = window.frameGeometry()

    assert frame.width() <= available.width()
    assert frame.height() <= available.height()
    assert window.height() >= min(860, int(available.height() * 0.98))
    window.close()


def test_editor_window_keeps_global_actions_in_top_navigation(tmp_path: Path):
    window = _build_window(tmp_path)
    window.show()
    QApplication.processEvents()

    action_rail = window.findChild(QWidget, "EditorActionRail")
    top_actions = window.findChild(QWidget, "TopActionBar")
    section_scroll = window.findChild(QScrollArea, "EditorSectionScroll")

    assert action_rail is None
    assert top_actions is not None
    assert section_scroll is not None
    assert window.findChild(QPushButton, "SaveReportButton") is not None
    assert window.findChild(QPushButton, "SaveAsVersionButton") is not None
    assert window.findChild(QPushButton, "PolishCurrentPageButton") is not None
    assert window.findChild(QPushButton, "OpenPreviewWindowButton") is not None
    for index in range(len(window.sections)):
        window._set_section(index)
        QApplication.processEvents()
        assert top_actions.parent() is window.findChild(QWidget, "TopNavBar")
        assert section_scroll.width() > int(window.width() * 0.82)

    window.close()


def test_editor_window_workspace_uses_single_editor_surface_without_inline_preview(tmp_path: Path):
    window = _build_window(tmp_path)
    window.show()
    QApplication.processEvents()

    assert window.findChild(QSplitter, "WorkspaceSplitter") is None
    assert not window.findChildren(ReportPreviewPanel)
    assert window.findChild(QPushButton, "OpenPreviewWindowButton") is not None
    window.close()


def test_editor_window_uses_top_navigation_instead_of_left_rail(tmp_path: Path):
    window = _build_window(tmp_path)

    rail = window.findChild(QWidget, "NavRail")
    top_nav = window.findChild(QWidget, "TopSectionNav")

    assert rail is None
    assert top_nav is not None
    button_texts = [button.text() for button in top_nav.findChildren(QPushButton)]
    assert button_texts == ["基本信息", "本周成果", "项目进展", "待跟进事项", "预览"]
    window.close()


def test_editor_window_combines_ai_with_basic_and_feeling_with_results(tmp_path: Path):
    window = _build_window(tmp_path)

    assert len(window.sections) == 5
    assert window.ai_config_section.parent() is not None
    assert window.feeling_section.parent() is not None
    assert window.ai_config_section.parent() is not window.stack
    assert window.feeling_section.parent() is not window.stack

    window.close()


def test_basic_info_and_ai_config_are_split_into_two_columns(tmp_path: Path):
    window = _build_window(tmp_path)
    window.show()
    QApplication.processEvents()

    page = window.findChild(QWidget, "BasicInfoCombinedPage")
    blocks = page.findChildren(QWidget, "CombinedSectionBlock", Qt.FindDirectChildrenOnly)
    section_scroll = window.findChild(QScrollArea, "EditorSectionScroll")

    assert len(blocks) == 2
    assert blocks[0].x() < blocks[1].x()
    assert abs(blocks[0].y() - blocks[1].y()) <= 2
    assert abs(blocks[0].width() - blocks[1].width()) <= 80
    assert section_scroll is not None
    assert section_scroll.horizontalScrollBar().maximum() == 0
    window.close()


def test_editor_window_uses_fixed_workspace_size_across_sections(tmp_path: Path):
    window = _build_window(tmp_path)
    window.show()
    QApplication.processEvents()

    section_scroll = window.findChild(QScrollArea, "EditorSectionScroll")
    assert section_scroll is not None

    sizes = []
    for index in range(len(window.sections)):
        window._set_section(index)
        QApplication.processEvents()
        sizes.append(section_scroll.size())

    assert len({(size.width(), size.height()) for size in sizes}) == 1
    window.close()


def test_basic_info_section_has_breathing_room(tmp_path: Path):
    window = _build_window(tmp_path)
    window.show()
    QApplication.processEvents()

    content = window.basic_info_section.findChild(QWidget, "BasicInfoContent")

    assert content is not None
    assert content.maximumWidth() <= 980
    expected_width = min(content.maximumWidth(), max(0, window.basic_info_section.width() - 72))
    assert content.width() >= expected_width
    margins = content.layout().contentsMargins()
    assert margins.left() >= 24
    assert margins.right() >= 24
    assert window.basic_info_section.summary_edit.maximumHeight() <= 180
    window.close()


def test_basic_info_section_keeps_fixed_workspace_without_horizontal_scroll(tmp_path: Path):
    window = _build_window(tmp_path)
    window.show()
    QApplication.processEvents()

    section_scroll = window.findChild(QScrollArea, "EditorSectionScroll")

    assert section_scroll is not None
    assert section_scroll.horizontalScrollBar().maximum() == 0
    window.close()


def test_projects_section_does_not_expand_window_past_screen(tmp_path: Path):
    app = QApplication.instance() or QApplication([])
    window = _build_window(tmp_path)
    window._set_section(2)
    window.show()
    QApplication.processEvents()

    screen = window.screen() or app.primaryScreen()
    available = screen.availableGeometry()
    frame = window.frameGeometry()

    assert frame.width() <= available.width()
    assert window.minimumSizeHint().width() <= available.width()
    window.close()


def test_projects_section_list_page_fits_without_horizontal_scroll(tmp_path: Path):
    window = _build_window(tmp_path)
    window._set_section(2)
    window.show()
    QApplication.processEvents()

    section_scroll = window.findChild(QScrollArea, "EditorSectionScroll")

    assert section_scroll is not None
    assert section_scroll.horizontalScrollBar().maximum() == 0
    window.close()


def test_projects_section_uses_single_clear_workflow_panel(tmp_path: Path):
    window = _build_window(tmp_path)
    window._set_section(2)
    window.show()
    QApplication.processEvents()

    section_scroll = window.findChild(QScrollArea, "EditorSectionScroll")
    workflow = window.findChild(QWidget, "ProjectUnifiedPanel")
    page_stack = window.findChild(QStackedWidget, "ProjectPagesStack")

    assert page_stack is None
    assert workflow is not None
    labels = "\n".join(label.text() for label in workflow.findChildren(QWidget) if hasattr(label, "text"))
    assert "1. 项目摘要" in labels
    assert "2. 结果沉淀" in labels
    assert "3. 时间线" in labels
    assert section_scroll is not None
    assert section_scroll.horizontalScrollBar().maximum() == 0
    window.close()


def test_projects_section_visually_separates_picker_and_workflow(tmp_path: Path):
    window = _build_window(tmp_path)
    window._set_section(2)
    window.show()
    QApplication.processEvents()

    picker = window.findChild(QWidget, "ProjectPickerColumn")
    workflow = window.findChild(QWidget, "ProjectWorkflowColumn")
    summary = window.findChild(QWidget, "ProjectWorkflowSummary")
    result = window.findChild(QWidget, "ProjectWorkflowResult")
    timeline = window.findChild(QWidget, "ProjectWorkflowTimeline")

    assert picker is not None
    assert workflow is not None
    assert picker.x() < workflow.x()
    assert picker.width() < workflow.width()
    for step in (summary, result, timeline):
        assert step is not None
        assert step.property("workflowStep") is True

    window.close()


def test_preview_markdown_editor_uses_full_workspace_height(tmp_path: Path):
    window = _build_window(tmp_path)
    window._set_section(4)
    window.show()
    QApplication.processEvents()

    section_scroll = window.findChild(QScrollArea, "EditorSectionScroll")
    markdown_edit = window.preview_section.findChild(QPlainTextEdit)

    assert section_scroll is not None
    assert markdown_edit is not None
    assert markdown_edit.height() >= int(section_scroll.height() * 0.75)
    window.close()


def test_editor_window_opens_preview_in_separate_window(tmp_path: Path):
    app = QApplication.instance() or QApplication([])
    window = _build_window(tmp_path)

    window._open_preview_window()
    QApplication.processEvents()

    assert window.preview_window is not None
    assert window.preview_window.isVisible()
    assert window.preview_window.centralWidget() is window.preview_panel

    screen = window.preview_window.screen() or app.primaryScreen()
    available = screen.availableGeometry()
    frame = window.preview_window.frameGeometry()
    assert frame.width() <= available.width()
    assert frame.height() <= available.height()

    window.preview_window.close()

    window.close()


def test_editor_window_import_result_images_saves_first_for_unsaved_report(tmp_path: Path, monkeypatch):
    window = _build_window(tmp_path)
    window.projects_section.current_index = 0
    source = tmp_path / "demo.png"
    source.write_bytes(b"png")

    save_calls: list[str] = []
    imported: list[tuple[int, str]] = []

    def fake_save_current():
        save_calls.append("save")
        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        window.controller.current_json_path = data_dir / "2611.json"
        window.controller.current_markdown_path = tmp_path / "2611.md"
        window.controller.current_stem = "2611"
        return window.controller.current_json_path, window.controller.current_markdown_path

    monkeypatch.setattr(window, "_save_current", fake_save_current)
    monkeypatch.setattr(QFileDialog, "getOpenFileNames", lambda *args, **kwargs: ([str(source)], ""))
    monkeypatch.setattr(
        window.controller,
        "import_project_result_image",
        lambda index, path: imported.append((index, Path(path).name)) or "figs/demo.png",
    )
    monkeypatch.setattr(window.projects_section, "load_from_report", lambda: None)
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: None)

    window._import_project_result_images()

    assert save_calls == ["save"]
    assert imported == [(0, "demo.png")]
    window.close()


def test_editor_window_removes_result_image_from_current_project(tmp_path: Path, monkeypatch):
    window = _build_window(tmp_path)
    window.projects_section.current_index = 0
    removed: list[tuple[int, str]] = []

    monkeypatch.setattr(
        window.controller,
        "remove_project_result_image",
        lambda index, relative_path: removed.append((index, relative_path)),
    )
    monkeypatch.setattr(window.projects_section, "load_from_report", lambda: None)

    window._remove_project_result_image("figs/demo.png")

    assert removed == [(0, "figs/demo.png")]
    window.close()


def test_default_report_directory_uses_exe_parent_when_frozen(tmp_path: Path, monkeypatch):
    exe_path = tmp_path / "WeekFlow.exe"
    exe_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe_path))

    assert default_report_directory() == tmp_path


def test_new_report_uses_packaged_exe_directory_for_data(tmp_path: Path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    exe_path = tmp_path / "WeekFlow.exe"
    exe_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe_path))
    coordinator = AppCoordinator()
    captured: list[EditorController] = []
    monkeypatch.setattr(coordinator, "_show_editor", captured.append)

    coordinator._open_new_report({"report_id": "2611", "cycle": "", "topic": ""})
    controller = captured[0]
    controller.save_current()

    assert controller.default_directory == tmp_path
    assert (tmp_path / "data" / "2611" / "2611.json").exists()
    assert (tmp_path / "data" / "2611" / "2611.md").exists()
    assert (tmp_path / "data" / "2611" / "figs").is_dir()

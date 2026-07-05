import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

from WeekFlow.models.report import ProjectItem, RecordItem
from WeekFlow.ui.widgets.project_list_panel import ProjectListPanel
from WeekFlow.ui.widgets.project_detail_panel import ProjectDetailPanel, ProjectViewPanel
from WeekFlow.ui.widgets.result_images_panel import ResultImagesPanel


def test_result_images_panel_lists_and_removes_images():
    app = QApplication.instance() or QApplication([])

    panel = ResultImagesPanel()
    panel.set_images(["figs/result-001.png"])

    assert panel.list_widget.count() == 1
    assert panel.list_widget.item(0).text() == "figs/result-001.png"

    removed: list[str] = []
    panel.remove_requested.connect(removed.append)
    panel.list_widget.setCurrentRow(0)
    panel.remove_button.click()

    assert removed == ["figs/result-001.png"]
    panel.close()


def test_result_images_panel_shows_empty_guidance():
    app = QApplication.instance() or QApplication([])

    panel = ResultImagesPanel()
    panel.set_images([])
    panel.show()
    QApplication.processEvents()

    empty_label = panel.findChild(QLabel, "ResultImagesEmptyLabel")

    assert empty_label is not None
    assert empty_label.isVisible()
    assert "截图" in empty_label.text()

    panel.set_images(["figs/result-001.png"])
    assert not empty_label.isVisible()
    panel.close()


def test_project_detail_panel_emits_multiline_result_and_images():
    app = QApplication.instance() or QApplication([])

    panel = ProjectDetailPanel("result")
    emitted: list[ProjectItem] = []
    panel.project_changed.connect(emitted.append)
    panel.set_project(ProjectItem(name="项目 A"))
    QApplication.processEvents()

    panel.result_text_edit.setPlainText("第一行\n第二行")
    panel.result_images_panel.set_images(["figs/result-001.png"])
    panel._emit_project()

    assert emitted[-1].issue == "第一行\n第二行"
    assert emitted[-1].result_images == ["figs/result-001.png"]
    panel.close()


def test_project_detail_panel_uses_wrapping_multiline_summary_and_next_step():
    app = QApplication.instance() or QApplication([])

    panel = ProjectDetailPanel()
    emitted: list[ProjectItem] = []
    panel.project_changed.connect(emitted.append)
    panel.set_project(ProjectItem(name="项目 A"))
    QApplication.processEvents()

    assert isinstance(panel.summary_edit, QPlainTextEdit)
    assert isinstance(panel.next_step_edit, QPlainTextEdit)

    panel.summary_edit.setPlainText("第一行内容\n第二行内容")
    panel.next_step_edit.setPlainText("第一步\n第二步")
    panel._emit_project()

    assert emitted[-1].summary == "第一行内容\n第二行内容"
    assert emitted[-1].next_step == "第一步\n第二步"
    panel.close()


def test_project_list_panel_renders_scannable_project_rows():
    app = QApplication.instance() or QApplication([])

    panel = ProjectListPanel()
    panel.set_projects(
        [
            ProjectItem(
                name="项目 A",
                summary="完成 AI 配置入口梳理",
                next_step="验证链接粘贴",
                result_images=["figs/result-001.png"],
                records=[RecordItem(date="2026-06-30", time="10:00", name="配置", change="调整", result="通过")],
            )
        ]
    )

    row = panel.list_widget.itemWidget(panel.list_widget.item(0))
    assert row is not None
    texts = "\n".join(label.text() for label in row.findChildren(QLabel))
    assert "项目 A" in texts
    assert "完成 AI 配置入口梳理" in texts
    assert "下一步：验证链接粘贴" in texts
    assert "1 条流水" in texts
    assert "1 张图片" in texts
    button_texts = [button.text() for button in panel.findChildren(QPushButton)]
    assert "新增项目" in button_texts
    assert "删除项目" in button_texts
    assert "上移" in button_texts
    assert "下移" in button_texts
    panel.close()


def test_project_list_panel_project_rows_have_room_for_wrapped_text():
    app = QApplication.instance() or QApplication([])

    panel = ProjectListPanel()
    panel.set_projects(
        [
            ProjectItem(
                name="未命名项目",
                summary="暂无项目内容",
                next_step="待补充",
            )
        ]
    )

    item = panel.list_widget.item(0)
    assert item.sizeHint().height() >= 84
    panel.close()


def test_project_list_panel_does_not_show_horizontal_scrollbar():
    app = QApplication.instance() or QApplication([])

    panel = ProjectListPanel()
    panel.resize(240, 480)
    panel.set_projects(
        [
            ProjectItem(
                name="一个很长的未命名项目标题",
                summary="这是一段比较长的项目内容，用来确认列表卡片会换行而不是横向撑开。",
                next_step="继续验证布局",
            )
        ]
    )
    panel.show()
    QApplication.processEvents()

    assert panel.list_widget.horizontalScrollBar().maximum() == 0
    panel.close()


def test_project_detail_panel_uses_open_sections_without_nested_frames():
    app = QApplication.instance() or QApplication([])

    panel = ProjectDetailPanel("progress")
    result_panel = ProjectDetailPanel("result")

    assert panel.findChild(QFrame, "ProjectCoreGroup") is None
    assert panel.findChild(QFrame, "ProjectResultGroup") is None
    assert result_panel.findChild(QFrame, "ProjectResultGroup") is None
    assert result_panel.findChild(QFrame, "ProjectTimelineGroup") is None
    assert result_panel.findChild(QFrame, "ProjectSectionDivider") is not None
    panel.close()
    result_panel.close()


def test_project_detail_panel_splits_progress_and_results_into_separate_pages():
    app = QApplication.instance() or QApplication([])

    progress_panel = ProjectDetailPanel("progress")
    result_panel = ProjectDetailPanel("result")

    progress_page = progress_panel.findChild(QWidget, "ProjectProgressPage")
    result_page = result_panel.findChild(QWidget, "ProjectResultPage")

    assert progress_page is not None
    assert result_page is not None
    assert progress_panel.findChild(QFrame, "ProjectCoreGroup") is None
    assert progress_panel.findChild(QFrame, "ProjectResultGroup") is None
    assert result_panel.findChild(QFrame, "ProjectResultGroup") is None
    assert result_panel.findChild(QFrame, "ProjectTimelineGroup") is None
    assert result_panel.findChild(QFrame, "ProjectCoreGroup") is None
    progress_panel.close()
    result_panel.close()


def test_project_detail_panel_core_fields_use_guided_single_column_layout():
    app = QApplication.instance() or QApplication([])

    panel = ProjectDetailPanel()

    core_fields = panel.findChild(QWidget, "ProjectCoreFields")
    hints = "\n".join(label.text() for label in panel.findChildren(QLabel))

    assert core_fields is not None
    assert isinstance(core_fields.layout(), QVBoxLayout)
    assert "本周实际推进" in panel.summary_edit.placeholderText()
    assert "下一步动作" in panel.next_step_edit.placeholderText()
    assert "只写本周推进" in hints
    assert panel.minimumSizeHint().width() <= 480
    assert panel.summary_edit.maximumHeight() <= 150
    assert panel.next_step_edit.maximumHeight() <= 150
    panel.close()


def test_project_result_page_uses_guided_result_layout():
    app = QApplication.instance() or QApplication([])

    panel = ProjectDetailPanel("result")

    result_body = panel.findChild(QWidget, "ProjectResultBody")
    hints = "\n".join(label.text() for label in panel.findChildren(QLabel))

    assert result_body is not None
    assert isinstance(result_body.layout(), QVBoxLayout)
    assert "交付链接" in panel.result_text_edit.placeholderText()
    assert "说明、图片和时间线" in hints
    assert panel.result_text_edit.maximumHeight() <= 200
    panel.close()


def test_project_view_panel_shows_readonly_project_summary():
    app = QApplication.instance() or QApplication([])

    panel = ProjectViewPanel()
    panel.set_project(
        ProjectItem(
            name="项目 A",
            summary="完成入口迁移",
            issue="已完成验收",
            next_step="整理发布包",
            result_images=["figs/result-001.png"],
            records=[RecordItem(date="2026-07-01", time="10:00", name="验收", change="确认", result="通过")],
        )
    )

    texts = "\n".join(label.text() for label in panel.findChildren(QLabel))

    assert "项目查看" in texts
    assert "项目 A" in texts
    assert "完成入口迁移" in texts
    assert "已完成验收" in texts
    assert "figs/result-001.png" in texts
    assert "验收" in texts
    panel.close()

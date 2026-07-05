import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel

from WeekFlow.ui.widgets.report_preview_panel import ReportPreviewPanel


def test_preview_panel_places_theme_controls_inline_with_title():
    app = QApplication.instance() or QApplication([])

    panel = ReportPreviewPanel()

    header_row = panel.layout().itemAt(0).widget()
    header_layout = header_row.layout()

    assert isinstance(header_layout, QHBoxLayout)
    assert header_layout.itemAt(0).widget() is panel.title_label

    theme_label = header_layout.itemAt(header_layout.count() - 2).widget()
    assert isinstance(theme_label, QLabel)
    assert theme_label.text() == "主题"
    assert header_layout.itemAt(header_layout.count() - 1).widget() is panel.theme_combo

    panel.close()

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton

from WeekFlow.ui.home_window import HomeWindow


def test_home_window_enables_open_last_button_for_existing_file(tmp_path: Path):
    app = QApplication.instance() or QApplication([])
    report_path = tmp_path / "demo.data.json"
    report_path.write_text("{}", encoding="utf-8")

    window = HomeWindow()
    window.set_last_report_path(report_path, opened_text="2026-03-23 09:30")
    QApplication.processEvents()

    assert window.open_last_button.isEnabled()
    assert window.open_last_button.text() == "上次文件"

    emitted: list[str] = []
    window.open_report_requested.connect(emitted.append)
    window.open_last_button.click()

    assert emitted == [str(report_path)]
    window.close()


def test_home_window_disables_open_last_button_when_file_missing(tmp_path: Path):
    app = QApplication.instance() or QApplication([])

    window = HomeWindow()
    window.set_last_report_path(tmp_path / "missing.data.json")
    QApplication.processEvents()

    assert not window.open_last_button.isEnabled()
    assert window.open_last_button.text() == "上次文件"
    window.close()


def test_home_window_uses_flat_layout_without_nested_cards():
    app = QApplication.instance() or QApplication([])

    window = HomeWindow()

    assert not hasattr(window, "hero_card")
    assert window.layout().count() >= 1
    window.close()


def test_home_window_expands_content_in_upper_area():
    app = QApplication.instance() or QApplication([])

    window = HomeWindow()

    assert hasattr(window, "content_container")
    assert window.layout().itemAt(0).widget() is window.content_container
    assert window.content_container.maximumWidth() >= 960
    assert window.layout().itemAt(1).spacerItem() is not None

    button_texts = [button.text() for button in window.findChildren(QPushButton)]
    assert {"新建文件", "上次文件", "打开文件"} <= set(button_texts)
    assert len([text for text in button_texts if text in {"新建文件", "上次文件", "打开文件"}]) == 3

    window.close()


def test_home_window_can_center_on_screen():
    app = QApplication.instance() or QApplication([])

    window = HomeWindow()
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


def test_home_window_initial_size_fits_available_screen():
    app = QApplication.instance() or QApplication([])

    window = HomeWindow()
    window.show()
    QApplication.processEvents()

    screen = window.screen() or app.primaryScreen()
    available = screen.availableGeometry()
    frame = window.frameGeometry()

    assert frame.width() <= available.width()
    assert frame.height() <= available.height()
    window.close()

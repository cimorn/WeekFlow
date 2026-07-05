from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from WeekFlow.controllers.editor_controller import EditorController
from WeekFlow.services.app_state import AppStateStore
from WeekFlow.ui.editor_window import EditorWindow
from WeekFlow.ui.home_window import HomeWindow
from WeekFlow.ui.resources import resource_path
from WeekFlow.ui.theme import APP_STYLESHEET, apply_preferred_app_font


def default_report_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def main() -> int:
    app = QApplication([])
    app.setApplicationName("WeekFlow")
    apply_preferred_app_font(app)
    app.setStyleSheet(APP_STYLESHEET)
    logo = resource_path("src", "weekflow_logo.ico")
    if logo.exists():
        app.setWindowIcon(QIcon(str(logo)))

    coordinator = AppCoordinator()
    coordinator.show()
    return app.exec()


class AppCoordinator:
    def __init__(self, app_state: AppStateStore | None = None) -> None:
        self.app_state = app_state or AppStateStore()
        self.home_window = HomeWindow()
        self.editor_window: EditorWindow | None = None

        self.home_window.set_last_report_path(
            self.app_state.get_last_report_path(),
            self.app_state.get_last_opened_text(),
        )
        self.home_window.new_report_requested.connect(self._open_new_report)
        self.home_window.open_report_requested.connect(self._open_existing_report)

    def show(self) -> None:
        self.home_window.show()
        self.home_window.center_on_screen()

    def _open_new_report(self, payload: dict[str, str]) -> None:
        controller = EditorController(default_directory=default_report_directory())
        controller.create_new_report(
            report_id=payload["report_id"],
            cycle=payload.get("cycle", ""),
            topic=payload.get("topic", ""),
        )
        self._show_editor(controller)

    def _open_existing_report(self, path: str) -> None:
        controller = EditorController(default_directory=Path(path).parent)
        try:
            controller.load_from_json(Path(path))
        except Exception as exc:  # pragma: no cover - dialog path
            QMessageBox.critical(self.home_window, "打开失败", f"无法读取周报数据：\n{exc}")
            return
        self._remember_report_path(Path(path))
        self._show_editor(controller)

    def _show_editor(self, controller: EditorController) -> None:
        if self.editor_window is not None:
            self.editor_window.close()
            self.editor_window.deleteLater()
        self.editor_window = EditorWindow(controller)
        self.editor_window.back_requested.connect(self._return_home)
        self.editor_window.report_saved.connect(self._handle_report_saved)
        self.editor_window.show()
        self.editor_window.center_on_screen()
        self.home_window.hide()

    def _return_home(self) -> None:
        if self.editor_window is not None:
            self.editor_window.close()
            self.editor_window.deleteLater()
            self.editor_window = None
        self.home_window.set_last_report_path(
            self.app_state.get_last_report_path(),
            self.app_state.get_last_opened_text(),
        )
        self.home_window.show()
        self.home_window.center_on_screen()
        self.home_window.raise_()

    def _handle_report_saved(self, path: str) -> None:
        self._remember_report_path(Path(path))

    def _remember_report_path(self, path: Path) -> None:
        self.app_state.set_last_report_path(path)
        self.home_window.set_last_report_path(path, self.app_state.get_last_opened_text())


if __name__ == "__main__":
    raise SystemExit(main())

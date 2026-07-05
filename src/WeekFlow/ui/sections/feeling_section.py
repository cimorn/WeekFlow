from __future__ import annotations

from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from WeekFlow.controllers.editor_controller import EditorController


class FeelingSection(QWidget):
    def __init__(self, controller: EditorController, on_change) -> None:
        super().__init__()
        self.controller = controller
        self.on_change = on_change
        self._loading = False

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("记录本周感受、复盘判断，或者对下周推进的预期。")
        self.text_edit.setMinimumHeight(180)
        self.text_edit.setMaximumHeight(260)
        self.text_edit.textChanged.connect(self._apply_changes)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text_edit)

    def load_from_report(self) -> None:
        self._loading = True
        self.text_edit.setPlainText(self.controller.report.feeling)
        self._loading = False

    def _apply_changes(self) -> None:
        if self._loading:
            return
        self.controller.report.feeling = self.text_edit.toPlainText().strip()
        self.controller.mark_dirty()
        self.on_change()

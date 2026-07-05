from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from WeekFlow.controllers.editor_controller import EditorController


class OverviewSection(QWidget):
    def __init__(self, controller: EditorController, on_change) -> None:
        super().__init__()
        self.controller = controller
        self.on_change = on_change
        self._loading = False

        self.results_input = QLineEdit()
        self.results_input.setPlaceholderText("新增一条本周成果")
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(170)
        self.results_list.setMaximumHeight(240)
        self.results_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        add_result_button = QPushButton("添加成果")
        add_result_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        delete_result_button = QPushButton("删除成果")
        delete_result_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))

        add_result_button.clicked.connect(self._add_result)
        delete_result_button.clicked.connect(self._delete_result)
        self.results_list.itemChanged.connect(self._apply_changes)

        input_row = QHBoxLayout()
        input_row.addWidget(self.results_input)
        input_row.addWidget(add_result_button)

        controls = QHBoxLayout()
        controls.addWidget(delete_result_button)
        controls.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addLayout(input_row)
        layout.addWidget(self.results_list)
        layout.addLayout(controls)

    def load_from_report(self) -> None:
        self._loading = True
        self.results_list.clear()
        for item in self.controller.report.achievements:
            self.results_list.addItem(self._make_editable_item(item))
        self._loading = False

    def _make_editable_item(self, text: str) -> QListWidgetItem:
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        return item

    def _add_result(self) -> None:
        text = self.results_input.text().strip()
        if not text:
            return
        self.results_list.addItem(self._make_editable_item(text))
        self.results_input.clear()
        self._apply_changes()

    def _delete_result(self) -> None:
        row = self.results_list.currentRow()
        if row >= 0:
            self.results_list.takeItem(row)
            self._apply_changes()

    def _apply_changes(self) -> None:
        if self._loading:
            return
        self.controller.report.achievements = [
            self.results_list.item(index).text().strip()
            for index in range(self.results_list.count())
            if self.results_list.item(index).text().strip()
        ]
        self.controller.report.overview = {
            "mainline": "",
            "mainlines": [],
            "judgment": "",
            "focus": "",
        }
        self.controller.mark_dirty()
        self.on_change()

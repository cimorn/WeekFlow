from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from WeekFlow.controllers.editor_controller import EditorController
from WeekFlow.models.report import TodoItem


class TodosSection(QWidget):
    def __init__(self, controller: EditorController, on_change) -> None:
        super().__init__()
        self.controller = controller
        self.on_change = on_change
        self._loading = False

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("新增一条待跟进事项")
        self.list_widget = QListWidget()

        add_button = QPushButton("新增")
        delete_button = QPushButton("删除")
        up_button = QPushButton("上移")
        down_button = QPushButton("下移")
        add_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        up_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        down_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))

        add_button.clicked.connect(self._add_item)
        delete_button.clicked.connect(self._delete_item)
        up_button.clicked.connect(lambda: self._move_item(-1))
        down_button.clicked.connect(lambda: self._move_item(1))
        self.list_widget.itemChanged.connect(self._sync_to_report)

        top = QHBoxLayout()
        top.addWidget(self.input_edit)
        top.addWidget(add_button)

        controls = QHBoxLayout()
        controls.addWidget(delete_button)
        controls.addWidget(up_button)
        controls.addWidget(down_button)
        controls.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addLayout(top)
        layout.addWidget(self.list_widget)
        layout.addLayout(controls)

    def load_from_report(self) -> None:
        self._loading = True
        self.list_widget.clear()
        for todo in self.controller.report.todos:
            self.list_widget.addItem(self._make_item(todo))
        self._loading = False

    def _make_item(self, todo: TodoItem) -> QListWidgetItem:
        item = QListWidgetItem(todo.text)
        item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if todo.done else Qt.Unchecked)
        return item

    def _add_item(self) -> None:
        text = self.input_edit.text().strip()
        if not text:
            return
        self.list_widget.addItem(self._make_item(TodoItem(done=False, text=text)))
        self.input_edit.clear()
        self._sync_to_report()

    def _delete_item(self) -> None:
        row = self.list_widget.currentRow()
        if row >= 0:
            self.list_widget.takeItem(row)
            self._sync_to_report()

    def _move_item(self, delta: int) -> None:
        row = self.list_widget.currentRow()
        target = row + delta
        if row < 0 or target < 0 or target >= self.list_widget.count():
            return
        item = self.list_widget.takeItem(row)
        self.list_widget.insertItem(target, item)
        self.list_widget.setCurrentRow(target)
        self._sync_to_report()

    def _sync_to_report(self) -> None:
        if self._loading:
            return
        todos: list[TodoItem] = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            text = item.text().strip()
            if text:
                todos.append(TodoItem(done=item.checkState() == Qt.Checked, text=text))
        self.controller.report.todos = todos
        self.controller.mark_dirty()
        self.on_change()

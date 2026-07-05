from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QSizePolicy,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from WeekFlow.models.report import RecordItem


class RecordsTable(QWidget):
    records_changed = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._loading = False

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["日期", "时间", "名称", "内容", "结果"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.setMinimumWidth(0)
        self.table.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        self.table.itemChanged.connect(self._emit_records)

        add_button = QPushButton("新增记录")
        delete_button = QPushButton("删除记录")
        up_button = QPushButton("上移")
        down_button = QPushButton("下移")
        add_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        up_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        down_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))

        add_button.clicked.connect(self._add_record)
        delete_button.clicked.connect(self._delete_record)
        up_button.clicked.connect(lambda: self._move_record(-1))
        down_button.clicked.connect(lambda: self._move_record(1))

        controls = QGridLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setHorizontalSpacing(8)
        controls.setVerticalSpacing(8)
        controls.addWidget(add_button, 0, 0)
        controls.addWidget(delete_button, 0, 1)
        controls.addWidget(up_button, 1, 0)
        controls.addWidget(down_button, 1, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.table)
        layout.addLayout(controls)

    def set_records(self, records: list[RecordItem]) -> None:
        self._loading = True
        self.table.setRowCount(0)
        for record in records:
            self._append_row(record)
        self._loading = False

    def get_records(self) -> list[RecordItem]:
        records: list[RecordItem] = []
        for row in range(self.table.rowCount()):
            record = RecordItem(
                date=self._cell_text(row, 0),
                time=self._cell_text(row, 1),
                name=self._cell_text(row, 2),
                change=self._cell_text(row, 3),
                result=self._cell_text(row, 4),
            )
            if record.date or record.time or record.name or record.change or record.result:
                records.append(record)
        return records

    def _cell_text(self, row: int, column: int) -> str:
        item = self.table.item(row, column)
        return item.text().strip() if item else ""

    def _append_row(self, record: RecordItem) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        date, time = record.normalized_date_time()
        self.table.setItem(row, 0, self._make_item(date))
        self.table.setItem(row, 1, self._make_item(time))
        self.table.setItem(row, 2, self._make_item(record.name))
        self.table.setItem(row, 3, self._make_item(record.change))
        self.table.setItem(row, 4, self._make_item(record.result))

    def _make_item(self, value: str) -> QTableWidgetItem:
        item = QTableWidgetItem(value)
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def _add_record(self) -> None:
        self._append_row(RecordItem())
        self._emit_records()

    def _delete_record(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
            self._emit_records()

    def _move_record(self, delta: int) -> None:
        row = self.table.currentRow()
        target = row + delta
        if row < 0 or target < 0 or target >= self.table.rowCount():
            return
        records = self.get_records()
        records[row], records[target] = records[target], records[row]
        self.set_records(records)
        self.table.selectRow(target)
        self._emit_records()

    def _emit_records(self) -> None:
        if self._loading:
            return
        self.records_changed.emit(self.get_records())

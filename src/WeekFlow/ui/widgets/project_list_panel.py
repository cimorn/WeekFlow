from __future__ import annotations

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from WeekFlow.models.report import ProjectItem


class _ProjectRow(QWidget):
    ROW_HEIGHT = 94

    def __init__(self, project: ProjectItem) -> None:
        super().__init__()
        self.setObjectName("ProjectRow")
        self.setMinimumHeight(self.ROW_HEIGHT)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        self.index_label = QLabel()
        self.index_label.setObjectName("ProjectRowIndex")
        self.index_label.setProperty("role", "pill")
        self.index_label.setFixedWidth(34)
        self.index_label.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel(project.name or "未命名项目")
        self.title_label.setObjectName("ProjectRowTitle")
        self.title_label.setProperty("role", "board-title")

        summary = project.summary.strip() or "暂无项目内容"
        self.summary_label = QLabel(summary)
        self.summary_label.setObjectName("ProjectRowSummary")
        self.summary_label.setProperty("role", "muted")
        self.summary_label.setWordWrap(False)

        next_step = project.next_step.strip() or "待补充"
        self.next_step_label = QLabel(f"下一步：{next_step}")
        self.next_step_label.setObjectName("ProjectRowNextStep")
        self.next_step_label.setProperty("role", "muted")
        self.next_step_label.setWordWrap(False)

        self.meta_label = QLabel(f"{len(project.records)} 条流水 · {len(project.result_images)} 张图片")
        self.meta_label.setObjectName("ProjectRowMeta")
        self.meta_label.setProperty("role", "pill")
        self.meta_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.summary_label)
        text_layout.addWidget(self.next_step_label)
        text_layout.addWidget(self.meta_label)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        layout.addWidget(self.index_label, 0, Qt.AlignTop)
        layout.addLayout(text_layout, 1)

    def set_index(self, index: int) -> None:
        self.index_label.setText(str(index).zfill(2))

    def set_project(self, project: ProjectItem) -> None:
        self.title_label.setText(project.name or "未命名项目")
        self.summary_label.setText(project.summary.strip() or "暂无项目内容")
        self.next_step_label.setText(f"下一步：{project.next_step.strip() or '待补充'}")
        self.meta_label.setText(f"{len(project.records)} 条流水 · {len(project.result_images)} 张图片")


class ProjectListPanel(QWidget):
    selection_changed = Signal(int)
    add_requested = Signal()
    delete_requested = Signal()
    move_up_requested = Signal()
    move_down_requested = Signal()
    open_view_requested = Signal()
    open_progress_requested = Signal()
    open_result_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ProjectListPanel")

        title = QLabel("项目列表")
        title.setProperty("role", "section-title")

        helper = QLabel("先选一个项目，再进入对应页面填写。本页只负责管理项目顺序。")
        helper.setObjectName("ProjectListHelp")
        helper.setProperty("role", "muted")
        helper.setWordWrap(True)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("ProjectFlatList")
        self.list_widget.setSpacing(0)
        self.list_widget.setMinimumHeight(260)
        self.list_widget.setMaximumHeight(16777215)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.currentRowChanged.connect(self._on_current_row_changed)
        self.list_widget.itemDoubleClicked.connect(lambda _item: self.open_progress_requested.emit())

        add_button = QPushButton("新增项目")
        self.delete_button = QPushButton("删除项目")
        self.up_button = QPushButton("上移")
        self.down_button = QPushButton("下移")
        add_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        self.delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.up_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.down_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))

        add_button.clicked.connect(self.add_requested.emit)
        self.delete_button.clicked.connect(self.delete_requested.emit)
        self.up_button.clicked.connect(self.move_up_requested.emit)
        self.down_button.clicked.connect(self.move_down_requested.emit)

        header_text = QVBoxLayout()
        header_text.setContentsMargins(0, 0, 0, 0)
        header_text.setSpacing(6)
        header_text.addWidget(title)
        header_text.addWidget(helper)

        controls = QGridLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(8)
        controls.addWidget(add_button, 0, 0)
        controls.addWidget(self.delete_button, 0, 1)
        controls.addWidget(self.up_button, 1, 0)
        controls.addWidget(self.down_button, 1, 1)

        header = QVBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(12)
        header.addLayout(header_text)
        header.addLayout(controls)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addLayout(header)
        layout.addWidget(self.list_widget, 1)
        self._update_entry_buttons()

    def set_projects(self, projects: list[ProjectItem], current_index: int = -1) -> None:
        self.list_widget.clear()
        for index, project in enumerate(projects):
            item = QListWidgetItem()
            item.setData(Qt.UserRole, project.name or "未命名项目")
            row = _ProjectRow(project)
            row.set_index(index + 1)
            item.setSizeHint(QSize(0, _ProjectRow.ROW_HEIGHT))
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, row)
        if projects:
            if current_index < 0 or current_index >= len(projects):
                current_index = 0
            self.list_widget.setCurrentRow(current_index)
        self._update_entry_buttons()

    def _on_current_row_changed(self, index: int) -> None:
        self._update_entry_buttons()
        self.selection_changed.emit(index)

    def _update_entry_buttons(self) -> None:
        has_selection = self.list_widget.currentRow() >= 0
        self.delete_button.setEnabled(has_selection)
        self.up_button.setEnabled(has_selection)
        self.down_button.setEnabled(has_selection)

    def update_project(self, index: int, project: ProjectItem) -> None:
        if 0 <= index < self.list_widget.count():
            display_name = project.name or "未命名项目"
            item = self.list_widget.item(index)
            item.setData(Qt.UserRole, display_name)
            row = self.list_widget.itemWidget(item)
            if isinstance(row, _ProjectRow):
                row.set_project(project)

    def update_project_name(self, index: int, name: str) -> None:
        if 0 <= index < self.list_widget.count():
            item = self.list_widget.item(index)
            row = self.list_widget.itemWidget(item)
            if isinstance(row, _ProjectRow):
                row.title_label.setText(name or "未命名项目")
            item.setData(Qt.UserRole, name or "未命名项目")

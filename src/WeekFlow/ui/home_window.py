from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)

from WeekFlow.ui.resources import resource_path
from WeekFlow.ui.window_positioning import center_top_level_window, resize_top_level_window_to_fit_screen


class NewReportDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("新建周报")
        self.resize(420, 210)

        self.report_id_edit = QLineEdit()
        self.topic_edit = QLineEdit()
        self.report_id_edit.setPlaceholderText("例如 2611")
        self.topic_edit.setPlaceholderText("例如 社区活动筹备与资料整理")

        helper = QLabel("新建后会带一份空白模板，首次保存时会同时生成 .data.json 和 .md 文件。")
        helper.setProperty("role", "muted")
        helper.setWordWrap(True)

        form = QFormLayout()
        form.addRow("编号", self.report_id_edit)
        form.addRow("主题", self.topic_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("开始填写")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(helper)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> dict[str, str]:
        return {
            "report_id": self.report_id_edit.text().strip(),
            "cycle": "",
            "topic": self.topic_edit.text().strip(),
        }


class HomeWindow(QWidget):
    new_report_requested = Signal(dict)
    open_report_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("HomeRoot")
        self.setWindowTitle("WeekFlow")
        resize_top_level_window_to_fit_screen(
            self,
            900,
            560,
            width_ratio=0.88,
            height_ratio=0.78,
            minimum_width=640,
            minimum_height=420,
        )
        self._last_report_path: Path | None = None
        self._set_logo()

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(str(resource_path("src", "weekflow_logo.ico")))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(74, 74, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedHeight(86)

        title = QLabel("WeekFlow")
        title.setProperty("role", "hero-title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("把零散工作记录整理成结构化内容，并实时预览 Markdown 周报。")
        subtitle.setProperty("role", "hero-subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)

        self.new_button = QPushButton("新建文件")
        self.open_last_button = QPushButton("上次文件")
        self.open_button = QPushButton("打开文件")

        for button in (self.new_button, self.open_last_button, self.open_button):
            button.setMinimumHeight(46)
            button.setMinimumWidth(176)

        self.new_button.setProperty("variant", "primary")
        self.open_last_button.setProperty("variant", "secondary")
        self.open_button.setProperty("variant", "subtle")

        self.new_button.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        self.open_last_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.open_button.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))

        self.new_button.clicked.connect(self._show_new_report_dialog)
        self.open_last_button.clicked.connect(self._open_last_report)
        self.open_button.clicked.connect(self._open_existing_report)

        actions = QHBoxLayout()
        actions.setSpacing(14)
        actions.addStretch(1)
        actions.addWidget(self.new_button)
        actions.addWidget(self.open_last_button)
        actions.addWidget(self.open_button)
        actions.addStretch(1)

        content = QVBoxLayout()
        content.setSpacing(18)
        content.addWidget(logo_label)
        content.addWidget(title)
        content.addWidget(subtitle)
        content.addSpacing(10)
        content.addLayout(actions)

        self.content_container = QWidget()
        self.content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.content_container.setMaximumWidth(1200)
        self.content_container.setLayout(content)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(52, 56, 52, 40)
        layout.setSpacing(0)
        layout.addWidget(self.content_container, 0, Qt.AlignHCenter | Qt.AlignTop)
        layout.addStretch(1)

        self.set_last_report_path(None)

    def center_on_screen(self) -> None:
        center_top_level_window(self)

    def set_last_report_path(self, path: Path | None, opened_text: str = "") -> None:
        del opened_text
        self._last_report_path = Path(path) if path else None
        has_last_report = bool(self._last_report_path and self._last_report_path.exists())
        self.open_last_button.setEnabled(has_last_report)
        self.open_last_button.setText("上次文件")
        self.open_last_button.setToolTip(str(self._last_report_path) if has_last_report else "还没有可直接打开的上次文件")

        if not has_last_report:
            self._last_report_path = None

    def _set_logo(self) -> None:
        logo = resource_path("src", "weekflow_logo.ico")
        if logo.exists():
            self.setWindowIcon(QIcon(str(logo)))

    def _show_new_report_dialog(self) -> None:
        dialog = NewReportDialog(self)
        if dialog.exec():
            payload = dialog.values()
            if payload["report_id"]:
                self.new_report_requested.emit(payload)

    def _open_existing_report(self) -> None:
        start_path = self._last_report_path if self._last_report_path is not None else Path.cwd()
        path, _ = QFileDialog.getOpenFileName(
            self,
            "打开周报数据",
            str(start_path),
            "WeekFlow data (*.data.json);;JSON files (*.json)",
        )
        if path:
            self.open_report_requested.emit(path)

    def _open_last_report(self) -> None:
        if self._last_report_path is not None and self._last_report_path.exists():
            self.open_report_requested.emit(str(self._last_report_path))

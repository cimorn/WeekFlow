from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from WeekFlow.ui.theme import THEME_DISPLAY_NAMES, normalize_theme_key


class ReportPreviewPanel(QFrame):
    theme_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Card")
        self._loading_theme = False

        self.title_label = QLabel("当前预览")
        self.title_label.setProperty("role", "section-title")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.hint_label = QLabel("右侧只显示当前板块的排版效果。")
        self.hint_label.setProperty("role", "muted")
        self.hint_label.setAlignment(Qt.AlignLeft)
        self.hint_label.setWordWrap(True)

        self.theme_combo = QComboBox()
        for key, label in THEME_DISPLAY_NAMES.items():
            self.theme_combo.addItem(label, key)
        self.theme_combo.currentIndexChanged.connect(self._emit_theme_changed)

        self.theme_label = QLabel("主题")
        self.theme_label.setProperty("role", "muted")

        header_row = QWidget()
        header_layout = QHBoxLayout(header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.theme_label)
        header_layout.addWidget(self.theme_combo)

        self.view = QWebEngineView()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        layout.addWidget(header_row)
        layout.addWidget(self.hint_label)
        layout.addWidget(self.view, 1)

    def set_preview_meta(self, title: str, is_full_document: bool) -> None:
        self.title_label.setText(f"{title}预览")
        if is_full_document:
            self.hint_label.setText("当前显示整篇周报的最终排版效果。")
        else:
            self.hint_label.setText("当前只显示这一块内容，方便边写边看。")

    def set_theme(self, theme_key: str) -> None:
        active_theme = normalize_theme_key(theme_key)
        index = self.theme_combo.findData(active_theme)
        if index < 0:
            index = 0
        self._loading_theme = True
        self.theme_combo.setCurrentIndex(index)
        self._loading_theme = False

    def refresh_preview(self, html: str, base_directory: Path | None = None) -> None:
        if base_directory is None:
            self.view.setHtml(html)
            return
        base_url = QUrl.fromLocalFile(str(base_directory.resolve()) + "/")
        self.view.setHtml(html, base_url)

    def _emit_theme_changed(self) -> None:
        if self._loading_theme:
            return
        self.theme_changed.emit(self.current_theme())

    def current_theme(self) -> str:
        return normalize_theme_key(self.theme_combo.currentData())

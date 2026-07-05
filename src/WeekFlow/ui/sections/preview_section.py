from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from WeekFlow.controllers.editor_controller import EditorController


class PreviewSection(QWidget):
    def __init__(self, controller: EditorController) -> None:
        super().__init__()
        self.controller = controller

        label = QLabel("这里显示整篇周报的 Markdown 源文，右侧继续展示主题渲染后的最终预览。")
        label.setProperty("role", "muted")
        label.setWordWrap(True)

        self.preview_edit = QPlainTextEdit()
        self.preview_edit.setObjectName("MarkdownPreviewEdit")
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.preview_edit.setMinimumHeight(560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(label)
        layout.addWidget(self.preview_edit, 1)

    def refresh_preview(self) -> None:
        self.preview_edit.setPlainText(self.controller.render_markdown())

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QLineEdit, QSizePolicy, QTextEdit, QVBoxLayout, QWidget

from WeekFlow.controllers.editor_controller import EditorController


class BasicInfoSection(QWidget):
    def __init__(self, controller: EditorController, on_change) -> None:
        super().__init__()
        self.controller = controller
        self.on_change = on_change
        self._loading = False
        self.setObjectName("BasicInfoSection")

        self.report_id_edit = QLineEdit()
        self.topic_edit = QLineEdit()
        self.summary_edit = QTextEdit()
        self.report_id_edit.setPlaceholderText("例如 第08周")
        self.topic_edit.setPlaceholderText("例如 社区活动筹备与资料整理")
        self.summary_edit.setPlaceholderText("点击“AI 润色当前页”后，会基于全文自动生成一句话总结。")
        self.summary_edit.setMinimumHeight(96)
        self.summary_edit.setMaximumHeight(112)

        helper = QLabel("这里不再填写周期。编号会直接作为顶部标题显示，一句话总结支持 AI 基于全文生成。")
        helper.setProperty("role", "muted")
        helper.setWordWrap(True)

        content = QWidget()
        content.setObjectName("BasicInfoContent")
        content.setMaximumWidth(940)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 10, 24, 12)
        content_layout.setSpacing(12)
        content_layout.addWidget(helper)
        content_layout.addWidget(self._build_field("编号", self.report_id_edit))
        content_layout.addWidget(self._build_field("主题", self.topic_edit))
        content_layout.addWidget(self._build_field("一句话总结", self.summary_edit))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(content, 0, Qt.AlignTop)

        self.report_id_edit.textChanged.connect(self._apply_changes)
        self.topic_edit.textChanged.connect(self._apply_changes)
        self.summary_edit.textChanged.connect(self._apply_changes)

    def _build_field(self, label_text: str, editor: QWidget) -> QWidget:
        field = QWidget()
        label = QLabel(label_text)
        label.setProperty("role", "field-label")

        layout = QVBoxLayout(field)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)
        layout.addWidget(label)
        layout.addWidget(editor)
        return field

    def load_from_report(self) -> None:
        self._loading = True
        self.report_id_edit.setText(self.controller.report.report_id)
        self.topic_edit.setText(self.controller.report.topic)
        self.summary_edit.setPlainText(self.controller.report.one_line_summary)
        self._loading = False

    def _apply_changes(self) -> None:
        if self._loading:
            return
        report = self.controller.report
        report.report_id = self.report_id_edit.text().strip()
        report.topic = self.topic_edit.text().strip()
        report.one_line_summary = self.summary_edit.toPlainText().strip()
        self.controller.mark_dirty()
        self.on_change()

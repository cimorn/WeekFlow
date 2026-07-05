from __future__ import annotations

from typing import Literal

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from WeekFlow.models.report import ProjectItem
from WeekFlow.ui.widgets.records_table import RecordsTable
from WeekFlow.ui.widgets.result_images_panel import ResultImagesPanel


ProjectPageMode = Literal["progress", "result"]


class ProjectDetailPanel(QFrame):
    project_changed = Signal(object)
    back_requested = Signal()
    switch_to_progress_requested = Signal()
    switch_to_result_requested = Signal()
    add_result_image_requested = Signal()
    remove_result_image_requested = Signal(str)

    def __init__(self, mode: ProjectPageMode = "progress") -> None:
        super().__init__()
        self.mode = mode
        self.setObjectName("ProjectDetailPage")
        self.setProperty("projectPage", mode)
        self._loading = False
        self._has_project = False
        self._current_project = ProjectItem()

        self.name_edit = QLineEdit()
        self.summary_edit = QPlainTextEdit()
        self.summary_edit.setObjectName("ProjectSummaryEdit")
        self.next_step_edit = QPlainTextEdit()
        self.next_step_edit.setObjectName("ProjectNextStepEdit")
        self.result_text_edit = QPlainTextEdit()
        self.result_text_edit.setObjectName("ProjectResultTextEdit")
        self.result_images_panel = ResultImagesPanel()
        self.records_table = RecordsTable()

        self.name_edit.setPlaceholderText("例如：周报工具打包 / AI 配置入口优化")
        self.summary_edit.setPlaceholderText("写本周实际推进：完成了什么、解决了什么问题。")
        self.next_step_edit.setPlaceholderText("写下一步动作：谁来做、什么时候验证。")
        self.result_text_edit.setPlaceholderText("沉淀最终结论、交付链接或复盘说明。")

        for edit in (self.summary_edit, self.next_step_edit):
            edit.setMinimumHeight(92)
            edit.setMaximumHeight(128)
        self.result_text_edit.setMinimumHeight(132)
        self.result_text_edit.setMaximumHeight(190)
        self.result_images_panel.setMinimumHeight(126)
        self.result_images_panel.setMaximumHeight(176)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        layout.addWidget(self._build_header())
        if mode == "progress":
            layout.addWidget(self._build_progress_body(), 1)
        else:
            layout.addWidget(self._build_result_body(), 1)

        self.name_edit.textChanged.connect(self._emit_project)
        self.summary_edit.textChanged.connect(self._emit_project)
        self.next_step_edit.textChanged.connect(self._emit_project)
        self.result_text_edit.textChanged.connect(self._emit_project)
        self.records_table.records_changed.connect(lambda _records: self._emit_project())
        self.result_images_panel.add_requested.connect(self.add_result_image_requested.emit)
        self.result_images_panel.remove_requested.connect(self.remove_result_image_requested.emit)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("ProjectDetailHeader")

        title = QLabel("进展填写" if self.mode == "progress" else "结果记录")
        title.setProperty("role", "section-title")

        self.project_name_label = QLabel("未选择项目")
        self.project_name_label.setObjectName("ProjectCurrentNameLabel")
        self.project_name_label.setProperty("role", "pill")
        self.project_name_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.project_name_label.setMinimumHeight(32)
        self.project_name_label.setMaximumHeight(38)
        self.project_name_label.setMaximumWidth(220)

        helper_text = (
            "只写本周推进和下一步，结果内容放到“结果记录”。"
            if self.mode == "progress"
            else "只整理已经有结论的内容：说明、图片和时间线。"
        )
        helper = QLabel(helper_text)
        helper.setProperty("role", "muted")
        helper.setWordWrap(True)

        back_button = QPushButton("返回列表")
        back_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        back_button.clicked.connect(self.back_requested.emit)

        switch_button = QPushButton("去记录结果" if self.mode == "progress" else "去填写进展")
        switch_button.setProperty("variant", "primary" if self.mode == "progress" else "subtle")
        switch_button.setIcon(
            self.style().standardIcon(
                QStyle.SP_FileDialogContentsView if self.mode == "progress" else QStyle.SP_FileDialogDetailedView
            )
        )
        if self.mode == "progress":
            switch_button.clicked.connect(self.switch_to_result_requested.emit)
        else:
            switch_button.clicked.connect(self.switch_to_progress_requested.emit)

        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(6)
        title_column.addWidget(title)
        title_column.addWidget(helper)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(8)
        actions.addWidget(self.project_name_label)
        actions.addWidget(back_button)
        actions.addWidget(switch_button)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(16)
        layout.addLayout(title_column, 1)
        layout.addLayout(actions)
        return header

    def _build_progress_body(self) -> QWidget:
        body = QWidget()
        body.setObjectName("ProjectProgressPage")

        section_title = QLabel("核心信息")
        section_title.setProperty("role", "board-group-title")
        section_hint = QLabel("用于周报顶部三列表格：名称、内容、预计。先写短标题，再写实际推进和下一步。")
        section_hint.setProperty("role", "muted")
        section_hint.setWordWrap(True)

        fields = QWidget()
        fields.setObjectName("ProjectCoreFields")
        fields_layout = QVBoxLayout(fields)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        fields_layout.setSpacing(16)
        fields_layout.addWidget(self._build_field("名称", "项目在周报里显示的标题，尽量短。", self.name_edit))

        planning_fields = QWidget()
        planning_fields.setObjectName("ProjectPlanningFields")
        planning_layout = QHBoxLayout(planning_fields)
        planning_layout.setContentsMargins(0, 0, 0, 0)
        planning_layout.setSpacing(14)
        planning_layout.addWidget(self._build_field("内容", "写已经推进的事实，不用写长段总结。", self.summary_edit), 1)
        planning_layout.addWidget(self._build_field("预计", "写下一步计划、验证方式或交付时间。", self.next_step_edit), 1)
        fields_layout.addWidget(planning_fields)

        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(section_title)
        layout.addWidget(section_hint)
        layout.addWidget(fields)
        layout.addStretch(1)
        return body

    def _build_result_body(self) -> QWidget:
        body = QWidget()
        body.setObjectName("ProjectResultPage")

        result_title = QLabel("结果沉淀")
        result_title.setProperty("role", "board-group-title")

        result_fields = QWidget()
        result_fields.setObjectName("ProjectResultBody")
        result_fields_layout = QVBoxLayout(result_fields)
        result_fields_layout.setContentsMargins(0, 0, 0, 0)
        result_fields_layout.setSpacing(14)
        result_fields_layout.addWidget(
            self._build_field("结果说明", "结论、交付链接或复盘说明。", self.result_text_edit)
        )
        result_fields_layout.addWidget(self._build_field("结果图片", "可选：截图、照片或设计稿。", self.result_images_panel))

        divider = QFrame()
        divider.setObjectName("ProjectSectionDivider")
        divider.setFrameShape(QFrame.HLine)

        timeline_title = QLabel("时间线")
        timeline_title.setProperty("role", "board-group-title")
        records_label = QLabel("可选：记录关键变更，例如会议、确认、交付、验收。")
        records_label.setProperty("role", "muted")
        records_label.setWordWrap(True)

        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(result_title)
        layout.addWidget(result_fields)
        layout.addWidget(divider)
        layout.addWidget(timeline_title)
        layout.addWidget(records_label)
        layout.addWidget(self.records_table, 1)
        return body

    def _build_field(self, label_text: str, hint_text: str, editor: QWidget) -> QWidget:
        field = QWidget()
        field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        label = QLabel(label_text)
        label.setProperty("role", "field-label")

        hint = QLabel(hint_text)
        hint.setProperty("role", "muted")
        hint.setWordWrap(True)

        layout = QVBoxLayout(field)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)
        layout.addWidget(label)
        if hint_text:
            layout.addWidget(hint)
        layout.addWidget(editor)
        return field

    def set_project(self, project: ProjectItem | None) -> None:
        self._loading = True
        self._has_project = project is not None
        self._current_project = project if project is not None else ProjectItem()
        if project is None:
            self.name_edit.clear()
            self.summary_edit.clear()
            self.next_step_edit.clear()
            self.result_text_edit.clear()
            self.result_images_panel.set_images([])
            self.records_table.set_records([])
            self._set_project_name_label("未选择项目")
        else:
            self.name_edit.setText(project.name)
            self.summary_edit.setPlainText(project.summary)
            self.next_step_edit.setPlainText(project.next_step)
            self.result_text_edit.setPlainText(project.issue)
            self.result_images_panel.set_images(project.result_images)
            self.records_table.set_records(project.records)
            self._set_project_name_label(project.name or "未命名项目")

        for widget in (
            self.name_edit,
            self.summary_edit,
            self.next_step_edit,
            self.result_text_edit,
            self.result_images_panel,
            self.records_table,
        ):
            widget.setEnabled(self._has_project)
        self._loading = False

    def _set_project_name_label(self, name: str) -> None:
        display_name = name if len(name) <= 14 else f"{name[:13]}…"
        self.project_name_label.setText(display_name)
        self.project_name_label.setToolTip(name)

    def _emit_project(self) -> None:
        if self._loading or not self._has_project:
            return
        base = self._current_project
        if self.mode == "progress":
            project = ProjectItem(
                name=self.name_edit.text().strip(),
                summary=self.summary_edit.toPlainText().strip(),
                issue=base.issue,
                next_step=self.next_step_edit.toPlainText().strip(),
                result_images=base.result_images,
                records=base.records,
            )
        else:
            project = ProjectItem(
                name=base.name,
                summary=base.summary,
                issue=self.result_text_edit.toPlainText().strip(),
                next_step=base.next_step,
                result_images=self.result_images_panel.images(),
                records=self.records_table.get_records(),
            )
        self._current_project = project
        self._set_project_name_label(project.name or "未命名项目")
        self.project_changed.emit(project)


class ProjectUnifiedPanel(QFrame):
    project_changed = Signal(object)
    add_result_image_requested = Signal()
    remove_result_image_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ProjectUnifiedPanel")
        self._loading = False
        self._has_project = False
        self._current_project = ProjectItem()

        self.name_edit = QLineEdit()
        self.summary_edit = QPlainTextEdit()
        self.summary_edit.setObjectName("ProjectSummaryEdit")
        self.next_step_edit = QPlainTextEdit()
        self.next_step_edit.setObjectName("ProjectNextStepEdit")
        self.result_text_edit = QPlainTextEdit()
        self.result_text_edit.setObjectName("ProjectResultTextEdit")
        self.result_images_panel = ResultImagesPanel()
        self.records_table = RecordsTable()

        self.name_edit.setPlaceholderText("项目标题，例如：周报工具打包 / AI 配置入口优化")
        self.summary_edit.setPlaceholderText("写本周实际推进：完成了什么、解决了什么问题。")
        self.next_step_edit.setPlaceholderText("写下一步动作：谁来做、什么时候验证。")
        self.result_text_edit.setPlaceholderText("有结论后再填：交付链接、复盘说明或最终结果。")

        for edit in (self.summary_edit, self.next_step_edit):
            edit.setMinimumHeight(82)
            edit.setMaximumHeight(112)
        self.result_text_edit.setMinimumHeight(104)
        self.result_text_edit.setMaximumHeight(150)
        self.result_images_panel.setMinimumHeight(112)
        self.result_images_panel.setMaximumHeight(156)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(self._build_header())
        layout.addWidget(self._build_summary_group())
        layout.addWidget(self._build_result_group())
        layout.addWidget(self._build_timeline_group(), 1)

        self.name_edit.textChanged.connect(self._emit_project)
        self.summary_edit.textChanged.connect(self._emit_project)
        self.next_step_edit.textChanged.connect(self._emit_project)
        self.result_text_edit.textChanged.connect(self._emit_project)
        self.records_table.records_changed.connect(lambda _records: self._emit_project())
        self.result_images_panel.add_requested.connect(self.add_result_image_requested.emit)
        self.result_images_panel.remove_requested.connect(self.remove_result_image_requested.emit)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("ProjectWorkflowHeader")

        title = QLabel("当前项目")
        title.setProperty("role", "section-title")

        helper = QLabel("按顺序填写：先选项目，再写摘要；有结果时补结果说明、图片和时间线。")
        helper.setProperty("role", "muted")
        helper.setWordWrap(True)

        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(6)
        layout.addWidget(title)
        layout.addWidget(helper)
        return header

    def _build_summary_group(self) -> QWidget:
        group = QFrame()
        group.setObjectName("ProjectWorkflowSummary")
        group.setProperty("workflowStep", True)

        title = QLabel("1. 项目摘要")
        title.setProperty("role", "board-group-title")
        hint = QLabel("这部分会进入周报的三列表格：名称 / 内容 / 预计。")
        hint.setProperty("role", "muted")
        hint.setWordWrap(True)

        planning_fields = QWidget()
        planning_layout = QHBoxLayout(planning_fields)
        planning_layout.setContentsMargins(0, 0, 0, 0)
        planning_layout.setSpacing(14)
        planning_layout.addWidget(self._build_field("本周推进", "", self.summary_edit), 1)
        planning_layout.addWidget(self._build_field("下一步", "", self.next_step_edit), 1)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(9)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(self._build_field("名称", "", self.name_edit))
        layout.addWidget(planning_fields)
        return group

    def _build_result_group(self) -> QWidget:
        group = QFrame()
        group.setObjectName("ProjectWorkflowResult")
        group.setProperty("workflowStep", True)

        title = QLabel("2. 结果沉淀")
        title.setProperty("role", "board-group-title")
        hint = QLabel("没有明确结论可以先留空；有交付链接、截图或复盘时再补。")
        hint.setProperty("role", "muted")
        hint.setWordWrap(True)

        result_fields = QWidget()
        result_layout = QHBoxLayout(result_fields)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(14)
        result_layout.addWidget(self._build_field("结果说明", "", self.result_text_edit), 1)
        result_layout.addWidget(self._build_field("结果图片", "", self.result_images_panel), 1)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(9)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(result_fields)
        return group

    def _build_timeline_group(self) -> QWidget:
        group = QFrame()
        group.setObjectName("ProjectWorkflowTimeline")
        group.setProperty("workflowStep", True)

        title = QLabel("3. 时间线")
        title.setProperty("role", "board-group-title")
        hint = QLabel("可选：只记录关键节点，例如会议、确认、交付、验收。")
        hint.setProperty("role", "muted")
        hint.setWordWrap(True)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(9)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(self.records_table, 1)
        return group

    def _build_field(self, label_text: str, hint_text: str, editor: QWidget) -> QWidget:
        field = QWidget()
        field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        label = QLabel(label_text)
        label.setProperty("role", "field-label")

        layout = QVBoxLayout(field)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(label)
        if hint_text:
            hint = QLabel(hint_text)
            hint.setProperty("role", "muted")
            hint.setWordWrap(True)
            layout.addWidget(hint)
        layout.addWidget(editor)
        return field

    def _build_divider(self) -> QFrame:
        divider = QFrame()
        divider.setObjectName("ProjectSectionDivider")
        divider.setFrameShape(QFrame.HLine)
        return divider

    def set_project(self, project: ProjectItem | None) -> None:
        self._loading = True
        self._has_project = project is not None
        self._current_project = project if project is not None else ProjectItem()
        if project is None:
            self.name_edit.clear()
            self.summary_edit.clear()
            self.next_step_edit.clear()
            self.result_text_edit.clear()
            self.result_images_panel.set_images([])
            self.records_table.set_records([])
        else:
            self.name_edit.setText(project.name)
            self.summary_edit.setPlainText(project.summary)
            self.next_step_edit.setPlainText(project.next_step)
            self.result_text_edit.setPlainText(project.issue)
            self.result_images_panel.set_images(project.result_images)
            self.records_table.set_records(project.records)

        for widget in (
            self.name_edit,
            self.summary_edit,
            self.next_step_edit,
            self.result_text_edit,
            self.result_images_panel,
            self.records_table,
        ):
            widget.setEnabled(self._has_project)
        self._loading = False

    def _emit_project(self) -> None:
        if self._loading or not self._has_project:
            return
        project = ProjectItem(
            name=self.name_edit.text().strip(),
            summary=self.summary_edit.toPlainText().strip(),
            issue=self.result_text_edit.toPlainText().strip(),
            next_step=self.next_step_edit.toPlainText().strip(),
            result_images=self.result_images_panel.images(),
            records=self.records_table.get_records(),
        )
        self._current_project = project
        self.project_changed.emit(project)


class ProjectViewPanel(QFrame):
    back_requested = Signal()
    switch_to_progress_requested = Signal()
    switch_to_result_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ProjectViewPage")

        self.title_value = QLabel("未命名项目")
        self.summary_value = QLabel("暂无项目内容")
        self.next_step_value = QLabel("待补充")
        self.result_value = QLabel("暂无结果说明")
        self.images_value = QLabel("暂无结果图片")
        self.records_value = QLabel("暂无时间线记录")

        for label in (
            self.title_value,
            self.summary_value,
            self.next_step_value,
            self.result_value,
            self.images_value,
            self.records_value,
        ):
            label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        layout.addWidget(self._build_header())
        layout.addWidget(self._build_body(), 1)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("ProjectDetailHeader")

        title = QLabel("项目查看")
        title.setProperty("role", "section-title")

        helper = QLabel("集中查看当前项目会出现在周报里的内容，确认后再回去补充。")
        helper.setProperty("role", "muted")
        helper.setWordWrap(True)

        back_button = QPushButton("返回列表")
        back_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        back_button.clicked.connect(self.back_requested.emit)

        progress_button = QPushButton("填写进展")
        progress_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        progress_button.clicked.connect(self.switch_to_progress_requested.emit)

        result_button = QPushButton("记录结果")
        result_button.setProperty("variant", "primary")
        result_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        result_button.clicked.connect(self.switch_to_result_requested.emit)

        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(6)
        title_column.addWidget(title)
        title_column.addWidget(helper)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(8)
        actions.addWidget(back_button)
        actions.addWidget(progress_button)
        actions.addWidget(result_button)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(16)
        layout.addLayout(title_column, 1)
        layout.addLayout(actions)
        return header

    def _build_body(self) -> QWidget:
        body = QWidget()
        body.setObjectName("ProjectViewBody")

        divider = QFrame()
        divider.setObjectName("ProjectSectionDivider")
        divider.setFrameShape(QFrame.HLine)

        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(self._build_section_title("项目摘要"))
        layout.addWidget(self._build_readonly_field("名称", self.title_value))
        layout.addWidget(self._build_readonly_field("内容", self.summary_value))
        layout.addWidget(self._build_readonly_field("预计", self.next_step_value))
        layout.addWidget(divider)
        layout.addWidget(self._build_section_title("结果与附件"))
        layout.addWidget(self._build_readonly_field("结果说明", self.result_value))
        layout.addWidget(self._build_readonly_field("结果图片", self.images_value))
        layout.addWidget(self._build_readonly_field("时间线", self.records_value))
        layout.addStretch(1)
        return body

    def _build_section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setProperty("role", "board-group-title")
        return label

    def _build_readonly_field(self, label_text: str, value_label: QLabel) -> QWidget:
        field = QWidget()
        label = QLabel(label_text)
        label.setProperty("role", "field-label")
        value_label.setObjectName("ProjectViewValue")
        value_label.setProperty("role", "muted")

        layout = QVBoxLayout(field)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(label)
        layout.addWidget(value_label)
        return field

    def set_project(self, project: ProjectItem | None) -> None:
        if project is None:
            self.title_value.setText("未命名项目")
            self.summary_value.setText("暂无项目内容")
            self.next_step_value.setText("待补充")
            self.result_value.setText("暂无结果说明")
            self.images_value.setText("暂无结果图片")
            self.records_value.setText("暂无时间线记录")
            return

        self.title_value.setText(project.name or "未命名项目")
        self.summary_value.setText(project.summary or "暂无项目内容")
        self.next_step_value.setText(project.next_step or "待补充")
        self.result_value.setText(project.issue or "暂无结果说明")
        self.images_value.setText("\n".join(project.result_images) if project.result_images else "暂无结果图片")
        if project.records:
            rows = []
            for record in project.records:
                date, time = record.normalized_date_time()
                title = " / ".join(part for part in (date, time, record.name) if part)
                detail = "：".join(part for part in (record.change, record.result) if part)
                rows.append(" - ".join(part for part in (title, detail) if part))
            self.records_value.setText("\n".join(rows))
        else:
            self.records_value.setText("暂无时间线记录")

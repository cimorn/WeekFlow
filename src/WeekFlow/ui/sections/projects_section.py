from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from WeekFlow.controllers.editor_controller import EditorController
from WeekFlow.models.report import ProjectItem
from WeekFlow.ui.widgets.project_detail_panel import ProjectUnifiedPanel
from WeekFlow.ui.widgets.project_list_panel import ProjectListPanel


class ProjectsSection(QWidget):
    add_result_image_requested = Signal(int)
    remove_result_image_requested = Signal(int, str)
    layout_changed = Signal()

    def __init__(self, controller: EditorController, on_change) -> None:
        super().__init__()
        self.setObjectName("ProjectsSection")
        self.controller = controller
        self.on_change = on_change
        self.current_index = -1
        self._loading = False

        self.list_panel = ProjectListPanel()
        self.detail_panel = ProjectUnifiedPanel()

        self.list_panel.selection_changed.connect(self._select_project)
        self.list_panel.add_requested.connect(self._add_project)
        self.list_panel.delete_requested.connect(self._delete_project)
        self.list_panel.move_up_requested.connect(lambda: self._move_project(-1))
        self.list_panel.move_down_requested.connect(lambda: self._move_project(1))
        self.list_panel.open_progress_requested.connect(lambda: self.detail_panel.name_edit.setFocus())
        self.detail_panel.project_changed.connect(self._update_project)
        self.detail_panel.add_result_image_requested.connect(self._request_add_result_image)
        self.detail_panel.remove_result_image_requested.connect(self._request_remove_result_image)

        self.picker_column = QFrame()
        self.picker_column.setObjectName("ProjectPickerColumn")
        self.picker_column.setMinimumWidth(270)
        self.picker_column.setMaximumWidth(340)
        picker_layout = QVBoxLayout(self.picker_column)
        picker_layout.setContentsMargins(14, 14, 14, 14)
        picker_layout.setSpacing(0)
        picker_layout.addWidget(self.list_panel, 1)

        self.workflow_column = QFrame()
        self.workflow_column.setObjectName("ProjectWorkflowColumn")
        workflow_layout = QVBoxLayout(self.workflow_column)
        workflow_layout.setContentsMargins(14, 16, 14, 16)
        workflow_layout.setSpacing(0)
        workflow_layout.addWidget(self.detail_panel, 1)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(self.picker_column)
        layout.addWidget(self.workflow_column, 1)

    def load_from_report(self) -> None:
        self._loading = True
        projects = self.controller.report.projects
        if not projects:
            self.current_index = -1
            self.list_panel.set_projects([])
            self.detail_panel.set_project(None)
        else:
            if self.current_index < 0 or self.current_index >= len(projects):
                self.current_index = 0
            self.list_panel.set_projects(projects, self.current_index)
            self.detail_panel.set_project(projects[self.current_index])
        self._loading = False
        self._emit_layout_changed()

    def _select_project(self, index: int) -> None:
        if self._loading:
            return
        self.current_index = index
        if 0 <= index < len(self.controller.report.projects):
            self.detail_panel.set_project(self.controller.report.projects[index])
        else:
            self.detail_panel.set_project(None)
        self.on_change()
        self._emit_layout_changed()

    def _add_project(self) -> None:
        project_number = len(self.controller.report.projects) + 1
        self.controller.report.projects.append(ProjectItem(name=f"新项目 {project_number}"))
        self.current_index = len(self.controller.report.projects) - 1
        self.controller.mark_dirty()
        self.load_from_report()
        self.detail_panel.name_edit.setFocus()
        self.on_change()

    def _delete_project(self) -> None:
        if 0 <= self.current_index < len(self.controller.report.projects):
            self.controller.report.projects.pop(self.current_index)
            if self.current_index >= len(self.controller.report.projects):
                self.current_index = len(self.controller.report.projects) - 1
            self.controller.mark_dirty()
            self.load_from_report()
            self.on_change()

    def _move_project(self, delta: int) -> None:
        target = self.current_index + delta
        projects = self.controller.report.projects
        if self.current_index < 0 or target < 0 or target >= len(projects):
            return
        projects[self.current_index], projects[target] = projects[target], projects[self.current_index]
        self.current_index = target
        self.controller.mark_dirty()
        self.load_from_report()
        self.on_change()

    def _update_project(self, project: ProjectItem) -> None:
        if 0 <= self.current_index < len(self.controller.report.projects):
            self.controller.report.projects[self.current_index] = project
            self.list_panel.update_project(self.current_index, project)
            self.controller.mark_dirty()
            self.on_change()

    def _emit_layout_changed(self) -> None:
        self.updateGeometry()
        self.layout_changed.emit()

    def _request_add_result_image(self) -> None:
        if self.current_index >= 0:
            self.add_result_image_requested.emit(self.current_index)

    def _request_remove_result_image(self, relative_path: str) -> None:
        if self.current_index >= 0:
            self.remove_result_image_requested.emit(self.current_index, relative_path)

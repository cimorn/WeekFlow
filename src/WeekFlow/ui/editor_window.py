from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from WeekFlow.controllers.editor_controller import EditorController
from WeekFlow.services.ai import AIConfigError, AIService
from WeekFlow.services.preview import build_preview_document
from WeekFlow.services.renderer import render_title
from WeekFlow.services.versioning import next_version_stem
from WeekFlow.ui.sections.ai_config_section import AIConfigSection
from WeekFlow.ui.sections.basic_info_section import BasicInfoSection
from WeekFlow.ui.sections.feeling_section import FeelingSection
from WeekFlow.ui.sections.overview_section import OverviewSection
from WeekFlow.ui.sections.preview_section import PreviewSection
from WeekFlow.ui.sections.projects_section import ProjectsSection
from WeekFlow.ui.sections.todos_section import TodosSection
from WeekFlow.ui.widgets.report_preview_panel import ReportPreviewPanel
from WeekFlow.ui.window_positioning import center_top_level_window, resize_top_level_window_to_fit_screen


class CurrentPageStackedWidget(QStackedWidget):
    def sizeHint(self):  # noqa: N802
        widget = self.currentWidget()
        return widget.sizeHint() if widget is not None else super().sizeHint()

    def minimumSizeHint(self):  # noqa: N802
        widget = self.currentWidget()
        return widget.minimumSizeHint() if widget is not None else super().minimumSizeHint()


class EditorWindow(QMainWindow):
    back_requested = Signal()
    report_saved = Signal(str)

    def __init__(self, controller: EditorController) -> None:
        super().__init__()
        self.controller = controller
        self.ai_service = AIService()
        self.setWindowTitle("WeekFlow")
        resize_top_level_window_to_fit_screen(
            self,
            1280,
            900,
            width_ratio=0.92,
            height_ratio=0.98,
            minimum_width=680,
            minimum_height=640,
        )

        container = QWidget()
        container.setObjectName("EditorRoot")
        self.setCentralWidget(container)

        self.report_label = QLabel()
        self.report_label.setProperty("role", "pill")
        self.path_label = QLabel()
        self.path_label.setProperty("role", "pill")
        self.status_label = QLabel()
        self.status_label.setProperty("role", "pill")
        self.section_title_label = QLabel()
        self.section_title_label.setProperty("role", "section-title")
        self.section_title_label.setAlignment(Qt.AlignCenter)
        self.section_hint_label = QLabel()
        self.section_hint_label.setProperty("role", "muted")
        self.section_hint_label.setAlignment(Qt.AlignCenter)
        self.section_hint_label.setWordWrap(True)

        self.stack = CurrentPageStackedWidget()
        self.stack.setObjectName("EditorSectionStack")
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.section_scroll: QScrollArea | None = None
        self.section_buttons: list[QPushButton] = []

        self.basic_info_section = BasicInfoSection(controller, self._on_content_changed)
        self.overview_section = OverviewSection(controller, self._on_content_changed)
        self.projects_section = ProjectsSection(controller, self._on_content_changed)
        self.projects_section.add_result_image_requested.connect(lambda _index: self._import_project_result_images())
        self.projects_section.remove_result_image_requested.connect(
            lambda _index, relative_path: self._remove_project_result_image(relative_path)
        )
        self.projects_section.layout_changed.connect(self._sync_current_section_geometry)
        self.todos_section = TodosSection(controller, self._on_content_changed)
        self.feeling_section = FeelingSection(controller, self._on_content_changed)
        self.ai_config_section = AIConfigSection(controller, self._on_content_changed)
        self.ai_config_section.setObjectName("AIConfigSection")
        self.ai_config_section.test_requested.connect(self._test_ai_connection)
        self.preview_section = PreviewSection(controller)
        self.preview_panel = ReportPreviewPanel()
        self.preview_panel.theme_changed.connect(self._on_theme_changed)
        self.preview_window: QMainWindow | None = None

        self.basic_info_page = self._build_combined_page(
            "BasicInfoCombinedPage",
            [
                ("基本信息", "编号、主题和一句话总结。", self.basic_info_section, 5),
                ("AI 配置", "接口、模型和提示词。", self.ai_config_section, 4),
            ],
            columns=True,
        )
        self.overview_page = self._build_combined_page(
            "OverviewFeelingCombinedPage",
            [
                ("本周成果", "一条一条写清楚已经完成的事情。", self.overview_section, 5),
                ("本周感受", "复盘判断和下周预期放这里。", self.feeling_section, 4),
            ],
            columns=True,
        )

        self.sections = [
            {
                "key": "basic_info",
                "label": "基本信息",
                "hint": "维护编号、主题、一句话总结和 AI 配置。",
                "widget": self.basic_info_page,
                "icon": QStyle.SP_FileDialogDetailedView,
            },
            {
                "key": "overview",
                "label": "本周成果",
                "hint": "成果和本周感受放在同一个页面里。",
                "widget": self.overview_page,
                "icon": QStyle.SP_FileDialogContentsView,
            },
            {
                "key": "projects",
                "label": "项目进展",
                "hint": "先在项目列表选择项目，再分别进入进展填写或结果记录页面。",
                "widget": self.projects_section,
                "icon": QStyle.SP_MediaPlay,
            },
            {
                "key": "todos",
                "label": "待跟进事项",
                "hint": "维护待跟进清单和顺序，右侧会同步显示更轻的勾选样式。",
                "widget": self.todos_section,
                "icon": QStyle.SP_MessageBoxQuestion,
            },
            {
                "key": "preview",
                "label": "预览",
                "hint": "左侧是 Markdown 源文，右侧是最终主题预览。",
                "widget": self.preview_section,
                "icon": QStyle.SP_FileDialogListView,
            },
        ]

        root_layout = QVBoxLayout(container)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(12)
        root_layout.addWidget(self._build_status_row())
        root_layout.addWidget(self._build_workspace(), 1)

        self.reload_from_controller()
        self._set_section(0)
        self.setFixedSize(self.size())

    def center_on_screen(self) -> None:
        center_top_level_window(self)

    def _build_status_row(self) -> QWidget:
        row = QFrame()
        row.setObjectName("TopNavBar")

        back_button = QPushButton("返回首页")
        back_button.setProperty("compact", True)
        back_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        back_button.clicked.connect(self.back_requested.emit)

        nav = QWidget()
        nav.setObjectName("TopSectionNav")
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(8)
        for index, section in enumerate(self.sections):
            button = QPushButton(section["label"])
            button.setCheckable(True)
            button.setProperty("topNav", True)
            button.clicked.connect(lambda _checked=False, idx=index: self._set_section(idx))
            self.section_buttons.append(button)
            self.stack.addWidget(section["widget"])
            nav_layout.addWidget(button)
        nav_layout.addStretch(1)

        nav_scroll = QScrollArea()
        nav_scroll.setObjectName("TopSectionNavScroll")
        nav_scroll.setFrameShape(QFrame.NoFrame)
        nav_scroll.setWidgetResizable(False)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setMinimumHeight(42)
        nav_scroll.setMaximumHeight(52)
        nav_scroll.setWidget(nav)
        nav_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        layout.addWidget(self.report_label)
        layout.addWidget(nav_scroll, 1)
        layout.addWidget(self._build_top_action_bar())
        layout.addWidget(back_button)
        return row

    def _build_workspace(self) -> QFrame:
        return self._build_editor_panel()

    def _build_combined_page(
        self,
        object_name: str,
        blocks: list[tuple[str, str, QWidget, int]],
        *,
        columns: bool = False,
    ) -> QWidget:
        page = QWidget()
        page.setObjectName(object_name)

        layout = QHBoxLayout(page) if columns else QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20 if columns else 14)
        for title, hint, widget, stretch in blocks:
            block = self._build_combined_block(title, hint, widget)
            if columns:
                layout.addWidget(block, stretch, Qt.AlignTop)
            else:
                layout.addWidget(block)
        if not columns:
            layout.addStretch(1)
        return page

    def _build_combined_block(self, title_text: str, hint_text: str, widget: QWidget) -> QWidget:
        block = QWidget()
        block.setObjectName("CombinedSectionBlock")
        block.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        title = QLabel(title_text)
        title.setProperty("role", "section-title")

        hint = QLabel(hint_text)
        hint.setProperty("role", "muted")
        hint.setWordWrap(True)

        layout = QVBoxLayout(block)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(widget)
        return block

    def _build_editor_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("EditorPanel")

        self.section_scroll = QScrollArea()
        section_scroll = self.section_scroll
        section_scroll.setObjectName("EditorSectionScroll")
        section_scroll.setFrameShape(QFrame.NoFrame)
        section_scroll.setWidgetResizable(True)
        section_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        section_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        section_scroll.viewport().setObjectName("EditorSectionViewport")
        section_scroll.setWidget(self.stack)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(0)
        layout.addWidget(section_scroll, 1)
        return panel

    def _build_top_action_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("TopActionBar")
        save_button = QPushButton("保存")
        save_button.setObjectName("SaveReportButton")
        save_button.setProperty("variant", "primary")
        save_button.setProperty("topAction", True)
        save_button.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))

        save_as_button = QPushButton("另存")
        save_as_button.setObjectName("SaveAsVersionButton")
        save_as_button.setProperty("topAction", True)
        save_as_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))

        ai_button = QPushButton("AI 润色")
        ai_button.setObjectName("PolishCurrentPageButton")
        ai_button.setProperty("topAction", True)
        ai_button.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))

        preview_button = QPushButton("预览窗口")
        preview_button.setObjectName("OpenPreviewWindowButton")
        preview_button.setProperty("topAction", True)
        preview_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogListView))

        save_button.clicked.connect(self._save_current)
        save_as_button.clicked.connect(self._save_as_new_version)
        ai_button.clicked.connect(self._run_ai_for_current_section)
        preview_button.clicked.connect(self._open_preview_window)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(save_button)
        layout.addWidget(save_as_button)
        layout.addWidget(ai_button)
        layout.addWidget(preview_button)
        return bar

    def reload_from_controller(self) -> None:
        self.basic_info_section.load_from_report()
        self.overview_section.load_from_report()
        self.projects_section.load_from_report()
        self.todos_section.load_from_report()
        self.feeling_section.load_from_report()
        self.ai_config_section.load_from_report()
        self.preview_section.refresh_preview()
        self.preview_panel.set_theme(self.controller.report.preview_theme)
        self._update_status()
        self._refresh_previews()

    def _set_section(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for idx, button in enumerate(self.section_buttons):
            button.setChecked(idx == index)

        section = self.sections[index]
        self.section_title_label.setText("")
        self.section_hint_label.setText("")
        self._sync_current_section_geometry()
        self._refresh_previews()

    def _sync_current_section_geometry(self) -> None:
        current_widget = self.stack.currentWidget()
        if current_widget is None:
            return
        current_widget.updateGeometry()
        self.stack.setMinimumHeight(0)
        self.stack.setMaximumHeight(16777215)
        self.stack.updateGeometry()
        if self.section_scroll is not None:
            self.section_scroll.setMinimumHeight(0)
            self.section_scroll.setMaximumHeight(16777215)
            self.section_scroll.verticalScrollBar().setValue(0)
            self.section_scroll.horizontalScrollBar().setValue(0)
            self.section_scroll.updateGeometry()

    def _current_section(self) -> dict[str, object]:
        return self.sections[self.stack.currentIndex()]

    def _refresh_previews(self) -> None:
        self.preview_section.refresh_preview()
        section = self._current_section()
        key = str(section["key"])
        project_index = self.projects_section.current_index if key == "projects" else None
        if project_index is not None and project_index < 0:
            project_index = None

        is_full_document = key == "preview"
        self.preview_panel.set_preview_meta(str(section["label"]), is_full_document=is_full_document)
        preview_root = self.controller.report_root_directory() or self.controller.default_directory
        self.preview_panel.refresh_preview(
            build_preview_document(
                self.controller.report,
                section_key=key,
                theme_key=self.controller.report.preview_theme,
                project_index=project_index,
            ),
            base_directory=preview_root,
        )

    def _on_content_changed(self) -> None:
        self._update_status()
        self._refresh_previews()

    def _on_theme_changed(self, theme_key: str) -> None:
        if self.controller.report.preview_theme == theme_key:
            return
        self.controller.report.preview_theme = theme_key
        self.controller.mark_dirty()
        self._update_status()
        self._refresh_previews()

    def _test_ai_connection(self) -> None:
        try:
            message = self.ai_service.test_connection(self.controller.report)
        except AIConfigError as exc:
            self.ai_config_section.set_status_message(str(exc))
            QMessageBox.warning(self, "AI 配置", str(exc))
            return
        self.ai_config_section.set_status_message(f"连接测试成功：{message}")
        QMessageBox.information(self, "AI 配置", f"连接测试成功：{message}")

    def _run_ai_for_current_section(self) -> None:
        section = self._current_section()
        key = str(section["key"])
        project_index = self.projects_section.current_index if key == "projects" else None
        try:
            self.ai_service.polish_current_section(
                self.controller.report,
                section_key=key,
                project_index=project_index,
            )
        except AIConfigError as exc:
            QMessageBox.warning(self, "AI 润色", str(exc))
            return

        self.controller.mark_dirty()
        self.reload_from_controller()
        QMessageBox.information(self, "AI 润色", f"已完成“{section['label']}”的润色。")

    def _update_status(self) -> None:
        report_id = self.controller.report.report_id
        report_title = render_title(report_id) if report_id else "未命名周报"
        json_path = self.controller.current_json_path
        path_text = json_path.name if json_path is not None else "未保存"
        status_text = "已修改" if self.controller.is_dirty else "已保存"

        self.report_label.setText(report_title)
        self.path_label.setText("")
        self.path_label.setToolTip(str(json_path) if json_path is not None else "")
        self.status_label.setText("")

    def _ensure_save_directory(self) -> bool:
        if self.controller.current_json_path is not None:
            return True
        directory = QFileDialog.getExistingDirectory(self, "选择周报保存目录", str(Path.cwd()))
        if not directory:
            return False
        self.controller.default_directory = Path(directory)
        return True

    def _save_current(self) -> None:
        if not self.controller.report.report_id.strip():
            QMessageBox.warning(self, "无法保存", "请先填写周报编号。")
            return
        if not self._ensure_save_directory():
            return
        json_path, markdown_path = self.controller.save_current()
        self.report_saved.emit(str(json_path))
        self._update_status()
        self._refresh_previews()
        QMessageBox.information(self, "保存完成", f"已保存：\n{json_path}\n{markdown_path}")

    def _ensure_saved_before_importing_assets(self) -> bool:
        if self.controller.current_json_path is not None:
            return True
        self._save_current()
        return self.controller.current_json_path is not None

    def _import_project_result_images(self) -> None:
        project_index = self.projects_section.current_index
        if project_index < 0:
            return
        if not self._ensure_saved_before_importing_assets():
            return

        start_dir = self.controller.report_root_directory() or self.controller.default_directory
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择结果图片",
            str(start_dir),
            "Image Files (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if not paths:
            return

        for path in paths:
            self.controller.import_project_result_image(project_index, Path(path))

        self.projects_section.load_from_report()
        self._update_status()
        self._refresh_previews()
        QMessageBox.information(self, "结果图片", f"已添加 {len(paths)} 张图片。")

    def _open_preview_window(self) -> None:
        if self.preview_window is None:
            self.preview_window = QMainWindow(self)
            self.preview_window.setWindowTitle("WeekFlow 预览")
            self.preview_window.setCentralWidget(self.preview_panel)
            resize_top_level_window_to_fit_screen(
                self.preview_window,
                860,
                700,
                width_ratio=0.88,
                height_ratio=0.86,
                minimum_width=620,
                minimum_height=500,
            )
        self._refresh_previews()
        self.preview_window.show()
        center_top_level_window(self.preview_window)
        self.preview_window.raise_()
        self.preview_window.activateWindow()

    def _remove_project_result_image(self, relative_path: str) -> None:
        project_index = self.projects_section.current_index
        if project_index < 0:
            return
        self.controller.remove_project_result_image(project_index, relative_path)
        self.projects_section.load_from_report()
        self._update_status()
        self._refresh_previews()

    def _save_as_new_version(self) -> None:
        if not self.controller.report.report_id.strip():
            QMessageBox.warning(self, "无法另存", "请先填写周报编号。")
            return
        if not self._ensure_save_directory():
            return
        if self.controller.current_json_path is None:
            self._save_current()
            return
        default_stem = next_version_stem(
            self.controller.default_directory,
            self.controller.report.report_id or self.controller.current_stem or "weekly-report",
        )
        custom_stem, accepted = QInputDialog.getText(
            self,
            "另存新版本",
            "请输入新的文件名（不含扩展名）：",
            text=default_stem,
        )
        if not accepted:
            return
        custom_stem = custom_stem.strip()
        if not custom_stem:
            QMessageBox.warning(self, "无法另存", "文件名不能为空。")
            return
        json_path, markdown_path = self.controller.save_as_named_version(custom_stem)
        self.report_saved.emit(str(json_path))
        self._update_status()
        self._refresh_previews()
        QMessageBox.information(self, "已另存新版本", f"已保存新版本：\n{json_path}\n{markdown_path}")

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)


class ResultImagesPanel(QWidget):
    add_requested = Signal()
    remove_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.list_widget = QListWidget()
        self.empty_label = QLabel("添加截图、设计稿或结果图，预览里会跟随展示。")
        self.empty_label.setObjectName("ResultImagesEmptyLabel")
        self.empty_label.setProperty("role", "empty-state")
        self.empty_label.setWordWrap(True)
        self.empty_label.setMinimumHeight(72)

        self.add_button = QPushButton("添加图片")
        self.remove_button = QPushButton("删除图片")
        self.add_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        self.remove_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))

        self.add_button.clicked.connect(self.add_requested.emit)
        self.remove_button.clicked.connect(self._emit_remove_requested)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(8)
        controls.addWidget(self.add_button)
        controls.addWidget(self.remove_button)
        controls.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.list_widget)
        layout.addLayout(controls)

        self.set_images([])

    def set_images(self, images: list[str]) -> None:
        self.list_widget.clear()
        for image in images:
            self.list_widget.addItem(image)
        has_images = bool(images)
        self.empty_label.setVisible(not has_images)
        self.list_widget.setVisible(has_images)

    def images(self) -> list[str]:
        return [self.list_widget.item(index).text() for index in range(self.list_widget.count())]

    def setEnabled(self, enabled: bool) -> None:  # noqa: N802
        super().setEnabled(enabled)
        self.empty_label.setEnabled(enabled)
        self.list_widget.setEnabled(enabled)
        self.add_button.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)

    def _emit_remove_requested(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            return
        self.remove_requested.emit(item.text())

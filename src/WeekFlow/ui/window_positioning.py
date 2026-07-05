from __future__ import annotations

from PySide6.QtCore import QPoint
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget


def resize_top_level_window_to_fit_screen(
    window: QWidget,
    preferred_width: int,
    preferred_height: int,
    *,
    width_ratio: float = 0.92,
    height_ratio: float = 0.88,
    minimum_width: int = 640,
    minimum_height: int = 480,
) -> None:
    screen = window.screen() or QGuiApplication.primaryScreen()
    if screen is None:
        window.resize(preferred_width, preferred_height)
        return

    available = screen.availableGeometry()
    max_width = max(1, int(available.width() * width_ratio))
    max_height = max(1, int(available.height() * height_ratio))

    bounded_min_width = min(minimum_width, max_width)
    bounded_min_height = min(minimum_height, max_height)
    target_width = max(bounded_min_width, min(preferred_width, max_width))
    target_height = max(bounded_min_height, min(preferred_height, max_height))

    window.resize(target_width, target_height)


def center_top_level_window(window: QWidget) -> None:
    screen = window.screen() or QGuiApplication.primaryScreen()
    if screen is None:
        return

    available = screen.availableGeometry()
    frame = window.frameGeometry()
    frame.moveCenter(available.center())
    top_left = frame.topLeft()
    max_x = available.right() - frame.width() + 1
    max_y = available.bottom() - frame.height() + 1
    x = max(available.left(), min(top_left.x(), max_x))
    y = max(available.top(), min(top_left.y(), max_y))
    window.move(QPoint(x, y))

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


FORMAT_BY_SUFFIX = {
    ".ico": "ICO",
    ".icns": "ICNS",
}


def export_icon(source: Path, destination: Path, size: int = 256) -> None:
    image_format = FORMAT_BY_SUFFIX.get(destination.suffix.lower())
    if image_format is None:
        supported = ", ".join(sorted(FORMAT_BY_SUFFIX))
        raise RuntimeError(f"Unsupported icon format for {destination}. Expected one of: {supported}")

    if source.suffix.lower() == ".svg":
        renderer = QSvgRenderer(str(source))
        if not renderer.isValid():
            raise RuntimeError(f"Invalid SVG icon: {source}")

        image = QImage(size, size, QImage.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            painter.fillRect(image.rect(), QColor(0, 0, 0, 0))
            renderer.render(painter, QRectF(0, 0, size, size))
        finally:
            painter.end()
    else:
        image = QImage(str(source))
        if image.isNull():
            raise RuntimeError(f"Invalid icon source: {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(destination), image_format):
        raise RuntimeError(f"Failed to write icon file: {destination}")


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: export_app_icon.py <source-image> <destination-icon>")

    app = QGuiApplication([])
    source = Path(sys.argv[1]).resolve()
    destination = Path(sys.argv[2]).resolve()
    export_icon(source, destination)
    app.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

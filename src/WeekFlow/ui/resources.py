from __future__ import annotations

import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
    return base_dir.joinpath(*parts)

from __future__ import annotations

import shutil
from pathlib import Path


def ensure_report_asset_dirs(report_dir: Path, stem: str) -> tuple[Path, Path]:
    data_dir = Path(report_dir) / "data" / stem
    figs_dir = data_dir / "figs"
    data_dir.mkdir(parents=True, exist_ok=True)
    figs_dir.mkdir(parents=True, exist_ok=True)
    return data_dir, figs_dir


def import_result_image(source: Path, report_dir: Path, stem: str) -> str:
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError(source)

    _data_dir, figs_dir = ensure_report_asset_dirs(report_dir, stem)
    target_name = _deduplicated_name(figs_dir, source.name)
    target_path = figs_dir / target_name
    shutil.copy2(source, target_path)
    return (Path("figs") / target_name).as_posix()


def _deduplicated_name(directory: Path, source_name: str) -> str:
    source_path = Path(source_name)
    stem = source_path.stem or "result"
    suffix = source_path.suffix
    candidate = f"{stem}{suffix}"
    counter = 2

    while (directory / candidate).exists():
        candidate = f"{stem}-{counter}{suffix}"
        counter += 1

    return candidate

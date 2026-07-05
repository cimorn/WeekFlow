from __future__ import annotations

from pathlib import Path


def base_pair_paths(directory: Path, stem: str) -> tuple[Path, Path]:
    report_dir = directory / "data" / stem
    return report_dir / f"{stem}.json", report_dir / f"{stem}.md"


def next_version_stem(directory: Path, stem: str) -> str:
    version = 2
    while True:
        candidate = f"{stem}-v{version}"
        json_path, markdown_path = base_pair_paths(directory, candidate)
        if not json_path.exists() and not markdown_path.exists():
            return candidate
        version += 1

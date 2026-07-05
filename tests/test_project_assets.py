from pathlib import Path

from WeekFlow.services.project_assets import import_result_image


def test_import_result_image_copies_into_figs_and_returns_relative_path(tmp_path: Path):
    source = tmp_path / "origin.png"
    source.write_bytes(b"png")
    report_dir = tmp_path / "weekly"

    relative_path = import_result_image(source, report_dir, "2611")

    assert relative_path.startswith("figs/")
    assert (report_dir / "data" / "2611" / relative_path).exists()


def test_import_result_image_deduplicates_names(tmp_path: Path):
    report_dir = tmp_path / "weekly"
    source = tmp_path / "origin.png"
    source.write_bytes(b"png")

    first_path = import_result_image(source, report_dir, "2611")
    second_path = import_result_image(source, report_dir, "2611")

    assert first_path != second_path
    assert (report_dir / "data" / "2611" / first_path).exists()
    assert (report_dir / "data" / "2611" / second_path).exists()

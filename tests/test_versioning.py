from pathlib import Path

from WeekFlow.services.versioning import base_pair_paths, next_version_stem


def test_base_pair_paths_uses_stem_for_json_and_markdown(tmp_path: Path):
    json_path, markdown_path = base_pair_paths(tmp_path, "2611")

    assert json_path == tmp_path / "data" / "2611" / "2611.json"
    assert markdown_path == tmp_path / "data" / "2611" / "2611.md"


def test_next_version_name_returns_v2_when_no_versions_exist(tmp_path: Path):
    assert next_version_stem(tmp_path, "2611") == "2611-v2"


def test_next_version_name_skips_existing_versions(tmp_path: Path):
    data_dir = tmp_path / "data" / "2611-v2"
    data_dir.mkdir(parents=True)
    (data_dir / "2611-v2.json").write_text("{}", encoding="utf-8")

    assert next_version_stem(tmp_path, "2611") == "2611-v3"

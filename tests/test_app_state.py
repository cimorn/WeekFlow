from pathlib import Path

from WeekFlow.services.app_state import AppStateStore


def test_app_state_store_persists_last_report_path(tmp_path: Path):
    store = AppStateStore(state_file=tmp_path / "state.json")
    report_path = tmp_path / "demo.data.json"
    report_path.write_text("{}", encoding="utf-8")

    store.set_last_report_path(report_path, opened_text="2026-03-23 09:30")

    reloaded = AppStateStore(state_file=tmp_path / "state.json")
    assert reloaded.get_last_report_path() == report_path
    assert reloaded.get_last_opened_text() == "2026-03-23 09:30"


def test_app_state_store_ignores_missing_last_report_path(tmp_path: Path):
    store = AppStateStore(state_file=tmp_path / "state.json")

    store.set_last_report_path(tmp_path / "missing.data.json")

    assert store.get_last_report_path() is None


def test_app_state_store_persists_custom_opened_time(tmp_path: Path):
    store = AppStateStore(state_file=tmp_path / "state.json")
    report_path = tmp_path / "demo.data.json"
    report_path.write_text("{}", encoding="utf-8")

    store.set_last_report_path(report_path, opened_text="2026-03-23 09:30")

    payload = (tmp_path / "state.json").read_text(encoding="utf-8")

    assert "2026-03-23 09:30" in payload

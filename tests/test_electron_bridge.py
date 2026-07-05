import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

from WeekFlow.electron_bridge import ElectronBridgeSession
from WeekFlow.models.report import WeeklyReport


def test_electron_bridge_creates_data_tree_at_startup(tmp_path: Path):
    ElectronBridgeSession(default_directory=tmp_path)

    assert (tmp_path / "data").is_dir()
    assert not (tmp_path / "data" / "figs").exists()


def test_electron_bridge_creates_updates_and_saves_report(tmp_path: Path):
    session = ElectronBridgeSession(default_directory=tmp_path)

    created = session.handle(
        {
            "type": "createReport",
            "payload": {
                "report_id": "2611",
                "cycle": "2026.03.12 - 2026.03.18",
                "topic": "Electron editor rebuild",
            },
        }
    )

    assert created["ok"] is True
    assert created["state"]["report"]["report_id"] == "2611"
    assert created["state"]["report"]["projects"]
    assert created["state"]["current_json_path"] is None
    assert "# Week 11" in created["state"]["markdown"]
    assert "<!DOCTYPE html>" in created["state"]["preview_html"]

    report = created["state"]["report"]
    report["one_line_summary"] = "Electron UI handles the editor surface."
    report["achievements"] = ["Replaced the cramped Qt layout."]
    report["projects"][0] = {
        "name": "Editor rewrite",
        "summary": "Moved the complex board to Electron.",
        "issue": "The old Qt layout was too brittle.",
        "next_step": "Package the Electron app.",
        "result_images": [],
        "records": [
            {
                "date": "2026-07-01",
                "time": "10:30",
                "name": "UI",
                "change": "Created Electron bridge",
                "result": "Ready for renderer",
            }
        ],
    }

    updated = session.handle({"type": "replaceReport", "payload": {"report": report}})

    assert updated["ok"] is True
    assert updated["state"]["is_dirty"] is True
    assert "Electron UI handles the editor surface." in updated["state"]["markdown"]
    assert "Editor rewrite" in updated["state"]["markdown"]

    saved = session.handle({"type": "saveCurrent", "payload": {}})

    assert saved["ok"] is True
    assert saved["state"]["is_dirty"] is False
    assert Path(saved["state"]["current_json_path"]) == tmp_path / "data" / "2611" / "2611.json"
    assert Path(saved["state"]["current_markdown_path"]) == tmp_path / "data" / "2611" / "2611.md"
    assert (tmp_path / "data" / "2611" / "figs").is_dir()


def test_electron_bridge_saves_new_report_with_requested_file_stem(tmp_path: Path):
    session = ElectronBridgeSession(default_directory=tmp_path)

    created = session.handle(
        {
            "type": "createReport",
            "payload": {"stem": "client-demo", "report_id": "01", "topic": "客户演示"},
        }
    )
    saved = session.handle({"type": "saveCurrent", "payload": {}})

    assert created["ok"] is True
    assert saved["ok"] is True
    assert saved["state"]["current_stem"] == "client-demo"
    assert Path(saved["state"]["current_json_path"]) == tmp_path / "data" / "client-demo" / "client-demo.json"
    assert Path(saved["state"]["current_markdown_path"]) == tmp_path / "data" / "client-demo" / "client-demo.md"
    assert (tmp_path / "data" / "client-demo" / "figs").is_dir()
    assert saved["state"]["report"]["report_id"] == "01"


def test_electron_bridge_lists_reports_from_data_directory(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    first = WeeklyReport(report_id="01", topic="第一个项目")
    second = WeeklyReport(report_id="02", topic="第二个项目")
    (data_dir / "alpha").mkdir()
    (data_dir / "beta").mkdir()
    (data_dir / "alpha" / "alpha.json").write_text(
        json.dumps(first.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (data_dir / "beta" / "beta.json").write_text(
        json.dumps(second.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    session = ElectronBridgeSession(default_directory=tmp_path)

    result = session.handle({"type": "listReports", "payload": {}})

    assert result["ok"] is True
    reports = result["state"]["available_reports"]
    assert [item["stem"] for item in reports] == ["alpha", "beta"]
    assert reports[0]["path"] == str(data_dir / "alpha" / "alpha.json")
    assert reports[0]["report_id"] == "01"
    assert reports[0]["topic"] == "第一个项目"


def test_electron_bridge_lists_legacy_flat_reports_from_data_directory(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    report = WeeklyReport(report_id="01", topic="旧版平铺文件")
    legacy_json = data_dir / "legacy.json"
    legacy_json.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    session = ElectronBridgeSession(default_directory=tmp_path)

    result = session.handle({"type": "listReports", "payload": {}})

    assert result["ok"] is True
    assert result["state"]["available_reports"][0]["path"] == str(legacy_json)
    assert result["state"]["available_reports"][0]["stem"] == "legacy"


def test_electron_bridge_exports_data_backup_zip(tmp_path: Path):
    session = ElectronBridgeSession(default_directory=tmp_path)
    created = session.handle(
        {
            "type": "createReport",
            "payload": {"stem": "client-demo", "report_id": "01", "topic": "客户演示"},
        }
    )
    saved = session.handle({"type": "saveCurrent", "payload": {}})
    image_path = tmp_path / "source.png"
    image_path.write_bytes(b"png")
    report = saved["state"]["report"]
    report["projects"][0]["name"] = "演示项目"
    replaced = session.handle({"type": "replaceReport", "payload": {"report": report}})
    assert created["ok"] is True
    assert replaced["ok"] is True
    imported = session.handle(
        {
            "type": "importProjectImage",
            "payload": {"project_index": 0, "source_path": str(image_path)},
        }
    )
    assert imported["ok"] is True
    backup_path = tmp_path / "backup" / "weekflow-backup.zip"

    exported = session.handle({"type": "exportDataBackup", "payload": {"path": str(backup_path)}})

    assert exported["ok"] is True
    assert exported["state"]["backup_path"] == str(backup_path)
    assert backup_path.exists()
    with zipfile.ZipFile(backup_path) as archive:
        names = set(archive.namelist())
    assert "data/client-demo/client-demo.json" in names
    assert "data/client-demo/client-demo.md" in names
    assert "data/client-demo/figs/source.png" in names


def test_electron_bridge_returns_structured_error_for_unknown_command(tmp_path: Path):
    session = ElectronBridgeSession(default_directory=tmp_path)

    result = session.handle({"type": "missingCommand", "payload": {}})

    assert result["ok"] is False
    assert "Unsupported bridge command" in result["error"]["message"]


def test_electron_bridge_saves_opened_report_into_app_data_directory(tmp_path: Path):
    app_directory = tmp_path / "app"
    external_directory = tmp_path / "external"
    external_json = external_directory / "data" / "outside.json"
    external_json.parent.mkdir(parents=True)
    report = WeeklyReport(report_id="2601", topic="外部项目")
    external_json.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    session = ElectronBridgeSession(default_directory=app_directory)

    opened = session.handle({"type": "openReport", "payload": {"path": str(external_json)}})
    saved = session.handle({"type": "saveCurrent", "payload": {}})

    assert opened["ok"] is True
    assert saved["ok"] is True
    assert Path(saved["state"]["current_json_path"]) == app_directory / "data" / "outside" / "outside.json"
    assert Path(saved["state"]["current_markdown_path"]) == app_directory / "data" / "outside" / "outside.md"
    assert (app_directory / "data" / "outside" / "figs").is_dir()
    assert not (external_directory / "outside.md").exists()


def test_electron_bridge_stdout_is_utf8_even_when_windows_locale_is_not(tmp_path: Path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    env["PYTHONIOENCODING"] = "cp936"
    message = json.dumps(
        {
            "type": "createReport",
            "payload": {"report_id": "1", "topic": "中文主题"},
        },
        ensure_ascii=False,
    )

    result = subprocess.run(
        [sys.executable, "-m", "WeekFlow.electron_bridge", str(tmp_path)],
        input=f"{message}\n".encode("utf-8"),
        capture_output=True,
        timeout=10,
        env=env,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout.decode("utf-8"))
    assert payload["ok"] is True
    assert "中文主题" in payload["state"]["markdown"]

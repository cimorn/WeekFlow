import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_DEMO_JSON = ROOT / "examples" / "demo-2611.data.json"
LEGACY_DEMO_JSON = ROOT / "examples" / "demo-community.data.json"
NEW_DEMO_DIR = ROOT / "examples" / "data" / "demo-community"
NEW_DEMO_JSON = NEW_DEMO_DIR / "demo-community.json"
NEW_DEMO_MD = NEW_DEMO_DIR / "demo-community.md"
NEW_DEMO_IMAGE = NEW_DEMO_DIR / "figs" / "demo-result-01.png"


def test_old_demo_json_is_removed_and_new_demo_assets_exist():
    assert not OLD_DEMO_JSON.exists()
    assert not LEGACY_DEMO_JSON.exists()
    assert NEW_DEMO_DIR.exists()
    assert NEW_DEMO_JSON.exists()
    assert NEW_DEMO_MD.exists()
    assert NEW_DEMO_IMAGE.exists()


def test_new_demo_assets_use_new_chinese_content():
    payload = json.loads(NEW_DEMO_JSON.read_text(encoding="utf-8"))
    markdown_text = NEW_DEMO_MD.read_text(encoding="utf-8")

    assert payload["report_id"] == "第08周"
    assert payload["topic"] == "社区活动筹备与资料整理"
    assert payload["projects"][0]["name"] == "场地与物资确认"
    assert payload["projects"][0]["result_images"] == ["figs/demo-result-01.png"]
    assert payload["projects"][0]["issue"] == "场地动线和物资摆放已经整理成可直接执行的版本。\n活动前一天只需要按清单复核。"
    assert payload["achievements"][0] == "整理了活动流程、物资清单和志愿者分工表。"
    assert "Offline RL" not in markdown_text
    assert "社区活动筹备与资料整理" in markdown_text
    assert "![结果图 1](figs/demo-result-01.png)" in markdown_text

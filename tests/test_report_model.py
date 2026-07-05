from WeekFlow.models.report import ProjectItem, RecordItem, WeeklyReport


def test_report_to_dict_contains_expected_top_level_keys():
    report = WeeklyReport(report_id="2611", preview_theme="spring")

    payload = report.to_dict()

    assert payload["schema_version"] == 2
    assert payload["report_id"] == "2611"
    assert payload["preview_theme"] == "spring"
    assert payload["overview"]["mainlines"] == []
    assert payload["ai"]["provider"] == "openai_compatible"
    assert payload["ai"]["config"]["base_url"] == ""
    assert payload["ai"]["config"]["model"] == ""
    assert "projects" in payload
    assert "todos" in payload


def test_report_from_legacy_payload_adds_new_defaults():
    source = {
        "schema_version": 1,
        "report_id": "2611",
        "cycle": "2026.03.12 - 2026.03.18",
        "topic": "Community activity prep",
        "one_line_summary": "This week kept refining materials and onsite preparation.",
        "preview_theme": "pink",
        "overview": {
            "mainline": "Keep coordinating venue and sign-up details.",
            "judgment": "The overall arrangement is clearer than last week.",
            "focus": "Continue confirming onsite execution details.",
        },
        "projects": [
            {
                "name": "Venue setup",
                "summary": "The first inspection round is complete.",
                "issue": "Still need to confirm the final supply count.",
                "next_step": "Keep filling the remaining reminder materials.",
                "records": [
                    {
                        "time": "260318-1251",
                        "change": "Checked desks, routes, and sign-in spots.",
                        "result": "The onsite layout is much clearer now.",
                    }
                ],
            }
        ],
        "achievements": ["Organized the supply checklist and volunteer arrangement."],
        "todos": [{"done": False, "text": "Continue confirming the final registration count."}],
        "feeling": "The overall pace feels smoother now.",
        "ai": {"provider": None, "config": {}},
    }

    report = WeeklyReport.from_dict(source)
    payload = report.to_dict()

    assert payload["schema_version"] == 1
    assert payload["overview"]["mainline"] == "Keep coordinating venue and sign-up details."
    assert payload["overview"]["mainlines"] == ["Keep coordinating venue and sign-up details."]
    assert payload["projects"][0]["name"] == "Venue setup"
    assert payload["projects"][0]["result_images"] == []
    assert payload["todos"][0]["text"] == "Continue confirming the final registration count."
    assert payload["ai"]["provider"] == "openai_compatible"
    assert payload["ai"]["config"]["base_url"] == ""
    assert payload["ai"]["config"]["model"] == ""


def test_record_item_round_trips_name_field():
    item = RecordItem(date="260318", time="1251", name="Coordination", change="Adjust API", result="Verified")

    payload = item.to_dict()
    restored = RecordItem.from_dict(payload)

    assert payload["name"] == "Coordination"
    assert restored.name == "Coordination"


def test_project_item_round_trips_result_images():
    project = ProjectItem(
        name="Venue setup",
        issue="Result notes",
        result_images=["figs/result-001.png", "figs/result-002.jpg"],
    )

    payload = project.to_dict()
    restored = ProjectItem.from_dict(payload)

    assert payload["result_images"] == ["figs/result-001.png", "figs/result-002.jpg"]
    assert restored.result_images == ["figs/result-001.png", "figs/result-002.jpg"]


def test_legacy_project_payload_defaults_result_images_to_empty():
    restored = ProjectItem.from_dict({"name": "Venue setup", "issue": "Legacy result"})

    assert restored.issue == "Legacy result"
    assert restored.result_images == []

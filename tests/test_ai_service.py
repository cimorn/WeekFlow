import json
from io import BytesIO
from urllib.error import HTTPError

import pytest

from WeekFlow.models.report import ProjectItem, WeeklyReport
from WeekFlow.services.ai import AIConfigError, AIService


def _configured_report(**kwargs) -> WeeklyReport:
    report = WeeklyReport(**kwargs)
    report.ai["config"]["api_key"] = "test-key"
    report.ai["config"]["base_url"] = "https://example.test/v1"
    report.ai["config"]["model"] = "test-model"
    return report


def test_ai_service_requires_configuration():
    report = WeeklyReport()
    report.ai["config"]["api_key"] = ""

    service = AIService()

    try:
        service.test_connection(report)
    except AIConfigError as exc:
        assert "API Key" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected AIConfigError when API Key is missing")


def test_ai_service_rejects_aliyun_console_url():
    report = _configured_report()
    report.ai["provider"] = "openai_compatible"
    report.ai["config"]["base_url"] = "https://bailian.console.aliyun.com/cn-beijing#/api/?type=model"
    report.ai["config"]["model"] = "qwen-plus"

    service = AIService()

    with pytest.raises(AIConfigError) as exc_info:
        service.test_connection(report)

    message = str(exc_info.value)
    assert "控制台页面链接" in message
    assert "https://dashscope.aliyuncs.com/compatible-mode/v1" in message


def test_ai_service_rejects_unresolved_workspace_placeholder():
    report = _configured_report()
    report.ai["provider"] = "openai_compatible"
    report.ai["config"]["base_url"] = "https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
    report.ai["config"]["model"] = "qwen-plus"

    service = AIService()

    with pytest.raises(AIConfigError) as exc_info:
        service.test_connection(report)

    message = str(exc_info.value)
    assert "{WorkspaceId}" in message
    assert "真实业务空间 ID" in message


def test_ai_service_summarizes_basic_info_from_full_report(monkeypatch):
    report = _configured_report(
        topic="社区活动筹备",
        achievements=["完成了志愿者分工表", "整理了活动物资清单"],
        projects=[ProjectItem(name="项目 A", summary="完善报名说明", next_step="继续确认现场安排")],
    )
    service = AIService()
    seen_messages = {}

    def fake_chat(_config, messages):
        seen_messages["messages"] = messages
        return json.dumps({"one_line_summary": "集中整理了活动安排与资料信息。"}, ensure_ascii=False)

    monkeypatch.setattr(service, "_chat", fake_chat)

    polished = service.polish_current_section(report, section_key="basic_info")

    assert polished.one_line_summary == "集中整理了活动安排与资料信息。"
    prompt_text = seen_messages["messages"][1]["content"]
    assert "当前 Markdown" in prompt_text
    assert "精炼成一句总结" in prompt_text
    assert "## 项目进展" in prompt_text
    assert "项目 A" in prompt_text
    assert "完成了志愿者分工表" in prompt_text


def test_ai_service_polishes_feeling_as_segmented_emotional_reflection(monkeypatch):
    report = _configured_report(feeling="这周推进很累，但把关键问题理顺了。")
    service = AIService()
    seen_messages = {}

    def fake_chat(_config, messages):
        seen_messages["messages"] = messages
        return json.dumps({"feeling": "这周推进并不轻松，但关键问题终于被理顺。\n\n接下来更需要稳住节奏。"}, ensure_ascii=False)

    monkeypatch.setattr(service, "_chat", fake_chat)

    polished = service.polish_current_section(report, section_key="feeling")

    assert "\n\n" in polished.feeling
    prompt_text = seen_messages["messages"][1]["content"]
    assert "偏向复盘和情绪表达" in prompt_text
    assert "分成 2-3 段" in prompt_text


def test_ai_service_polishes_weekly_results_with_stubbed_response(monkeypatch):
    report = _configured_report(achievements=["旧成果"])
    service = AIService()

    def fake_chat(_config, _messages):
        return json.dumps({"achievements": ["新成果", "补充说明"]}, ensure_ascii=False)

    monkeypatch.setattr(service, "_chat", fake_chat)

    polished = service.polish_current_section(report, section_key="overview")

    assert polished.achievements == ["新成果", "补充说明"]


def test_ai_service_polishes_current_project_with_stubbed_response(monkeypatch):
    report = _configured_report(projects=[ProjectItem(name="项目 A", summary="旧内容", next_step="旧计划")])
    service = AIService()

    def fake_chat(_config, _messages):
        return json.dumps({"summary": "新内容", "next_step": "新计划"}, ensure_ascii=False)

    monkeypatch.setattr(service, "_chat", fake_chat)

    polished = service.polish_current_section(report, section_key="projects", project_index=0)

    assert polished.projects[0].name == "项目 A"
    assert polished.projects[0].summary == "新内容"
    assert polished.projects[0].next_step == "新计划"


def test_ai_service_uses_openai_compatible_defaults():
    report = WeeklyReport()

    assert report.ai["provider"] == "openai_compatible"
    assert report.ai["config"]["model"] == ""


def test_ai_service_uses_short_timeout_for_openai_compatible(monkeypatch):
    report = _configured_report()
    report.ai["provider"] = "openai_compatible"
    report.ai["config"]["base_url"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    report.ai["config"]["model"] = "qwen-plus"
    service = AIService()
    seen = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({"choices": [{"message": {"content": "连接成功"}}]}).encode("utf-8")

    def fake_urlopen(_req, timeout=60):
        seen["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("WeekFlow.services.ai.request.urlopen", fake_urlopen)

    assert service.test_connection(report) == "连接成功"
    assert seen["timeout"] == 20


def test_ai_service_uses_ark_sdk_for_volcengine_ark(monkeypatch):
    report = _configured_report()
    report.ai["provider"] = "volcengine_ark"
    report.ai["config"]["base_url"] = "https://ark.cn-beijing.volces.com/api/v3"
    report.ai["config"]["model"] = "doubao-seed-2-0-lite-260215"
    service = AIService()
    called = {}

    def fake_ark(self, config, messages):
        called["provider"] = config.provider
        called["message_count"] = len(messages)
        return "连接成功"

    def fail_openai(self, config, messages):  # pragma: no cover
        pytest.fail("volcengine_ark provider should use Ark SDK path")

    monkeypatch.setattr(AIService, "_chat_with_ark", fake_ark, raising=False)
    monkeypatch.setattr(AIService, "_chat_with_openai_compatible", fail_openai, raising=False)

    assert service.test_connection(report) == "连接成功"
    assert called["provider"] == "volcengine_ark"
    assert called["message_count"] == 2


def test_ai_service_maps_http_401_to_clear_configuration_hint(monkeypatch):
    report = _configured_report()
    report.ai["provider"] = "volcengine_plan"
    report.ai["config"]["base_url"] = "https://operator.las.cn-beijing.volces.com/api/v1"
    report.ai["config"]["model"] = "doubao-seed-2-0-pro-260215"
    service = AIService()

    def fake_urlopen(_req, timeout=60):
        raise HTTPError(
            url="https://operator.las.cn-beijing.volces.com/api/v1/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=BytesIO(b'{"path":"/api/v1/chat/completions","message":"Unauthorized"}'),
        )

    monkeypatch.setattr("WeekFlow.services.ai.request.urlopen", fake_urlopen)

    try:
        service.test_connection(report)
    except AIConfigError as exc:
        message = str(exc)
        assert "HTTP 401" in message
        assert "火山引擎plan" in message
        assert "API Key" in message
        assert "Base URL" in message
    else:  # pragma: no cover
        raise AssertionError("Expected AIConfigError for HTTP 401")


def test_ai_service_keeps_project_result_details_when_polishing(monkeypatch):
    report = _configured_report(
        projects=[
            ProjectItem(
                name="Project A",
                summary="old summary",
                issue="existing result note",
                next_step="old next",
                result_images=["figs/result-001.png"],
            )
        ]
    )
    service = AIService()

    def fake_chat(_config, _messages):
        return json.dumps({"summary": "new summary", "next_step": "new next"}, ensure_ascii=False)

    monkeypatch.setattr(service, "_chat", fake_chat)

    polished = service.polish_current_section(report, section_key="projects", project_index=0)

    assert polished.projects[0].summary == "new summary"
    assert polished.projects[0].next_step == "new next"
    assert polished.projects[0].issue == "existing result note"
    assert polished.projects[0].result_images == ["figs/result-001.png"]

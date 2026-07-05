import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from WeekFlow.controllers.editor_controller import EditorController
from WeekFlow.services.ai_config import (
    DEFAULT_AI_CONFIGS,
    normalize_ai_payload,
    normalize_ai_provider,
)
from WeekFlow.ui.sections.ai_config_section import AIConfigSection


def test_normalize_ai_provider_prefers_operator_url_for_plan():
    provider, defaults = normalize_ai_provider(
        "volcengine_ark",
        "https://operator.las.cn-beijing.volces.com/api/v1",
    )

    assert provider == "volcengine_plan"
    assert defaults["base_url"] == "https://operator.las.cn-beijing.volces.com/api/v1"
    assert defaults["model"] == DEFAULT_AI_CONFIGS["volcengine_plan"]["model"]


def test_normalize_ai_provider_prefers_ark_url_for_ark():
    provider, defaults = normalize_ai_provider(
        "volcengine_plan",
        "https://ark.cn-beijing.volces.com/api/v3",
    )

    assert provider == "volcengine_ark"
    assert defaults["base_url"] == "https://ark.cn-beijing.volces.com/api/v3"
    assert defaults["model"] == DEFAULT_AI_CONFIGS["volcengine_ark"]["model"]


def test_normalize_ai_provider_maps_legacy_operator_name():
    provider, defaults = normalize_ai_provider("volcengine_operator", "")

    assert provider == "volcengine_plan"
    assert defaults["base_url"] == DEFAULT_AI_CONFIGS["volcengine_plan"]["base_url"]


def test_free_tier_ai_provider_presets_are_available():
    assert DEFAULT_AI_CONFIGS["openrouter_free"]["base_url"] == "https://openrouter.ai/api/v1"
    assert DEFAULT_AI_CONFIGS["openrouter_free"]["model"].endswith(":free")
    assert DEFAULT_AI_CONFIGS["groq"]["base_url"] == "https://api.groq.com/openai/v1"
    assert DEFAULT_AI_CONFIGS["groq"]["model"] == "openai/gpt-oss-20b"
    assert DEFAULT_AI_CONFIGS["gemini"]["base_url"] == "https://generativelanguage.googleapis.com/v1beta/openai"
    assert DEFAULT_AI_CONFIGS["gemini"]["model"] == "gemini-3.5-flash"


def test_normalize_ai_provider_detects_public_free_tier_urls():
    assert normalize_ai_provider("openai_compatible", "https://openrouter.ai/api/v1")[0] == "openrouter_free"
    assert normalize_ai_provider("openai_compatible", "https://api.groq.com/openai/v1")[0] == "groq"
    assert (
        normalize_ai_provider("openai_compatible", "https://generativelanguage.googleapis.com/v1beta/openai")[0]
        == "gemini"
    )


def test_normalize_ai_payload_strips_pasted_chat_suffix_and_keeps_operator_url():
    payload = normalize_ai_payload(
        "openai_compatible",
        {"base_url": " https://operator.las.cn-beijing.volces.com/api/v1/chat/completions "},
    )

    assert payload["provider"] == "volcengine_plan"
    assert payload["config"]["base_url"] == "https://operator.las.cn-beijing.volces.com/api/v1"


def test_normalize_ai_payload_keeps_custom_pasted_url_and_existing_model():
    payload = normalize_ai_payload(
        "openai_compatible",
        {
            "base_url": "https://example.test/v1/chat/completions",
            "model": "custom-model",
            "api_key": "key",
        },
    )

    assert payload["provider"] == "openai_compatible"
    assert payload["config"]["base_url"] == "https://example.test/v1"
    assert payload["config"]["model"] == "custom-model"
    assert payload["config"]["api_key"] == "key"


def test_ai_config_section_syncs_provider_from_pasted_url_without_erasing_fields(tmp_path: Path):
    app = QApplication.instance() or QApplication([])
    controller = EditorController(default_directory=tmp_path)
    controller.create_new_report(report_id="2611")
    section = AIConfigSection(controller, lambda: None)
    section.load_from_report()

    section.provider_combo.setCurrentIndex(section.provider_combo.findData("openai_compatible"))
    section.api_key_edit.setText("keep-key")
    section.model_edit.setText("custom-model")
    section.system_prompt_edit.setPlainText("keep prompt")
    section.base_url_edit.setText(" https://ark.cn-beijing.volces.com/api/v3/responses ")
    app.processEvents()

    assert section.current_provider() == "volcengine_ark"
    assert section.base_url_edit.text() == "https://ark.cn-beijing.volces.com/api/v3"
    assert controller.report.ai["provider"] == "volcengine_ark"
    assert controller.report.ai["config"]["api_key"] == "keep-key"
    assert controller.report.ai["config"]["model"] == "custom-model"
    assert controller.report.ai["config"]["system_prompt"] == "keep prompt"

    section.close()

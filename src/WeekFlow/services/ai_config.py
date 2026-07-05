from __future__ import annotations

from copy import deepcopy


DEFAULT_SYSTEM_PROMPT = "你是周报润色助手。请保留事实、数字和结构，只优化措辞，使表达更清晰、专业、简洁。"


DEFAULT_AI_CONFIGS = {
    "volcengine_plan": {
        "base_url": "https://operator.las.cn-beijing.volces.com/api/v1",
        "model": "doubao-seed-2-0-pro-260215",
    },
    "volcengine_ark": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-seed-2-0-lite-260215",
    },
    "openrouter_free": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "openai/gpt-oss-20b",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-3.5-flash",
    },
    "openai_compatible": {
        "base_url": "",
        "model": "",
    },
}


PROVIDER_DISPLAY_NAMES = {
    "volcengine_plan": "火山引擎plan",
    "volcengine_ark": "火山方舟 Ark",
    "openrouter_free": "OpenRouter 免费模型",
    "groq": "Groq 免费层",
    "gemini": "Gemini 免费层",
    "openai_compatible": "自定义 OpenAI 兼容",
}


def _clean_base_url(base_url: str | None) -> str:
    cleaned = str(base_url or "").strip().rstrip("/")
    for suffix in ("/chat/completions", "/responses"):
        if cleaned.lower().endswith(suffix):
            return cleaned[: -len(suffix)].rstrip("/")
    return cleaned


def normalize_ai_provider(provider: str | None, base_url: str | None) -> tuple[str, dict[str, str]]:
    normalized = (provider or "openai_compatible").strip() or "openai_compatible"
    if normalized == "volcengine_operator":
        normalized = "volcengine_plan"

    lowered_url = _clean_base_url(base_url).lower()
    if "operator.las.cn-beijing.volces.com" in lowered_url:
        normalized = "volcengine_plan"
    elif "ark.cn-beijing.volces.com" in lowered_url:
        normalized = "volcengine_ark"
    elif "openrouter.ai" in lowered_url:
        normalized = "openrouter_free"
    elif "api.groq.com" in lowered_url:
        normalized = "groq"
    elif "generativelanguage.googleapis.com" in lowered_url:
        normalized = "gemini"

    if normalized not in DEFAULT_AI_CONFIGS:
        normalized = "openai_compatible"
    return normalized, deepcopy(DEFAULT_AI_CONFIGS[normalized])


def normalize_ai_payload(provider: str | None, config: dict | None) -> dict:
    incoming = dict(config or {})
    normalized_provider, defaults = normalize_ai_provider(provider, incoming.get("base_url", ""))

    base_url = _clean_base_url(incoming.get("base_url", "")) or defaults["base_url"]
    model = str(incoming.get("model", "")).strip() or defaults["model"]
    api_key = str(incoming.get("api_key", "")).strip()
    system_prompt = str(incoming.get("system_prompt", "")).strip() or DEFAULT_SYSTEM_PROMPT

    return {
        "provider": normalized_provider,
        "config": {
            "base_url": base_url,
            "api_key": api_key,
            "model": model,
            "system_prompt": system_prompt,
        },
    }


def provider_display_name(provider: str | None, base_url: str | None = None) -> str:
    normalized, _defaults = normalize_ai_provider(provider, base_url)
    return PROVIDER_DISPLAY_NAMES.get(normalized, normalized)

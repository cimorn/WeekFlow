from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from WeekFlow.models.report import ProjectItem, TodoItem, WeeklyReport
from WeekFlow.services.ai_config import (
    DEFAULT_SYSTEM_PROMPT,
    normalize_ai_payload,
    provider_display_name,
)
from WeekFlow.services.renderer import render_markdown


class AIConfigError(RuntimeError):
    pass


@dataclass(slots=True)
class AIConfig:
    provider: str
    base_url: str
    api_key: str
    model: str
    system_prompt: str


class AIService:
    def test_connection(self, report: WeeklyReport) -> str:
        config = self._config_from_report(report)
        content = self._chat(
            config,
            [
                {"role": "system", "content": "你是一个用于测试接口连通性的助手。"},
                {"role": "user", "content": "请只回复：连接成功"},
            ],
        )
        return content.strip()

    def polish_current_section(
        self,
        report: WeeklyReport,
        section_key: str,
        project_index: int | None = None,
    ) -> WeeklyReport:
        config = self._config_from_report(report)
        if section_key == "basic_info":
            report.one_line_summary = self._summarize_report(config, report)
            return report

        if section_key == "overview":
            payload = {"achievements": list(report.achievements)}
            polished = self._polish_json(config, "润色本周成果卡片", payload)
            report.achievements = [item.strip() for item in polished.get("achievements", payload["achievements"]) if item.strip()]
            return report

        if section_key == "projects":
            if project_index is None or project_index < 0 or project_index >= len(report.projects):
                raise AIConfigError("当前没有可润色的项目，请先选中一个项目。")
            project = report.projects[project_index]
            payload = {
                "summary": project.summary,
                "next_step": project.next_step,
            }
            polished = self._polish_json(config, f"润色项目进展：{project.name}", payload)
            report.projects[project_index] = ProjectItem(
                name=project.name,
                summary=polished.get("summary", project.summary).strip(),
                issue=project.issue,
                next_step=polished.get("next_step", project.next_step).strip(),
                result_images=project.result_images,
                records=project.records,
            )
            return report

        if section_key == "todos":
            payload = {"todos": [item.text for item in report.todos]}
            polished = self._polish_json(config, "润色待跟进事项", payload)
            done_flags = [item.done for item in report.todos]
            report.todos = [
                TodoItem(done=done_flags[index] if index < len(done_flags) else False, text=text.strip())
                for index, text in enumerate(polished.get("todos", payload["todos"]))
                if text.strip()
            ]
            return report

        if section_key == "feeling":
            report.feeling = self._polish_feeling(config, report)
            return report

        if section_key == "preview":
            return self.polish_report(report)

        raise AIConfigError("当前板块暂不支持 AI 润色。")

    def polish_report(self, report: WeeklyReport) -> WeeklyReport:
        config = self._config_from_report(report)
        payload = {
            "one_line_summary": report.one_line_summary,
            "achievements": list(report.achievements),
            "projects": [
                {
                    "name": project.name,
                    "summary": project.summary,
                    "next_step": project.next_step,
                }
                for project in report.projects
            ],
            "todos": [item.text for item in report.todos],
            "feeling": report.feeling,
        }
        polished = self._polish_json(config, "润色整篇周报", payload)

        report.one_line_summary = polished.get("one_line_summary", report.one_line_summary).strip()
        report.achievements = [item.strip() for item in polished.get("achievements", report.achievements) if item.strip()]

        incoming_projects = polished.get("projects", [])
        for index, project in enumerate(report.projects):
            if index >= len(incoming_projects):
                continue
            polished_project = incoming_projects[index]
            report.projects[index] = ProjectItem(
                name=project.name,
                summary=polished_project.get("summary", project.summary).strip(),
                issue=project.issue,
                next_step=polished_project.get("next_step", project.next_step).strip(),
                result_images=project.result_images,
                records=project.records,
            )

        done_flags = [item.done for item in report.todos]
        report.todos = [
            TodoItem(done=done_flags[index] if index < len(done_flags) else False, text=text.strip())
            for index, text in enumerate(polished.get("todos", [item.text for item in report.todos]))
            if text.strip()
        ]
        report.feeling = polished.get("feeling", report.feeling).strip()
        return report

    def _summarize_report(self, config: AIConfig, report: WeeklyReport) -> str:
        markdown = render_markdown(report)
        content = self._chat(
            config,
            [
                {"role": "system", "content": config.system_prompt or DEFAULT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "请阅读当前 Markdown 周报内容，提炼本周最核心的一句话总结。\n"
                        "要求：精炼成一句总结，不超过 45 个中文字符；只写已经在 Markdown 中出现的信息，不要补充新事实。\n"
                        "请只返回 JSON，格式为 {\"one_line_summary\": \"...\"}。\n\n"
                        f"当前 Markdown：\n{markdown}"
                    ),
                },
            ],
        )
        payload = json.loads(self._extract_json(content))
        return str(payload.get("one_line_summary", "")).strip()

    def _polish_feeling(self, config: AIConfig, report: WeeklyReport) -> str:
        markdown = render_markdown(report)
        payload = {"feeling": report.feeling}
        schema = json.dumps(payload, ensure_ascii=False, indent=2)
        content = self._chat(
            config,
            [
                {"role": "system", "content": config.system_prompt or DEFAULT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "请润色“本周感受”，偏向复盘和情绪表达，不要写成工作成果总结。\n"
                        "要求：保留原有事实和情绪，不编造新事情；语气自然、克制、有一点个人感受；分成 2-3 段，段落之间用空行分隔。\n"
                        "请参考当前 Markdown 的上下文，但输出只改 feeling 字段。\n"
                        "请只返回 JSON，不要输出解释。\n\n"
                        f"输入 JSON：\n{schema}\n\n"
                        f"当前 Markdown：\n{markdown}"
                    ),
                },
            ],
        )
        polished = json.loads(self._extract_json(content))
        return str(polished.get("feeling", report.feeling)).strip()

    def _config_from_report(self, report: WeeklyReport) -> AIConfig:
        normalized = normalize_ai_payload(
            report.ai.get("provider"),
            report.ai.get("config", {}),
        )
        report.ai = normalized
        ai_config = normalized.get("config", {})
        config = AIConfig(
            provider=str(normalized.get("provider", "openai_compatible")),
            base_url=str(ai_config.get("base_url", "")).strip(),
            api_key=str(ai_config.get("api_key", "")).strip(),
            model=str(ai_config.get("model", "")).strip(),
            system_prompt=str(ai_config.get("system_prompt", "")).strip(),
        )
        if not config.api_key:
            raise AIConfigError("AI 还没有配置 API Key，请先在 AI 配置页面完成填写。")
        if not config.base_url:
            raise AIConfigError("AI 还没有配置 Base URL，请先在 AI 配置页面完成填写。")
        if not config.model:
            raise AIConfigError("AI 还没有配置 Model / Endpoint，请先在 AI 配置页面完成填写。")
        self._validate_base_url(config.base_url)
        return config

    def _validate_base_url(self, base_url: str) -> None:
        lowered = base_url.lower()
        if "bailian.console.aliyun.com" in lowered or "modelstudio.console.aliyun.com" in lowered:
            raise AIConfigError(
                "这个不是模型 API 地址，而是阿里云百炼控制台页面链接。\n"
                "请在 Base URL 填 OpenAI 兼容接口地址，例如：\n"
                "https://dashscope.aliyuncs.com/compatible-mode/v1\n"
                "或把业务空间地址中的 {WorkspaceId} 替换成真实业务空间 ID：\n"
                "https://你的业务空间ID.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
            )
        if "{workspaceid}" in lowered or "{workspace_id}" in lowered or "{" in base_url or "}" in base_url:
            raise AIConfigError(
                "Base URL 里还有占位符，不能直接测试。\n"
                "请把 {WorkspaceId} 替换成阿里云百炼里的真实业务空间 ID。\n"
                "华北 2（北京）示例：\n"
                "https://你的业务空间ID.cn-beijing.maas.aliyuncs.com/compatible-mode/v1\n"
                "如果暂时不想填业务空间专属域名，也可以先用：\n"
                "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )

    def _polish_json(self, config: AIConfig, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        schema = json.dumps(payload, ensure_ascii=False, indent=2)
        user_prompt = (
            f"任务：{task}\n"
            "请保留事实、数字、实体名和结构，只优化表达，使其更简洁、专业、自然。\n"
            "请只返回 JSON，不要输出解释。\n"
            f"输入 JSON：\n{schema}"
        )
        content = self._chat(
            config,
            [
                {"role": "system", "content": config.system_prompt or DEFAULT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        try:
            return json.loads(self._extract_json(content))
        except json.JSONDecodeError as exc:
            raise AIConfigError(f"AI 返回内容无法解析为 JSON，请稍后重试。\n原始返回：{content}") from exc

    def _chat(self, config: AIConfig, messages: list[dict[str, str]]) -> str:
        if config.provider == "volcengine_ark":
            return self._chat_with_ark(config, messages)
        return self._chat_with_openai_compatible(config, messages)

    def _chat_with_openai_compatible(self, config: AIConfig, messages: list[dict[str, str]]) -> str:
        endpoint = self._chat_endpoint(config.base_url)
        payload = json.dumps(
            {
                "model": config.model,
                "temperature": 0.3,
                "messages": messages,
            }
        ).encode("utf-8")

        req = request.Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.api_key}",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=20) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise AIConfigError(self._build_http_error_message(config, exc.code, detail)) from exc
        except error.URLError as exc:
            raise AIConfigError(f"AI 请求失败，无法连接到服务。\n{exc}") from exc

        choices = body.get("choices", [])
        if not choices:
            raise AIConfigError(f"AI 返回为空：{body}")
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, list):
            return "".join(str(item.get("text", "")) for item in content if isinstance(item, dict))
        return str(content)

    def _chat_with_ark(self, config: AIConfig, messages: list[dict[str, str]]) -> str:
        try:
            from volcenginesdkarkruntime import Ark
        except ImportError as exc:  # pragma: no cover - depends on local env
            raise AIConfigError("未安装火山方舟 SDK，请先安装 volcengine-python-sdk[ark]。") from exc

        system_message = "\n\n".join(
            item["content"].strip()
            for item in messages
            if item.get("role") == "system" and item.get("content", "").strip()
        )
        user_blocks = [
            item["content"].strip()
            for item in messages
            if item.get("role") != "system" and item.get("content", "").strip()
        ]
        response = Ark(base_url=config.base_url, api_key=config.api_key).responses.create(
            model=config.model,
            instructions=system_message or None,
            input="\n\n".join(user_blocks),
        )
        return self._extract_ark_response_text(response)

    def _chat_endpoint(self, base_url: str) -> str:
        normalized = base_url.rstrip("/")
        if normalized.endswith("/chat/completions"):
            return normalized
        return f"{normalized}/chat/completions"

    def _extract_ark_response_text(self, response: object) -> str:
        direct_text = getattr(response, "output_text", "")
        if isinstance(direct_text, str) and direct_text.strip():
            return direct_text

        if hasattr(response, "model_dump"):
            payload = response.model_dump()
        elif isinstance(response, dict):
            payload = response
        else:
            payload = getattr(response, "__dict__", {})

        outputs = payload.get("output", []) if isinstance(payload, dict) else []
        parts: list[str] = []
        for output in outputs:
            for content_item in output.get("content", []):
                text = content_item.get("text", "")
                if text:
                    parts.append(str(text))
        if parts:
            return "".join(parts)
        return str(response)

    def _build_http_error_message(self, config: AIConfig, code: int, detail: str) -> str:
        message = [f"AI 请求失败（HTTP {code}）。"]
        if code == 401:
            provider_label = provider_display_name(config.provider, config.base_url)
            message.extend(
                [
                    f"当前 Provider：{provider_label}",
                    "请优先检查以下几项：",
                    "1. API Key 是否填写正确，并且确实来自当前 Provider。",
                    f"2. Base URL 是否正确：{config.base_url}",
                    f"3. Model / Endpoint 是否正确：{config.model}",
                ]
            )
            if config.provider == "volcengine_plan":
                message.append(
                    "火山引擎plan 默认使用 https://operator.las.cn-beijing.volces.com/api/v1，并配合对应服务的 API Key。"
                )
        if detail:
            message.append(detail)
        return "\n".join(message)

    def _extract_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            return text
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return text[start : end + 1]
        raise AIConfigError(f"AI 返回中没有找到 JSON 内容。\n原始返回：{text}")

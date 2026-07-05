from __future__ import annotations

from WeekFlow.models.report import ProjectItem, WeeklyReport


def build_report_template(report_id: str, cycle: str = "", topic: str = "") -> WeeklyReport:
    return WeeklyReport(
        report_id=report_id,
        cycle=cycle,
        topic=topic,
        preview_theme="report",
        one_line_summary="",
        overview={
            "mainline": "",
            "mainlines": [],
            "judgment": "",
            "focus": "",
        },
        projects=[ProjectItem()],
        achievements=[],
        todos=[],
        feeling="",
        ai={
            "provider": "openai_compatible",
            "config": {
                "base_url": "",
                "api_key": "",
                "model": "",
                "system_prompt": "你是周报润色助手。请保留事实、数字和结构，只优化措辞，使表达更清晰、专业、简洁。",
            },
        },
    )

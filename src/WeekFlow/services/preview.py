from __future__ import annotations

import re
from html import escape

from markdown import markdown

from WeekFlow.models.report import ProjectItem, RecordItem, WeeklyReport
from WeekFlow.services.ai_config import provider_display_name
from WeekFlow.services.renderer import (
    render_feeling_lines,
    render_header_lines,
    render_markdown,
    render_meta_line,
    render_projects_lines,
    render_results_lines,
    render_title,
    render_todos_lines,
)
from WeekFlow.ui.theme import normalize_theme_key, preview_css_for


_BR_TAG_PATTERN = re.compile(r"(?i)<br\s*/?>")


def render_section_markdown(
    report: WeeklyReport,
    section_key: str,
    project_index: int | None = None,
) -> str:
    if section_key == "basic_info":
        return "\n".join(render_header_lines(report))
    if section_key == "overview":
        return "\n".join(render_results_lines(report))
    if section_key == "projects":
        return "\n".join(render_projects_lines(report, project_index=project_index))
    if section_key == "todos":
        return "\n".join(render_todos_lines(report))
    if section_key == "feeling":
        return "\n".join(render_feeling_lines(report))
    if section_key == "preview":
        return render_markdown(report)
    if section_key == "ai_config":
        return "## AI 配置\n\n- 在这里配置火山引擎、OpenRouter、Groq、Gemini 或其他兼容模型。"
    return "\n".join(render_header_lines(report))


def build_preview_document(
    report: WeeklyReport,
    section_key: str,
    theme_key: str | None = None,
    project_index: int | None = None,
) -> str:
    active_theme = normalize_theme_key(theme_key or report.preview_theme)
    mode = "document" if section_key == "preview" else "section"
    if active_theme == "report":
        body_html = _build_report_theme_markup(report, section_key, project_index)
    else:
        body_html = markdown(
            _normalize_markdown_breaks(render_section_markdown(report, section_key, project_index=project_index)),
            extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
        )
    return _wrap_preview_body(body_html, mode=mode, theme_key=active_theme)


def render_preview_html(markdown_text: str, mode: str = "section", theme_key: str = "report") -> str:
    body_html = markdown(
        _normalize_markdown_breaks(markdown_text),
        extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
    )
    return _wrap_preview_body(body_html, mode=mode, theme_key=theme_key)


def _wrap_preview_body(body_html: str, mode: str, theme_key: str) -> str:
    active_theme = normalize_theme_key(theme_key)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>{preview_css_for(active_theme)}</style>
  </head>
  <body data-theme="{active_theme}">
    <div class="preview-shell {mode}-view" data-theme="{active_theme}">
      <div class="preview-paper">
        {body_html}
      </div>
    </div>
  </body>
</html>
"""


def _build_report_theme_markup(report: WeeklyReport, section_key: str, project_index: int | None) -> str:
    blocks: list[str] = []
    if section_key in {"basic_info", "preview"}:
        blocks.append(_render_header_markup(report))
    if section_key in {"overview", "preview"}:
        blocks.append(_render_results_markup(report))
    if section_key in {"projects", "preview"}:
        blocks.append(_render_projects_markup(report, project_index))
    if section_key in {"todos", "preview"}:
        blocks.append(_render_todos_markup(report))
    if section_key in {"feeling", "preview"}:
        blocks.append(_render_feeling_markup(report))
    if section_key == "ai_config":
        blocks.append(_render_ai_markup(report))
    return "\n".join(block for block in blocks if block.strip())


def _render_header_markup(report: WeeklyReport) -> str:
    parts = [f"<h1>{escape(render_title(report.report_id))}</h1>"]
    meta = render_meta_line(report)
    if meta:
        parts.append(f'<p class="report-meta">{escape(meta)}</p>')
    if report.one_line_summary.strip():
        parts.append(f'<div class="hero-summary">{_format_rich_text(report.one_line_summary.strip())}</div>')
    return f'<div class="report-hero">{"".join(parts)}</div>'


def _render_results_markup(report: WeeklyReport) -> str:
    achievements = [item.strip() for item in report.achievements if item.strip()]
    cards = "\n".join(
        f'<div class="achievement-card"><p>{_format_rich_text(item)}</p></div>'
        for item in achievements
    )
    if not cards:
        cards = '<div class="plain-card"><p>本周成果将在这里汇总显示。</p></div>'
    return f"""
<h2>本周成果</h2>
<div class="achievement-grid">
  {cards}
</div>
""".strip()


def _render_projects_markup(report: WeeklyReport, project_index: int | None) -> str:
    projects = _selected_projects(report, project_index)
    blocks = ["<h2>项目进展</h2>"]
    if not projects:
        blocks.append('<div class="plain-card"><p>项目进展将在这里显示。</p></div>')
        return "\n".join(blocks)
    for project in projects:
        blocks.append(_render_project_box(project))
    return "\n".join(blocks)


def _render_project_box(project: ProjectItem) -> str:
    summary_html = f"""
<table class="project-summary-table">
  <thead>
    <tr>
      <th>名称</th>
      <th>内容</th>
      <th>预计</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>{_format_rich_text(project.name.strip())}</td>
      <td>{_format_rich_text(project.summary.strip())}</td>
      <td>{_format_rich_text(project.next_step.strip())}</td>
    </tr>
  </tbody>
</table>
""".strip()

    result_html = _render_project_result_block(project)
    timeline_html = _render_timeline_table(project.records)

    return f"""
<div class="project-compact-box">
  {summary_html}
  {result_html}
  {timeline_html}
</div>
""".strip()


def _render_project_result_block(project: ProjectItem) -> str:
    has_copy = bool(project.issue.strip())
    has_images = any(path.strip() for path in project.result_images)

    copy_html = ""
    if has_copy:
        copy_html = f'<div class="project-result-copy">{_format_rich_text(project.issue.strip())}</div>'

    images_html = ""
    image_items = [
        _render_result_image_card(relative_path.strip(), index)
        for index, relative_path in enumerate(project.result_images, start=1)
        if relative_path.strip()
    ]
    if image_items:
        images_html = '<div class="result-image-grid">' + "".join(image_items) + "</div>"

    if not copy_html and not images_html:
        copy_html = '<div class="project-result-copy muted">暂未填写结果内容</div>'

    return f"""
<div class="project-result-block">
  <h4>结果</h4>
  {copy_html}
  {images_html}
</div>
""".strip()


def _render_result_image_card(relative_path: str, index: int) -> str:
    source = escape(relative_path)
    label = escape(f"结果图 {index}")
    return f"""
<figure class="result-image-card">
  <img src="{source}" alt="{label}" />
  <figcaption>{label}</figcaption>
</figure>
""".strip()


def _render_timeline_table(records: list[RecordItem]) -> str:
    rows: list[str] = []
    for record in records:
        date, time = record.normalized_date_time()
        name = record.name.strip()
        change = record.change.strip()
        result = record.result.strip()
        if date or time or name or change or result:
            rows.append(
                f"""
<tr>
  <td>{escape(date)}</td>
  <td>{escape(time)}</td>
  <td>{_format_rich_text(name)}</td>
  <td>{_format_rich_text(change)}</td>
  <td>{_format_rich_text(result)}</td>
</tr>
""".strip()
            )

    if not rows:
        return ""

    rows_html = "\n      ".join(rows)
    return f"""
<div class="timeline-table-wrap">
  <table class="timeline-table">
    <thead>
      <tr>
        <th>日期</th>
        <th>时间</th>
        <th>名称</th>
        <th>内容</th>
        <th>结果</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</div>
""".strip()


def _render_todos_markup(report: WeeklyReport) -> str:
    rows = "\n".join(
        f"""
<div class="todo-check-row{' done' if todo.done else ''}">
  <span class="todo-indicator">{'✓' if todo.done else ''}</span>
  <span class="todo-text">{_format_rich_text(todo.text.strip())}</span>
</div>
""".strip()
        for todo in report.todos
        if todo.text.strip()
    )
    if not rows:
        rows = '<div class="plain-card"><p>待跟进事项会在这里显示。</p></div>'
    return f"""
<h2>待跟进事项</h2>
<div class="todo-list-card">
  {rows}
</div>
""".strip()


def _render_feeling_markup(report: WeeklyReport) -> str:
    if not report.feeling.strip():
        return ""
    return f"""
<h2>本周感受</h2>
<div class="feeling-card">{_format_rich_text(report.feeling.strip())}</div>
""".strip()


def _render_ai_markup(report: WeeklyReport) -> str:
    config = report.ai.get("config", {})
    api_key_status = "已填写" if config.get("api_key") else "未填写"
    return f"""
<h2>AI 配置</h2>
<div class="plain-card">
  <p><strong>Provider:</strong> {escape(provider_display_name(report.ai.get('provider'), config.get('base_url', '')))}</p>
  <p><strong>Base URL:</strong> {escape(config.get('base_url', ''))}</p>
  <p><strong>Model / Endpoint:</strong> {escape(config.get('model', ''))}</p>
  <p><strong>API Key:</strong> {api_key_status}</p>
</div>
""".strip()


def _selected_projects(report: WeeklyReport, project_index: int | None) -> list[ProjectItem]:
    projects = report.projects
    if project_index is not None and projects:
        safe_index = max(0, min(project_index, len(projects) - 1))
        return [projects[safe_index]]
    return projects


def _normalize_markdown_breaks(text: str) -> str:
    return _BR_TAG_PATTERN.sub("<br />", text)


def _format_rich_text(value: str) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    normalized = _BR_TAG_PATTERN.sub("\n", normalized)
    return "<br />".join(escape(part) for part in normalized.split("\n"))

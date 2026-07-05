from __future__ import annotations

from WeekFlow.models.report import ProjectItem, RecordItem, WeeklyReport


def render_markdown(report: WeeklyReport) -> str:
    sections = [
        render_header_lines(report),
        render_results_lines(report),
        render_projects_lines(report),
        render_todos_lines(report),
        render_feeling_lines(report),
    ]
    return "\n\n".join("\n".join(lines) for lines in sections if lines)


def render_header_lines(report: WeeklyReport) -> list[str]:
    lines = [f"# {render_title(report.report_id)}"]
    meta_line = render_meta_line(report)
    if meta_line:
        lines.append(meta_line)
    summary_block = render_summary_block(report)
    if summary_block:
        lines.append(summary_block)
    return lines


def render_results_lines(report: WeeklyReport) -> list[str]:
    lines = ["## 本周成果"]
    achievements = [item.strip() for item in report.achievements if item.strip()]
    if achievements:
        lines.append("")
        lines.extend(f"- {item}" for item in achievements)
    return lines


def render_projects_lines(report: WeeklyReport, project_index: int | None = None) -> list[str]:
    lines = ["## 项目进展"]
    projects = report.projects
    if project_index is not None and projects:
        safe_index = max(0, min(project_index, len(projects) - 1))
        projects = [projects[safe_index]]

    if not projects:
        return lines

    for project in projects:
        lines.extend(["", *render_project_lines(project)])
    return lines


def render_todos_lines(report: WeeklyReport) -> list[str]:
    lines = ["## 待跟进事项"]
    todo_lines = []
    for todo in report.todos:
        text = todo.text.strip()
        if not text:
            continue
        marker = "x" if todo.done else " "
        todo_lines.append(f"- [{marker}] {text}")
    if todo_lines:
        lines.extend(["", *todo_lines])
    return lines


def render_feeling_lines(report: WeeklyReport) -> list[str]:
    lines = ["## 本周感受"]
    feeling = report.feeling.strip()
    if feeling:
        lines.extend(["", *_normalize_rich_text(feeling)])
    return lines


def render_title(report_id: str) -> str:
    week_suffix = report_id[-2:] if len(report_id) >= 2 else report_id or "00"
    try:
        week_number = int(week_suffix)
        return f"Week {week_number:02d}"
    except ValueError:
        return report_id or "Weekly Report"


def render_meta_line(report: WeeklyReport) -> str:
    topic = report.topic.strip()
    return f"主题：{topic}" if topic else ""


def render_summary_block(report: WeeklyReport) -> str:
    summary = report.one_line_summary.strip()
    return f"> {summary}" if summary else ""


def render_project_lines(project: ProjectItem) -> list[str]:
    lines: list[str] = []
    title = project.name.strip()
    if title:
        lines.append(f"### {title}")

    summary_lines = _render_project_summary_table_lines(project)
    if summary_lines:
        if lines:
            lines.append("")
        lines.extend(summary_lines)

    result_lines = _render_project_result_lines(project)
    if result_lines:
        if lines:
            lines.append("")
        lines.extend(result_lines)

    record_lines = _render_record_table_lines(project.records)
    if record_lines:
        if lines:
            lines.append("")
        lines.extend(record_lines)
    return lines


def _render_project_summary_table_lines(project: ProjectItem) -> list[str]:
    if not any(
        [
            project.name.strip(),
            project.summary.strip(),
            project.next_step.strip(),
        ]
    ):
        return []

    return [
        "| 名称 | 内容 | 预计 |",
        "| :--: | :--: | :--: |",
        (
            f"| {_escape_md_cell(project.name.strip())} | "
            f"{_escape_md_cell(project.summary.strip())} | "
            f"{_escape_md_cell(project.next_step.strip())} |"
        ),
    ]


def _render_project_result_lines(project: ProjectItem) -> list[str]:
    if not project.issue.strip() and not project.result_images:
        return []

    lines = ["#### 结果"]
    issue_lines = _normalize_rich_text(project.issue)
    if issue_lines:
        lines.extend(["", *issue_lines])

    image_lines = [
        f"![结果图 {index}]({relative_path.strip()})"
        for index, relative_path in enumerate(project.result_images, start=1)
        if relative_path.strip()
    ]
    if image_lines:
        lines.extend(["", *image_lines] if issue_lines else ["", *image_lines])
    return lines


def _render_record_table_lines(records: list[RecordItem]) -> list[str]:
    rows: list[str] = []
    for record in records:
        date, time = record.normalized_date_time()
        name = record.name.strip()
        change = record.change.strip()
        result = record.result.strip()
        if date or time or name or change or result:
            rows.append(
                f"| {_escape_md_cell(date)} | {_escape_md_cell(time)} | {_escape_md_cell(name)} | "
                f"{_escape_md_cell(change)} | {_escape_md_cell(result)} |"
            )

    if not rows:
        return []

    return [
        "| 日期 | 时间 | 名称 | 内容 | 结果 |",
        "| :--: | :--: | :--: | :--: | :--: |",
        *rows,
    ]


def _normalize_rich_text(value: str) -> list[str]:
    normalized = value.replace("<BR>", "\n").replace("<br>", "\n").strip()
    return [line.rstrip() for line in normalized.splitlines() if line.strip()]


def _escape_md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>").replace("<BR>", "<br>").replace("<br>", "<br>")

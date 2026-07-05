from WeekFlow.models.report import ProjectItem, RecordItem, TodoItem, WeeklyReport
from WeekFlow.services.preview import (
    build_preview_document,
    render_preview_html,
    render_section_markdown,
)


def _sample_report() -> WeeklyReport:
    return WeeklyReport(
        report_id="2611",
        cycle="2026.03.19 - 2026.03.25",
        topic="Community activity prep",
        one_line_summary="This week focused on venue prep and result review.",
        projects=[
            ProjectItem(
                name="Venue setup",
                summary="Finished the first onsite review",
                issue="Execution conditions are now clearly aligned<BR>Ready to lock the final seat map.",
                next_step="Confirm the remaining supplies",
                result_images=["figs/result-001.png"],
                records=[
                    RecordItem(
                        date="2026.03.24",
                        time="10:30",
                        name="Coordination",
                        change="Checked table layout and route",
                        result="Onsite arrangement is clearer now",
                    )
                ],
            ),
            ProjectItem(
                name="Sign-up follow-up",
                summary="Closed the late registration list",
                issue="The reminder copy is now aligned",
                next_step="Send the final reminder message",
                records=[
                    RecordItem(
                        date="2026.03.25",
                        time="18:20",
                        name="Reminder",
                        change="Adjusted the closing message",
                        result="The wording is now consistent",
                    )
                ],
            ),
        ],
        achievements=["Finished materials checklist", "Completed sign-up summary"],
        todos=[TodoItem(done=False, text="Keep confirming the final attendance count")],
        feeling="Progress this week was smoother and the conclusion is clearer.",
    )


def test_weekly_results_preview_contains_cards_only():
    markdown = render_section_markdown(_sample_report(), "overview")

    assert "## 本周成果" in markdown
    assert "Finished materials checklist" in markdown
    assert "主线" not in markdown
    assert "阶段判断" not in markdown


def test_projects_preview_only_contains_selected_project():
    markdown = render_section_markdown(_sample_report(), "projects", project_index=1)

    assert "## 项目进展" in markdown
    assert "### Sign-up follow-up" in markdown
    assert "| 名称 | 内容 | 预计 |" in markdown
    assert "Send the final reminder message" in markdown
    assert "Venue setup" not in markdown


def test_preview_section_returns_full_report():
    markdown = render_section_markdown(_sample_report(), "preview")

    assert "# Week 11" in markdown
    assert "## 本周成果" in markdown
    assert "## 项目进展" in markdown
    assert "### Venue setup" in markdown


def test_preview_html_wraps_markdown_with_theme():
    html = render_preview_html("## 本周成果\n\n- Confirm reward shaping gain\n", mode="section", theme_key="spring")

    assert "<style>" in html
    assert "--weekly-accent" in html
    assert 'class="preview-shell section-view"' in html
    assert 'data-theme="spring"' in html
    assert "<h2>本周成果</h2>" in html


def test_report_theme_preview_uses_summary_table_result_block_and_timeline():
    html = build_preview_document(_sample_report(), section_key="preview", theme_key="report")

    assert 'class="achievement-card"' in html
    assert 'class="project-compact-box"' in html
    assert 'class="project-summary-table"' in html
    assert "<th>名称</th>" in html
    assert "<th>内容</th>" in html
    assert "<th>预计</th>" in html
    assert "<td>Venue setup</td>" in html
    assert "<td>Finished the first onsite review</td>" in html
    assert "<td>Confirm the remaining supplies</td>" in html
    assert 'class="project-result-block"' in html
    assert "<h4>结果</h4>" in html
    assert "Execution conditions are now clearly aligned<br />Ready to lock the final seat map." in html
    assert 'class="result-image-grid"' in html
    assert 'src="figs/result-001.png"' in html
    assert 'class="timeline-table-wrap"' in html
    assert "<th>日期</th>" in html
    assert "<th>时间</th>" in html
    assert "<th>名称</th>" in html
    assert "<th>内容</th>" in html
    assert "<th>结果</th>" in html
    assert 'class="todo-check-row"' in html
    assert "font-size: 10pt;" in html
    assert "font-size: 12pt;" in html
    assert ".project-summary-table td {" in html
    assert ".project-result-block {" in html
    assert ".result-image-grid {" in html
    assert ".timeline-table tbody td {" in html


def test_report_theme_preview_supports_br_line_breaks_in_project_fields():
    report = WeeklyReport(
        report_id="2611",
        projects=[
            ProjectItem(
                name="Project A",
                summary="Line one<BR>Line two",
                issue="Result one<BR>Result two",
                next_step="Keep going",
                records=[
                    RecordItem(
                        date="2026.03.24",
                        time="10:30",
                        name="Coordination",
                        change="Line one<BR>Line two",
                        result="Result A\nResult B",
                    )
                ],
            )
        ],
    )

    html = build_preview_document(report, section_key="preview", theme_key="report")

    assert "Line one<br />Line two" in html
    assert "Result one<br />Result two" in html
    assert "Result A<br />Result B" in html
    assert "&lt;BR&gt;" not in html

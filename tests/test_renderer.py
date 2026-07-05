from WeekFlow.models.report import ProjectItem, RecordItem, WeeklyReport
from WeekFlow.services.renderer import render_markdown, render_title


def test_render_title_uses_week_format_for_numeric_report_id():
    assert render_title("2611") == "Week 11"
    assert render_title("2603") == "Week 03"


def test_renderer_outputs_topic_and_weekly_results_without_cycle():
    report = WeeklyReport(
        report_id="2611",
        cycle="2026.03.12 - 2026.03.18",
        topic="Community activity prep",
        achievements=["Finished materials checklist", "Completed sign-up summary"],
    )

    markdown = render_markdown(report)

    assert "# Week 11" in markdown
    assert "主题：Community activity prep" in markdown
    assert "周期：" not in markdown
    assert "## 本周成果" in markdown
    assert "- Finished materials checklist" in markdown
    assert "- Completed sign-up summary" in markdown


def test_renderer_outputs_projects_with_summary_table_result_section_and_record_table():
    report = WeeklyReport(
        report_id="2611",
        projects=[
            ProjectItem(
                name="Venue setup",
                summary="Finished the first onsite review",
                issue="Execution conditions are now clearly aligned",
                next_step="Confirm the remaining supplies",
                result_images=["figs/result-001.png"],
                records=[
                    RecordItem(
                        time="260318-1251",
                        name="Coordination",
                        change="Checked table layout and route",
                        result="Onsite arrangement is clearer now",
                    ),
                    RecordItem(
                        time="260318-1908",
                        name="Supplies",
                        change="Completed the sign-in supply list",
                        result="The missing items are now organized",
                    ),
                ],
            )
        ],
    )

    markdown = render_markdown(report)

    assert "## 项目进展" in markdown
    assert "### Venue setup" in markdown
    assert "| 名称 | 内容 | 预计 |" in markdown
    assert "| :--: | :--: | :--: |" in markdown
    assert "| Venue setup | Finished the first onsite review | Confirm the remaining supplies |" in markdown
    assert "#### 结果" in markdown
    assert "Execution conditions are now clearly aligned" in markdown
    assert "![结果图 1](figs/result-001.png)" in markdown
    assert "| 日期 | 时间 | 名称 | 内容 | 结果 |" in markdown
    assert "| 260318 | 1251 | Coordination | Checked table layout and route | Onsite arrangement is clearer now |" in markdown
    assert "| 260318 | 1908 | Supplies | Completed the sign-in supply list | The missing items are now organized |" in markdown

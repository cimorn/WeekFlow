from WeekFlow.ui.theme import APP_STYLESHEET, FONT_FAMILY_CANDIDATES, build_font_family_css, preferred_app_font_family


def test_preferred_app_font_family_prefers_chinese_fonts_over_segoe():
    available = {"Segoe UI", "Microsoft YaHei", "SimSun"}

    assert preferred_app_font_family(available) == "Microsoft YaHei"


def test_build_font_family_css_puts_chinese_font_first():
    css = build_font_family_css(FONT_FAMILY_CANDIDATES)

    assert css.startswith('"Microsoft YaHei", "Microsoft YaHei UI"')
    assert '"Segoe UI"' in css


def test_app_stylesheet_uses_10pt_body_and_12pt_titles():
    assert "font-size: 10pt;" in APP_STYLESHEET
    assert 'QLabel[role="brand-title"]' in APP_STYLESHEET
    assert 'QLabel[role="section-title"]' in APP_STYLESHEET
    assert "font-size: 12pt;" in APP_STYLESHEET
    assert "font-weight: 700;" in APP_STYLESHEET

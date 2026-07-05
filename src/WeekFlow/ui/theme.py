from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtGui import QFontDatabase


FONT_FAMILY_CANDIDATES = [
    "Microsoft YaHei",
    "Microsoft YaHei UI",
    "Noto Sans SC",
    "PingFang SC",
    "Microsoft JhengHei",
    "Microsoft JhengHei UI",
    "SimHei",
    "SimSun",
    "Segoe UI",
    "sans-serif",
]


def build_font_family_css(font_families: Iterable[str]) -> str:
    return ", ".join(name if name == "sans-serif" else f'"{name}"' for name in font_families)


def preferred_app_font_family(available_families: Iterable[str]) -> str:
    available = set(available_families)
    for name in FONT_FAMILY_CANDIDATES:
        if name != "sans-serif" and name in available:
            return name
    return "Segoe UI"


def apply_preferred_app_font(app) -> str:
    family = preferred_app_font_family(QFontDatabase.families())
    font = app.font()
    font.setFamily(family)
    app.setFont(font)
    return family


FONT_FAMILY_CSS = build_font_family_css(FONT_FAMILY_CANDIDATES)


THEME_DISPLAY_NAMES = {
    "report": "报告蓝",
    "spring": "浅蓝",
    "pink": "深蓝",
}


APP_STYLESHEET = """
QMainWindow,
QWidget#HomeRoot,
QWidget#EditorRoot {
    background: #f8fafc;
}

QWidget {
    color: #2d3845;
    font-family: """ + FONT_FAMILY_CSS + """;
    font-size: 10.5pt;
}

QLabel {
    background: transparent;
    border: none;
}

QFrame#Card,
QFrame#TopNavBar {
    background: #ffffff;
    border: 1px solid #e1e8ef;
    border-radius: 12px;
}

QFrame#EditorPanel {
    background: #ffffff;
    border: none;
    border-radius: 0;
}

QFrame#EditorActionRail {
    background: #f8fafc;
    border: 1px solid #e3eaf2;
    border-radius: 10px;
}

QWidget#TopActionBar {
    background: transparent;
    border: none;
}

QLabel[role="brand-title"] {
    font-size: 12pt;
    font-weight: 700;
    color: #24476a;
}

QLabel[role="hero-title"] {
    font-size: 18pt;
    font-weight: 700;
    color: #214d83;
}

QLabel[role="hero-subtitle"] {
    font-size: 11pt;
    color: #5f7082;
}

QLabel[role="section-title"] {
    font-size: 12pt;
    font-weight: 700;
    color: #27445f;
}

QLabel[role="muted"] {
    color: #738191;
}

QLabel[role="pill"] {
    padding: 2px 8px;
    border: 1px solid #e0e7ef;
    border-radius: 999px;
    background: #fbfcfe;
    color: #627488;
    font-size: 9pt;
}

QLabel[role="board-title"] {
    font-size: 10.5pt;
    font-weight: 700;
    color: #27445f;
}

QLabel[role="board-group-title"] {
    font-size: 10pt;
    font-weight: 700;
    color: #36506b;
}

QLabel[role="field-label"] {
    color: #36506b;
    font-weight: 700;
    font-size: 10pt;
}

QLabel[role="empty-state"] {
    padding: 12px;
    border: 1px dashed #cbd8e6;
    border-radius: 8px;
    background: #f8fafc;
    color: #6e7f91;
}

QScrollArea#EditorSectionScroll,
QScrollArea#TopSectionNavScroll,
QWidget#TopSectionNav,
QWidget#EditorSectionViewport,
QStackedWidget#EditorSectionStack,
QWidget#BasicInfoCombinedPage,
QWidget#OverviewFeelingCombinedPage,
QWidget#CombinedSectionBlock,
QWidget#AIConfigSection,
QWidget#ProjectsSection,
QWidget#ProjectListPanel,
QWidget#ProjectSubNav,
QWidget#ProjectUnifiedPanel,
QWidget#ProjectProgressPage,
QWidget#ProjectResultPage,
QWidget#ProjectViewBody,
QWidget#BasicInfoSection,
QWidget#BasicInfoContent {
    background: transparent;
    border: none;
}

QPushButton,
QComboBox {
    min-height: 36px;
    padding: 0 14px;
    border: 1px solid #d5dfe8;
    border-radius: 8px;
    background: #ffffff;
    color: #27445f;
    font-weight: 600;
}

QPushButton:hover,
QComboBox:hover {
    background: #f8fbfd;
    border-color: #b9cadd;
}

QPushButton:pressed {
    background: #eef4f8;
}

QPushButton[variant="primary"] {
    background: #5f86b3;
    color: #ffffff;
    border-color: #5f86b3;
}

QPushButton[variant="primary"]:hover {
    background: #5378a1;
    border-color: #5378a1;
}

QPushButton[variant="secondary"] {
    background: #7a9bbc;
    color: #ffffff;
    border-color: #7a9bbc;
}

QPushButton[variant="secondary"]:hover {
    background: #6d8fb1;
    border-color: #6d8fb1;
}

QPushButton[variant="subtle"] {
    background: #f4f7fb;
    color: #36506b;
    border-color: #cdd9e5;
}

QPushButton[variant="subtle"]:hover {
    background: #ebf1f7;
    border-color: #bccdde;
}

QPushButton[nav="true"] {
    text-align: left;
    padding-left: 12px;
    min-height: 38px;
}

QPushButton[nav="true"]:checked {
    background: #eef4f9;
    border-color: #bfd0e0;
    color: #27445f;
}

QPushButton[topNav="true"] {
    min-height: 34px;
    padding: 0 10px;
    border-radius: 8px;
    background: #fbfdff;
    color: #36506b;
}

QPushButton[topNav="true"]:checked {
    background: #5f86b3;
    border-color: #5f86b3;
    color: #ffffff;
}

QPushButton[topAction="true"] {
    min-height: 32px;
    padding: 0 9px;
    border-radius: 8px;
    font-size: 9.5pt;
}

QPushButton[subnav="true"] {
    min-height: 30px;
    padding: 0 4px;
    border: none;
    border-radius: 0;
    background: transparent;
    color: #36506b;
}

QPushButton[subnav="true"]:checked {
    background: transparent;
    border: none;
    border-bottom: 2px solid #5f86b3;
    color: #1f4264;
}

QPushButton[compact="true"] {
    min-height: 28px;
    padding: 0 9px;
}

QFrame#EditorActionRail QPushButton {
    min-height: 38px;
    padding: 0 8px;
    text-align: left;
}

QLineEdit,
QTextEdit,
QPlainTextEdit,
QListWidget,
QTableWidget,
QGroupBox,
QDialog {
    background: #ffffff;
}

QGroupBox {
    border: 1px solid #dbe3ec;
    border-radius: 8px;
    margin-top: 8px;
    padding-top: 8px;
    font-weight: 600;
    color: #39536b;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
}

QLineEdit,
QTextEdit,
QPlainTextEdit,
QListWidget,
QTableWidget {
    border: 1px solid #dbe3ec;
    border-radius: 8px;
    padding: 8px;
    selection-background-color: #cfdceb;
    font-size: 10.5pt;
}

QLineEdit,
QComboBox {
    min-height: 38px;
}

QTextEdit,
QPlainTextEdit {
    min-height: 118px;
}

QPlainTextEdit#ProjectSummaryEdit,
QPlainTextEdit#ProjectNextStepEdit {
    min-height: 64px;
    max-height: 86px;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QListWidget:focus,
QTableWidget:focus,
QComboBox:focus {
    border: 1px solid #7fa4c9;
}

QTextEdit,
QPlainTextEdit,
QListWidget,
QTableWidget {
    padding: 7px;
}

QListWidget::item {
    padding: 0;
    border-radius: 7px;
    margin: 0;
    border: 1px solid #e2eaf2;
    background: #ffffff;
}

QListWidget::item:selected {
    background: #eef4f9;
    border: 1px solid #9eb7d0;
    color: #27445f;
}

QListWidget::item:focus {
    outline: none;
}

QListWidget#ProjectFlatList {
    border: none;
    background: transparent;
    padding: 0;
}

QListWidget#ProjectFlatList::item {
    margin: 0;
    border: none;
    border-radius: 0;
    border-bottom: 1px solid #e9eef4;
    background: transparent;
}

QListWidget#ProjectFlatList::item:hover {
    background: #f8fafc;
}

QListWidget#ProjectFlatList::item:selected {
    background: #f5f9fd;
    border: none;
    border-left: 3px solid #5f86b3;
    border-bottom: 1px solid #e9eef4;
    color: #27445f;
}

QWidget#ProjectRow {
    background: transparent;
}

QFrame#ProjectPickerColumn {
    background: #f7fafc;
    border: 1px solid #e0e8f0;
    border-radius: 10px;
}

QFrame#ProjectWorkflowColumn {
    background: #ffffff;
    border: none;
}

QFrame#ProjectWorkflowSummary,
QFrame#ProjectWorkflowResult,
QFrame#ProjectWorkflowTimeline {
    background: #fbfdff;
    border: 1px solid #e0e8f0;
    border-radius: 10px;
}

QFrame#ProjectWorkflowResult {
    background: #f3f7ff;
    border-color: #c6d8f2;
}

QFrame#ProjectWorkflowTimeline {
    background: #eef7ff;
    border-color: #c7ddf7;
}

QLabel#ProjectRowIndex {
    color: #5f86b3;
    background: transparent;
    border: none;
    padding: 0;
}

QFrame#ProjectDetailPage {
    background: transparent;
    border: none;
}

QWidget#ProjectDetailHeader {
    border-bottom: 1px solid #e7edf3;
}

QFrame#ProjectViewPage {
    background: transparent;
    border: none;
}

QLabel#ProjectViewValue {
    padding: 4px 0 10px;
    border: none;
    border-bottom: 1px solid #edf2f6;
    background: transparent;
}

QLabel#ProjectRowSummary,
QLabel#ProjectRowNextStep {
    color: #657789;
    line-height: 1.35;
}

QLabel#ProjectRowMeta {
    margin-top: 3px;
    color: #58718d;
    background: transparent;
    border: none;
    padding: 0;
}

QFrame#ProjectCoreGroup,
QFrame#ProjectResultGroup,
QFrame#ProjectTimelineGroup {
    background: transparent;
    border: none;
}

QFrame#ProjectSectionDivider {
    color: #e7edf3;
    background: #e7edf3;
    max-height: 1px;
    margin-top: 8px;
    margin-bottom: 8px;
}

QListWidget::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #90a8bf;
    border-radius: 5px;
    background: #ffffff;
}

QListWidget::indicator:checked {
    background: #6f93b6;
    border: 1px solid #6f93b6;
}

QHeaderView::section {
    background: #f5f8fb;
    color: #456179;
    padding: 7px;
    border: 0;
    border-bottom: 1px solid #dbe3ec;
    font-weight: 600;
}

QTableCornerButton::section {
    background: #f5f8fb;
    border: 0;
    border-bottom: 1px solid #dbe3ec;
    border-right: 1px solid #dbe3ec;
}

QScrollBar:vertical,
QScrollBar:horizontal {
    background: transparent;
    border: none;
    margin: 0;
}

QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background: #c8d4e1;
    border-radius: 6px;
    min-height: 24px;
    min-width: 24px;
}

QSplitter::handle {
    background: #e8edf3;
    width: 3px;
    height: 3px;
}
"""


PREVIEW_BASE_CSS = """
html, body {
  margin: 0;
  padding: 0;
  background: var(--weekly-bg);
  color: var(--weekly-text);
  font-family: """ + FONT_FAMILY_CSS + """;
  font-size: 10pt;
}

body {
  padding: 10px;
}

.preview-shell {
  max-width: 960px;
  margin: 0 auto;
}

.preview-shell.section-view {
  max-width: 860px;
}

.preview-paper {
  background: var(--weekly-panel);
  border: 1px solid var(--weekly-border);
  border-radius: 12px;
  padding: 18px 22px 22px;
  box-shadow: 0 12px 28px rgba(31, 53, 78, 0.05);
  margin: 0 auto;
}

.report-hero {
  display: grid;
  justify-items: center;
  text-align: center;
  gap: 10px;
  margin-bottom: 10px;
}

.preview-paper h1 {
  margin: 0 0 0.5rem;
  text-align: center;
  font-size: 12pt;
  line-height: 1.35;
  color: var(--weekly-heading);
  font-weight: 700;
}

.preview-paper h2 {
  margin-top: 1.7rem;
  margin-bottom: 0.85rem;
  padding: 0;
  background: transparent;
  font-size: 12pt;
  font-weight: 700;
  color: var(--weekly-heading);
  text-align: center;
  width: auto;
  min-width: 0;
  margin-left: 0;
  margin-right: 0;
  box-shadow: none;
}

.preview-paper h3 {
  margin: 0 0 0.55rem;
  color: var(--weekly-subheading);
  font-size: 12pt;
  font-weight: 700;
  text-align: center;
}

.preview-paper h4 {
  margin: 0 0 0.65rem;
  color: var(--weekly-subheading);
  font-size: 10pt;
  font-weight: 700;
  text-align: center;
}

.preview-paper p {
  margin: 0.3rem 0;
  font-size: 10pt;
  line-height: 1.6;
}

.preview-paper p,
.preview-paper li,
.preview-paper td,
.preview-paper th,
.hero-summary,
.chip-value,
.timeline-row-compact .timeline-col,
.todo-text,
.feeling-card,
.plain-card p {
  overflow-wrap: anywhere;
  word-break: break-word;
}

.preview-paper table {
  width: 100%;
  margin: 10px 0 14px;
  border-collapse: collapse;
  table-layout: fixed;
}

.preview-paper th,
.preview-paper td {
  padding: 8px 10px;
  border: 1px solid var(--weekly-border);
  text-align: center;
  vertical-align: middle;
  white-space: normal;
}

.report-meta {
  margin: 0 auto 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 5px 12px;
  border-radius: 999px;
  border: 1px solid var(--weekly-border);
  background: var(--weekly-muted-bg);
  color: var(--weekly-muted-text);
  font-size: 9pt;
  line-height: 1.4;
}

.hero-summary {
  border: 1px solid var(--weekly-border-strong);
  border-radius: 10px;
  padding: 10px 12px;
  background: #fbfdff;
  margin: 4px 0 14px;
  line-height: 1.6;
  width: min(100%, 720px);
  text-align: center;
}

.achievement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin: 14px 0 24px;
}

.achievement-card {
  position: relative;
  border: 1px solid var(--weekly-card-stroke);
  border-color: var(--weekly-card-stroke);
  border-radius: 10px;
  padding: 10px 12px;
  background: var(--weekly-card-bg);
  min-height: 58px;
  box-shadow: none;
}

.achievement-card::before {
  content: "";
  display: block;
  width: 38px;
  height: 4px;
  margin-bottom: 10px;
  border-radius: 999px;
  background: var(--weekly-accent);
}

.project-compact-box {
  margin: 18px 0 28px;
  padding: 0 0 14px;
  border: none;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.project-compact-box + .project-compact-box {
  margin-top: 34px;
  padding-top: 22px;
  border-top: 1px solid var(--weekly-divider);
}

.project-summary-table {
  width: 100%;
  margin: 0 0 16px;
  table-layout: fixed;
  border-collapse: collapse;
  background: var(--weekly-panel);
}

.project-summary-table td {
  border: 1px solid var(--weekly-border);
  padding: 8px 12px;
  font-size: 9pt;
  line-height: 1.6;
  text-align: center;
  vertical-align: middle;
}

.project-summary-table th {
  background: var(--weekly-muted-bg);
  color: var(--weekly-heading);
  font-size: 10pt;
  font-weight: 700;
  text-align: center;
  border: 1px solid var(--weekly-border);
  padding: 8px 12px;
}

.project-result-block {
  margin: 0 0 16px;
  padding: 12px 14px;
  border: 1px solid var(--weekly-card-stroke);
  border-radius: 10px;
  background: var(--weekly-card-bg);
}

.project-result-copy {
  text-align: center;
  font-size: 10pt;
  line-height: 1.7;
}

.project-result-copy.muted {
  color: var(--weekly-muted-text);
}

.result-image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.result-image-card {
  margin: 0;
  padding: 10px;
  border: 1px solid var(--weekly-border);
  border-radius: 10px;
  background: var(--weekly-panel);
}

.result-image-card img {
  display: block;
  width: 100%;
  max-height: 220px;
  object-fit: contain;
  border-radius: 8px;
  background: var(--weekly-muted-bg);
}

.result-image-card figcaption {
  margin-top: 8px;
  text-align: center;
  color: var(--weekly-muted-text);
  font-size: 9pt;
}

.timeline-table-wrap {
  overflow-x: auto;
  border: none;
  border-radius: 0;
  background: transparent;
  margin-top: 10px;
}

.timeline-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  background: var(--weekly-panel);
}

.timeline-table thead th {
  padding: 10px 8px;
  border-bottom: 1px solid var(--weekly-border);
  background: var(--weekly-muted-bg);
  color: var(--weekly-muted-text);
  font-size: 10pt;
  font-weight: 600;
  letter-spacing: 0;
  text-transform: none;
  white-space: nowrap;
  text-align: center;
}

.timeline-table th:nth-child(1),
.timeline-table td:nth-child(1) {
  width: 10%;
  text-align: center;
}

.timeline-table th:nth-child(2),
.timeline-table td:nth-child(2) {
  width: 9%;
  text-align: center;
}

.timeline-table th:nth-child(3),
.timeline-table td:nth-child(3) {
  width: 13%;
}

.timeline-table th:nth-child(4),
.timeline-table td:nth-child(4) {
  width: 34%;
}

.timeline-table th:nth-child(5),
.timeline-table td:nth-child(5) {
  width: 34%;
}

.timeline-table tbody td {
  padding: 10px 10px;
  border-top: 1px solid var(--weekly-border);
  font-size: 9pt;
  line-height: 1.5;
  text-align: center;
  vertical-align: middle;
}

.timeline-table tbody tr:nth-child(even) {
  background: var(--weekly-row-alt);
}

.todo-list-card {
  display: grid;
  gap: 8px;
  margin: 16px 0 24px;
}

.todo-check-row {
  display: grid;
  grid-template-columns: 18px 1fr;
  gap: 8px;
  align-items: center;
  padding: 8px 10px;
  border: 1px solid var(--weekly-card-stroke);
  border-color: var(--weekly-card-stroke);
  border-radius: 10px;
  background: var(--weekly-panel);
}

.todo-check-row.done {
  opacity: 0.78;
  border-color: var(--weekly-border-strong);
  background: var(--weekly-muted-bg);
}

.todo-indicator {
  width: 14px;
  height: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--weekly-accent);
  border-radius: 50%;
  color: var(--weekly-accent);
  font-size: 10px;
}

.todo-check-row.done .todo-indicator {
  background: var(--weekly-accent);
  color: #ffffff;
}

.todo-text {
  line-height: 1.45;
}

.plain-card,
.feeling-card {
  padding: 12px 14px;
  margin: 16px 0 24px;
  border-radius: 10px;
  border: 1px solid var(--weekly-card-stroke);
  border-color: var(--weekly-card-stroke);
  background: var(--weekly-card-bg);
  box-shadow: none;
}

@media (max-width: 760px) {
  body {
    padding: 8px;
  }

  .preview-shell,
  .preview-shell.section-view {
    max-width: 100%;
  }

  .preview-paper {
    padding: 14px 14px 16px;
    border-radius: 14px;
  }

  .result-image-grid {
    grid-template-columns: 1fr;
  }

  .timeline-table {
    display: table;
  }

  .preview-paper table:not(.timeline-table) {
    overflow-x: auto;
  }
}
"""


PREVIEW_THEME_VARS = {
    "report": {
        "weekly-bg": "#f6f8fb",
        "weekly-panel": "#ffffff",
        "weekly-paper-end": "#fbfdff",
        "weekly-text": "#2d3845",
        "weekly-heading": "#2f4f6f",
        "weekly-subheading": "#425f78",
        "weekly-accent": "#7fa4c9",
        "weekly-border": "#dce4ec",
        "weekly-border-strong": "#d7dee8",
        "weekly-card-stroke": "#dde6ef",
        "weekly-divider": "#dce4ec",
        "weekly-muted-bg": "#f5f8fc",
        "weekly-card-bg": "#fcfdff",
        "weekly-row-alt": "#f8fbfe",
        "weekly-muted-text": "#5c6b7a",
        "weekly-hero-start": "#f7fafc",
        "weekly-hero-end": "#eef4fb",
    },
    "spring": {
        "weekly-bg": "#f1f7ff",
        "weekly-panel": "#ffffff",
        "weekly-paper-end": "#f8fbff",
        "weekly-text": "#213149",
        "weekly-heading": "#245f9f",
        "weekly-subheading": "#3e6f9d",
        "weekly-accent": "#5b8def",
        "weekly-border": "#d5e5f8",
        "weekly-border-strong": "#c6d8f2",
        "weekly-card-stroke": "#d6e5f7",
        "weekly-divider": "#dbe8f8",
        "weekly-muted-bg": "#f3f8ff",
        "weekly-card-bg": "#fbfdff",
        "weekly-row-alt": "#f5f9ff",
        "weekly-muted-text": "#62738a",
        "weekly-hero-start": "#f7fbff",
        "weekly-hero-end": "#e9f3ff",
    },
    "pink": {
        "weekly-bg": "#edf4ff",
        "weekly-panel": "#ffffff",
        "weekly-paper-end": "#f7fbff",
        "weekly-text": "#152944",
        "weekly-heading": "#1d4ed8",
        "weekly-subheading": "#315f9a",
        "weekly-accent": "#2563eb",
        "weekly-border": "#cfe0f5",
        "weekly-border-strong": "#b9cdea",
        "weekly-card-stroke": "#cfdef2",
        "weekly-divider": "#d5e2f3",
        "weekly-muted-bg": "#eef6ff",
        "weekly-card-bg": "#fbfdff",
        "weekly-row-alt": "#f3f7ff",
        "weekly-muted-text": "#5f7088",
        "weekly-hero-start": "#f4f9ff",
        "weekly-hero-end": "#e2efff",
    },
}


def normalize_theme_key(theme_key: str | None) -> str:
    return theme_key if theme_key in THEME_DISPLAY_NAMES else "report"


def preview_css_for(theme_key: str) -> str:
    theme_key = normalize_theme_key(theme_key)
    vars_block = "\n".join(f"  --{name}: {value};" for name, value in PREVIEW_THEME_VARS[theme_key].items())
    return f":root {{\n{vars_block}\n}}\n{PREVIEW_BASE_CSS}"

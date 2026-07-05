from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from WeekFlow.controllers.editor_controller import EditorController
from WeekFlow.services.ai_config import (
    DEFAULT_AI_CONFIGS,
    DEFAULT_SYSTEM_PROMPT,
    PROVIDER_DISPLAY_NAMES,
    normalize_ai_payload,
)


PROVIDER_OPTIONS = [(value, label) for value, label in PROVIDER_DISPLAY_NAMES.items()]


class AIConfigSection(QWidget):
    test_requested = Signal()

    def __init__(self, controller: EditorController, on_change) -> None:
        super().__init__()
        self.controller = controller
        self.on_change = on_change
        self._loading = False

        self.provider_combo = QComboBox()
        for value, label in PROVIDER_OPTIONS:
            self.provider_combo.addItem(label, value)

        self.base_url_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.model_edit = QLineEdit()
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlaceholderText("设置默认润色提示词")
        self.system_prompt_edit.setMinimumHeight(90)
        self.system_prompt_edit.setMaximumHeight(120)
        self.status_label = QLabel("未测试连接")
        self.status_label.setProperty("role", "muted")
        self.status_label.setWordWrap(True)

        test_button = QPushButton("测试连接")
        test_button.clicked.connect(self.test_requested.emit)

        helper = QLabel(
            "内置火山引擎、OpenRouter、Groq、Gemini 和自定义 OpenAI 兼容配置。"
            "免费层通常仍需要填写自己的 API Key；粘贴完整接口链接时会自动识别 Provider 并清理 Base URL。"
        )
        helper.setProperty("role", "muted")
        helper.setWordWrap(True)

        fields = QVBoxLayout()
        fields.setContentsMargins(0, 0, 0, 0)
        fields.setSpacing(9)
        fields.addWidget(self._build_field("Provider", self.provider_combo))
        fields.addWidget(self._build_field("Base URL", self.base_url_edit))
        fields.addWidget(self._build_field("API Key", self.api_key_edit))
        fields.addWidget(self._build_field("Model / Endpoint", self.model_edit))
        fields.addWidget(self._build_field("System Prompt", self.system_prompt_edit))

        actions = QHBoxLayout()
        actions.addWidget(test_button)
        actions.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(helper)
        layout.addLayout(fields)
        layout.addLayout(actions)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.provider_combo.currentIndexChanged.connect(self._provider_changed)
        self.base_url_edit.textChanged.connect(self._apply_changes)
        self.api_key_edit.textChanged.connect(self._apply_changes)
        self.model_edit.textChanged.connect(self._apply_changes)
        self.system_prompt_edit.textChanged.connect(self._apply_changes)

    def _build_field(self, label_text: str, editor: QWidget) -> QWidget:
        field = QWidget()
        label = QLabel(label_text)
        label.setProperty("role", "field-label")

        layout = QVBoxLayout(field)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(label)
        layout.addWidget(editor)
        return field

    def load_from_report(self) -> None:
        self._loading = True
        normalized = normalize_ai_payload(
            self.controller.report.ai.get("provider"),
            self.controller.report.ai.get("config", {}),
        )
        self.controller.report.ai = normalized
        provider = normalized.get("provider", "volcengine_plan")
        index = self.provider_combo.findData(provider)
        if index < 0:
            index = 0
        self.provider_combo.setCurrentIndex(index)

        config = normalized.get("config", {})
        defaults = DEFAULT_AI_CONFIGS.get(provider, DEFAULT_AI_CONFIGS["openai_compatible"])
        self.base_url_edit.setText(config.get("base_url", defaults["base_url"]))
        self.api_key_edit.setText(config.get("api_key", ""))
        self.model_edit.setText(config.get("model", defaults["model"]))
        self.system_prompt_edit.setPlainText(config.get("system_prompt", DEFAULT_SYSTEM_PROMPT))
        self._loading = False

    def set_status_message(self, message: str) -> None:
        self.status_label.setText(message)

    def current_provider(self) -> str:
        return str(self.provider_combo.currentData())

    def _provider_changed(self) -> None:
        if self._loading:
            return
        defaults = DEFAULT_AI_CONFIGS.get(self.current_provider(), DEFAULT_AI_CONFIGS["openai_compatible"])
        self.base_url_edit.setText(defaults["base_url"])
        self.model_edit.setText(defaults["model"])
        self._apply_changes()

    def _apply_changes(self) -> None:
        if self._loading:
            return
        normalized = normalize_ai_payload(
            self.current_provider(),
            {
                "base_url": self.base_url_edit.text().strip(),
                "api_key": self.api_key_edit.text().strip(),
                "model": self.model_edit.text().strip(),
                "system_prompt": self.system_prompt_edit.toPlainText().strip(),
            },
        )
        self.controller.report.ai = normalized
        self._sync_normalized_fields(normalized)
        self.controller.mark_dirty()
        self.on_change()

    def _sync_normalized_fields(self, normalized: dict) -> None:
        provider = str(normalized.get("provider", self.current_provider()))
        config = normalized.get("config", {})
        base_url = str(config.get("base_url", ""))
        current_base_url = self.base_url_edit.text().strip()

        provider_index = self.provider_combo.findData(provider)
        needs_provider_sync = provider_index >= 0 and provider != self.current_provider()
        needs_base_url_sync = bool(current_base_url) and current_base_url != base_url
        if not needs_provider_sync and not needs_base_url_sync:
            return

        self._loading = True
        if needs_provider_sync:
            self.provider_combo.setCurrentIndex(provider_index)
        if needs_base_url_sync:
            self.base_url_edit.setText(base_url)
        self._loading = False

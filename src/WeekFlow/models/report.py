from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from WeekFlow.services.ai_config import normalize_ai_payload


def _split_legacy_timestamp(raw: str) -> tuple[str, str]:
    text = raw.strip()
    if not text:
        return "", ""
    if "-" in text:
        date_part, time_part = text.split("-", 1)
        if date_part.strip() and time_part.strip():
            return date_part.strip(), time_part.strip()
    return "", text


@dataclass(slots=True)
class RecordItem:
    date: str = ""
    time: str = ""
    name: str = ""
    change: str = ""
    result: str = ""

    def normalized_date_time(self) -> tuple[str, str]:
        if self.date.strip():
            return self.date.strip(), self.time.strip()
        return _split_legacy_timestamp(self.time)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RecordItem":
        date = str(payload.get("date", "")).strip()
        time = str(payload.get("time", "")).strip()
        if not date:
            date, time = _split_legacy_timestamp(time)
        return cls(
            date=date,
            time=time,
            name=str(payload.get("name", "")).strip(),
            change=payload.get("change", ""),
            result=payload.get("result", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        date, time = self.normalized_date_time()
        return {
            "date": date,
            "time": time,
            "name": self.name,
            "change": self.change,
            "result": self.result,
        }


@dataclass(slots=True)
class ProjectItem:
    name: str = ""
    summary: str = ""
    issue: str = ""
    next_step: str = ""
    result_images: list[str] = field(default_factory=list)
    records: list[RecordItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ProjectItem":
        return cls(
            name=payload.get("name", ""),
            summary=payload.get("summary", ""),
            issue=payload.get("issue", ""),
            next_step=payload.get("next_step", ""),
            result_images=[str(item).strip() for item in payload.get("result_images", []) if str(item).strip()],
            records=[RecordItem.from_dict(item) for item in payload.get("records", [])],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "summary": self.summary,
            "issue": self.issue,
            "next_step": self.next_step,
            "result_images": list(self.result_images),
            "records": [item.to_dict() for item in self.records],
        }


@dataclass(slots=True)
class TodoItem:
    done: bool = False
    text: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TodoItem":
        return cls(
            done=bool(payload.get("done", False)),
            text=payload.get("text", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "done": self.done,
            "text": self.text,
        }


def _default_ai() -> dict[str, Any]:
    return normalize_ai_payload("openai_compatible", {})


@dataclass(slots=True)
class WeeklyReport:
    report_id: str = ""
    schema_version: int = 2
    cycle: str = ""
    topic: str = ""
    one_line_summary: str = ""
    preview_theme: str = "report"
    overview: dict[str, Any] = field(
        default_factory=lambda: {
            "mainline": "",
            "mainlines": [],
            "judgment": "",
            "focus": "",
        }
    )
    projects: list[ProjectItem] = field(default_factory=list)
    achievements: list[str] = field(default_factory=list)
    todos: list[TodoItem] = field(default_factory=list)
    feeling: str = ""
    ai: dict[str, Any] = field(default_factory=_default_ai)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WeeklyReport":
        overview_payload = payload.get("overview", {})
        legacy_mainline = overview_payload.get("mainline", "")
        mainlines = list(overview_payload.get("mainlines", []))
        if not mainlines and legacy_mainline:
            mainlines = [line.strip() for line in legacy_mainline.splitlines() if line.strip()]
        if not mainlines and legacy_mainline.strip():
            mainlines = [legacy_mainline.strip()]

        return cls(
            schema_version=payload.get("schema_version", 2),
            report_id=payload.get("report_id", ""),
            cycle=payload.get("cycle", ""),
            topic=payload.get("topic", ""),
            one_line_summary=payload.get("one_line_summary", ""),
            preview_theme=payload.get("preview_theme", "report"),
            overview={
                "mainline": "\n".join(mainlines),
                "mainlines": mainlines,
                "judgment": overview_payload.get("judgment", ""),
                "focus": overview_payload.get("focus", ""),
            },
            projects=[ProjectItem.from_dict(item) for item in payload.get("projects", [])],
            achievements=list(payload.get("achievements", [])),
            todos=[TodoItem.from_dict(item) for item in payload.get("todos", [])],
            feeling=payload.get("feeling", ""),
            ai=normalize_ai_payload(
                payload.get("ai", {}).get("provider"),
                payload.get("ai", {}).get("config", {}),
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        mainlines = [line.strip() for line in self.overview.get("mainlines", []) if line.strip()]
        if not mainlines and self.overview.get("mainline", "").strip():
            mainlines = [line.strip() for line in self.overview.get("mainline", "").splitlines() if line.strip()]

        return {
            "schema_version": self.schema_version,
            "report_id": self.report_id,
            "cycle": self.cycle,
            "topic": self.topic,
            "one_line_summary": self.one_line_summary,
            "preview_theme": self.preview_theme,
            "overview": {
                "mainline": "\n".join(mainlines),
                "mainlines": mainlines,
                "judgment": self.overview.get("judgment", ""),
                "focus": self.overview.get("focus", ""),
            },
            "projects": [item.to_dict() for item in self.projects],
            "achievements": list(self.achievements),
            "todos": [item.to_dict() for item in self.todos],
            "feeling": self.feeling,
            "ai": normalize_ai_payload(
                self.ai.get("provider"),
                self.ai.get("config", {}),
            ),
        }

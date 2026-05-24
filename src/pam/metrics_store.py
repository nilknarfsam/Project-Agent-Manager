"""Persistência de eventos de métricas em ai/metrics/ (JSONL)."""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from pam.config_loader import project_root

METRICS_DIR = "ai/metrics"
ERROR_SUMMARY_MAX = 500

_SENSITIVE_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*\S+"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}"),
)


@dataclass
class MetricsEvent:
    """Evento operacional registrado após uma execução PAM."""

    event_id: str
    timestamp: str
    project: str
    command: str
    agent: str | None = None
    provider: str | None = None
    model: str | None = None
    task_id: str | None = None
    status: str = "unknown"
    duration_ms: int = 0
    success: bool = False
    error_summary: str | None = None
    run_file: str | None = None
    pipeline_name: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "MetricsEvent":
        return cls(
            event_id=str(data["event_id"]),
            timestamp=str(data["timestamp"]),
            project=str(data["project"]),
            command=str(data["command"]),
            agent=data.get("agent"),
            provider=data.get("provider"),
            model=data.get("model"),
            task_id=data.get("task_id"),
            status=str(data.get("status", "unknown")),
            duration_ms=int(data.get("duration_ms") or 0),
            success=bool(data.get("success", False)),
            error_summary=data.get("error_summary"),
            run_file=data.get("run_file"),
            pipeline_name=data.get("pipeline_name"),
        )


class MetricsStore:
    """Registra e carrega eventos de execução em arquivos JSONL mensais."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or project_root()

    def metrics_dir(self) -> Path:
        directory = self.base_dir / METRICS_DIR
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @staticmethod
    def utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def sanitize_text(text: str | None, *, max_len: int = ERROR_SUMMARY_MAX) -> str | None:
        """Remove padrões sensíveis e trunca texto para métricas."""
        if not text:
            return None
        cleaned = str(text).strip()
        for pattern in _SENSITIVE_PATTERNS:
            cleaned = pattern.sub("[REDACTED]", cleaned)
        if len(cleaned) > max_len:
            return cleaned[: max_len - 3] + "..."
        return cleaned or None

    @staticmethod
    def duration_ms_between(start: str, end: str) -> int:
        """Calcula duração entre timestamps ISO 8601."""
        try:
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
            delta = (end_dt - start_dt).total_seconds() * 1000
            return max(0, int(delta))
        except (ValueError, TypeError):
            return 0

    def events_path_for_month(self, when: datetime | None = None) -> Path:
        moment = when or datetime.now(timezone.utc)
        filename = f"events_{moment.strftime('%Y%m')}.jsonl"
        return self.metrics_dir() / filename

    def record_execution(
        self,
        *,
        project: str,
        command: str,
        status: str,
        success: bool,
        duration_ms: int = 0,
        agent: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        task_id: str | None = None,
        error_summary: str | None = None,
        run_file: str | Path | None = None,
        pipeline_name: str | None = None,
        timestamp: str | None = None,
    ) -> MetricsEvent:
        """Registra um evento de execução (nunca inclui prompts ou chaves)."""
        event = MetricsEvent(
            event_id=str(uuid.uuid4()),
            timestamp=timestamp or self.utc_now(),
            project=project,
            command=command,
            agent=agent,
            provider=provider,
            model=model,
            task_id=task_id,
            status=status,
            duration_ms=max(0, int(duration_ms)),
            success=success,
            error_summary=self.sanitize_text(error_summary),
            run_file=str(run_file) if run_file else None,
            pipeline_name=pipeline_name,
        )
        self._append_event(event)
        return event

    def record_from_run_payload(
        self,
        payload: dict,
        *,
        run_file: str | Path,
        task_id: str | None = None,
        pipeline_name: str | None = None,
        error_summary: str | None = None,
    ) -> MetricsEvent:
        """Cria evento a partir do payload de ai/runs/ (sem prompt)."""
        status = str(payload.get("status", "unknown"))
        success = status.lower() not in {"error", "failed", "failure"}
        return self.record_execution(
            project=str(payload.get("project", "")),
            command=str(payload.get("command", "unknown")),
            status=status,
            success=success,
            duration_ms=int(payload.get("duration_ms") or 0),
            agent=payload.get("agent_name"),
            provider=payload.get("provider"),
            model=payload.get("model"),
            task_id=task_id,
            error_summary=error_summary or (None if success else status),
            run_file=run_file,
            pipeline_name=pipeline_name,
        )

    def _append_event(self, event: MetricsEvent) -> Path:
        path = self.events_path_for_month()
        line = json.dumps(event.to_dict(), ensure_ascii=False)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        return path

    def list_event_files(self) -> list[Path]:
        directory = self.metrics_dir()
        return sorted(p for p in directory.glob("events_*.jsonl") if p.is_file())

    def load_events(
        self,
        *,
        project: str | None = None,
        last: int | None = None,
    ) -> list[MetricsEvent]:
        """Carrega eventos de todos os arquivos JSONL, opcionalmente filtrados."""
        events: list[MetricsEvent] = []
        for path in self.list_event_files():
            try:
                content = path.read_text(encoding="utf-8")
            except OSError:
                continue
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    event = MetricsEvent.from_dict(data)
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
                if project and event.project != project:
                    continue
                events.append(event)

        events.sort(key=lambda item: item.timestamp, reverse=True)
        if last is not None and last > 0:
            return events[:last]
        return events

    def aggregate(self, events: list[MetricsEvent] | None = None) -> dict:
        """Agrega totais básicos a partir de uma lista de eventos."""
        items = events if events is not None else self.load_events()
        total = len(items)
        successes = sum(1 for event in items if event.success)
        failures = total - successes

        by_project: dict[str, int] = {}
        by_provider: dict[str, int] = {}
        by_agent: dict[str, int] = {}
        durations: list[int] = []

        for event in items:
            by_project[event.project] = by_project.get(event.project, 0) + 1
            provider = event.provider or "unknown"
            by_provider[provider] = by_provider.get(provider, 0) + 1
            if event.agent:
                by_agent[event.agent] = by_agent.get(event.agent, 0) + 1
            if event.duration_ms > 0:
                durations.append(event.duration_ms)

        avg_duration_ms = int(sum(durations) / len(durations)) if durations else 0

        return {
            "total_executions": total,
            "successes": successes,
            "failures": failures,
            "by_project": dict(sorted(by_project.items())),
            "by_provider": dict(sorted(by_provider.items())),
            "by_agent": dict(sorted(by_agent.items())),
            "avg_duration_ms": avg_duration_ms,
            "last_executions": items[:10],
        }

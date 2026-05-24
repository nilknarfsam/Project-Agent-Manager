"""Serviço de observabilidade — agregação e relatórios de métricas PAM."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pam.metrics_store import MetricsEvent, MetricsStore


@dataclass
class ObservabilitySummary:
    """Resumo agregado de execuções registradas."""

    total_executions: int
    successes: int
    failures: int
    avg_duration_ms: int
    by_project: dict[str, int]
    by_provider: dict[str, int]
    by_agent: dict[str, int]
    last_executions: list[MetricsEvent]
    project_filter: str | None = None

    @classmethod
    def from_aggregate(
        cls,
        data: dict,
        *,
        project_filter: str | None = None,
        last_limit: int | None = None,
    ) -> "ObservabilitySummary":
        last = data.get("last_executions") or []
        if last_limit is not None and last_limit > 0:
            last = last[:last_limit]
        return cls(
            total_executions=int(data.get("total_executions") or 0),
            successes=int(data.get("successes") or 0),
            failures=int(data.get("failures") or 0),
            avg_duration_ms=int(data.get("avg_duration_ms") or 0),
            by_project=dict(data.get("by_project") or {}),
            by_provider=dict(data.get("by_provider") or {}),
            by_agent=dict(data.get("by_agent") or {}),
            last_executions=last,
            project_filter=project_filter,
        )


class ObservabilityService:
    """Consulta métricas locais e produz relatórios para CLI e GUI."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.store = MetricsStore(base_dir)

    def get_summary(
        self,
        *,
        project: str | None = None,
        last: int | None = None,
    ) -> ObservabilitySummary:
        events = self.store.load_events(project=project)
        aggregate = self.store.aggregate(events)
        if last is not None and last > 0:
            aggregate["last_executions"] = events[:last]
        return ObservabilitySummary.from_aggregate(
            aggregate,
            project_filter=project,
            last_limit=last,
        )

    @staticmethod
    def format_duration_ms(duration_ms: int) -> str:
        if duration_ms <= 0:
            return "—"
        if duration_ms < 1000:
            return f"{duration_ms} ms"
        seconds = duration_ms / 1000
        if seconds < 60:
            return f"{seconds:.1f} s"
        minutes = int(seconds // 60)
        remainder = seconds % 60
        return f"{minutes}m {remainder:.0f}s"

    def format_cli_report(self, summary: ObservabilitySummary) -> str:
        lines = ["Observabilidade PAM — métricas locais (ai/metrics/)", ""]
        if summary.project_filter:
            lines.append(f"Filtro de projeto: {summary.project_filter}")
            lines.append("")

        lines.extend(
            [
                f"Total de execuções: {summary.total_executions}",
                f"Sucessos:             {summary.successes}",
                f"Falhas:               {summary.failures}",
                f"Duração média:        {self.format_duration_ms(summary.avg_duration_ms)}",
                "",
            ]
        )

        if summary.by_project:
            lines.append("Execuções por projeto:")
            for name, count in summary.by_project.items():
                lines.append(f"  - {name}: {count}")
            lines.append("")

        if summary.by_provider:
            lines.append("Execuções por provider:")
            for name, count in summary.by_provider.items():
                lines.append(f"  - {name}: {count}")
            lines.append("")

        if summary.by_agent:
            lines.append("Execuções por agente:")
            for name, count in summary.by_agent.items():
                lines.append(f"  - {name}: {count}")
            lines.append("")

        if summary.last_executions:
            lines.append("Últimas execuções:")
            for event in summary.last_executions:
                status_icon = "OK" if event.success else "FAIL"
                duration = self.format_duration_ms(event.duration_ms)
                agent = event.agent or "—"
                provider = event.provider or "—"
                lines.append(
                    f"  [{status_icon}] {event.timestamp[:19]}  "
                    f"{event.project:12}  {event.command:12}  "
                    f"{provider:8}  {agent:12}  {duration}"
                )
        else:
            lines.append("Nenhuma execução registrada ainda.")
            lines.append(
                "Execute plan, run, review, pipeline ou ai-* para gerar eventos."
            )

        return "\n".join(lines)

"""Modelos de resultado consolidado de pipelines multi-agente."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PipelineStepResult:
    """Resultado de um step individual no pipeline."""

    agent: str
    status: str
    started_at: str
    finished_at: str
    summary: str
    run_path: str | None = None
    error: str | None = None
    provider: str | None = None
    model: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PipelineStepResult":
        return cls(
            agent=str(data["agent"]),
            status=str(data["status"]),
            started_at=str(data["started_at"]),
            finished_at=str(data["finished_at"]),
            summary=str(data.get("summary", "")),
            run_path=data.get("run_path"),
            error=data.get("error"),
            provider=data.get("provider"),
            model=data.get("model"),
        )


@dataclass
class PipelineResult:
    """Resultado consolidado de uma execução de pipeline."""

    pipeline_name: str
    task_id: str
    project: str
    started_at: str
    finished_at: str
    steps: list[PipelineStepResult] = field(default_factory=list)
    final_summary: str = ""
    success: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_name": self.pipeline_name,
            "task_id": self.task_id,
            "project": self.project,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "steps": [step.to_dict() for step in self.steps],
            "final_summary": self.final_summary,
            "success": self.success,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PipelineResult":
        return cls(
            pipeline_name=str(data["pipeline_name"]),
            task_id=str(data["task_id"]),
            project=str(data["project"]),
            started_at=str(data["started_at"]),
            finished_at=str(data["finished_at"]),
            steps=[
                PipelineStepResult.from_dict(item)
                for item in data.get("steps", [])
            ],
            final_summary=str(data.get("final_summary", "")),
            success=bool(data.get("success", False)),
        )

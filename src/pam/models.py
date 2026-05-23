"""Modelos de dados compartilhados do PAM."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectConfig:
    """Configuração de um projeto gerenciado pelo PAM."""

    name: str
    repo_path: Path
    default_runtime: str
    default_model: str
    description: str


@dataclass(frozen=True)
class RunContext:
    """Contexto mínimo para uma execução agentica (plan, run ou review)."""

    project: ProjectConfig
    command: str
    prompt: str | None = None

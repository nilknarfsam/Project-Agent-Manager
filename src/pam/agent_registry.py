"""Registro de agentes especializados do PAM (ai/agents/)."""

from __future__ import annotations

from pathlib import Path

from pam.config_loader import project_root

AGENTS_DIR = "ai/agents"

DEFAULT_AGENTS: dict[str, str] = {
    "plan": "architect",
    "run": "implementer",
    "review": "reviewer",
    "resume": "architect",
}


class AgentNotFoundError(ValueError):
    """Agente solicitado não existe no registro."""


class AgentRegistry:
    """Lista, valida e carrega definições de agentes em Markdown."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or project_root()

    def agents_dir(self) -> Path:
        return self.base_dir / AGENTS_DIR

    def agent_path(self, name: str) -> Path:
        return self.agents_dir() / f"{name}.md"

    def list_agents(self) -> list[str]:
        """Retorna nomes dos agentes disponíveis (sem extensão .md)."""
        directory = self.agents_dir()
        if not directory.is_dir():
            return []

        return sorted(path.stem for path in directory.glob("*.md"))

    def exists(self, name: str) -> bool:
        return self.agent_path(name).is_file()

    def validate(self, name: str) -> str:
        """Valida e retorna o nome do agente."""
        if not self.exists(name):
            available = ", ".join(self.list_agents()) or "(nenhum)"
            raise AgentNotFoundError(
                f"Agente '{name}' não encontrado em ai/agents/.\n"
                f"Disponíveis: {available}\n"
                f"Use 'python -m pam.main agents' para listar."
            )
        return name

    def load(self, name: str) -> str:
        """Carrega e retorna o conteúdo Markdown do agente."""
        self.validate(name)
        return self.agent_path(name).read_text(encoding="utf-8").strip()

    @classmethod
    def default_for_command(cls, command: str) -> str:
        """Retorna o agente padrão para plan/run/review/resume."""
        default = DEFAULT_AGENTS.get(command)
        if not default:
            raise ValueError(f"Comando sem agente padrão: {command}")
        return default

    def resolve(
        self,
        command: str,
        agent_name: str | None = None,
    ) -> str:
        """
        Resolve o agente a usar: explícito (--agent) ou padrão do comando.

        Raises:
            AgentNotFoundError: se --agent informado não existir.
        """
        if agent_name:
            return self.validate(agent_name)
        return self.default_for_command(command)

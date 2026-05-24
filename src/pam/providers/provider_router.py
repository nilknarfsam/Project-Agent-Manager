"""Roteamento de tarefas entre Gemini (leve) e Cursor (profundo)."""

from __future__ import annotations

from pam.providers.gemini_provider import GeminiProvider

GEMINI_TASK_TYPES = frozenset(
    {
        "analysis",
        "summarize",
        "docs",
        "roadmap",
        "tasks",
        "classify",
        "memory",
        "context",
        "pipeline_light",
    }
)

CURSOR_TASK_TYPES = frozenset(
    {
        "code_edit",
        "refactor",
        "deep_agent",
        "plan",
        "run",
        "review",
        "resume",
        "pipeline",
    }
)


class ProviderRouterError(ValueError):
    """Tarefa roteada para provider incorreto ou desconhecido."""


class ProviderRouter:
    """
    Decide qual runtime usar.

    Gemini: análise, sumarização, docs, tasks, roadmap leve.
    Cursor: edição de código, refactors, agentes profundos, pipelines completos.
    """

    def route(self, task_type: str) -> str:
        """Retorna 'gemini' ou 'cursor' para o tipo de tarefa."""
        normalized = task_type.strip().lower()
        if normalized in GEMINI_TASK_TYPES:
            return "gemini"
        if normalized in CURSOR_TASK_TYPES:
            return "cursor"
        raise ProviderRouterError(
            f"Tipo de tarefa desconhecido: '{task_type}'. "
            f"Gemini: {', '.join(sorted(GEMINI_TASK_TYPES))}. "
            f"Cursor: {', '.join(sorted(CURSOR_TASK_TYPES))}."
        )

    def get_gemini_provider(self, task_type: str) -> GeminiProvider:
        """Retorna GeminiProvider se a tarefa for leve; senão erro."""
        if self.route(task_type) != "gemini":
            raise ProviderRouterError(
                f"Tarefa '{task_type}' deve usar Cursor (plan/run/review/pipeline), "
                "não Gemini."
            )
        return GeminiProvider()

    def assert_cursor_task(self, task_type: str) -> None:
        """Valida que tarefa profunda não foi enviada ao Gemini por engano."""
        if self.route(task_type) == "gemini":
            raise ProviderRouterError(
                f"Tarefa '{task_type}' é leve — use ai-summary/ai-tasks/ai-docs."
            )

    def describe_routing(self) -> str:
        """Resumo legível do roteamento (debug/docs)."""
        lines = [
            "Provider routing (PAM):",
            "",
            "Gemini (leve):",
            "  " + ", ".join(sorted(GEMINI_TASK_TYPES)),
            "",
            "Cursor (profundo):",
            "  " + ", ".join(sorted(CURSOR_TASK_TYPES)),
        ]
        return "\n".join(lines)

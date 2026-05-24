"""Serviço compartilhado para comandos ai-* (Gemini)."""

from __future__ import annotations

from pam.config_loader import load_project
from pam.context_engine import ContextEngine
from pam.providers.provider_router import ProviderRouter
from pam.providers.base_provider import ProviderError


def collect_project_context(project_name: str) -> str:
    """Monta bloco de contexto PAM + metadata do projeto."""
    project = load_project(project_name)
    engine = ContextEngine()
    context_block = engine.build_context_block(project_name)

    header = (
        f"# Projeto: {project.name}\n\n"
        f"- **Repositório:** {project.repo_path}\n"
        f"- **Descrição:** {project.description}\n"
        f"- **Runtime PAM:** {project.default_runtime}\n\n"
    )
    body = context_block if context_block else "_(Nenhum arquivo em ai/context/ ou ai/memory/)_"
    return header + body


def run_ai_summary(project_name: str, extra: str | None = None) -> str:
    router = ProviderRouter()
    provider = router.get_gemini_provider("summarize")
    context = collect_project_context(project_name)
    if extra:
        context += f"\n\n## Instruções adicionais\n\n{extra.strip()}"
    return provider.summarize(context)


def run_ai_tasks(project_name: str, extra: str | None = None) -> str:
    router = ProviderRouter()
    provider = router.get_gemini_provider("tasks")
    context = collect_project_context(project_name)
    if extra:
        context += f"\n\n## Instruções adicionais\n\n{extra.strip()}"
    return provider.generate_tasks(context)


def run_ai_docs(project_name: str, extra: str | None = None) -> str:
    router = ProviderRouter()
    provider = router.get_gemini_provider("docs")
    context = collect_project_context(project_name)
    if extra:
        context += f"\n\n## Instruções adicionais\n\n{extra.strip()}"
    return provider.generate_docs(context)


def format_provider_error(exc: ProviderError) -> str:
    return str(exc)

"""Serviço compartilhado para comandos ai-* (Gemini)."""

from __future__ import annotations

import time

from pam.config_loader import load_project
from pam.context_engine import ContextEngine
from pam.metrics_store import MetricsStore
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


def _record_ai_metric(
    *,
    project_name: str,
    command: str,
    provider_name: str,
    model: str | None,
    duration_ms: int,
    success: bool,
    error_summary: str | None = None,
) -> None:
    try:
        MetricsStore().record_execution(
            project=project_name,
            command=command,
            status="success" if success else "error",
            success=success,
            duration_ms=duration_ms,
            provider=provider_name,
            model=model,
            error_summary=error_summary,
        )
    except Exception:
        pass


def _run_timed_ai(
    project_name: str,
    command: str,
    operation: str,
    runner,
    context: str,
) -> str:
    router = ProviderRouter()
    provider = router.get_gemini_provider(operation)
    model = provider.default_model
    started = time.perf_counter()
    try:
        result = runner(provider, context)
    except ProviderError as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        _record_ai_metric(
            project_name=project_name,
            command=command,
            provider_name=provider.name,
            model=model,
            duration_ms=duration_ms,
            success=False,
            error_summary=str(exc),
        )
        raise

    duration_ms = int((time.perf_counter() - started) * 1000)
    _record_ai_metric(
        project_name=project_name,
        command=command,
        provider_name=provider.name,
        model=model,
        duration_ms=duration_ms,
        success=True,
    )
    return result


def run_ai_summary(project_name: str, extra: str | None = None) -> str:
    context = collect_project_context(project_name)
    if extra:
        context += f"\n\n## Instruções adicionais\n\n{extra.strip()}"
    return _run_timed_ai(
        project_name,
        "ai-summary",
        "summarize",
        lambda provider, ctx: provider.summarize(ctx),
        context,
    )


def run_ai_tasks(project_name: str, extra: str | None = None) -> str:
    context = collect_project_context(project_name)
    if extra:
        context += f"\n\n## Instruções adicionais\n\n{extra.strip()}"
    return _run_timed_ai(
        project_name,
        "ai-tasks",
        "tasks",
        lambda provider, ctx: provider.generate_tasks(ctx),
        context,
    )


def run_ai_docs(project_name: str, extra: str | None = None) -> str:
    context = collect_project_context(project_name)
    if extra:
        context += f"\n\n## Instruções adicionais\n\n{extra.strip()}"
    return _run_timed_ai(
        project_name,
        "ai-docs",
        "docs",
        lambda provider, ctx: provider.generate_docs(ctx),
        context,
    )


def format_provider_error(exc: ProviderError) -> str:
    return str(exc)

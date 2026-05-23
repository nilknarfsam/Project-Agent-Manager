"""CLI do Project Agent Manager."""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

from pam.config_loader import list_projects, load_project
from pam.cursor_runner import CursorRunner
from pam.session_store import SessionStore, SessionStoreError


def _add_project_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "project",
        help="Nome do projeto (ex.: auratime, nilkplayer)",
    )
    parser.add_argument(
        "--task",
        default=None,
        help="Caminho para arquivo .md com a tarefa (ex.: ai/tasks/sprint_001_analyze_project.md)",
    )
    parser.add_argument(
        "--prompt",
        "-p",
        default=None,
        help="Instruções adicionais ao prompt base",
    )


def _execute_command(args: argparse.Namespace, command: str) -> int:
    project = load_project(args.project)
    runner = CursorRunner()

    task_path = CursorRunner.resolve_task_path(args.task)
    prompt = CursorRunner.build_prompt(
        command,
        task_path=task_path,
        extra_prompt=args.prompt,
        project=project.name,
    )
    mode = CursorRunner.mode_for_command(command)

    print(f"[{command}] Projeto: {project.name}")
    print(f"         Repo:   {project.repo_path}")
    print(f"         Modelo: {project.default_model}")
    print(f"         Modo:   {mode}")
    if task_path:
        print(f"         Tarefa: {task_path}")
    print(f"[{command}] Enviando prompt ao agente local...")

    try:
        record = runner.run(
            project,
            command,
            prompt,
            task_path=task_path,
        )
    except RuntimeError as exc:
        print(f"[{command}] Erro: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"[{command}] Erro: {exc}", file=sys.stderr)
        return 1
    except SessionStoreError as exc:
        print(f"[{command}] Erro: {exc}", file=sys.stderr)
        return 1

    print(f"[{command}] Concluído.")
    print(f"         Log:    {record.run_path}")
    print(f"         Status: {record.result.status}")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    """Planeja uma tarefa agentica para o projeto (modo plan)."""
    return _execute_command(args, "plan")


def cmd_run(args: argparse.Namespace) -> int:
    """Executa um fluxo agentico no projeto (modo agent)."""
    return _execute_command(args, "run")


def cmd_review(args: argparse.Namespace) -> int:
    """Revisa alterações ou resultados (prompt de revisão, modo agent)."""
    return _execute_command(args, "review")


def cmd_resume(args: argparse.Namespace) -> int:
    """Retoma sessão salva via Agent.resume() e envia novo prompt."""
    project = load_project(args.project)
    store = SessionStore()

    print(f"[resume] Projeto: {project.name}")

    try:
        if not store.has_session(project.name):
            print(
                "[resume] Nenhuma sessão encontrada para este projeto.\n"
                "         Execute plan primeiro para criar uma sessão, por exemplo:\n"
                "         python -m pam.main plan auratime "
                "--task ai/tasks/sprint_001_analyze_project.md"
            )
            return 0

        session = store.get_session(project.name)
        if session:
            print(f"         Agent ID:   {session.agent_id}")
            print(f"         Modo:       {session.mode}")

        runner = CursorRunner()
        task_path = (
            CursorRunner.resolve_task_path(args.task) if args.task else None
        )
        if task_path:
            print(f"         Tarefa:     {task_path}")
        if args.prompt:
            print("         Extra:      (instruções via -p)")

        print("[resume] Retomando agente e enviando prompt...")

        record = runner.resume_existing_session(
            project,
            task_path=task_path,
            extra_prompt=args.prompt,
        )
    except SessionStoreError as exc:
        print(f"[resume] Erro: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"[resume] Erro: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"[resume] Erro: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"[resume] Erro: {exc}", file=sys.stderr)
        return 1

    print("[resume] Concluído.")
    print(f"         Log:    {record.run_path}")
    print(f"         Status: {record.result.status}")
    return 0


def cmd_clear_session(args: argparse.Namespace) -> int:
    """Remove metadata de sessão do projeto (não apaga ai/runs/)."""
    project = load_project(args.project)
    store = SessionStore()

    print(f"[clear-session] Projeto: {project.name}")

    if store.clear_session(project.name):
        print(
            "[clear-session] Sessão removida de ai/sessions/.\n"
            "                Logs antigos em ai/runs/ foram preservados."
        )
    else:
        print("[clear-session] Nenhuma sessão salva para este projeto.")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pam",
        description=(
            "Project Agent Manager — Operating System for AI Development. "
            "Controlador Python para orquestrar agentes Cursor SDK."
        ),
    )
    parser.add_argument(
        "--list-projects",
        action="store_true",
        help="Lista projetos configurados em ai/projects/",
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    plan_parser = subparsers.add_parser(
        "plan",
        help="Planeja uma tarefa agentica (modo plan, somente leitura)",
    )
    _add_project_argument(plan_parser)
    plan_parser.set_defaults(func=cmd_plan)

    run_parser = subparsers.add_parser(
        "run",
        help="Executa um fluxo agentico (modo agent)",
    )
    _add_project_argument(run_parser)
    run_parser.set_defaults(func=cmd_run)

    review_parser = subparsers.add_parser(
        "review",
        help="Revisa o repositório com prompt dedicado",
    )
    _add_project_argument(review_parser)
    review_parser.set_defaults(func=cmd_review)

    resume_parser = subparsers.add_parser(
        "resume",
        help="Retoma sessão salva e envia novo prompt (Agent.resume)",
    )
    _add_project_argument(resume_parser)
    resume_parser.set_defaults(func=cmd_resume)

    clear_parser = subparsers.add_parser(
        "clear-session",
        help="Remove sessão salva do projeto (preserva ai/runs/)",
    )
    clear_parser.add_argument(
        "project",
        help="Nome do projeto (ex.: auratime, nilkplayer)",
    )
    clear_parser.set_defaults(func=cmd_clear_session)

    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_projects:
        projects = list_projects()
        if not projects:
            print("Nenhum projeto configurado em ai/projects/.")
            return 0
        print("Projetos disponíveis:")
        for name in projects:
            print(f"  - {name}")
        return 0

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

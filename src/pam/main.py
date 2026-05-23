"""CLI do Project Agent Manager."""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

from pam.config_loader import list_projects, load_project
from pam.cursor_runner import CursorRunner


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pam",
        description=(
            "Project Agent Manager — controlador agentico para projetos "
            "via Cursor Python SDK."
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

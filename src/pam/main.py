"""CLI do Project Agent Manager."""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

from pam.agent_registry import AgentNotFoundError, AgentRegistry
from pam.config_loader import list_projects, load_project
from pam.cursor_runner import CursorRunner
from pam.session_store import SessionStore, SessionStoreError
from pam.task_manager import TaskManager, TaskManagerError


def _add_project_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "project",
        help="Nome do projeto (ex.: auratime, nilkplayer)",
    )
    parser.add_argument(
        "--task",
        default=None,
        help=(
            "Tarefa: TASK-0001, caminho .md ou legado "
            "(ex.: ai/tasks/sprint_001_analyze_project.md)"
        ),
    )
    parser.add_argument(
        "--prompt",
        "-p",
        default=None,
        help="Instruções adicionais ao prompt base",
    )
    parser.add_argument(
        "--agent",
        default=None,
        help=(
            "Agente especializado (ex.: architect, implementer, reviewer). "
            "Padrões: plan->architect, run->implementer, review->reviewer"
        ),
    )


def _resolve_managed_task_id(
    task_manager: TaskManager,
    task_path,
) -> str | None:
    if not task_path:
        return None
    tid = task_manager.task_id_from_path(task_path)
    if tid and task_manager.find_task_files(tid):
        return tid
    return None


def _execute_command(args: argparse.Namespace, command: str) -> int:
    project = load_project(args.project)
    runner = CursorRunner()
    task_manager = TaskManager()

    try:
        agent_name = CursorRunner.resolve_agent_name(command, args.agent)
    except AgentNotFoundError as exc:
        print(f"[{command}] Erro: {exc}", file=sys.stderr)
        return 1

    task_path = None
    task_id: str | None = None

    try:
        if args.task:
            if command == "plan":
                raw_path = CursorRunner.resolve_task_path(args.task)
                meta, task_path = task_manager.ensure_task_for_plan(
                    project.name,
                    raw_path,
                    agent_name,
                )
                task_id = meta.task_id
            else:
                task_path = CursorRunner.resolve_task_path(args.task)
                task_id = _resolve_managed_task_id(task_manager, task_path)
                if task_id and command == "run":
                    task_manager.on_command_start(command, task_id)
        else:
            task_path = None
    except (TaskManagerError, FileNotFoundError) as exc:
        print(f"[{command}] Erro: {exc}", file=sys.stderr)
        return 1

    prompt = CursorRunner.build_prompt(
        command,
        task_path=task_path,
        extra_prompt=args.prompt,
        project=project.name,
        agent_name=args.agent,
    )
    mode = CursorRunner.mode_for_command(command)

    print(f"[{command}] Projeto: {project.name}")
    print(f"         Repo:   {project.repo_path}")
    print(f"         Modelo: {project.default_model}")
    print(f"         Agente: {agent_name}")
    print(f"         Modo:   {mode}")
    if task_id:
        print(f"         Task ID: {task_id}")
    if task_path:
        print(f"         Tarefa:  {task_path}")
    print(f"[{command}] Enviando prompt ao agente local...")

    try:
        record = runner.run(
            project,
            command,
            prompt,
            task_path=task_path,
            agent_name=agent_name,
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

    if task_id:
        try:
            task_manager.on_command_success(command, task_id)
        except TaskManagerError as exc:
            print(f"[{command}] Aviso (task): {exc}", file=sys.stderr)

    print(f"[{command}] Concluído.")
    print(f"         Log:    {record.run_path}")
    print(f"         Status: {record.result.status}")
    if task_id:
        meta = task_manager.load(task_id)
        print(f"         Task:   {meta.status}")
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


def cmd_agents(_args: argparse.Namespace) -> int:
    """Lista agentes especializados disponíveis em ai/agents/."""
    registry = AgentRegistry()
    agents = registry.list_agents()

    if not agents:
        print("Nenhum agente configurado em ai/agents/.")
        return 0

    print("Agentes especializados disponíveis:")
    for name in agents:
        print(f"  - {name}")
    print("\nPadroes por comando: plan->architect, run->implementer, review->reviewer")
    return 0


def cmd_tasks(args: argparse.Namespace) -> int:
    """Lista tarefas do Task Lifecycle System."""
    task_manager = TaskManager()
    project = getattr(args, "project", None)
    tasks = task_manager.list_tasks(project=project)

    if not tasks:
        label = f" para '{project}'" if project else ""
        print(f"Nenhuma tarefa gerenciada{label}.")
        return 0

    print("Tarefas gerenciadas:")
    for meta in tasks:
        folder = task_manager.find_task_files(meta.task_id)
        loc = folder[0].parent.name if folder else "?"
        print(
            f"  {meta.task_id}  [{meta.status:9}]  "
            f"{meta.project:12}  {loc:10}  {meta.title[:50]}"
        )
    return 0


def cmd_task_status(args: argparse.Namespace) -> int:
    """Exibe status e histórico de uma tarefa."""
    task_manager = TaskManager()
    try:
        meta = task_manager.load(args.task_id)
    except TaskManagerError as exc:
        print(f"[task-status] Erro: {exc}", file=sys.stderr)
        return 1

    files = task_manager.find_task_files(meta.task_id)
    location = files[0].parent.name if files else "?"

    print(f"Task:      {meta.task_id}")
    print(f"Titulo:    {meta.title}")
    print(f"Projeto:   {meta.project}")
    print(f"Status:    {meta.status}")
    print(f"Agente:    {meta.agent}")
    print(f"Pasta:     ai/tasks/{location}/")
    print(f"Criada:    {meta.created_at}")
    print(f"Atualizada:{meta.updated_at}")
    print("\nHistorico:")
    for entry in meta.history:
        ts = entry.get("timestamp", "?")
        msg = entry.get("message", "")
        frm = entry.get("from_status")
        to = entry.get("to_status", "?")
        if frm:
            print(f"  - {ts}: {frm} -> {to} ({msg})")
        else:
            print(f"  - {ts}: -> {to} ({msg})")
    return 0


def _task_status_command(
    args: argparse.Namespace,
    new_status: str,
    *,
    label: str,
    message: str,
) -> int:
    task_manager = TaskManager()
    try:
        meta = task_manager.update_status(
            args.task_id,
            new_status,
            message=message,
        )
    except TaskManagerError as exc:
        print(f"[{label}] Erro: {exc}", file=sys.stderr)
        return 1

    files = task_manager.find_task_files(meta.task_id)
    location = files[0].parent.name if files else "?"
    print(f"[{label}] {meta.task_id} -> {meta.status} (ai/tasks/{location}/)")
    return 0


def cmd_approve_task(args: argparse.Namespace) -> int:
    return _task_status_command(
        args, "approved", label="approve-task", message="approved manually"
    )


def cmd_complete_task(args: argparse.Namespace) -> int:
    return _task_status_command(
        args, "done", label="complete-task", message="completed manually"
    )


def cmd_block_task(args: argparse.Namespace) -> int:
    return _task_status_command(
        args, "blocked", label="block-task", message="blocked manually"
    )


def cmd_cancel_task(args: argparse.Namespace) -> int:
    return _task_status_command(
        args, "cancelled", label="cancel-task", message="cancelled manually"
    )


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
        if not session:
            print("[resume] Erro: sessão não encontrada.", file=sys.stderr)
            return 1

        print(f"         Agent ID:   {session.agent_id}")
        print(f"         Modo:       {session.mode}")
        if session.agent_name:
            print(f"         Agente:     {session.agent_name}")

        runner = CursorRunner()
        try:
            resume_agent = runner.resolve_resume_agent_name(
                session,
                explicit_agent=args.agent,
            )
        except AgentNotFoundError as exc:
            print(f"[resume] Erro: {exc}", file=sys.stderr)
            return 1

        task_path = None
        if args.task:
            try:
                task_path = CursorRunner.resolve_task_path(args.task)
            except FileNotFoundError as exc:
                print(f"[resume] Erro: {exc}", file=sys.stderr)
                return 1
            print(f"         Tarefa:     {task_path}")
        print(f"         Agente:     {resume_agent}")
        if args.prompt:
            print("         Extra:      (instruções via -p)")

        print("[resume] Retomando agente e enviando prompt...")

        record = runner.resume_existing_session(
            project,
            task_path=task_path,
            extra_prompt=args.prompt,
            agent_name=args.agent,
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


def _add_task_id_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "task_id",
        help="ID da tarefa (ex.: TASK-0001)",
    )


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

    agents_parser = subparsers.add_parser(
        "agents",
        help="Lista agentes especializados do PAM",
    )
    agents_parser.set_defaults(func=cmd_agents)

    tasks_parser = subparsers.add_parser(
        "tasks",
        help="Lista tarefas do Task Lifecycle System",
    )
    tasks_parser.add_argument(
        "--project",
        default=None,
        help="Filtrar por projeto (ex.: auratime)",
    )
    tasks_parser.set_defaults(func=cmd_tasks)

    task_status_parser = subparsers.add_parser(
        "task-status",
        help="Exibe status e histórico de uma tarefa",
    )
    _add_task_id_argument(task_status_parser)
    task_status_parser.set_defaults(func=cmd_task_status)

    approve_parser = subparsers.add_parser(
        "approve-task",
        help="Marca tarefa como approved",
    )
    _add_task_id_argument(approve_parser)
    approve_parser.set_defaults(func=cmd_approve_task)

    complete_parser = subparsers.add_parser(
        "complete-task",
        help="Marca tarefa como done",
    )
    _add_task_id_argument(complete_parser)
    complete_parser.set_defaults(func=cmd_complete_task)

    block_parser = subparsers.add_parser(
        "block-task",
        help="Marca tarefa como blocked",
    )
    _add_task_id_argument(block_parser)
    block_parser.set_defaults(func=cmd_block_task)

    cancel_parser = subparsers.add_parser(
        "cancel-task",
        help="Marca tarefa como cancelled",
    )
    _add_task_id_argument(cancel_parser)
    cancel_parser.set_defaults(func=cmd_cancel_task)

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

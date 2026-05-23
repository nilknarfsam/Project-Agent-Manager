"""Integração com o Cursor Python SDK."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from cursor_sdk import Agent, AgentOptions, LocalAgentOptions, RunResult

from pam.agent_registry import AgentRegistry
from pam.config_loader import project_root
from pam.context_engine import ContextEngine
from pam.models import ProjectConfig
from pam.session_store import SessionMetadata, SessionStore
from pam.task_manager import TaskManager, TaskManagerError

PROMPTS_DIR = "ai/prompts"
RUNS_DIR = "ai/runs"

COMMAND_PROMPTS = {
    "plan": "plan_prompt.md",
    "run": "run_prompt.md",
    "review": "review_prompt.md",
}

COMMAND_MODES = {
    "plan": "plan",
    "run": "agent",
    "review": "agent",
}


@dataclass(frozen=True)
class RunRecord:
    """Metadados de uma execução persistida em ai/runs/."""

    run_path: Path
    result: RunResult


class CursorRunner:
    """Wrapper sobre cursor-sdk para execuções locais."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        session_store: SessionStore | None = None,
        context_engine: ContextEngine | None = None,
        agent_registry: AgentRegistry | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("CURSOR_API_KEY")
        self.session_store = session_store or SessionStore()
        self.context_engine = context_engine or ContextEngine()
        self.agent_registry = agent_registry or AgentRegistry()

    def ensure_api_key(self) -> str:
        if not self.api_key:
            raise RuntimeError(
                "CURSOR_API_KEY não definida. Configure em .env ou no ambiente."
            )
        return self.api_key

    def build_agent_options(
        self,
        project: ProjectConfig,
        *,
        mode: str = "agent",
    ) -> AgentOptions:
        """Monta opções do agente local com modo plan ou agent."""
        api_key = self.ensure_api_key()
        cwd = Path(project.repo_path)

        if not cwd.is_dir():
            raise FileNotFoundError(
                f"Repositório do projeto não encontrado: {cwd}"
            )

        if project.default_runtime != "local":
            if project.default_runtime == "cloud":
                raise NotImplementedError(
                    "Runtime 'cloud' ainda não implementado. Use 'local'."
                )
            raise ValueError(
                f"Runtime desconhecido '{project.default_runtime}' "
                f"para {project.name}."
            )

        return AgentOptions(
            api_key=api_key,
            model=project.default_model,
            mode=mode,  # type: ignore[arg-type]
            local=LocalAgentOptions(cwd=str(cwd)),
        )

    @staticmethod
    def prompts_dir() -> Path:
        return project_root() / PROMPTS_DIR

    @staticmethod
    def runs_dir() -> Path:
        directory = project_root() / RUNS_DIR
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @classmethod
    def load_prompt_template(cls, command: str) -> str:
        filename = COMMAND_PROMPTS.get(command)
        if not filename:
            raise ValueError(f"Comando sem template de prompt: {command}")

        path = cls.prompts_dir() / filename
        if not path.is_file():
            raise FileNotFoundError(f"Template de prompt não encontrado: {path}")

        return path.read_text(encoding="utf-8").strip()

    @classmethod
    def resolve_task_path(cls, task: str | None) -> Path | None:
        """Resolve tarefa legada, TASK-XXXX ou caminho em ai/tasks/."""
        if not task:
            return None

        try:
            return TaskManager().resolve_task_reference(task)
        except TaskManagerError as exc:
            raise FileNotFoundError(str(exc)) from exc

    @classmethod
    def resolve_agent_name(cls, command: str, agent_name: str | None = None) -> str:
        """Resolve agente explícito ou padrão do comando."""
        return AgentRegistry().resolve(command, agent_name)

    @classmethod
    def build_prompt(
        cls,
        command: str,
        *,
        task_path: Path | None = None,
        extra_prompt: str | None = None,
        project: str | None = None,
        agent_name: str | None = None,
        context_engine: ContextEngine | None = None,
        agent_registry: AgentRegistry | None = None,
    ) -> str:
        """
        Monta prompt com: contexto global, memória, agente, template, tarefa, extras.
        """
        registry = agent_registry or AgentRegistry()
        resolved_agent = registry.resolve(command, agent_name)
        sections: list[str] = []

        if project:
            engine = context_engine or ContextEngine()
            context_block = engine.build_context_block(project)
            if context_block:
                sections.append(context_block)

        agent_body = registry.load(resolved_agent)
        sections.append(
            f"## Agente especializado: {resolved_agent}\n\n{agent_body}"
        )

        sections.append(cls.load_prompt_template(command))

        if task_path:
            task_body = task_path.read_text(encoding="utf-8").strip()
            sections.append(f"## Tarefa\n\n{task_body}")

        if extra_prompt:
            sections.append(
                f"## Instruções adicionais\n\n{extra_prompt.strip()}"
            )

        return "\n\n---\n\n".join(sections)

    @staticmethod
    def mode_for_command(command: str) -> str:
        mode = COMMAND_MODES.get(command)
        if not mode:
            raise ValueError(f"Comando desconhecido: {command}")
        return mode

    def create_session(
        self,
        project: ProjectConfig,
        mode: str,
        *,
        task: str | None = None,
    ) -> SessionMetadata:
        """
        Ponto de extensão: registrar nova sessão antes de criar o agente.

        Sprint 3: passará a chamar Agent.create() e persistir agent_id real.
        """
        return self.session_store.create_metadata(
            project=project.name,
            agent_id="",
            mode=mode,
            task=task,
            status="pending",
        )

    def save_session_metadata(self, metadata: SessionMetadata) -> Path:
        """Persiste metadata da sessão em ai/sessions/<project>.json."""
        return self.session_store.save(metadata)

    def resume_session(
        self,
        project: ProjectConfig,
        agent_id: str,
        *,
        mode: str = "agent",
    ) -> Agent:
        """Retoma agente existente via Agent.resume(agent_id, options)."""
        if not agent_id or not agent_id.strip():
            raise ValueError("agent_id inválido para retomada de sessão.")

        options = self.build_agent_options(project, mode=mode)
        return Agent.resume(agent_id, options)

    def resolve_resume_agent_name(
        self,
        session: SessionMetadata,
        *,
        explicit_agent: str | None = None,
    ) -> str:
        """Usa --agent, depois sessão salva, depois architect como fallback."""
        if explicit_agent:
            return self.agent_registry.resolve("resume", explicit_agent)
        if session.agent_name:
            return self.agent_registry.validate(session.agent_name)
        return self.agent_registry.default_for_command("resume")

    def build_resume_prompt(
        self,
        project_name: str,
        session: SessionMetadata,
        *,
        task_path: Path | None = None,
        extra_prompt: str | None = None,
        agent_name: str | None = None,
    ) -> str:
        """Monta prompt de retomada com contexto, agente e modo da sessão."""
        resolved_agent = self.resolve_resume_agent_name(
            session,
            explicit_agent=agent_name,
        )
        template_command = "plan" if session.mode == "plan" else "run"
        sections: list[str] = []

        context_block = self.context_engine.build_context_block(project_name)
        if context_block:
            sections.append(context_block)

        agent_body = self.agent_registry.load(resolved_agent)
        sections.append(
            f"## Agente especializado: {resolved_agent}\n\n{agent_body}"
        )

        sections.append(self.load_prompt_template(template_command))

        sections.append(
            "## Retomada de sessão\n\n"
            f"Continue a partir da sessão do agente `{session.agent_id}` "
            f"(último run: {session.last_run_id or 'nenhum'})."
        )

        if task_path:
            task_body = task_path.read_text(encoding="utf-8").strip()
            sections.append(f"## Tarefa\n\n{task_body}")

        if extra_prompt:
            sections.append(
                f"## Instruções adicionais\n\n{extra_prompt.strip()}"
            )

        return "\n\n---\n\n".join(sections)

    def resume_existing_session(
        self,
        project: ProjectConfig,
        *,
        task_path: Path | None = None,
        extra_prompt: str | None = None,
        agent_name: str | None = None,
    ) -> RunRecord:
        """
        Retoma sessão salva, envia prompt e persiste run + metadata.

        Fluxo: carregar sessão → Agent.resume → send → wait → ai/runs → ai/sessions.
        """
        session = self.session_store.get_session(project.name)
        if not session or not session.agent_id.strip():
            raise ValueError(
                f"Nenhuma sessão ativa para '{project.name}'. "
                "Execute plan, run ou review primeiro."
            )

        mode = session.mode
        resolved_agent = self.resolve_resume_agent_name(
            session,
            explicit_agent=agent_name,
        )
        prompt = self.build_resume_prompt(
            project.name,
            session,
            task_path=task_path,
            extra_prompt=extra_prompt,
            agent_name=agent_name,
        )

        with self.resume_session(project, session.agent_id, mode=mode) as agent:
            result = agent.send(prompt).wait()

        command = "resume"
        if str(result.status).lower() == "error":
            run_path = self._save_run(
                project,
                command,
                mode,
                prompt,
                result,
                task_path=task_path,
            )
            self.session_store.update_session_run(
                project.name,
                last_run_id=result.id,
                status=str(result.status),
                mode=mode,
                task=str(task_path) if task_path else session.task,
                agent_name=resolved_agent,
            )
            raise RuntimeError(
                f"Retomada falhou (status={result.status}). "
                f"Detalhes em {run_path}"
            )

        return self._finalize_run(
            project,
            command,
            mode,
            prompt,
            result,
            task_path=task_path,
            session_agent_id=session.agent_id,
            agent_name=resolved_agent,
        )

    def run_prompt(
        self,
        project: ProjectConfig,
        prompt: str,
        *,
        mode: str = "agent",
        use_session: bool = False,
    ) -> RunResult:
        """
        Envia o prompt ao agente local.

        Por padrão usa Agent.prompt (create + send + wait).
        Com use_session=True, usa Agent.create + agent.send().wait().
        """
        options = self.build_agent_options(project, mode=mode)

        if use_session:
            with Agent.create(options) as agent:
                return agent.send(prompt).wait()

        return Agent.prompt(prompt, options)

    def run(
        self,
        project: ProjectConfig,
        command: str,
        prompt: str,
        *,
        task_path: Path | None = None,
        use_session: bool = False,
        agent_name: str | None = None,
    ) -> RunRecord:
        """Executa o agente e persiste o resultado em ai/runs/."""
        mode = self.mode_for_command(command)
        result = self.run_prompt(
            project,
            prompt,
            mode=mode,
            use_session=use_session,
        )

        if str(result.status).lower() == "error":
            run_path = self._save_run(
                project,
                command,
                mode,
                prompt,
                result,
                task_path=task_path,
            )
            raise RuntimeError(
                f"Execução falhou (status={result.status}). "
                f"Detalhes em {run_path}"
            )

        return self._finalize_run(
            project,
            command,
            mode,
            prompt,
            result,
            task_path=task_path,
            agent_name=agent_name,
        )

    def _finalize_run(
        self,
        project: ProjectConfig,
        command: str,
        mode: str,
        prompt: str,
        result: RunResult,
        *,
        task_path: Path | None,
        session_agent_id: str | None = None,
        agent_name: str | None = None,
    ) -> RunRecord:
        """Persiste run e atualiza ou cria metadata de sessão."""
        run_path = self._save_run(
            project,
            command,
            mode,
            prompt,
            result,
            task_path=task_path,
            agent_name=agent_name,
        )

        task_str = str(task_path) if task_path else None
        agent_id = session_agent_id or result.agent_id
        existing = self.session_store.get_session(project.name)

        if existing and existing.agent_id:
            self.session_store.update_session_run(
                project.name,
                last_run_id=result.id,
                status=str(result.status),
                mode=mode,
                task=task_str if task_str else existing.task,
                agent_name=agent_name if agent_name else existing.agent_name,
            )
        else:
            self.save_session_metadata(
                self.session_store.create_metadata(
                    project=project.name,
                    agent_id=agent_id,
                    last_run_id=result.id,
                    mode=mode,
                    task=task_str,
                    agent_name=agent_name,
                    status=str(result.status),
                )
            )

        return RunRecord(run_path=run_path, result=result)

    def _save_run(
        self,
        project: ProjectConfig,
        command: str,
        mode: str,
        prompt: str,
        result: RunResult,
        *,
        task_path: Path | None,
        agent_name: str | None = None,
    ) -> Path:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base_name = f"{timestamp}_{project.name}_{command}"
        runs_dir = self.runs_dir()

        payload = {
            "timestamp": timestamp,
            "project": project.name,
            "command": command,
            "mode": mode,
            "agent_name": agent_name,
            "model": project.default_model,
            "repo_path": str(project.repo_path),
            "task_path": str(task_path) if task_path else None,
            "status": str(result.status),
            "run_id": result.id,
            "agent_id": result.agent_id,
            "duration_ms": result.duration_ms,
            "result": result.result,
        }

        json_path = runs_dir / f"{base_name}.json"
        json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        md_path = runs_dir / f"{base_name}.md"
        md_path.write_text(
            self._format_run_markdown(payload, prompt),
            encoding="utf-8",
        )

        return md_path

    @staticmethod
    def _format_run_markdown(payload: dict, prompt: str) -> str:
        lines = [
            f"# Run {payload['timestamp']} — {payload['project']} ({payload['command']})",
            "",
            f"- **Modo SDK:** {payload['mode']}",
        ]
        if payload.get("agent_name"):
            lines.append(f"- **Agente PAM:** {payload['agent_name']}")
        lines.extend([
            f"- **Modelo:** {payload['model']}",
            f"- **Repositório:** `{payload['repo_path']}`",
            f"- **Status:** {payload['status']}",
            f"- **Run ID:** {payload['run_id']}",
            f"- **Agent ID:** {payload['agent_id']}",
            f"- **Duração:** {payload['duration_ms']} ms",
        ])
        if payload.get("task_path"):
            lines.append(f"- **Tarefa:** `{payload['task_path']}`")

        lines.extend(
            [
                "",
                "## Prompt enviado",
                "",
                "```",
                prompt,
                "```",
                "",
                "## Resultado",
                "",
                payload.get("result") or "_(vazio)_",
                "",
            ]
        )
        return "\n".join(lines)

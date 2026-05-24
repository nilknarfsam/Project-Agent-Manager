"""Multi-Agent Orchestration — execução sequencial de pipelines YAML."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

from pam.agent_registry import AgentRegistry
from pam.config_loader import project_root
from pam.cursor_runner import AgentStepRecord, CursorRunner
from pam.models import ProjectConfig
from pam.pipeline_result import PipelineResult, PipelineStepResult
from pam.providers.base_provider import ProviderError
from pam.providers.gemini_provider import GeminiProvider
from pam.providers.provider_router import ProviderRouter
from pam.runtime_profiles import AgentRuntimeProfile, format_profile_error
from pam.task_manager import TaskManager, TaskManagerError

PIPELINES_DIR = "ai/pipelines"
PIPELINE_RUNS_DIR = "ai/runs/pipelines"
MAX_CONTEXT_CHARS = 12_000
SUMMARY_CHARS = 2_000


class PipelineEngineError(ValueError):
    """Erro de validação ou execução de pipeline."""


@dataclass(frozen=True)
class PipelineDefinition:
    """Definição carregada de ai/pipelines/<nome>.yaml."""

    name: str
    steps: tuple[str, ...]
    description: str = ""


class PipelineEngine:
    """Orquestra pipelines sequenciais de agentes especializados."""

    def __init__(
        self,
        base_dir: Path | None = None,
        runner: CursorRunner | None = None,
        task_manager: TaskManager | None = None,
        agent_registry: AgentRegistry | None = None,
    ) -> None:
        self.base_dir = base_dir or project_root()
        self.runner = runner or CursorRunner()
        self.task_manager = task_manager or TaskManager(self.base_dir)
        self.agent_registry = agent_registry or AgentRegistry(self.base_dir)
        self.provider_router = ProviderRouter()

    def pipelines_dir(self) -> Path:
        return self.base_dir / PIPELINES_DIR

    def pipeline_runs_dir(self) -> Path:
        directory = self.base_dir / PIPELINE_RUNS_DIR
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @staticmethod
    def utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def list_pipelines(self) -> list[str]:
        directory = self.pipelines_dir()
        if not directory.is_dir():
            return []
        return sorted(path.stem for path in directory.glob("*.yaml"))

    def load_pipeline(self, name: str) -> PipelineDefinition:
        """Carrega definição YAML do pipeline."""
        path = self.pipelines_dir() / f"{name}.yaml"
        if not path.is_file():
            available = ", ".join(self.list_pipelines()) or "(nenhum)"
            raise PipelineEngineError(
                f"Pipeline '{name}' não encontrado em {path}. "
                f"Disponíveis: {available}"
            )

        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)

        if not isinstance(data, dict):
            raise PipelineEngineError(f"YAML inválido em {path}: esperado mapping.")

        steps_raw = data.get("steps")
        if not isinstance(steps_raw, list) or not steps_raw:
            raise PipelineEngineError(
                f"Pipeline '{name}' deve definir 'steps' como lista não vazia."
            )

        steps: list[str] = []
        for item in steps_raw:
            agent = str(item).strip()
            if not agent:
                continue
            self.agent_registry.validate(agent)
            steps.append(agent)

        if not steps:
            raise PipelineEngineError(f"Pipeline '{name}' não possui steps válidos.")

        pipeline_name = str(data.get("name", name)).strip() or name
        description = str(data.get("description", "")).strip()

        return PipelineDefinition(
            name=pipeline_name,
            steps=tuple(steps),
            description=description,
        )

    def resolve_steps(
        self,
        pipeline: PipelineDefinition,
        from_step: str | None = None,
    ) -> list[str]:
        """Retorna steps a executar, opcionalmente a partir de --from-step."""
        steps = list(pipeline.steps)
        if not from_step:
            return steps

        agent = from_step.strip()
        self.agent_registry.validate(agent)
        if agent not in steps:
            raise PipelineEngineError(
                f"Agente '{agent}' não faz parte do pipeline '{pipeline.name}'. "
                f"Steps: {', '.join(steps)}"
            )
        start_index = steps.index(agent)
        return steps[start_index:]

    @staticmethod
    def _truncate(text: str, limit: int) -> str:
        text = text.strip()
        if len(text) <= limit:
            return text
        return text[: limit - 3] + "..."

    def _append_accumulated_context(
        self,
        accumulated: str,
        agent: str,
        summary: str,
    ) -> str:
        block = f"### Step: {agent}\n\n{summary.strip()}\n"
        combined = (accumulated + "\n\n" + block).strip() if accumulated else block.strip()
        return self._truncate(combined, MAX_CONTEXT_CHARS)

    @staticmethod
    def _resolved_model(profile: AgentRuntimeProfile, project: ProjectConfig) -> str:
        if profile.model:
            return profile.model
        if profile.provider == "gemini":
            return profile.display_model()
        return project.default_model

    def _save_gemini_pipeline_run(
        self,
        project: ProjectConfig,
        *,
        agent_name: str,
        command: str,
        mode: str,
        prompt: str,
        result_text: str,
        model: str,
        task_path: Path | None,
        file_label: str,
    ) -> Path:
        """Persiste log de step Gemini em ai/runs/pipelines/."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base_name = f"{timestamp}_{project.name}_{file_label}"
        runs_dir = self.runner.pipelines_dir()

        payload = {
            "timestamp": timestamp,
            "project": project.name,
            "command": command,
            "mode": mode,
            "agent_name": agent_name,
            "provider": "gemini",
            "model": model,
            "repo_path": str(project.repo_path),
            "task_path": str(task_path) if task_path else None,
            "status": "success",
            "run_id": f"gemini-{timestamp}",
            "agent_id": "",
            "duration_ms": 0,
            "result": result_text,
            "file_label": file_label,
        }

        json_path = runs_dir / f"{base_name}.json"
        json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        md_path = runs_dir / f"{base_name}.md"
        md_path.write_text(
            self.runner._format_run_markdown(payload, prompt),
            encoding="utf-8",
        )
        return md_path

    def _run_gemini_agent_step(
        self,
        project: ProjectConfig,
        agent_name: str,
        profile: AgentRuntimeProfile,
        *,
        task_path: Path | None = None,
        previous_context: str | None = None,
        pipeline_name: str | None = None,
        task_id: str | None = None,
        step_index: int | None = None,
    ) -> AgentStepRecord:
        """Executa step de pipeline via Gemini (agentes leves)."""
        command = self.runner.pipeline_command_for_agent(agent_name)
        mode = profile.mode or "gemini"
        prompt = self.runner.build_pipeline_step_prompt(
            agent_name,
            command=command,
            task_path=task_path,
            previous_context=previous_context,
            project=project.name,
            pipeline_name=pipeline_name,
        )
        model = self._resolved_model(profile, project)

        try:
            provider = GeminiProvider(default_model=model)
            result_text = provider.generate(prompt, model=model)
        except ProviderError as exc:
            raise RuntimeError(format_profile_error("gemini", exc)) from exc

        summary = self._truncate(result_text, SUMMARY_CHARS)

        label_parts = ["pipeline"]
        if pipeline_name:
            label_parts.append(pipeline_name)
        if task_id:
            label_parts.append(task_id.lower())
        if step_index is not None:
            label_parts.append(f"step{step_index:02d}")
        label_parts.append(agent_name)
        file_label = "_".join(label_parts)

        run_path = self._save_gemini_pipeline_run(
            project,
            agent_name=agent_name,
            command=command,
            mode=mode,
            prompt=prompt,
            result_text=result_text,
            model=model,
            task_path=task_path,
            file_label=file_label,
        )

        fake_result = SimpleNamespace(
            id=f"gemini-{agent_name}",
            agent_id="",
            status="success",
            result=result_text,
            duration_ms=0,
        )

        return AgentStepRecord(
            agent_name=agent_name,
            command=command,
            mode=mode,
            prompt=prompt,
            run_path=run_path,
            result=fake_result,  # type: ignore[arg-type]
            summary=summary,
            provider="gemini",
            model=model,
        )

    def _execute_agent_step(
        self,
        project: ProjectConfig,
        agent_name: str,
        profile: AgentRuntimeProfile,
        *,
        task_path: Path | None = None,
        previous_context: str | None = None,
        pipeline_name: str | None = None,
        task_id: str | None = None,
        step_index: int | None = None,
    ) -> AgentStepRecord:
        """Executa step conforme runtime profile (Cursor ou Gemini)."""
        if profile.provider == "cursor":
            return self.runner.run_agent_step(
                project,
                agent_name,
                task_path=task_path,
                previous_context=previous_context,
                pipeline_name=pipeline_name,
                task_id=task_id,
                step_index=step_index,
                mode_override=profile.mode,
                model_override=profile.model,
                provider=profile.provider,
            )
        if profile.provider == "gemini":
            return self._run_gemini_agent_step(
                project,
                agent_name,
                profile,
                task_path=task_path,
                previous_context=previous_context,
                pipeline_name=pipeline_name,
                task_id=task_id,
                step_index=step_index,
            )
        raise PipelineEngineError(
            f"Provider '{profile.provider}' para agente '{agent_name}' "
            "ainda não suportado em pipeline. "
            "Use cursor ou gemini em ai/runtime_profiles/default_profiles.yaml."
        )

    def _build_final_summary(self, steps: list[PipelineStepResult]) -> str:
        if not steps:
            return "Nenhum step executado."
        lines = [f"Pipeline concluiu {len(steps)} step(s):"]
        for step in steps:
            icon = "OK" if step.status == "success" else "FAIL"
            lines.append(f"- [{icon}] {step.agent}: {step.status}")
        return "\n".join(lines)

    def _save_pipeline_artifacts(
        self,
        result: PipelineResult,
        *,
        prompt_log: dict[str, str] | None = None,
    ) -> tuple[Path, Path]:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base_name = (
            f"{timestamp}_{result.project}_{result.pipeline_name}_{result.task_id}"
        )
        runs_dir = self.pipeline_runs_dir()

        json_path = runs_dir / f"{base_name}.json"
        json_path.write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        md_lines = [
            f"# Pipeline {result.pipeline_name} — {result.project}",
            "",
            f"- **Task:** {result.task_id}",
            f"- **Sucesso:** {result.success}",
            f"- **Início:** {result.started_at}",
            f"- **Fim:** {result.finished_at}",
            "",
            "## Resumo final",
            "",
            result.final_summary,
            "",
            "## Steps",
            "",
        ]
        for step in result.steps:
            md_lines.extend(
                [
                    f"### {step.agent} ({step.status})",
                    "",
                    f"- Início: {step.started_at}",
                    f"- Fim: {step.finished_at}",
                ]
            )
            if step.provider:
                md_lines.append(f"- Provider: {step.provider}")
            if step.model:
                md_lines.append(f"- Modelo: {step.model}")
            if step.run_path:
                md_lines.append(f"- Log: `{step.run_path}`")
            if step.error:
                md_lines.append(f"- Erro: {step.error}")
            md_lines.extend(["", step.summary or "_(sem resumo)_", ""])

        if prompt_log:
            md_lines.extend(["## Prompts por step", ""])
            for agent, prompt in prompt_log.items():
                md_lines.extend(
                    [
                        f"### Prompt — {agent}",
                        "",
                        "```",
                        prompt,
                        "```",
                        "",
                    ]
                )

        md_path = runs_dir / f"{base_name}.md"
        md_path.write_text("\n".join(md_lines), encoding="utf-8")
        return json_path, md_path

    def execute(
        self,
        project: ProjectConfig,
        task_id: str,
        *,
        pipeline_name: str = "default_pipeline",
        from_step: str | None = None,
    ) -> PipelineResult:
        """
        Executa pipeline sequencial para uma task gerenciada.

        Contexto acumulado de cada step é passado ao próximo agente.
        """
        pipeline = self.load_pipeline(pipeline_name)
        steps = self.resolve_steps(pipeline, from_step)

        tid = self.task_manager.normalize_task_id(task_id)
        meta = self.task_manager.load(tid)
        if meta.project != project.name:
            raise PipelineEngineError(
                f"Task {tid} pertence a '{meta.project}', não a '{project.name}'."
            )

        files = self.task_manager.find_task_files(tid)
        if not files:
            raise PipelineEngineError(f"Arquivos da task {tid} não encontrados.")
        task_path = files[0]

        started_at = self.utc_now()
        self.task_manager.update_status(
            tid,
            "running",
            message=f"pipeline {pipeline.name} started",
        )

        accumulated_context = ""
        step_results: list[PipelineStepResult] = []
        prompt_log: dict[str, str] = {}
        success = True

        for index, agent in enumerate(steps, start=1):
            step_started = self.utc_now()
            profile = self.provider_router.route_agent(agent)
            resolved_model = self._resolved_model(profile, project)
            print(
                f"[pipeline] Step {index}/{len(steps)}: {agent} "
                f"({pipeline.name} / {tid}) "
                f"[provider={profile.provider}, model={resolved_model}]"
            )

            try:
                record = self._execute_agent_step(
                    project,
                    agent,
                    profile,
                    task_path=task_path,
                    previous_context=accumulated_context or None,
                    pipeline_name=pipeline.name,
                    task_id=tid,
                    step_index=index,
                )
            except (RuntimeError, FileNotFoundError) as exc:
                step_finished = self.utc_now()
                step_result = PipelineStepResult(
                    agent=agent,
                    status="error",
                    started_at=step_started,
                    finished_at=step_finished,
                    summary="",
                    error=str(exc),
                    provider=profile.provider,
                    model=resolved_model,
                )
                step_results.append(step_result)
                self.task_manager.record_pipeline_step(
                    tid,
                    pipeline_name=pipeline.name,
                    agent=agent,
                    status="error",
                    started_at=step_started,
                    finished_at=step_finished,
                    summary="",
                    run_path=None,
                    error=str(exc),
                    provider=profile.provider,
                    model=resolved_model,
                )
                success = False
                break

            step_finished = self.utc_now()
            status = (
                "success"
                if str(record.result.status).lower() != "error"
                else "error"
            )
            summary = record.summary
            step_model = record.model or resolved_model

            step_result = PipelineStepResult(
                agent=agent,
                status=status,
                started_at=step_started,
                finished_at=step_finished,
                summary=summary,
                run_path=str(record.run_path),
                provider=record.provider,
                model=step_model,
            )
            step_results.append(step_result)
            prompt_log[agent] = record.prompt

            self.task_manager.record_pipeline_step(
                tid,
                pipeline_name=pipeline.name,
                agent=agent,
                status=status,
                started_at=step_started,
                finished_at=step_finished,
                summary=summary,
                run_path=str(record.run_path),
                provider=record.provider,
                model=step_model,
            )

            if status == "error":
                success = False
                step_result.error = summary or "execução retornou status error"
                break

            accumulated_context = self._append_accumulated_context(
                accumulated_context,
                agent,
                summary,
            )

            if agent == "reviewer":
                self.task_manager.update_status(
                    tid,
                    "reviewed",
                    message=f"pipeline step {agent} completed",
                )

        finished_at = self.utc_now()
        final_summary = self._build_final_summary(step_results)

        if success:
            self.task_manager.update_status(
                tid,
                "done",
                message=f"pipeline {pipeline.name} completed",
            )
        elif step_results:
            self.task_manager.update_status(
                tid,
                "blocked",
                message=(
                    f"pipeline {pipeline.name} failed at step "
                    f"{step_results[-1].agent}"
                ),
            )

        result = PipelineResult(
            pipeline_name=pipeline.name,
            task_id=tid,
            project=project.name,
            started_at=started_at,
            finished_at=finished_at,
            steps=step_results,
            final_summary=final_summary,
            success=success,
        )

        json_path, md_path = self._save_pipeline_artifacts(result, prompt_log=prompt_log)
        print(f"[pipeline] Resultado consolidado: {md_path}")
        print(f"[pipeline] JSON: {json_path}")
        print(f"[pipeline] Sucesso: {success}")

        return result

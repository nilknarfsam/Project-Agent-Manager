"""Task Lifecycle System — identidade, status, histórico e pastas por estado."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pam.config_loader import project_root

TASKS_DIR = "ai/tasks"
COUNTER_FILE = ".task_counter"

TASK_STATUSES = (
    "planned",
    "approved",
    "running",
    "reviewed",
    "done",
    "blocked",
    "cancelled",
)

STATUS_FOLDERS: dict[str, str] = {
    "planned": "active",
    "approved": "active",
    "running": "active",
    "reviewed": "active",
    "done": "completed",
    "blocked": "blocked",
    "cancelled": "archived",
}

LIFECYCLE_SUBDIRS = ("active", "completed", "blocked", "archived")

TASK_ID_PATTERN = re.compile(r"^TASK-\d{4}$", re.IGNORECASE)


class TaskManagerError(ValueError):
    """Erro de validação ou operação em tarefas."""


@dataclass
class TaskMetadata:
    """Metadata JSON de uma tarefa gerenciada pelo PAM."""

    task_id: str
    title: str
    project: str
    status: str
    agent: str
    created_at: str
    updated_at: str
    history: list[dict[str, Any]] = field(default_factory=list)
    pipeline_history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskMetadata":
        return cls(
            task_id=str(data["task_id"]).upper(),
            title=str(data["title"]),
            project=str(data["project"]),
            status=str(data["status"]),
            agent=str(data["agent"]),
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
            history=list(data.get("history", [])),
            pipeline_history=list(data.get("pipeline_history", [])),
        )


class TaskManager:
    """CRUD e ciclo de vida de tarefas em ai/tasks/."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or project_root()
        self._ensure_structure()

    def tasks_root(self) -> Path:
        return self.base_dir / TASKS_DIR

    def _ensure_structure(self) -> None:
        root = self.tasks_root()
        root.mkdir(parents=True, exist_ok=True)
        for subdir in LIFECYCLE_SUBDIRS:
            (root / subdir).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def validate_status(cls, status: str) -> str:
        if status not in TASK_STATUSES:
            raise TaskManagerError(
                f"Status inválido '{status}'. "
                f"Válidos: {', '.join(TASK_STATUSES)}"
            )
        return status

    @classmethod
    def normalize_task_id(cls, task_id: str) -> str:
        tid = task_id.strip().upper()
        if not TASK_ID_PATTERN.match(tid):
            raise TaskManagerError(
                f"ID de tarefa inválido '{task_id}'. Use formato TASK-0001."
            )
        return tid

    @classmethod
    def task_id_from_path(cls, path: Path) -> str | None:
        stem = path.stem.upper()
        if TASK_ID_PATTERN.match(stem):
            return stem
        return None

    def _counter_path(self) -> Path:
        return self.tasks_root() / COUNTER_FILE

    def next_task_id(self) -> str:
        """Gera próximo TASK-XXXX sequencial."""
        counter_path = self._counter_path()
        next_num = 1

        if counter_path.is_file():
            try:
                data = json.loads(counter_path.read_text(encoding="utf-8"))
                next_num = int(data.get("next", 1))
            except (json.JSONDecodeError, TypeError, ValueError):
                next_num = 1

        max_found = 0
        for meta in self.list_tasks():
            match = re.search(r"(\d+)$", meta.task_id)
            if match:
                max_found = max(max_found, int(match.group(1)))

        next_num = max(next_num, max_found + 1)
        task_id = f"TASK-{next_num:04d}"
        counter_path.write_text(
            json.dumps({"next": next_num + 1}, indent=2),
            encoding="utf-8",
        )
        return task_id

    def _folder_for_status(self, status: str) -> str:
        self.validate_status(status)
        return STATUS_FOLDERS[status]

    def json_path(self, task_id: str, status: str | None = None) -> Path:
        tid = self.normalize_task_id(task_id)
        if status is None:
            found = self.find_task_files(tid)
            if not found:
                raise TaskManagerError(f"Tarefa '{tid}' não encontrada.")
            return found[1]
        folder = self._folder_for_status(status)
        return self.tasks_root() / folder / f"{tid}.json"

    def md_path(self, task_id: str, status: str | None = None) -> Path:
        tid = self.normalize_task_id(task_id)
        if status is None:
            found = self.find_task_files(tid)
            if not found:
                raise TaskManagerError(f"Tarefa '{tid}' não encontrada.")
            return found[0]
        folder = self._folder_for_status(status)
        return self.tasks_root() / folder / f"{tid}.md"

    def find_task_files(self, task_id: str) -> tuple[Path, Path] | None:
        """Localiza .md e .json da tarefa em qualquer subpasta do lifecycle."""
        tid = self.normalize_task_id(task_id)
        for subdir in LIFECYCLE_SUBDIRS:
            md = self.tasks_root() / subdir / f"{tid}.md"
            js = self.tasks_root() / subdir / f"{tid}.json"
            if md.is_file() and js.is_file():
                return md, js
        return None

    def is_managed_task(self, path: Path) -> bool:
        tid = self.task_id_from_path(path)
        return tid is not None and self.find_task_files(tid) is not None

    def resolve_task_reference(self, task_ref: str | None) -> Path | None:
        """
        Resolve referência de tarefa: TASK-0001, caminho relativo ou legado em ai/tasks/.
        """
        if not task_ref:
            return None

        ref = task_ref.strip()
        if TASK_ID_PATTERN.match(ref.upper()):
            files = self.find_task_files(ref)
            if files:
                return files[0]
            raise TaskManagerError(
                f"Tarefa '{ref.upper()}' não encontrada em ai/tasks/."
            )

        path = Path(ref)
        if not path.is_absolute():
            path = self.base_dir / path

        if path.is_file():
            return path

        raise TaskManagerError(f"Arquivo de tarefa não encontrado: {path}")

    @staticmethod
    def _title_from_body(body: str, source: Path) -> str:
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip()
            if stripped:
                return stripped[:120]
        return source.stem.replace("_", " ").replace("-", " ").title()

    def create_task(
        self,
        *,
        task_id: str,
        title: str,
        project: str,
        agent: str,
        body: str,
        status: str = "planned",
    ) -> TaskMetadata:
        """Cria par .md + .json na pasta do status."""
        self.validate_status(status)
        tid = self.normalize_task_id(task_id)
        folder = self._folder_for_status(status)
        md = self.tasks_root() / folder / f"{tid}.md"
        js = self.tasks_root() / folder / f"{tid}.json"

        if md.exists() or js.exists():
            raise TaskManagerError(f"Tarefa '{tid}' já existe.")

        now = self.utc_now()
        meta = TaskMetadata(
            task_id=tid,
            title=title,
            project=project,
            status=status,
            agent=agent,
            created_at=now,
            updated_at=now,
            history=[
                {
                    "timestamp": now,
                    "from_status": None,
                    "to_status": status,
                    "message": "task created",
                }
            ],
        )

        md.write_text(body.strip() + "\n", encoding="utf-8")
        js.write_text(
            json.dumps(meta.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return meta

    def load(self, task_id: str) -> TaskMetadata:
        """Carrega metadata JSON da tarefa."""
        files = self.find_task_files(task_id)
        if not files:
            raise TaskManagerError(
                f"Tarefa '{self.normalize_task_id(task_id)}' não encontrada."
            )
        data = json.loads(files[1].read_text(encoding="utf-8"))
        return TaskMetadata.from_dict(data)

    def save(self, metadata: TaskMetadata) -> Path:
        """Persiste metadata no caminho atual da tarefa."""
        js = self.json_path(metadata.task_id)
        js.write_text(
            json.dumps(metadata.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return js

    def _append_history(
        self,
        metadata: TaskMetadata,
        *,
        from_status: str | None,
        to_status: str,
        message: str,
    ) -> None:
        metadata.history.append(
            {
                "timestamp": self.utc_now(),
                "from_status": from_status,
                "to_status": to_status,
                "message": message,
            }
        )

    def _move_task_files(self, task_id: str, new_status: str) -> tuple[Path, Path]:
        """Move .md e .json para a pasta do novo status."""
        files = self.find_task_files(task_id)
        if not files:
            raise TaskManagerError(f"Tarefa '{task_id}' não encontrada para mover.")

        md_src, js_src = files
        folder = self._folder_for_status(new_status)
        dest_dir = self.tasks_root() / folder
        dest_dir.mkdir(parents=True, exist_ok=True)

        tid = self.normalize_task_id(task_id)
        md_dest = dest_dir / f"{tid}.md"
        js_dest = dest_dir / f"{tid}.json"

        if md_src != md_dest:
            shutil.move(str(md_src), str(md_dest))
        if js_src != js_dest:
            shutil.move(str(js_src), str(js_dest))

        return md_dest, js_dest

    def update_status(
        self,
        task_id: str,
        new_status: str,
        *,
        message: str = "",
    ) -> TaskMetadata:
        """Atualiza status, histórico e move arquivos se necessário."""
        self.validate_status(new_status)
        meta = self.load(task_id)
        old_status = meta.status

        if old_status == new_status:
            return meta

        meta.status = new_status
        meta.updated_at = self.utc_now()
        self._append_history(
            meta,
            from_status=old_status,
            to_status=new_status,
            message=message or f"status -> {new_status}",
        )

        old_folder = STATUS_FOLDERS[old_status]
        new_folder = STATUS_FOLDERS[new_status]
        if old_folder != new_folder:
            self._move_task_files(task_id, new_status)

        self.save(meta)
        return meta

    def list_tasks(self, project: str | None = None) -> list[TaskMetadata]:
        """Lista todas as tarefas gerenciadas, opcionalmente filtradas por projeto."""
        tasks: list[TaskMetadata] = []
        for subdir in LIFECYCLE_SUBDIRS:
            directory = self.tasks_root() / subdir
            if not directory.is_dir():
                continue
            for json_file in sorted(directory.glob("TASK-*.json")):
                try:
                    meta = TaskMetadata.from_dict(
                        json.loads(json_file.read_text(encoding="utf-8"))
                    )
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    continue
                if project and meta.project != project:
                    continue
                tasks.append(meta)

        return sorted(tasks, key=lambda t: t.task_id)

    def ensure_task_for_plan(
        self,
        project: str,
        source_path: Path,
        agent: str,
    ) -> tuple[TaskMetadata, Path]:
        """
        Registra tarefa no lifecycle para comando plan.

        - Se já for TASK-XXXX gerenciada: atualiza para planned.
        - Se for arquivo legado: cria TASK-XXXX em active/ com conteúdo copiado.
        """
        existing_id = self.task_id_from_path(source_path)
        if existing_id and self.find_task_files(existing_id):
            meta = self.update_status(
                existing_id,
                "planned",
                message="plan command (re-plan)",
            )
            meta.agent = agent
            meta.updated_at = self.utc_now()
            self.save(meta)
            return meta, self.md_path(existing_id)

        body = source_path.read_text(encoding="utf-8")
        title = self._title_from_body(body, source_path)
        task_id = self.next_task_id()
        meta = self.create_task(
            task_id=task_id,
            title=title,
            project=project,
            agent=agent,
            body=body,
            status="planned",
        )
        return meta, self.md_path(task_id)

    def on_command_start(self, command: str, task_id: str) -> None:
        """Hooks ao iniciar plan/run/review."""
        if command == "run":
            self.update_status(task_id, "running", message="run started")

    def on_command_success(self, command: str, task_id: str) -> None:
        """Hooks ao concluir plan/run/review com sucesso."""
        if command == "run":
            self.update_status(task_id, "reviewed", message="run completed")
        elif command == "review":
            self.update_status(task_id, "done", message="review completed")

    def record_pipeline_step(
        self,
        task_id: str,
        *,
        pipeline_name: str,
        agent: str,
        status: str,
        started_at: str,
        finished_at: str,
        summary: str,
        run_path: str | None = None,
        error: str | None = None,
    ) -> TaskMetadata:
        """Registra step de pipeline em pipeline_history da task."""
        meta = self.load(task_id)
        entry: dict[str, Any] = {
            "pipeline_name": pipeline_name,
            "agent": agent,
            "status": status,
            "started_at": started_at,
            "finished_at": finished_at,
            "summary": self._truncate_pipeline_summary(summary),
            "run_path": run_path,
        }
        if error:
            entry["error"] = error
        meta.pipeline_history.append(entry)
        meta.updated_at = self.utc_now()
        self.save(meta)
        return meta

    @staticmethod
    def _truncate_pipeline_summary(summary: str, limit: int = 500) -> str:
        text = summary.strip()
        if len(text) <= limit:
            return text
        return text[: limit - 3] + "..."

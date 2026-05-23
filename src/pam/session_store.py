"""Persistência de metadata de sessões agenticas em ai/sessions/."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from pam.config_loader import project_root

SESSIONS_DIR = "ai/sessions"


@dataclass
class SessionMetadata:
    """Metadata de uma sessão agentica por projeto."""

    project: str
    agent_id: str
    last_run_id: str | None
    mode: str
    task: str | None
    created_at: str
    updated_at: str
    status: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SessionMetadata":
        return cls(
            project=str(data["project"]),
            agent_id=str(data["agent_id"]),
            last_run_id=data.get("last_run_id"),
            mode=str(data["mode"]),
            task=data.get("task"),
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
            status=str(data["status"]),
        )


class SessionStore:
    """Salva e carrega metadata de sessões em ai/sessions/<project>.json."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or project_root()

    def sessions_dir(self) -> Path:
        directory = self.base_dir / SESSIONS_DIR
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def session_path(self, project: str) -> Path:
        return self.sessions_dir() / f"{project}.json"

    def load(self, project: str) -> SessionMetadata | None:
        """Retorna a sessão salva do projeto, ou None se não existir."""
        path = self.session_path(project)
        if not path.is_file():
            return None

        data = json.loads(path.read_text(encoding="utf-8"))
        return SessionMetadata.from_dict(data)

    def save(self, metadata: SessionMetadata) -> Path:
        """Persiste metadata da sessão."""
        path = self.session_path(metadata.project)
        path.write_text(
            json.dumps(metadata.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def find_latest(self, project: str) -> SessionMetadata | None:
        """Retorna a sessão do projeto (uma sessão ativa por projeto na Sprint 2)."""
        return self.load(project)

    @staticmethod
    def utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_metadata(
        self,
        *,
        project: str,
        agent_id: str,
        mode: str,
        task: str | None = None,
        last_run_id: str | None = None,
        status: str = "active",
    ) -> SessionMetadata:
        """Cria objeto de metadata com timestamps atuais."""
        now = self.utc_now()
        return SessionMetadata(
            project=project,
            agent_id=agent_id,
            last_run_id=last_run_id,
            mode=mode,
            task=task,
            created_at=now,
            updated_at=now,
            status=status,
        )

    def touch(
        self,
        metadata: SessionMetadata,
        *,
        last_run_id: str | None = None,
        status: str | None = None,
    ) -> SessionMetadata:
        """Atualiza campos mutáveis e persiste."""
        updated = SessionMetadata(
            project=metadata.project,
            agent_id=metadata.agent_id,
            last_run_id=last_run_id if last_run_id is not None else metadata.last_run_id,
            mode=metadata.mode,
            task=metadata.task,
            created_at=metadata.created_at,
            updated_at=self.utc_now(),
            status=status if status is not None else metadata.status,
        )
        self.save(updated)
        return updated

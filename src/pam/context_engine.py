"""Motor de contexto — consolida ai/context e ai/memory para prompts."""

from __future__ import annotations

from pathlib import Path

from pam.config_loader import project_root

CONTEXT_DIR = "ai/context"
MEMORY_DIR = "ai/memory"

GLOBAL_CONTEXT_FILES = (
    "ARCHITECTURE.md",
    "ROADMAP.md",
    "CURRENT_SPRINT.md",
    "KNOWN_ISSUES.md",
    "STACK.md",
)

PROJECT_MEMORY_FILES = (
    "DECISIONS.md",
    "PATTERNS.md",
    "LEARNINGS.md",
)

FILE_LABELS = {
    "ARCHITECTURE.md": "Arquitetura (PAM)",
    "ROADMAP.md": "Roadmap",
    "CURRENT_SPRINT.md": "Sprint atual",
    "KNOWN_ISSUES.md": "Issues conhecidas",
    "STACK.md": "Stack",
    "DECISIONS.md": "Decisões",
    "PATTERNS.md": "Padrões",
    "LEARNINGS.md": "Aprendizados",
}


class ContextEngine:
    """Lê contexto global e memória por projeto; monta bloco para injeção em prompts."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or project_root()

    def context_dir(self) -> Path:
        return self.base_dir / CONTEXT_DIR

    def memory_dir(self, project: str) -> Path:
        return self.base_dir / MEMORY_DIR / project

    @staticmethod
    def _read_if_exists(path: Path) -> str | None:
        if not path.is_file():
            return None
        text = path.read_text(encoding="utf-8").strip()
        return text if text else None

    def load_global_context(self) -> dict[str, str]:
        """Carrega arquivos de ai/context/ (nome do arquivo → conteúdo)."""
        directory = self.context_dir()
        loaded: dict[str, str] = {}

        for filename in GLOBAL_CONTEXT_FILES:
            content = self._read_if_exists(directory / filename)
            if content:
                loaded[filename] = content

        return loaded

    def load_project_memory(self, project: str) -> dict[str, str]:
        """Carrega arquivos de ai/memory/<project>/ (nome do arquivo → conteúdo)."""
        directory = self.memory_dir(project)
        loaded: dict[str, str] = {}

        for filename in PROJECT_MEMORY_FILES:
            content = self._read_if_exists(directory / filename)
            if content:
                loaded[filename] = content

        return loaded

    def _format_section(self, title: str, filename: str, body: str) -> str:
        label = FILE_LABELS.get(filename, filename)
        return f"### {title} — {label}\n\n{body}"

    def build_context_block(self, project: str | None = None) -> str:
        """
        Monta bloco Markdown consolidado, pronto para injeção no início do prompt.

        Ordem: contexto global PAM → memória do projeto (se informado).
        """
        sections: list[str] = []

        global_ctx = self.load_global_context()
        if global_ctx:
            global_parts = [
                self._format_section("Global", name, body)
                for name, body in global_ctx.items()
            ]
            sections.append(
                "## Contexto PAM (global)\n\n" + "\n\n".join(global_parts)
            )

        if project:
            memory = self.load_project_memory(project)
            if memory:
                memory_parts = [
                    self._format_section(project, name, body)
                    for name, body in memory.items()
                ]
                sections.append(
                    f"## Memória do projeto ({project})\n\n"
                    + "\n\n".join(memory_parts)
                )

        if not sections:
            return ""

        header = (
            "# Contexto consolidado (Project Agent Manager)\n\n"
            "_Gerado automaticamente por context_engine — "
            "Operating System for AI Development._\n"
        )
        return header + "\n" + "\n\n---\n\n".join(sections)

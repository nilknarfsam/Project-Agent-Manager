"""Context Builder — monta pacotes de contexto a partir de arquivos do projeto."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from pam.config_loader import project_root

GENERATED_DIR = "ai/context/generated"
MAX_CONTEXT_CHARS = 120_000

IGNORED_DIR_NAMES = frozenset(
    {
        ".git",
        ".venv",
        "build",
        "dist",
        "node_modules",
        ".dart_tool",
        ".gradle",
        "__pycache__",
    }
)

IGNORED_PATH_PREFIXES = (
    "android/build",
    "ios/Pods",
)


class ContextBuilderError(ValueError):
    """Erro ao montar ou salvar contexto."""


@dataclass
class FileTreeNode:
    """Nó da árvore de arquivos do repositório."""

    rel_path: str
    name: str
    is_dir: bool
    children: list[FileTreeNode] = field(default_factory=list)


class ContextBuilder:
    """Lista arquivos do projeto e gera markdown consolidado para agentes."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or project_root()

    def generated_dir(self) -> Path:
        directory = self.base_dir / GENERATED_DIR
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @classmethod
    def is_ignored_relative(cls, rel: Path) -> bool:
        """True se caminho relativo deve ser ignorado."""
        if not rel.parts:
            return False

        if any(part in IGNORED_DIR_NAMES for part in rel.parts):
            return True

        posix = rel.as_posix()
        for prefix in IGNORED_PATH_PREFIXES:
            if posix == prefix or posix.startswith(f"{prefix}/"):
                return True
        return False

    def list_project_files(self, repo_path: Path) -> list[str]:
        """Lista caminhos relativos de arquivos (ordenados), ignorando pastas pesadas."""
        root = repo_path.expanduser().resolve()
        if not root.is_dir():
            raise ContextBuilderError(f"Repositório não encontrado: {root}")

        files: list[str] = []
        for dirpath, dirnames, filenames in os.walk(root):
            current = Path(dirpath)
            rel_dir = current.relative_to(root)

            if rel_dir != Path(".") and self.is_ignored_relative(rel_dir):
                dirnames.clear()
                continue

            dirnames[:] = sorted(
                name
                for name in dirnames
                if not self.is_ignored_relative(
                    rel_dir / name if rel_dir != Path(".") else Path(name)
                )
            )

            for filename in sorted(filenames):
                rel_file = (
                    rel_dir / filename if rel_dir != Path(".") else Path(filename)
                )
                if not self.is_ignored_relative(rel_file):
                    files.append(rel_file.as_posix())

        return files

    def build_file_tree(self, repo_path: Path) -> FileTreeNode:
        """Monta árvore hierárquica de arquivos para exibição na GUI."""
        root_path = repo_path.expanduser().resolve()
        root = FileTreeNode(rel_path="", name=root_path.name or str(root_path), is_dir=True)
        nodes: dict[str, FileTreeNode] = {"": root}

        for rel_str in self.list_project_files(root_path):
            parts = Path(rel_str).parts
            for index in range(len(parts)):
                dir_rel = "/".join(parts[: index + 1])
                is_file = index == len(parts) - 1

                if dir_rel in nodes:
                    continue

                parent_key = "/".join(parts[:index]) if index > 0 else ""
                parent = nodes[parent_key]
                node = FileTreeNode(
                    rel_path=dir_rel,
                    name=parts[index],
                    is_dir=not is_file,
                )
                parent.children.append(node)
                nodes[dir_rel] = node

        self._sort_tree(root)
        return root

    @staticmethod
    def _sort_tree(node: FileTreeNode) -> None:
        node.children.sort(key=lambda item: (not item.is_dir, item.name.lower()))
        for child in node.children:
            if child.is_dir:
                ContextBuilder._sort_tree(child)

    @staticmethod
    def _read_file_text(abs_path: Path) -> tuple[str, bool]:
        """Retorna (conteúdo, ok). ok=False para binário/encoding."""
        try:
            text = abs_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return "", False
        except OSError as exc:
            raise ContextBuilderError(f"Não foi possível ler {abs_path}: {exc}") from exc
        return text, True

    @staticmethod
    def _truncate_text(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        return text[: limit - 24] + "\n...(truncado por limite)"

    def build_context_markdown(
        self,
        project_name: str,
        repo_path: Path,
        file_paths: list[str],
    ) -> str:
        """Gera markdown consolidado a partir dos arquivos selecionados."""
        if not file_paths:
            raise ContextBuilderError("Nenhum arquivo selecionado para o contexto.")

        root = repo_path.expanduser().resolve()
        unique_files = sorted(set(file_paths))
        header_lines = [
            "# Generated Context",
            "",
            f"Projeto: {project_name}",
            "",
            "Arquivos incluídos:",
        ]

        for rel in unique_files:
            header_lines.append(f"- {rel}")

        header_lines.extend(["", "Conteúdo:", ""])
        header = "\n".join(header_lines)
        body_parts: list[str] = []
        budget = MAX_CONTEXT_CHARS - len(header)

        for rel in unique_files:
            abs_path = root / rel
            if not abs_path.is_file():
                body_parts.append(
                    f"## {rel}\n\n```text\n(arquivo não encontrado)\n```\n"
                )
                continue

            text, ok = self._read_file_text(abs_path)
            if not ok:
                body_parts.append(
                    f"## {rel}\n\n```text\n"
                    "(arquivo binário ou encoding não suportado — omitido)\n```\n"
                )
                continue

            section = f"## {rel}\n\n```text\n{text}\n```\n"
            if len(section) > budget:
                if budget < 80:
                    body_parts.append(
                        "_(limite de contexto atingido — arquivos restantes omitidos)_"
                    )
                    break
                allowed = max(budget - len(f"## {rel}\n\n```text\n\n```\n"), 0)
                truncated = self._truncate_text(text, allowed)
                section = f"## {rel}\n\n```text\n{truncated}\n```\n"
                body_parts.append(section)
                budget -= len(section)
                if budget <= 0:
                    body_parts.append(
                        "_(limite de contexto atingido — arquivos restantes omitidos)_"
                    )
                    break
                continue

            body_parts.append(section)
            budget -= len(section)

        return header + "\n".join(body_parts)

    def collect_files_under(
        self,
        repo_path: Path,
        rel_path: str,
        *,
        all_files: list[str] | None = None,
    ) -> list[str]:
        """Expande pasta selecionada para lista de arquivos relativos."""
        files = all_files if all_files is not None else self.list_project_files(repo_path)
        rel = rel_path.strip().replace("\\", "/")
        if not rel:
            return list(files)
        prefix = f"{rel}/"
        return [path for path in files if path == rel or path.startswith(prefix)]

    def save_context(self, markdown: str, *, project_name: str) -> Path:
        """Persiste contexto em ai/context/generated/context_YYYYMMDD_HHMMSS.md."""
        if not markdown.strip():
            raise ContextBuilderError("Contexto vazio — nada para salvar.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = self.generated_dir() / f"context_{timestamp}.md"
        path.write_text(markdown.strip() + "\n", encoding="utf-8")
        return path

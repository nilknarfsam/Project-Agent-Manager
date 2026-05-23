"""Carregamento de configurações YAML dos projetos."""

from __future__ import annotations

from pathlib import Path

import yaml

from pam.models import ProjectConfig

PROJECTS_DIR_NAME = "ai/projects"


def project_root() -> Path:
    """Retorna a raiz do repositório PAM (dois níveis acima de src/pam)."""
    return Path(__file__).resolve().parents[2]


def projects_dir(base_dir: Path | None = None) -> Path:
    """Diretório onde ficam os YAMLs de projeto."""
    root = base_dir or project_root()
    return root / PROJECTS_DIR_NAME


def list_projects(base_dir: Path | None = None) -> list[str]:
    """Lista os nomes dos projetos disponíveis (sem extensão .yaml)."""
    directory = projects_dir(base_dir)
    if not directory.is_dir():
        return []

    return sorted(path.stem for path in directory.glob("*.yaml"))


def load_project(name: str, base_dir: Path | None = None) -> ProjectConfig:
    """Carrega a configuração YAML de um projeto pelo nome."""
    config_path = projects_dir(base_dir) / f"{name}.yaml"

    if not config_path.is_file():
        available = ", ".join(list_projects(base_dir)) or "(nenhum)"
        raise FileNotFoundError(
            f"Projeto '{name}' não encontrado em {config_path}. "
            f"Disponíveis: {available}"
        )

    with config_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"YAML inválido em {config_path}: esperado um mapping.")

    required = ("name", "repo_path", "default_runtime", "default_model", "description")
    missing = [field for field in required if field not in data]
    if missing:
        raise ValueError(
            f"Campos obrigatórios ausentes em {config_path}: {', '.join(missing)}"
        )

    return ProjectConfig(
        name=str(data["name"]),
        repo_path=Path(str(data["repo_path"])),
        default_runtime=str(data["default_runtime"]),
        default_model=str(data["default_model"]),
        description=str(data["description"]),
    )

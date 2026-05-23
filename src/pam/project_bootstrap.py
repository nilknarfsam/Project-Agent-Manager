"""Project Onboarding System — estrutura OS4AI em projetos novos ou existentes."""

from __future__ import annotations

import platform
import re
import shutil
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from pam.config_loader import list_projects, load_project, project_root, projects_dir
from pam.template_engine import TemplateEngine, TemplateEngineError

STACK_LABELS: dict[str, str] = {
    "flutter": "Flutter / Dart",
    "python": "Python",
    "electron": "Electron / Node.js",
}

STACK_DETAILS: dict[str, str] = {
    "flutter": (
        "- Linguagem: Dart\n"
        "- Framework: Flutter\n"
        "- Estrutura base PAM-native; código da app a ser gerado em sprints futuras."
    ),
    "python": (
        "- Linguagem: Python 3.11+\n"
        "- Pacote/CLI conforme evolução do projeto\n"
        "- Estrutura base PAM-native; implementação em sprints futuras."
    ),
    "electron": (
        "- Runtime: Node.js\n"
        "- Framework: Electron\n"
        "- Estrutura base PAM-native; app desktop em sprints futuras."
    ),
}

GITIGNORE_BLOCK = """\
# PAM / OS4AI
ai/runs/
ai/sessions/*.json
"""

TASK_SUBDIRS = ("active", "completed", "blocked", "archived")


class ProjectBootstrapError(ValueError):
    """Erro de validação ou operação no onboarding."""


@dataclass
class BootstrapResult:
    """Resultado de onboard ou create-project."""

    project_slug: str
    repo_path: Path
    pam_yaml_path: Path | None = None
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def slugify(name: str) -> str:
    """Converte nome em slug para YAML e memória."""
    slug = name.strip().lower()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        raise ProjectBootstrapError(
            f"Nome de projeto inválido após normalização: '{name}'."
        )
    return slug


def display_name(slug: str) -> str:
    """Nome legível a partir do slug."""
    return slug.replace("-", " ").title()


class ProjectBootstrap:
    """Cria estrutura OS4AI e registra projeto no PAM."""

    def __init__(
        self,
        pam_root: Path | None = None,
        templates: TemplateEngine | None = None,
    ) -> None:
        self.pam_root = pam_root or project_root()
        self.templates = templates or TemplateEngine()
        self._pam_ai = self.pam_root / "ai"

    def default_projects_base(self) -> Path:
        """Inferir diretório pai dos projetos (ex.: C:\\src\\projects)."""
        for name in list_projects(self.pam_root):
            try:
                cfg = load_project(name, self.pam_root)
                return cfg.repo_path.parent
            except (FileNotFoundError, ValueError):
                continue
        if platform.system() == "Windows":
            return Path("C:/src/projects")
        return Path.home() / "projects"

    def _template_vars(
        self,
        project_slug: str,
        repo_path: Path,
        *,
        stack: str = "generic",
        description: str | None = None,
    ) -> dict[str, str]:
        stack_key = stack if stack in STACK_LABELS else "python"
        label = STACK_LABELS.get(stack, display_name(stack))
        details = STACK_DETAILS.get(
            stack,
            "- Stack definida no onboarding.\n- Atualizar este arquivo após análise.",
        )
        if stack == "generic":
            label = "Projeto existente (onboard)"
            details = (
                "- Projeto onboardado via PAM.\n"
                "- Atualizar stack real em STACK.md após análise."
            )

        desc = description or (
            f"Projeto {display_name(project_slug)} — gerenciado pelo Project Agent Manager."
        )
        return {
            "project_slug": project_slug,
            "project_display_name": display_name(project_slug),
            "description": desc,
            "repo_path": str(repo_path.resolve()),
            "date": date.today().isoformat(),
            "stack_label": label,
            "stack_details": details,
        }

    def _write_file(
        self,
        repo: Path,
        rel: Path,
        template: str,
        variables: dict[str, str],
        *,
        force: bool = False,
        result: BootstrapResult,
    ) -> None:
        dest = repo / rel
        rel_str = str(rel).replace("\\", "/")
        try:
            if dest.exists() and not force:
                result.skipped.append(rel_str)
                return
            if self.templates.write_rendered(template, dest, variables, force=force):
                result.created.append(rel_str)
            elif dest.exists():
                result.skipped.append(rel_str)
        except TemplateEngineError as exc:
            raise ProjectBootstrapError(str(exc)) from exc

    def _ensure_dirs(self, repo: Path, project_slug: str, result: BootstrapResult) -> None:
        dirs = [
            Path("ai/context"),
            Path("ai/memory") / project_slug,
            Path("ai/sessions"),
            Path("ai/runs"),
        ]
        for sub in TASK_SUBDIRS:
            dirs.append(Path("ai/tasks") / sub)

        for rel in dirs:
            path = repo / rel
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                result.created.append(f"{rel}/")
            else:
                result.skipped.append(f"{rel}/ (já existe)")

    def _copy_tree_if_missing(
        self,
        source: Path,
        dest: Path,
        *,
        force: bool = False,
        result: BootstrapResult,
        label: str,
    ) -> None:
        if not source.is_dir():
            result.warnings.append(f"Origem ausente no PAM: {source}")
            return
        if dest.exists():
            if any(dest.iterdir()) and not force:
                result.skipped.append(f"{label}/ (já possui conteúdo)")
                return
            if force or not any(dest.iterdir()):
                shutil.rmtree(dest)
        shutil.copytree(source, dest)
        result.created.append(f"{label}/ (copiado do PAM)")

    def _copy_protocol(
        self,
        repo: Path,
        *,
        force: bool = False,
        result: BootstrapResult,
    ) -> None:
        source = self.pam_root / "protocol"
        dest = repo / "protocol"
        if not source.is_dir():
            result.warnings.append(
                "Diretório protocol/ não encontrado no PAM — pulando cópia."
            )
            return
        if dest.exists() and any(dest.iterdir()) and not force:
            result.skipped.append("protocol/ (já possui conteúdo)")
            return
        if dest.exists() and force:
            shutil.rmtree(dest)
        shutil.copytree(
            source,
            dest,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        result.created.append("protocol/ (copiado do PAM)")

    def _append_gitignore(self, repo: Path, result: BootstrapResult) -> None:
        gitignore = repo / ".gitignore"
        if gitignore.is_file():
            content = gitignore.read_text(encoding="utf-8")
            if "ai/runs/" in content or "ai/sessions" in content:
                result.skipped.append(".gitignore (entradas PAM já presentes)")
                return
            gitignore.write_text(
                content.rstrip() + "\n\n" + GITIGNORE_BLOCK,
                encoding="utf-8",
            )
            result.created.append(".gitignore (entradas PAM adicionadas)")
        else:
            gitignore.write_text(GITIGNORE_BLOCK.strip() + "\n", encoding="utf-8")
            result.created.append(".gitignore")

    def _register_pam_yaml(
        self,
        project_slug: str,
        repo_path: Path,
        variables: dict[str, str],
        *,
        force: bool = False,
        result: BootstrapResult,
    ) -> None:
        yaml_path = projects_dir(self.pam_root) / f"{project_slug}.yaml"
        projects_dir(self.pam_root).mkdir(parents=True, exist_ok=True)

        if yaml_path.exists() and not force:
            result.skipped.append(
                f"ai/projects/{project_slug}.yaml (no PAM, já existe)"
            )
            result.pam_yaml_path = yaml_path
            return

        try:
            self.templates.write_rendered(
                "PROJECT_CONFIG",
                yaml_path,
                variables,
                force=force,
            )
            result.created.append(f"PAM: ai/projects/{project_slug}.yaml")
            result.pam_yaml_path = yaml_path
        except TemplateEngineError as exc:
            raise ProjectBootstrapError(str(exc)) from exc

    def _bootstrap_repo(
        self,
        repo: Path,
        project_slug: str,
        *,
        stack: str = "generic",
        description: str | None = None,
        force: bool = False,
        is_new_repo: bool = False,
    ) -> BootstrapResult:
        repo = repo.resolve()
        if not repo.is_dir():
            raise ProjectBootstrapError(f"Caminho não é um diretório: {repo}")

        result = BootstrapResult(project_slug=project_slug, repo_path=repo)
        variables = self._template_vars(
            project_slug, repo, stack=stack, description=description
        )

        ai_root = repo / "ai"
        if ai_root.exists() and not force:
            result.warnings.append(
                "Diretório ai/ já existe. Arquivos existentes serão preservados. "
                "Use --force para sobrescrever arquivos gerados por template."
            )

        self._ensure_dirs(repo, project_slug, result)

        context_files = {
            Path("ai/context/ARCHITECTURE.md"): "ARCHITECTURE",
            Path("ai/context/ROADMAP.md"): "ROADMAP",
            Path("ai/context/CURRENT_SPRINT.md"): "CURRENT_SPRINT",
            Path("ai/context/KNOWN_ISSUES.md"): "KNOWN_ISSUES",
            Path("ai/context/STACK.md"): "STACK",
        }
        for rel, tmpl in context_files.items():
            self._write_file(repo, rel, tmpl, variables, force=force, result=result)

        memory_files = {
            Path("ai/memory") / project_slug / "DECISIONS.md": "DECISIONS",
            Path("ai/memory") / project_slug / "PATTERNS.md": "PATTERNS",
            Path("ai/memory") / project_slug / "LEARNINGS.md": "LEARNINGS",
        }
        for rel, tmpl in memory_files.items():
            self._write_file(repo, rel, tmpl, variables, force=force, result=result)

        readme = repo / "README.md"
        if readme.exists() and not is_new_repo:
            self._write_file(
                repo,
                Path("README_PAM.md"),
                "README_PAM_SUPPLEMENT",
                variables,
                force=force,
                result=result,
            )
        else:
            self._write_file(
                repo, Path("README.md"), "README", variables, force=force, result=result
            )

        self._write_file(
            repo, Path("CHANGELOG.md"), "CHANGELOG", variables, force=force, result=result
        )

        self._copy_protocol(repo, force=force, result=result)
        self._copy_tree_if_missing(
            self._pam_ai / "agents",
            repo / "ai/agents",
            force=force,
            result=result,
            label="ai/agents",
        )
        self._copy_tree_if_missing(
            self._pam_ai / "prompts",
            repo / "ai/prompts",
            force=force,
            result=result,
            label="ai/prompts",
        )

        self._append_gitignore(repo, result)
        self._register_pam_yaml(project_slug, repo, variables, force=force, result=result)

        return result

    def onboard(
        self,
        repo_path: Path | str,
        *,
        project_slug: str | None = None,
        force: bool = False,
    ) -> BootstrapResult:
        """
        Aplica estrutura OS4AI em repositório existente.

        Não sobrescreve arquivos existentes sem --force.
        """
        repo = Path(repo_path).expanduser().resolve()
        if not repo.exists():
            raise ProjectBootstrapError(f"Caminho não encontrado: {repo}")
        if not repo.is_dir():
            raise ProjectBootstrapError(f"Caminho não é um diretório: {repo}")

        slug = project_slug or slugify(repo.name)
        return self._bootstrap_repo(
            repo, slug, stack="generic", force=force, is_new_repo=False
        )

    def create_project(
        self,
        stack: str,
        name: str,
        *,
        parent_dir: Path | str | None = None,
        force: bool = False,
    ) -> BootstrapResult:
        """
        Cria novo diretório PAM-native com estrutura OS4AI.

        stack: flutter | python | electron
        """
        stack_norm = stack.strip().lower()
        if stack_norm not in STACK_LABELS:
            raise ProjectBootstrapError(
                f"Stack '{stack}' inválida. Use: {', '.join(STACK_LABELS)}."
            )

        slug = slugify(name)
        base = Path(parent_dir).expanduser().resolve() if parent_dir else self.default_projects_base()
        repo = (base / slug).resolve()

        if repo.exists():
            if any(repo.iterdir()) and not force:
                raise ProjectBootstrapError(
                    f"Diretório já existe e não está vazio: {repo}. "
                    "Use --force para continuar."
                )
        else:
            repo.mkdir(parents=True, exist_ok=True)

        desc = (
            f"Projeto {display_name(slug)} ({STACK_LABELS[stack_norm]}) — "
            "criado pelo PAM (create-project)."
        )
        return self._bootstrap_repo(
            repo,
            slug,
            stack=stack_norm,
            description=desc,
            force=force,
            is_new_repo=True,
        )


def format_bootstrap_report(result: BootstrapResult) -> str:
    """Formata relatório legível para stdout."""
    lines = [
        "",
        f"Projeto: {result.project_slug}",
        f"Repositório: {result.repo_path}",
    ]
    if result.pam_yaml_path:
        lines.append(f"YAML PAM: {result.pam_yaml_path}")

    if result.created:
        lines.append("\nCriados / atualizados:")
        for item in result.created:
            lines.append(f"  + {item}")

    if result.skipped:
        lines.append("\nIgnorados (já existiam):")
        for item in result.skipped:
            lines.append(f"  - {item}")

    if result.warnings:
        lines.append("\nAvisos:")
        for item in result.warnings:
            lines.append(f"  ! {item}")

    lines.append("")
    return "\n".join(lines)

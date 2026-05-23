"""Renderização de templates para onboarding de projetos."""

from __future__ import annotations

import re
from pathlib import Path

VAR_PATTERN = re.compile(r"\{\{(\w+)\}\}")


class TemplateEngineError(ValueError):
    """Erro ao carregar ou renderizar template."""


class TemplateEngine:
    """Carrega templates de src/pam/templates/ e substitui variáveis {{nome}}."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        if templates_dir is None:
            templates_dir = Path(__file__).resolve().parent / "templates"
        self.templates_dir = templates_dir

    def template_path(self, name: str) -> Path:
        """Resolve caminho do arquivo de template."""
        if name.endswith(".tmpl"):
            candidates = [name]
        else:
            candidates = [
                f"{name}.tmpl",
                f"{name}.md.tmpl",
                f"{name}.yaml.tmpl",
            ]
        for filename in candidates:
            path = self.templates_dir / filename
            if path.is_file():
                return path
        raise TemplateEngineError(
            f"Template '{name}' não encontrado em {self.templates_dir}."
        )

    def load(self, name: str) -> str:
        """Lê conteúdo bruto do template."""
        return self.template_path(name).read_text(encoding="utf-8")

    @staticmethod
    def render(text: str, variables: dict[str, str]) -> str:
        """Substitui {{chave}} pelos valores fornecidos."""

        def replacer(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in variables:
                raise TemplateEngineError(
                    f"Variável '{{{{{key}}}}}' ausente. "
                    f"Disponíveis: {', '.join(sorted(variables)) or '(nenhuma)'}"
                )
            return variables[key]

        return VAR_PATTERN.sub(replacer, text)

    def render_template(self, name: str, variables: dict[str, str]) -> str:
        """Carrega e renderiza um template."""
        return self.render(self.load(name), variables)

    def write_rendered(
        self,
        name: str,
        destination: Path,
        variables: dict[str, str],
        *,
        force: bool = False,
    ) -> bool:
        """
        Grava arquivo renderizado em destination.

        Returns:
            True se o arquivo foi criado ou sobrescrito; False se ignorado.
        """
        if destination.exists() and not force:
            return False

        destination.parent.mkdir(parents=True, exist_ok=True)
        content = self.render_template(name, variables)
        destination.write_text(content, encoding="utf-8")
        return True

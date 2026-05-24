"""Interface base para providers de IA leves (Gemini)."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ProviderError(RuntimeError):
    """Erro de configuração ou execução em provider de IA."""


class BaseProvider(ABC):
    """Contrato mínimo para tarefas leves: análise, sumarização, docs, tasks."""

    name: str = "base"

    @abstractmethod
    def generate(self, prompt: str, model: str | None = None) -> str:
        """Gera texto a partir de um prompt."""

    def summarize(self, text: str, model: str | None = None) -> str:
        """Resume texto longo de forma estruturada."""
        prompt = (
            "Resuma o seguinte conteúdo de projeto de software de forma clara "
            "e estruturada em Markdown. Destaque: visão, stack, sprint atual, "
            "riscos e próximos passos.\n\n"
            f"{text.strip()}"
        )
        return self.generate(prompt, model=model)

    def classify(self, text: str, labels: list[str], model: str | None = None) -> str:
        """Classifica texto em uma das labels fornecidas."""
        label_list = ", ".join(f'"{label}"' for label in labels)
        prompt = (
            f"Classifique o texto abaixo em exatamente UMA destas categorias: "
            f"{label_list}.\n"
            "Responda apenas com o nome da categoria escolhida, sem explicação.\n\n"
            f"{text.strip()}"
        )
        return self.generate(prompt, model=model)

    def generate_tasks(self, context: str, model: str | None = None) -> str:
        """Sugere tasks pequenas e acionáveis a partir do contexto."""
        prompt = (
            "Com base no contexto do projeto abaixo, sugira de 3 a 7 tarefas "
            "pequenas e rastreáveis para o PAM (formato OS4AI).\n\n"
            "Para cada task use este formato Markdown:\n"
            "### TASK sugerida N — Título curto\n"
            "- **Objetivo:** ...\n"
            "- **Critérios de aceite:** ...\n"
            "- **Agente sugerido:** architect | implementer | reviewer | test_writer | "
            "docs_writer | release_manager\n\n"
            "Priorize mudanças pequenas. Não proponha refactors gigantes.\n\n"
            f"{context.strip()}"
        )
        return self.generate(prompt, model=model)

    def generate_docs(self, context: str, model: str | None = None) -> str:
        """Gera rascunho de documentação técnica a partir do contexto."""
        prompt = (
            "Gere um rascunho de documentação técnica em Markdown para o projeto "
            "descrito abaixo. Inclua: visão geral, arquitetura resumida, stack, "
            "como operar com agentes (plan/run/review) e notas de roadmap.\n"
            "Seja factual — não invente features não mencionadas no contexto.\n\n"
            f"{context.strip()}"
        )
        return self.generate(prompt, model=model)

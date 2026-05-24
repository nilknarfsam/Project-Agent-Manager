"""Provider Gemini — tarefas leves via google-genai."""

from __future__ import annotations

import os

from pam.providers.base_provider import BaseProvider, ProviderError

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


class GeminiProvider(BaseProvider):
    """Integração com Gemini Developer API (google-genai)."""

    name = "gemini"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        default_model: str | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.environ.get("GEMINI_API_KEY")
        self.default_model = (
            default_model
            if default_model is not None
            else os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        )
        self._client = None

    def ensure_api_key(self) -> str:
        if not self.api_key or not self.api_key.strip():
            raise ProviderError(
                "GEMINI_API_KEY não definida.\n"
                "Configure em .env: GEMINI_API_KEY=your_gemini_api_key_here\n"
                "ou defina a variável de ambiente.\n"
                "Obtenha uma chave em: https://aistudio.google.com/apikey"
            )
        return self.api_key.strip()

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from google import genai
        except ImportError as exc:
            raise ProviderError(
                "Pacote 'google-genai' não instalado. "
                "Execute: pip install google-genai"
            ) from exc

        self._client = genai.Client(api_key=self.ensure_api_key())
        return self._client

    def generate(self, prompt: str, model: str | None = None) -> str:
        client = self._get_client()
        model_id = model or self.default_model

        try:
            response = client.models.generate_content(
                model=model_id,
                contents=prompt,
            )
        except Exception as exc:  # noqa: BLE001 — SDK pode levantar vários tipos
            raise ProviderError(
                f"Falha na chamada Gemini (modelo={model_id}): {exc}"
            ) from exc

        text = getattr(response, "text", None) or ""
        text = text.strip()
        if not text:
            raise ProviderError(
                f"Gemini retornou resposta vazia (modelo={model_id})."
            )
        return text

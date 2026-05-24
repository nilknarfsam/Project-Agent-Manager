"""Gerenciamento seguro de chaves de API em .env local."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from pam.config_loader import project_root

PROVIDER_ENV_VARS: dict[str, str] = {
    "cursor": "CURSOR_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}

PROVIDER_LABELS: dict[str, str] = {
    "cursor": "Cursor",
    "gemini": "Gemini",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
}

# Ordem canônica ao gravar .env (variáveis extras preservadas após estas).
CANONICAL_ENV_ORDER: tuple[str, ...] = (
    "CURSOR_API_KEY",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
)

DEFAULT_ENV_VALUES: dict[str, str] = {
    "CURSOR_API_KEY": "your_cursor_api_key_here",
    "GEMINI_API_KEY": "your_gemini_api_key_here",
    "GEMINI_MODEL": "gemini-2.5-flash",
    "OPENAI_API_KEY": "your_openai_api_key_here",
    "ANTHROPIC_API_KEY": "your_anthropic_api_key_here",
}

PLACEHOLDER_SUFFIX = "_here"


class SettingsManagerError(ValueError):
    """Erro de validação ou I/O em configurações."""


@dataclass(frozen=True)
class ProviderStatus:
    """Status público de um provider (sem expor chave completa)."""

    provider: str
    label: str
    env_var: str
    configured: bool
    masked: str | None


class SettingsManager:
    """Lê e atualiza .env local sem expor chaves completas."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or project_root()
        self.env_path = self.base_dir / ".env"
        self.example_path = self.base_dir / ".env.example"

    @classmethod
    def validate_provider(cls, provider: str) -> str:
        key = provider.strip().lower()
        if key not in PROVIDER_ENV_VARS:
            available = ", ".join(sorted(PROVIDER_ENV_VARS))
            raise SettingsManagerError(
                f"Provider '{provider}' inválido. Use: {available}"
            )
        return key

    @staticmethod
    def is_placeholder(value: str | None) -> bool:
        if not value or not value.strip():
            return True
        text = value.strip()
        if text.startswith("your_") and text.endswith(PLACEHOLDER_SUFFIX):
            return True
        return False

    @classmethod
    def mask_key(cls, value: str | None) -> str:
        """
        Mascara chave para exibição segura.

        Ex.: sk-...abcd, AIza...WXYZ
        """
        if not value or not value.strip():
            return "(não configurada)"

        text = value.strip()
        if cls.is_placeholder(text):
            return "(placeholder)"

        if len(text) <= 8:
            return text[:2] + "..." + text[-2:]

        prefix_len = 4
        if text.startswith("sk-"):
            prefix_len = 3
        elif text.startswith("AIza"):
            prefix_len = 4

        prefix = text[:prefix_len]
        suffix = text[-4:]
        return f"{prefix}...{suffix}"

    def ensure_env_file(self) -> Path:
        """Cria .env a partir de .env.example se não existir."""
        if self.env_path.is_file():
            return self.env_path

        if self.example_path.is_file():
            shutil.copy(self.example_path, self.env_path)
            return self.env_path

        self._write_env_values(dict(DEFAULT_ENV_VALUES))
        return self.env_path

    @staticmethod
    def _parse_env_lines(content: str) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, _, raw_value = stripped.partition("=")
            key = key.strip()
            value = raw_value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key] = value
        return values

    def read_env_values(self) -> dict[str, str]:
        """Lê todas as variáveis do .env."""
        self.ensure_env_file()
        content = self.env_path.read_text(encoding="utf-8")
        parsed = self._parse_env_lines(content)

        merged = dict(DEFAULT_ENV_VALUES)
        merged.update(parsed)
        return merged

    def _write_env_values(self, values: dict[str, str]) -> None:
        """Grava .env mantendo ordem canônica e variáveis extras."""
        known = set(CANONICAL_ENV_ORDER)
        extra_keys = [k for k in values if k not in known]

        lines: list[str] = []
        for key in CANONICAL_ENV_ORDER:
            if key in values:
                lines.append(f"{key}={values[key]}")

        for key in sorted(extra_keys):
            lines.append(f"{key}={values[key]}")

        self.env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def reload_environment(self) -> None:
        """Recarrega .env no processo atual."""
        load_dotenv(self.env_path, override=True)

    def get_key(self, provider: str) -> str | None:
        """Retorna valor bruto da chave ou None se ausente/placeholder."""
        prov = self.validate_provider(provider)
        env_var = PROVIDER_ENV_VARS[prov]
        self.reload_environment()
        value = os.environ.get(env_var) or self.read_env_values().get(env_var)
        if self.is_placeholder(value):
            return None
        return value.strip() if value else None

    def has_key(self, provider: str) -> bool:
        return self.get_key(provider) is not None

    def set_key(self, provider: str, value: str) -> None:
        """Persiste chave no .env local e recarrega ambiente."""
        prov = self.validate_provider(provider)
        env_var = PROVIDER_ENV_VARS[prov]
        cleaned = value.strip()
        if not cleaned:
            raise SettingsManagerError("Chave vazia não pode ser salva.")

        values = self.read_env_values()
        values[env_var] = cleaned
        self._write_env_values(values)
        self.reload_environment()

    def list_providers_status(self) -> list[ProviderStatus]:
        """Lista status de todos os providers sem expor chaves completas."""
        values = self.read_env_values()
        statuses: list[ProviderStatus] = []

        for provider in sorted(PROVIDER_ENV_VARS):
            env_var = PROVIDER_ENV_VARS[provider]
            raw = values.get(env_var)
            configured = not self.is_placeholder(raw)
            masked = self.mask_key(raw) if configured else None
            statuses.append(
                ProviderStatus(
                    provider=provider,
                    label=PROVIDER_LABELS[provider],
                    env_var=env_var,
                    configured=configured,
                    masked=masked,
                )
            )
        return statuses

    def format_status_report(self) -> str:
        """Relatório textual para CLI `settings`."""
        lines = ["Provider settings (.env local):", ""]
        for item in self.list_providers_status():
            state = "configurado" if item.configured else "não configurado"
            masked = f" ({item.masked})" if item.configured and item.masked else ""
            lines.append(f"  {item.label:10} [{state}]{masked}")
        lines.extend(
            [
                "",
                "Configure via:",
                "  python -m pam.main set-key gemini",
                "  python -m pam.main gui  -> aba Configuracoes",
            ]
        )
        return "\n".join(lines)

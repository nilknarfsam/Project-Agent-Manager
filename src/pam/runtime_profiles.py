"""Agent Runtime Profiles — provider/model/mode por agente (YAML)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from pam.config_loader import project_root
from pam.settings_manager import SettingsManager

RUNTIME_PROFILES_DIR = "ai/runtime_profiles"
DEFAULT_PROFILES_FILE = "default_profiles.yaml"

KNOWN_PROVIDERS = frozenset({"cursor", "gemini", "openai", "anthropic"})

DEFAULT_CURSOR_MODE = "agent"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

_profiles_cache: dict[str, "AgentRuntimeProfile"] | None = None


class RuntimeProfileError(ValueError):
    """Erro ao carregar ou validar runtime profile."""


@dataclass(frozen=True)
class AgentRuntimeProfile:
    """Runtime resolvido para um agente PAM."""

    agent: str
    provider: str
    model: str | None = None
    mode: str | None = None
    source: str = "yaml"

    def display_model(self) -> str:
        if self.model:
            return self.model
        if self.provider == "gemini":
            return DEFAULT_GEMINI_MODEL
        return "(project default)"


def profiles_path(base_dir: Path | None = None) -> Path:
    root = base_dir or project_root()
    return root / RUNTIME_PROFILES_DIR / DEFAULT_PROFILES_FILE


def _normalize_agent_name(agent_name: str) -> str:
    return agent_name.strip().lower()


def validate_profile(
    profile: dict[str, Any],
    *,
    agent_name: str | None = None,
) -> AgentRuntimeProfile:
    """Valida e normaliza um profile de agente."""
    if not isinstance(profile, dict):
        raise RuntimeProfileError("Profile deve ser um mapping YAML.")

    provider_raw = profile.get("provider")
    if not provider_raw:
        raise RuntimeProfileError(
            f"Profile{' de ' + agent_name if agent_name else ''} "
            "deve definir 'provider'."
        )

    provider = str(provider_raw).strip().lower()
    if provider not in KNOWN_PROVIDERS:
        raise RuntimeProfileError(
            f"Provider '{provider}' inválido. "
            f"Conhecidos: {', '.join(sorted(KNOWN_PROVIDERS))}."
        )

    model_raw = profile.get("model")
    model = str(model_raw).strip() if model_raw else None
    if model == "":
        model = None

    mode_raw = profile.get("mode")
    mode = str(mode_raw).strip() if mode_raw else None
    if mode == "":
        mode = None

    if provider == "cursor" and mode is None:
        mode = DEFAULT_CURSOR_MODE

    agent = _normalize_agent_name(agent_name or str(profile.get("agent", "")))
    if not agent:
        raise RuntimeProfileError("Nome do agente é obrigatório.")

    return AgentRuntimeProfile(
        agent=agent,
        provider=provider,
        model=model,
        mode=mode,
        source="yaml",
    )


def load_profiles(*, base_dir: Path | None = None, reload: bool = False) -> dict[str, AgentRuntimeProfile]:
    """Carrega profiles de ai/runtime_profiles/default_profiles.yaml."""
    global _profiles_cache

    if _profiles_cache is not None and not reload and base_dir is None:
        return _profiles_cache

    path = profiles_path(base_dir)
    profiles: dict[str, AgentRuntimeProfile] = {}

    if not path.is_file():
        if base_dir is None:
            _profiles_cache = profiles
        return profiles

    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if data is None:
        if base_dir is None:
            _profiles_cache = profiles
        return profiles

    if not isinstance(data, dict):
        raise RuntimeProfileError(f"YAML inválido em {path}: esperado mapping.")

    for agent_key, raw_profile in data.items():
        agent = _normalize_agent_name(str(agent_key))
        if not agent:
            continue
        if not isinstance(raw_profile, dict):
            raise RuntimeProfileError(
                f"Profile de '{agent}' em {path} deve ser um mapping."
            )
        profiles[agent] = validate_profile(raw_profile, agent_name=agent)

    if base_dir is None:
        _profiles_cache = profiles
    return profiles


def fallback_profile(agent_name: str) -> AgentRuntimeProfile:
    """Fallback seguro: Cursor com modo padrão (comportamento legado)."""
    return AgentRuntimeProfile(
        agent=_normalize_agent_name(agent_name),
        provider="cursor",
        model=None,
        mode=DEFAULT_CURSOR_MODE,
        source="fallback",
    )


def get_agent_profile(
    agent_name: str,
    *,
    base_dir: Path | None = None,
) -> AgentRuntimeProfile:
    """Resolve profile do agente; fallback para Cursor se não existir."""
    agent = _normalize_agent_name(agent_name)
    profiles = load_profiles(base_dir=base_dir)
    return profiles.get(agent, fallback_profile(agent))


def get_provider_for_agent(
    agent_name: str,
    *,
    base_dir: Path | None = None,
) -> str:
    """Retorna provider resolvido para o agente."""
    return get_agent_profile(agent_name, base_dir=base_dir).provider


def list_resolved_profiles(
    agent_names: list[str] | None = None,
    *,
    base_dir: Path | None = None,
) -> list[AgentRuntimeProfile]:
    """Lista profiles resolvidos (YAML + fallback) para exibição."""
    from pam.agent_registry import AgentRegistry

    names = agent_names
    if names is None:
        names = AgentRegistry(base_dir).list_agents()

    return [get_agent_profile(name, base_dir=base_dir) for name in sorted(names)]


def format_profile_error(provider: str, exc: Exception) -> str:
    """Mensagem amigável quando provider do profile falha."""
    label = SettingsManager.PROVIDER_LABELS.get(provider, provider.capitalize())
    return (
        f"Provider '{label}' indisponível para este agente: {exc}\n"
        "Verifique a chave com: python -m pam.main set-key "
        f"{provider}\n"
        "Os demais comandos e agentes continuam funcionando."
    )

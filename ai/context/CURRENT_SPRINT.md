# Sprint 9 — Agent Runtime Profiles

**Status:** em andamento  
**Objetivo:** permitir que cada agente utilize providers e modelos diferentes via YAML configurável.

## Entregas

- [x] `ai/runtime_profiles/default_profiles.yaml` — profiles por agente
- [x] `runtime_profiles.py` — load, validate, resolve, fallback seguro
- [x] `provider_router.route_agent()` — roteamento por agente
- [x] `pipeline_engine` — resolve profile, logs provider/model, execução híbrida
- [x] `task_manager.pipeline_history` — campos `provider` e `model`
- [x] GUI aba **Runtime Profiles** (somente leitura)
- [x] README: seção Agent Runtime Profiles
- [x] CHANGELOG 1.0.0-beta

## Critérios de aceite

- Profiles carregam via YAML
- Cada agente resolve provider diferente
- Pipeline logs mostram provider/model
- GUI mostra runtime profiles
- Providers desacoplados
- Comandos antigos continuam funcionando (fallback Cursor)

## Próximo passo (Sprint 10)

Providers OpenAI/Anthropic em pipeline ou edição de profiles via GUI.

# Sprint 14 — Portable Build Foundation

**Status:** concluída  
**Objetivo:** preparar o PAM para distribuição portátil/executável (.exe no Windows) usando PyInstaller e arquitetura Dual-Path.

## Entregas

- [x] Ajuste em `config_loader.py` — suporte a `sys.frozen` com `bundled_root()` e `project_root()` ajustados.
- [x] Atualização de recursos imutáveis para `bundled_root()` — `agent_registry`, `cursor_runner`, `pipeline_engine`, `runtime_profiles`, `settings_manager`, `project_bootstrap`.
- [x] Escritas direcionadas a `project_root()` — `.env`, `ai/projects/`, runs, sessões, métricas e logs locais.
- [x] Ajuste dinâmico na GUI Workbench para salvar contextos de forma isolada na pasta do projeto.
- [x] Criação de `scripts/build_executable.py` — automação do build com PyInstaller.
- [x] Documentação em `docs/portable_build.md`.
- [x] Atualizações em README, CHANGELOG e CURRENT_SPRINT.

## Critérios de aceite

- CLI e GUI intactos rodando em modo de desenvolvimento (Python normal).
- Executável autônomo gerado sem erros através de `python scripts/build_executable.py`.
- Executável portátil inicializa limpo, gerando `.env` na pasta local se ausente.
- Nenhuma chave de API ou credencial real embutida no binário.
- Onboarding, execuções de agentes e pipelines funcionando perfeitamente a partir do executável portátil.

## Próximo passo (Sprint 15)

Com base no planejamento de distribuição portátil, as próximas direções podem incluir refinamentos de performance, empacotamento para macOS/Linux ou integração de novos providers locais offline.

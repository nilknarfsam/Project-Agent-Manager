# Sprint 6 — Project Onboarding System

**Status:** em andamento  
**Objetivo:** permitir onboarding de projetos existentes e criação de projetos PAM-native com estrutura OS4AI automática.

## Entregas

- [x] `project_bootstrap.py` — estrutura OS4AI, protocolo, agentes, YAML
- [x] `template_engine.py` + `src/pam/templates/`
- [x] Comando `onboard <caminho>`
- [x] Comando `create-project <stack> <nome>`
- [x] README, CHANGELOG 0.7.0, `protocol/PROJECT_BOOTSTRAP.md`
- [ ] Testes manuais em projeto real (auratime / projeto novo)

## Critérios de aceite

- `onboard` cria estrutura sem sobrescrever arquivos existentes (sem `--force`)
- `create-project` cria diretório e estrutura completa
- YAML gerado em `ai/projects/`
- Comandos legados (`plan`, `run`, `review`, tasks) inalterados

## Próximo passo (Sprint 7)

Orquestração multi-agente encadeada (architect → implementer → reviewer).

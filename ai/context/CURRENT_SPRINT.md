# Sprint 13 — Observability & Metrics Foundation

**Status:** em andamento  
**Objetivo:** fundação de observabilidade e métricas do PAM — acompanhar execuções, agentes, providers, pipelines, tasks, duração, sucesso/falha e histórico operacional.

## Entregas

- [x] `ai/metrics/` e `ai/observability/` — estrutura de diretórios
- [x] `metrics_store.py` — registro JSONL, sanitização, agregação básica
- [x] `observability_service.py` — relatórios e agregações
- [x] Integração em plan, run, review, resume, pipeline, ai-summary, ai-tasks, ai-docs
- [x] CLI `metrics` com `--project` e `--last`
- [x] GUI: aba **Observabilidade**
- [x] `docs/observability.md`
- [x] README: seção Observabilidade e Métricas
- [x] CHANGELOG 1.0.0-beta.4

## Critérios de aceite

- Comandos antigos funcionam (CLI e GUI intactos)
- Cada execução gera evento JSONL em `ai/metrics/events_YYYYMM.jsonl`
- Métricas não expõem API keys nem prompts completos
- GUI mostra aba Observabilidade
- CLI `metrics` funciona
- Documentação atualizada
- Arquitetura permanece modular (sem banco de dados, sem custos reais)

## Próximo passo (Sprint 14)

Custos estimados por provider, exportação de métricas, retenção/rotação de arquivos ou dashboard histórico.

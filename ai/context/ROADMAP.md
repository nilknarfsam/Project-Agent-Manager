# Roadmap — PAM

## Visão

Evoluir o PAM de controlador CLI para um **Operating System for AI Development** completo.

## Fases

### Sprint 1 — Integração SDK (concluída)
- CLI plan / run / review
- Cursor Python SDK local
- Logs em `ai/runs/`

### Sprint 2 — Sessões + Contexto (atual)
- Context Engine (`ai/context`, `ai/memory`)
- Session Store (`ai/sessions`)
- Stub `resume`
- Preparação para `Agent.resume()`

### Sprint 3 — Sessões persistentes (planejada)
- `resume` funcional com `Agent.resume(agent_id)`
- Continuidade de conversa entre execuções
- Atualização automática de memória

### Sprint 4+ — Evolução
- Runtime cloud opcional
- Templates de sprint e tarefas
- Integração CI
- Métricas e rastreabilidade avançada

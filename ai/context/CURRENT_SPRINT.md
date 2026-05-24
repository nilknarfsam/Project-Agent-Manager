# Sprint 8 — Gemini Provider Integration

**Status:** em andamento  
**Objetivo:** adicionar Gemini como provider leve para análise, docs e tasks — sem substituir Cursor.

## Entregas

- [x] `google-genai` + `.env.example` (`GEMINI_API_KEY`, `GEMINI_MODEL`)
- [x] `src/pam/providers/` — base, gemini, router
- [x] Comandos `ai-summary`, `ai-tasks`, `ai-docs`
- [x] `ai_service.py` — contexto + Gemini
- [x] README Multi-Provider Runtime, CHANGELOG 0.9.0

## Critérios de aceite

- CLI Cursor inalterada (plan/run/review/pipeline)
- Sem chaves reais versionadas
- Gemini falha com mensagem amigável sem `GEMINI_API_KEY`
- `provider_router` separa Gemini e Cursor

## Próximo passo (Sprint 9)

A definir — possivelmente persistência de outputs Gemini ou integração com memória/roadmap.

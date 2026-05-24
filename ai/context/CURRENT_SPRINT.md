# Sprint 8 — API Keys Settings + Gemini Provider

**Status:** em andamento  
**Objetivo:** configuração segura de chaves de API e runtime multi-provider com Gemini para tarefas leves.

## Entregas

- [x] `settings_manager.py` — .env seguro, mascaramento, get/set/has_key
- [x] Comandos `settings`, `set-key` (getpass)
- [x] GUI aba Configurações (password, status mascarado)
- [x] `.env.example` com 4 providers + GEMINI_MODEL
- [x] `providers/` + `ai-summary`, `ai-tasks`, `ai-docs`
- [x] README Provider Settings + Multi-Provider

## Critérios de aceite

- `.env` gitignored; `.env.example` só placeholders
- `settings` não expõe chaves completas
- `set-key` persiste no .env local
- GUI cadastra chave com campo password
- Comandos Cursor inalterados
- Gemini funciona com `GEMINI_API_KEY` configurada

## Próximo passo (Sprint 9)

Providers OpenAI/Anthropic ou persistência de outputs Gemini.

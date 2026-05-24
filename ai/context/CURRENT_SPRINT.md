# Sprint 11 — Context Builder Panel

**Status:** em andamento  
**Direção:** Agentic Workbench for Software Architects  
**Objetivo:** selecionar arquivos/pastas do projeto e montar pacote de contexto para agentes.

## Entregas

- [x] `context_builder.py` — listar arquivos, ignorar pastas pesadas, limite de tamanho, markdown
- [x] Salvamento em `ai/context/generated/context_YYYYMMDD_HHMMSS.md`
- [x] GUI aba **Context Builder** — árvore, adicionar, limpar, preview, salvar, usar no prompt
- [x] README: seção Context Builder
- [x] CHANGELOG 1.0.0-beta.2

## Critérios de aceite

- Árvore lista arquivos ignorando pastas pesadas
- Contexto montado em markdown com limite de tamanho
- Salvar e usar no prompt extra funcionam
- CLI inalterada; sem editor de código; sem lógica duplicada

## Próximo passo (Sprint 12)

Pipeline na GUI ou histórico de runs/contextos gerados.

# Sprint 10 — Agentic Workbench UI foundation

**Status:** em andamento  
**Direção:** Agentic Workbench for Software Architects  
**Objetivo:** evoluir a GUI Tkinter para uma primeira versão mais amigável, sem virar IDE completa.

## Entregas

- [x] Layout workbench — sidebar, área central, log inferior
- [x] Abas: Operações, Tasks, Runtime Profiles, Configurações, Logs
- [x] Melhorias visuais — padding, labels, prompt maior, janela maior
- [x] Botões Abrir no Cursor / Abrir no VS Code
- [x] `open_project_in_editor(editor, path)` — função única reutilizável
- [x] Preservação de onboard, plan/run/review/resume, profiles, configurações
- [x] README: seção Agentic Workbench UI
- [x] CHANGELOG 1.0.0-beta.1

## Critérios de aceite

- `python -m pam.main gui` abre interface reorganizada
- Comandos existentes funcionam
- Abrir no Cursor/VS Code funciona ou mostra erro amigável
- Sem lógica de negócio duplicada
- Interface mais clara e confortável

## Próximo passo (Sprint 11)

Pipeline na GUI, histórico de runs ou refinamentos visuais adicionais.

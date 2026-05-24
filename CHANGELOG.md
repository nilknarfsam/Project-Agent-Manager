# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-beta.4] - 2026-05-23

### Added (Sprint 13 — Observability & Metrics Foundation)

- Diretórios `ai/metrics/` e `ai/observability/` — fundação de observabilidade local.
- Módulo `metrics_store.py` — registro de eventos JSONL mensais, sanitização de dados sensíveis.
- Módulo `observability_service.py` — agregações (totais, por projeto/provider/agente, duração média).
- Integração de métricas em `plan`, `run`, `review`, `resume`, `pipeline`, `ai-summary`, `ai-tasks`, `ai-docs`.
- Comando CLI `metrics` com filtros `--project` e `--last`.
- GUI: aba **Observabilidade** (resumo, providers, agentes, últimas execuções, botão Atualizar).
- Documentação: `docs/observability.md`, seção no README.

### Changed

- `cursor_runner`, `pipeline_engine` e `ai_service` registram eventos sem alterar providers profundamente.
- `.gitignore` ignora `ai/metrics/events_*.jsonl`.
- `CURRENT_SPRINT` atualizado para Sprint 13.

## [1.0.0-beta.3] - 2026-05-23

### Added (Sprint 12 — Documentation Foundation)

- Diretório `docs/` — documentação oficial em português brasileiro (11 guias).
- Guias: primeiros passos, instalação, GUI, Context Builder, providers, runtime profiles, tasks, pipelines, arquitetura, onboarding, FAQ.
- README: seção Documentação, Quick Start, conceito Agentic Workbench, placeholders para screenshots.

### Changed

- README atualizado com links para `docs/`.
- `CURRENT_SPRINT` atualizado para Sprint 12.
- Projeto mais apresentável para comunidade, onboarding e demonstrações.

## [1.0.0-beta.2] - 2026-05-23

### Added (Sprint 11 — Context Builder Panel)

- Módulo `context_builder.py` — listagem de arquivos, filtros de pastas pesadas, markdown consolidado.
- Aba **Context Builder** na GUI: árvore, seleção, preview, salvar e usar no prompt.
- Contextos salvos em `ai/context/generated/context_YYYYMMDD_HHMMSS.md`.
- README: seção Context Builder.

### Changed

- `CURRENT_SPRINT` atualizado para Sprint 11.

## [1.0.0-beta.1] - 2026-05-23

### Added (Sprint 10 — Agentic Workbench UI foundation)

- GUI reorganizada em layout **Agentic Workbench**: sidebar de projetos, área central, log inferior.
- Abas: Operações, Tasks, Runtime Profiles, Configurações, Logs.
- Aba **Tasks** — listagem de tarefas do lifecycle por projeto.
- Botões **Abrir no Cursor** e **Abrir no VS Code** via `open_project_in_editor()`.
- Prompt extra multilinha; janela maior; padding e fonte monoespaçada no log.
- README: seção Agentic Workbench UI.

### Changed

- `gui_launcher.py` evoluído de Desktop Launcher para Agentic Workbench.
- Correção no redirecionamento de stdout/stderr durante execução em thread.
- `CURRENT_SPRINT` atualizado para Sprint 10.

## [1.0.0-beta] - 2026-05-23

### Added (Sprint 9 — Agent Runtime Profiles)

- `ai/runtime_profiles/default_profiles.yaml` — provider/model/mode por agente.
- Módulo `runtime_profiles.py` — `load_profiles`, `get_agent_profile`, `validate_profile`, `get_provider_for_agent`.
- `provider_router.route_agent()` — roteamento por agente via runtime profiles.
- Pipeline híbrido: steps Gemini (análise/docs) + Cursor (implementação) conforme profile.
- `pipeline_history` e logs de pipeline com `provider` e `model` por step.
- GUI: aba **Runtime Profiles** (somente leitura).
- README: seção Agent Runtime Profiles.

### Changed

- `pipeline_engine`, `cursor_runner`, `pipeline_result` e `task_manager` integrados a runtime profiles.
- Fallback seguro para Cursor quando profile ausente ou provider não configurado.
- `CURRENT_SPRINT` atualizado para Sprint 9.

## [0.9.0] - 2026-05-23

### Added (Sprint 8 — API Keys Settings + Gemini Provider)

- `settings_manager.py` — leitura/escrita segura de `.env`, mascaramento de chaves.
- Comandos `settings` e `set-key <provider>` (cursor, gemini, openai, anthropic) com `getpass`.
- GUI: aba **Configurações** com status mascarado e campos password por provider.
- Pacote `google-genai` e variáveis em `.env.example` (incl. OpenAI, Anthropic).
- Módulos `src/pam/providers/` — `base_provider`, `gemini_provider`, `provider_router`.
- Comandos `ai-summary`, `ai-tasks`, `ai-docs` — Gemini para tarefas leves.
- README: seções Provider Settings e Multi-Provider Runtime.

### Changed

- `cursor_runner` e `gemini_provider` usam `SettingsManager` para chaves.
- `CURRENT_SPRINT` atualizado para Sprint 8.

## [0.8.0] - 2026-05-23

### Added (Sprint 7 — Multi-Agent Orchestration foundation)

- Módulo `pipeline_engine.py` — execução sequencial de pipelines YAML.
- Módulo `pipeline_result.py` — modelo consolidado (`PipelineResult`, `PipelineStepResult`).
- Pipeline padrão `ai/pipelines/default_pipeline.yaml` (6 agentes).
- `cursor_runner.run_agent_step()` — step com contexto acumulado entre agentes.
- `task_manager.pipeline_history` — registro de steps por task.
- Comando `pipeline <projeto> <TASK-XXXX>` com `--pipeline` e `--from-step`.
- Logs consolidados em `ai/runs/pipelines/`.
- README: seção Multi-Agent Orchestration.

### Changed

- `CURRENT_SPRINT` atualizado para Sprint 7.

## [0.7.5] - 2026-05-23

### Added (Sprint 6.5 — Desktop Launcher foundation)

- Módulo `gui_launcher.py` — interface desktop Tkinter (sem dependências extras).
- Comando `gui` — abre o Desktop Launcher.
- Seleção de pasta, projeto cadastrado, onboard, listagem de projetos.
- Execução de `plan`, `run`, `review`, `resume` com agente, task e prompt extra.
- Área de log com saída capturada dos handlers CLI existentes.
- README: seção Desktop Launcher.

### Changed

- `CURRENT_SPRINT` atualizado para Sprint 6.5.

## [0.7.0] - 2026-05-23

### Added (Sprint 6 — Project Onboarding System)

- Módulo `project_bootstrap.py` — estrutura OS4AI, cópia de `protocol/`, agentes e prompts.
- Módulo `template_engine.py` — renderização de templates com variáveis `{{nome}}`.
- Templates em `src/pam/templates/` (README, CHANGELOG, contexto, memória, YAML).
- Comando `onboard <caminho>` — onboarding de repositório existente.
- Comando `create-project <stack> <nome>` — projetos PAM-native (flutter, python, electron).
- Flag `--force` para sobrescrever arquivos gerados; preservação de conteúdo existente por padrão.
- Registro automático em `ai/projects/<slug>.yaml` no repositório PAM.
- README: seção Project Onboarding System.

### Changed

- `protocol/PROJECT_BOOTSTRAP.md` — onboarding automatizado e create-project.
- `CURRENT_SPRINT` atualizado para Sprint 6.

## [0.6.5] - 2026-05-23

### Added (Sprint 5.5 — AI Engineering Protocol foundation)

- Diretório `protocol/` com especificação OS4AI reutilizável e agnóstica de ferramenta.
- `OPERATING_SYSTEM_FOR_AI_DEVELOPMENT.md` — visão, arquitetura modular, princípios obrigatórios.
- `AGENT_RULES.md` — responsabilidades, limites e colaboração dos seis agentes oficiais.
- `TASK_LIFECYCLE.md` — status, transições, metadata JSON e movimentação de tasks.
- `PROJECT_BOOTSTRAP.md` — onboarding, estrutura `ai/` e checklist para novos projetos.
- `DEVELOPMENT_PHILOSOPHY.md` — princípios de engenharia agêntica.
- `CONTEXT_INJECTION.md` — ordem de montagem e prioridade de contexto em prompts.
- `ARCHITECTURE_GUIDELINES.md` — modularidade, naming, organização e versionamento.

### Changed

- README: seção "AI Engineering Protocol".
- `CURRENT_SPRINT` atualizado para Sprint 5.5.

## [0.6.0] - 2026-05-23

### Added (Sprint 5 — Task Lifecycle System)

- Estrutura `ai/tasks/{active,completed,blocked,archived}/` com par `.md` + `.json`.
- Módulo `task_manager.py` — criar, listar, carregar, atualizar status e mover tarefas.
- Metadata: `task_id`, `title`, `project`, `status`, `agent`, timestamps, `history`.
- Comandos: `tasks`, `task-status`, `approve-task`, `complete-task`, `block-task`, `cancel-task`.
- Fluxo automático: `plan` cria TASK; `run` → running/reviewed; `review` → done.
- README: seção Task Lifecycle System.

### Changed

- `resolve_task_path` aceita `TASK-0001` e caminhos legados.
- `CURRENT_SPRINT` atualizado para Sprint 5.

## [0.5.0] - 2026-05-23

### Added (Sprint 4 — Specialized Agents foundation)

- Definições oficiais em `ai/agents/` (architect, implementer, reviewer, test_writer, docs_writer, release_manager).
- Módulo `agent_registry.py` — listar, validar e carregar agentes.
- Comando `agents` e flag `--agent` em plan/run/review/resume.
- Campo `agent_name` em `ai/sessions/` e logs de run.
- Injeção de definição do agente no prompt (após contexto, antes da tarefa).
- Padrões: plan→architect, run→implementer, review→reviewer, resume→sessão ou architect.

### Changed

- README: seção "Agentes especializados".
- `CURRENT_SPRINT` atualizado para Sprint 4.

## [0.4.0] - 2026-05-23

### Added (Sprint 3 — Real Agent Resume)

- Retomada real via `Agent.resume(agent_id)` em `resume_existing_session()`.
- `session_store`: `get_session`, `has_session`, `update_session_run`, `clear_session`.
- Leitura defensiva de JSON corrompido (`SessionStoreError` com mensagem amigável).
- Comando `clear-session` — remove apenas `ai/sessions/<projeto>.json`.
- Comando `resume` com `--task` e `-p` — envia prompt com contexto atualizado.
- README: seção "Retomando sessões".

### Changed

- `resume` deixa de ser stub e executa o agente retomado.
- Sessões existentes preservam `created_at` ao atualizar runs.
- `KNOWN_ISSUES` e `CURRENT_SPRINT` atualizados para Sprint 3.

## [0.3.0] - 2026-05-23

### Added (Sprint 2 — Persistent Sessions + Context Engine foundation)

- Posicionamento oficial: **Operating System for AI Development**.
- Estrutura `ai/context/` (ARCHITECTURE, ROADMAP, CURRENT_SPRINT, KNOWN_ISSUES, STACK).
- Memória por projeto em `ai/memory/<projeto>/` (DECISIONS, PATTERNS, LEARNINGS).
- Diretório `ai/sessions/` para metadata de sessões.
- Módulo `context_engine.py` — consolida contexto para injeção em prompts.
- Módulo `session_store.py` — persiste metadata (project, agent_id, run, mode, task, timestamps).
- Hooks em `cursor_runner.py`: `create_session()`, `resume_session()`, `save_session_metadata()`.
- Comando stub `resume` — localiza sessão existente (execução via `Agent.resume` na Sprint 3).
- Contexto injetado automaticamente em plan/run/review.

### Changed

- README com subtítulo e explicação do novo posicionamento.
- `.gitignore` ignora `ai/sessions/*.json`.

## [0.2.0] - 2026-05-23

### Added (Sprint 1)

- `.gitignore` protegendo `.env`, `.venv` e logs em `ai/runs/`.
- Integração real com Cursor Python SDK (`LocalAgentOptions`, modos `plan` e `agent`).
- Persistência de execuções em `ai/runs/` (`.md` + `.json` com timestamp).
- Parâmetro CLI `--task` para arquivos de tarefa em Markdown.
- Templates de prompt em `ai/prompts/` (`plan`, `run`, `review`).
- Tarefa exemplo `ai/tasks/sprint_001_analyze_project.md`.
- README com instalação, API key e exemplos do fluxo plan/run/review.

### Changed

- Comandos `plan`, `run` e `review` executam o agente local em vez de placeholders.
- `.env.example` usa placeholder em vez de chave real.

## [0.1.0] - 2026-05-23

### Added

- Estrutura inicial do Project Agent Manager (PAM).
- CLI com argparse e comandos: `plan`, `run`, `review`.
- Carregamento de configurações YAML em `ai/projects/`.
- Wrapper preparado para integração com `cursor-sdk`.
- Definições iniciais dos projetos AuraTime e Nilkplayer.

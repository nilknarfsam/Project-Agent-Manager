# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

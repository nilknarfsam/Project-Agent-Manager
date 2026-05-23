# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

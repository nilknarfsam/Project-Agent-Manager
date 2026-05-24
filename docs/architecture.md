# Arquitetura do PAM

Visão arquitetural completa do **Project Agent Manager** — camadas, módulos e fluxo de dados.

## Visão de alto nível

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE INTERFACE                       │
│  ┌──────────────┐              ┌──────────────────────────┐ │
│  │  CLI (main)  │              │  GUI (Agentic Workbench)   │ │
│  └──────┬───────┘              └─────────────┬────────────┘ │
└─────────┼────────────────────────────────────┼──────────────┘
          │                                    │
          └────────────────┬───────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      PAM CORE                                │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐  │
│  │ Task Manager│ │Agent Registry│ │  Config Loader      │  │
│  └─────────────┘ └──────────────┘ └─────────────────────┘  │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐  │
│  │Session Store│ │Context Engine│ │  Context Builder    │  │
│  └─────────────┘ └──────────────┘ └─────────────────────┘  │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐  │
│  │Cursor Runner│ │Pipeline Engine│ │ Runtime Profiles   │  │
│  └─────────────┘ └──────────────┘ └─────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE PROVIDERS                       │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐  ┌─────────┐ │
│  │   Cursor   │  │   Gemini   │  │  OpenAI  │  │Anthropic│ │
│  │    SDK     │  │    API     │  │ (futuro) │  │(futuro) │ │
│  └────────────┘  └────────────┘  └──────────┘  └─────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    DADOS (ai/ + protocol/)                   │
│  context · memory · tasks · sessions · agents · pipelines   │
│  runs · runtime_profiles · projects · prompts               │
└─────────────────────────────────────────────────────────────┘
```

## PAM Core

Núcleo em `src/pam/` — lógica de negócio independente de interface.

| Módulo | Responsabilidade |
|--------|------------------|
| `main.py` | CLI — parsing de argumentos e handlers |
| `config_loader.py` | Carrega `ai/projects/*.yaml` |
| `models.py` | Modelos de dados (ProjectConfig, etc.) |
| `settings_manager.py` | Chaves `.env` com mascaramento |

## GUI (Agentic Workbench)

| Módulo | Responsabilidade |
|--------|------------------|
| `gui_launcher.py` | Interface Tkinter — delega aos handlers da CLI |

Princípio: **zero duplicação de lógica** — a GUI chama `cmd_plan`, `cmd_run`, etc.

## Providers

| Módulo | Responsabilidade |
|--------|------------------|
| `providers/base_provider.py` | Contrato abstrato |
| `providers/gemini_provider.py` | Integração Gemini |
| `providers/provider_router.py` | Roteamento por tipo de tarefa e agente |
| `ai_service.py` | Comandos `ai-summary`, `ai-tasks`, `ai-docs` |

## Runtime

| Módulo | Responsabilidade |
|--------|------------------|
| `runtime_profiles.py` | Profiles YAML por agente |
| `cursor_runner.py` | Wrapper Cursor Python SDK |
| `ai/runtime_profiles/default_profiles.yaml` | Configuração padrão |

## Protocol (OS4AI)

Especificação reutilizável em `protocol/`:

| Documento | Conteúdo |
|-----------|----------|
| `OPERATING_SYSTEM_FOR_AI_DEVELOPMENT.md` | Visão e princípios |
| `AGENT_RULES.md` | Papéis e limites |
| `TASK_LIFECYCLE.md` | Status e transições |
| `PROJECT_BOOTSTRAP.md` | Onboarding |
| `CONTEXT_INJECTION.md` | Montagem de contexto |
| `ARCHITECTURE_GUIDELINES.md` | Modularidade |

O protocolo é **agnóstico de ferramenta** — pode ser adotado sem o PAM.

## Tasks

| Módulo / pasta | Responsabilidade |
|----------------|------------------|
| `task_manager.py` | CRUD, lifecycle, `pipeline_history` |
| `ai/tasks/` | Arquivos `.md` + `.json` por status |

## Sessions

| Módulo / pasta | Responsabilidade |
|----------------|------------------|
| `session_store.py` | Metadata de sessões |
| `ai/sessions/` | `agent_id`, modo, task, agente |
| `cursor_runner.py` | `Agent.resume()` |

## Context Engine

| Módulo / pasta | Responsabilidade |
|----------------|------------------|
| `context_engine.py` | Injeta `ai/context/` + `ai/memory/<projeto>/` |
| `ai/context/` | Arquitetura, roadmap, sprint, stack |
| `ai/memory/<projeto>/` | Decisões, padrões, aprendizados |

Injeção automática em **todo** prompt de agente.

## Context Builder

| Módulo / pasta | Responsabilidade |
|----------------|------------------|
| `context_builder.py` | Monta pacotes ad hoc de arquivos do repo |
| `ai/context/generated/` | Contextos salvos com timestamp |

Complementa o Context Engine — não o substitui.

## Pipeline Engine

| Módulo / pasta | Responsabilidade |
|----------------|------------------|
| `pipeline_engine.py` | Orquestração sequencial |
| `pipeline_result.py` | Modelos de resultado |
| `ai/pipelines/` | Definições YAML |
| `ai/runs/pipelines/` | Logs de execução |

## Agent Registry

| Módulo / pasta | Responsabilidade |
|----------------|------------------|
| `agent_registry.py` | Lista, valida, carrega agentes |
| `ai/agents/` | Definições Markdown por agente |
| `ai/prompts/` | Templates plan, run, review |

## Onboarding

| Módulo | Responsabilidade |
|--------|------------------|
| `project_bootstrap.py` | Estrutura OS4AI em novos repos |
| `template_engine.py` | Renderização de templates |

## Fluxo de um comando `run`

```
CLI: run auratime --task TASK-0001
        │
        ▼
config_loader.load_project("auratime")
        │
        ▼
task_manager.on_command_start("run", "TASK-0001")
        │
        ▼
context_engine.build_context_block("auratime")
agent_registry.load("implementer")
        │
        ▼
cursor_runner.run(project, prompt, mode="agent")
        │
        ▼
ai/runs/ ← log salvo
session_store ← metadata atualizada
task_manager.on_command_success("run", "TASK-0001")
```

## Estrutura de diretórios

```text
project_agent_manager/
├── docs/                  ← documentação PT-BR (esta pasta)
├── protocol/              ← OS4AI
├── ai/
│   ├── context/
│   ├── memory/
│   ├── tasks/
│   ├── sessions/
│   ├── projects/
│   ├── agents/
│   ├── prompts/
│   ├── pipelines/
│   ├── runtime_profiles/
│   └── runs/
└── src/pam/
```

## Princípios arquiteturais

1. **Separação de camadas** — interface ≠ core ≠ providers ≠ dados
2. **Modularidade** — cada módulo com responsabilidade única
3. **Extensibilidade** — novos providers, agentes e pipelines via configuração
4. **Rastreabilidade** — tudo gera log ou histórico
5. **Fallback seguro** — features novas não quebram comportamento legado

## Próximo passo

- [Primeiros passos](getting_started.md)
- [Providers](providers.md)
- [Pipelines](pipelines.md)

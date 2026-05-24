# Project Agent Manager (PAM)

## Operating System for AI Development

**Agentic Workbench for Software Architects** — orquestra agentes de IA em projetos reais com planejamento, execução, revisão, memória, contexto e rastreabilidade.

O **Project Agent Manager** é um controlador Python para orquestrar agentes do [Cursor Python SDK](https://cursor.com/docs/sdk/python) em projetos reais — com planejamento, execução, revisão, memória, contexto, rastreabilidade e sprints pequenas.

Não é só um CLI de prompts: é a camada que organiza **como** agentes trabalham nos seus repositórios (AuraTime, Nilkplayer e outros).

## Quick Start

```powershell
cd C:\src\projects\project_agent_manager
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python -m pam.main set-key cursor

$env:PYTHONPATH = "src"
python -m pam.main --list-projects
python -m pam.main gui
```

Fluxo mínimo: **onboard** → **plan** → **run** → **review**. Detalhes em [docs/getting_started.md](docs/getting_started.md).

## Documentação

Documentação oficial em **português brasileiro** — `docs/`:

| Guia | Descrição |
|------|-----------|
| [Primeiros passos](docs/getting_started.md) | O que é o PAM, OS4AI, fluxo básico |
| [Instalação](docs/installation.md) | Python, venv, chaves, problemas comuns |
| [GUI Workbench](docs/gui_workbench.md) | Interface gráfica completa |
| [Context Builder](docs/context_builder.md) | Montar pacotes de contexto |
| [Providers](docs/providers.md) | Cursor, Gemini, runtime híbrido |
| [Runtime Profiles](docs/runtime_profiles.md) | Provider/model por agente |
| [Ciclo de vida de tasks](docs/tasks_lifecycle.md) | TASK-XXXX, status, histórico |
| [Pipelines](docs/pipelines.md) | Orquestração multi-agente |
| [Arquitetura](docs/architecture.md) | Visão técnica completa |
| [Onboarding](docs/onboarding.md) | Integrar projetos ao OS4AI |
| [FAQ](docs/faq.md) | Perguntas frequentes |
| [Observabilidade](docs/observability.md) | Métricas, eventos JSONL, privacidade |
| [Distribuição Portátil](docs/portable_build.md) | Como compilar e rodar portátil (.exe) |

### Screenshots (em breve)

<!-- Placeholder para capturas da GUI -->
<!-- ![Agentic Workbench](docs/assets/workbench_overview.png) -->
<!-- ![Context Builder](docs/assets/context_builder.png) -->
<!-- ![Runtime Profiles](docs/assets/runtime_profiles.png) -->

### Capacidades

| Área | Descrição |
|------|-----------|
| **Planejamento** | `plan` — modo `plan`, análise sem alterar código |
| **Execução** | `run` — modo `agent`, implementa tarefas |
| **Revisão** | `review` — avaliação estruturada do repositório |
| **Memória** | `ai/memory/<projeto>/` — decisões, padrões, aprendizados |
| **Contexto** | `ai/context/` — arquitetura, roadmap, sprint, stack |
| **Rastreabilidade** | `ai/runs/` — logs de cada execução |
| **Sessões** | `ai/sessions/` — metadata + retomada via `Agent.resume()` |
| **Agentes** | `ai/agents/` — papéis especializados (architect, implementer, …) |
| **Sprints** | entregas pequenas e versionadas (ver `CHANGELOG.md`) |
| **Gemini (leve)** | `ai-summary`, `ai-tasks`, `ai-docs` — análise sem editar código |
| **Observabilidade** | `ai/metrics/` — eventos JSONL, CLI `metrics`, aba na GUI |

## Requisitos

- Python 3.11+
- Chave de API Cursor (`CURSOR_API_KEY`) — plan/run/review/pipeline
- Chave Gemini opcional (`GEMINI_API_KEY`) — comandos `ai-*`
- Repositórios dos projetos configurados e acessíveis no disco

## Instalação

```powershell
cd C:\src\projects\project_agent_manager
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edite `.env` e defina sua chave (nunca commite o arquivo `.env`):

```env
CURSOR_API_KEY=your_cursor_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Obtenha a chave Cursor em [Cursor Dashboard → Integrations](https://cursor.com/dashboard/integrations).  
Obtenha a chave Gemini em [Google AI Studio](https://aistudio.google.com/apikey).

## Uso

```powershell
$env:PYTHONPATH = "src"
python -m pam.main --list-projects
```

### Comandos

| Comando | Modo SDK | Descrição |
|---------|----------|-----------|
| `plan` | `plan` | Planejamento — análise sem editar arquivos |
| `run` | `agent` | Execução de tarefas no repositório |
| `review` | `agent` | Revisão com prompt dedicado |
| `resume` | (da sessão) | Retoma agente salvo com `Agent.resume()` |
| `agents` | — | Lista agentes especializados |
| `tasks` | — | Lista tarefas gerenciadas |
| `task-status` | — | Status e histórico de TASK-XXXX |
| `approve-task` | — | Marca tarefa como `approved` |
| `complete-task` | — | Marca tarefa como `done` |
| `block-task` | — | Marca tarefa como `blocked` |
| `cancel-task` | — | Marca tarefa como `cancelled` |
| `clear-session` | — | Remove metadata de sessão (preserva `ai/runs/`) |
| `onboard` | — | Aplica estrutura OS4AI em repositório existente |
| `create-project` | — | Cria novo projeto PAM-native (flutter / python / electron) |
| `gui` | — | Abre o Agentic Workbench (Tkinter) |
| `pipeline` | sequencial | Pipeline multi-agente para TASK-XXXX |
| `ai-summary` | Gemini | Sumariza contexto do projeto (leve) |
| `ai-tasks` | Gemini | Sugere tasks pequenas |
| `ai-docs` | Gemini | Rascunho de documentação |
| `settings` | — | Status das chaves (mascaradas) |
| `set-key` | — | Salva chave no `.env` local (entrada oculta) |
| `metrics` | — | Métricas e observabilidade (`ai/metrics/`) |

O **Context Engine** injeta `ai/context/` e `ai/memory/<projeto>/`. Cada execução também inclui a definição do **agente especializado** selecionado.

### Agentes especializados

Agentes oficiais em `ai/agents/`:

| Agente | Papel | Padrão em |
|--------|-------|-----------|
| `architect` | Arquitetura e planejamento | `plan` |
| `implementer` | Implementação de código | `run` |
| `reviewer` | Revisão e qualidade | `review` |
| `test_writer` | Testes automatizados | — |
| `docs_writer` | Documentação | — |
| `release_manager` | Checklist de release | — |

```powershell
python -m pam.main agents

python -m pam.main plan auratime --agent architect --task ai/tasks/sprint_001_analyze_project.md
python -m pam.main run auratime --agent implementer --task ai/tasks/sprint_001_analyze_project.md
python -m pam.main review auratime --agent reviewer
```

Sem `--agent`, o PAM usa o padrão do comando. O nome do agente é salvo em `ai/sessions/<projeto>.json` (`agent_name`). No `resume`, usa o agente da sessão ou `architect` como fallback.

### Task Lifecycle System

Toda tarefa gerenciada possui identidade (`TASK-XXXX`), status, timestamps, agente, projeto e histórico.

**Status oficiais:** `planned` · `approved` · `running` · `reviewed` · `done` · `blocked` · `cancelled`

**Estrutura:**

```
ai/tasks/
  active/      # planned, approved, running, reviewed
  completed/   # done
  blocked/     # blocked
  archived/    # cancelled
  TASK-0001.md + TASK-0001.json
```

**Fluxo automático:**

| Comando | Efeito na task |
|---------|----------------|
| `plan --task ...` | Cria `TASK-XXXX` com status `planned` |
| `run --task TASK-XXXX` | `running` ao iniciar → `reviewed` ao concluir |
| `review --task TASK-XXXX` | `done` ao concluir |

**Comandos manuais:**

```powershell
python -m pam.main tasks
python -m pam.main tasks --project auratime
python -m pam.main task-status TASK-0001
python -m pam.main approve-task TASK-0001
python -m pam.main complete-task TASK-0001
python -m pam.main block-task TASK-0001
python -m pam.main cancel-task TASK-0001
```

Arquivos legados (ex.: `ai/tasks/sprint_001_analyze_project.md`) continuam válidos; no `plan`, o PAM cria automaticamente um `TASK-XXXX` em `active/`.

### Retomando sessões

Após um `plan`, `run` ou `review` bem-sucedido, o PAM grava `ai/sessions/<projeto>.json` com o `agent_id`. Use `resume` para continuar a conversa no mesmo agente:

```powershell
# 1. Criar sessão com plan
python -m pam.main plan auratime --task ai/tasks/sprint_001_analyze_project.md

# 2. Retomar com instrução adicional
python -m pam.main resume auratime -p "Continue a análise e sugira a próxima tarefa pequena"

# 3. Retomar com nova tarefa em arquivo
python -m pam.main resume auratime --task ai/tasks/sprint_001_analyze_project.md

# 4. Limpar sessão (runs antigos permanecem)
python -m pam.main clear-session auratime
```

Sem sessão salva, `resume` orienta a executar `plan` primeiro.

### Project Onboarding System

Onboarding automatizado do protocolo OS4AI em projetos existentes ou novos.

**Onboard** — repositório já existente (não sobrescreve arquivos sem `--force`):

```powershell
python -m pam.main onboard "C:\src\projects\auratime"
python -m pam.main onboard "C:\src\projects\Nilkplayer" --project-name nilkplayer
python -m pam.main onboard "C:\src\projects\meu-repo" --force
```

Cria `ai/context/`, `ai/memory/<slug>/`, `ai/tasks/`, `ai/sessions/`, copia `protocol/`, agentes e prompts; gera `ai/projects/<slug>.yaml` no PAM. Se `README.md` já existir, adiciona `README_PAM.md` complementar.

**Create-project** — estrutura PAM-native (sem código de app ainda):

```powershell
python -m pam.main create-project python log-analyzer
python -m pam.main create-project flutter auratime
python -m pam.main create-project electron project-manager
python -m pam.main create-project python my-app --path D:\dev\projects
```

Stacks: `flutter`, `python`, `electron`. Diretório padrão: pai dos projetos já configurados (ex.: `C:\src\projects`).

### Agentic Workbench UI

Interface desktop (Tkinter) orientada a **arquitetos de software** — complementa a CLI sem duplicar lógica de negócio. Não é uma IDE completa; foco em clareza, organização e execução agentica.

```powershell
python -m pam.main gui
```

| Área | Conteúdo |
|------|----------|
| **Barra lateral** | Lista de projetos, Atualizar, Abrir pasta, onboard, Abrir no Cursor / VS Code |
| **Operações** | Comando, agente, task, prompt extra, Executar |
| **Tasks** | Tarefas do lifecycle (`ai/tasks/`) do projeto selecionado |
| **Context Builder** | Árvore de arquivos, montagem e salvamento de pacote de contexto |
| **Runtime Profiles** | Provider/model por agente (somente leitura) |
| **Configurações** | Chaves de API (.env) |
| **Logs** | Controles da saída em tempo real |
| **Painel inferior** | Log monoespaçado com saída dos comandos |

Abrir projeto no editor externo:

```text
cursor <caminho_do_projeto>
code <caminho_do_projeto>
```

Se o comando não estiver no PATH, a GUI exibe erro amigável com instruções.

Comandos delegados aos mesmos handlers da CLI: `plan`, `run`, `review`, `resume`, onboard.

### Context Builder

Monte pacotes de contexto a partir de arquivos do repositório do projeto — aba **Context Builder** na GUI.

| Recurso | Descrição |
|---------|-----------|
| Árvore de arquivos | Lista o repo ignorando `.git`, `.venv`, `node_modules`, `build`, etc. |
| Seleção | Adicionar arquivo ou pasta inteira ao pacote |
| Limite | Contexto truncado em ~120k caracteres |
| Salvar | `ai/context/generated/context_YYYYMMDD_HHMMSS.md` |
| Usar no prompt | Copia o markdown para o prompt extra (aba Operações) |

Formato: cabeçalho `# Generated Context`, projeto, lista de arquivos incluídos e seções `## caminho/arquivo` com conteúdo em bloco `text`.

Lógica em `context_builder.py` — complementa `context_engine` (contexto PAM global/memória), sem duplicá-lo.

Requisito: Python com Tkinter (incluído na instalação padrão do Windows).

### Multi-Agent Orchestration

Orquestração **sequencial** de agentes especializados via pipelines YAML — complementa execução single-agent (`plan` / `run` / `review`).

```powershell
python -m pam.main pipeline auratime TASK-0001
python -m pam.main pipeline auratime TASK-0001 --pipeline default_pipeline
python -m pam.main pipeline auratime TASK-0001 --from-step reviewer
```

| Conceito | Descrição |
|----------|-----------|
| Pipeline | Sequência de agentes definida em `ai/pipelines/*.yaml` |
| Execução | Um agente por vez; sem paralelismo |
| Contexto acumulado | Resumo de cada step passa ao próximo |
| Task lifecycle | Status atualizado; `pipeline_history` na metadata JSON |
| Logs | Steps em `ai/runs/pipelines/` + resultado consolidado `.json`/`.md` |

Pipeline padrão (`default_pipeline.yaml`):

```
architect → implementer → reviewer → test_writer → docs_writer → release_manager
```

Comandos single-agent continuam disponíveis e inalterados.

### Provider Settings

Chaves ficam **apenas no `.env` local** (gitignored). Nunca são salvas em JSON no repositório nem exibidas por completo em log ou GUI.

**Mascaramento:** `sk-...abcd`, `AIza...WXYZ` (prefixo + sufixo).

**CLI:**

```powershell
python -m pam.main settings
python -m pam.main set-key cursor
python -m pam.main set-key gemini
python -m pam.main set-key openai
python -m pam.main set-key anthropic
```

`set-key` usa entrada oculta (`getpass`) e confirma apenas o valor mascarado.

**GUI:** `python -m pam.main gui` → aba **Configurações** — status por provider e botões *Inserir/Atualizar chave* com campo password.

| Provider | Variável | Uso no PAM |
|----------|----------|------------|
| Cursor | `CURSOR_API_KEY` | `plan`, `run`, `review`, `pipeline` |
| Gemini | `GEMINI_API_KEY` | `ai-summary`, `ai-tasks`, `ai-docs` |
| OpenAI | `OPENAI_API_KEY` | reservado (futuro) |
| Anthropic | `ANTHROPIC_API_KEY` | reservado (futuro) |

`.env.example` contém apenas placeholders — copie para `.env` e use `set-key`.

### Multi-Provider Runtime

O PAM usa **dois runtimes complementares** — Gemini não substitui Cursor.

| Provider | Uso | Comandos |
|----------|-----|----------|
| **Cursor SDK** | Edição real de código, refactors, sessões persistentes, pipelines completos | `plan`, `run`, `review`, `resume`, `pipeline` |
| **Gemini** | Análise leve, sumarização, sugestão de tasks, rascunho de docs | `ai-summary`, `ai-tasks`, `ai-docs` |

Roteamento (`provider_router.py`):

| Tipo de tarefa | Provider |
|----------------|----------|
| `analysis`, `summarize`, `docs`, `roadmap`, `tasks` | Gemini |
| `code_edit`, `refactor`, `deep_agent`, `plan`, `run`, `review` | Cursor |

### Agent Runtime Profiles

Cada agente especializado pode usar **provider e modelo diferentes** — pipelines híbridos com otimização de custo e performance.

Configuração em `ai/runtime_profiles/default_profiles.yaml`:

```yaml
architect:
  provider: gemini
  model: gemini-2.5-pro

implementer:
  provider: cursor
  mode: deep_agent

reviewer:
  provider: gemini
  model: gemini-2.5-flash
```

| Conceito | Descrição |
|----------|-----------|
| **Agentes híbridos** | Um pipeline pode misturar Cursor (código) e Gemini (análise/docs) |
| **Providers diferentes** | `architect` e `reviewer` no Gemini; `implementer` no Cursor |
| **Custo / performance** | Modelos flash para steps leves; pro apenas onde necessário |
| **Runtime configurável** | YAML editável sem alterar código; GUI mostra profiles (somente leitura) |

Resolução (`runtime_profiles.py` + `provider_router.route_agent`):

- Profile definido no YAML → provider/model/mode do agente
- Profile ausente → **fallback Cursor** (comportamento legado)
- Provider indisponível → mensagem amigável; demais comandos continuam

Logs de pipeline e `pipeline_history` registram `provider` e `model` por step.

```powershell
python -m pam.main gui   # aba Runtime Profiles
python -m pam.main pipeline auratime TASK-0001
```

Variáveis de ambiente:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash   # opcional, padrão gemini-2.5-flash
```

Sem `GEMINI_API_KEY`, os comandos `ai-*` falham com mensagem amigável — os demais comandos Cursor continuam funcionando.

```powershell
python -m pam.main ai-summary auratime
python -m pam.main ai-tasks auratime -p "Foque em testes e documentação"
python -m pam.main ai-docs nilkplayer
```

### Exemplos

```powershell
python -m pam.main --list-projects
python -m pam.main plan auratime --task ai/tasks/sprint_001_analyze_project.md
python -m pam.main run auratime --task ai/tasks/minha_tarefa.md
python -m pam.main review nilkplayer
python -m pam.main resume auratime -p "Continue a análise"
python -m pam.main clear-session auratime
```

### Observabilidade e Métricas

Fundação de observabilidade local — cada execução gera um evento em `ai/metrics/events_YYYYMM.jsonl` (JSONL mensal).

| Recurso | Descrição |
|---------|-----------|
| **Eventos** | Metadados: projeto, comando, agente, provider, duração, sucesso/falha |
| **Privacidade** | Sem prompts completos nem chaves de API |
| **CLI** | `python -m pam.main metrics` |
| **GUI** | Aba **Observabilidade** no Agentic Workbench |
| **Agregações** | Total, por projeto/provider/agente, duração média, últimas execuções |

```powershell
python -m pam.main metrics
python -m pam.main metrics --project auratime
python -m pam.main metrics --last 10
```

Guia completo: [docs/observability.md](docs/observability.md).

**Limitações (Sprint 13):** armazenamento local apenas; sem custos reais de tokens; sem banco de dados.

### Distribuição Portátil (Sprint 14)

O PAM está preparado para distribuição executável/portátil (`pam.exe` no Windows) via PyInstaller, permitindo demonstrações imediatas e uso sem configuração local de Python.

- **Dual-Path Architecture:** recursos de leitura (agents, prompts, templates) são lidos do bundle empacotado (`bundled_root()`), enquanto configurações e estados graváveis (`.env`, `ai/projects/`, runs, sessions e métricas) são persistidos na pasta do executável (`project_root()`).
- **Sem chaves embutidas:** o executável distribuído nunca contém chaves ou variáveis do desenvolvedor, gerando um `.env` limpo com placeholders no primeiro start.

Guia completo: [docs/portable_build.md](docs/portable_build.md).

## Estrutura

```
project_agent_manager/
├── docs/              # documentação oficial PT-BR
├── protocol/          # OS4AI — especificação reutilizável (Sprint 5.5)
├── ai/
│   ├── context/       # contexto global PAM (+ generated/)
│   ├── memory/        # memória por projeto
│   ├── sessions/      # metadata de sessões agenticas
│   ├── projects/      # YAML por projeto
│   ├── tasks/         # Task Lifecycle (active/completed/blocked/archived)
│   ├── prompts/       # templates plan, run, review
│   ├── agents/        # definições de agentes especializados
│   ├── runtime_profiles/  # provider/model por agente (YAML)
│   ├── pipelines/     # pipelines multi-agente (YAML)
│   ├── metrics/       # eventos JSONL de observabilidade
│   ├── observability/ # reservado para agregações futuras
│   └── runs/          # logs de execução (local, incl. pipelines/)
├── src/pam/
│   ├── main.py
│   ├── config_loader.py
│   ├── cursor_runner.py
│   ├── metrics_store.py
│   ├── observability_service.py
│   ├── context_engine.py
│   ├── context_builder.py
│   ├── session_store.py
│   ├── agent_registry.py
│   ├── task_manager.py
│   ├── pipeline_engine.py
│   ├── pipeline_result.py
│   ├── runtime_profiles.py
│   ├── project_bootstrap.py
│   ├── template_engine.py
│   ├── gui_launcher.py
│   ├── ai_service.py
│   ├── settings_manager.py
│   ├── providers/
│   ├── templates/
│   └── models.py
└── README.md
```

Detalhes de arquitetura: [docs/architecture.md](docs/architecture.md) · `ai/context/ARCHITECTURE.md`

## AI Engineering Protocol

O PAM define o **Operating System for AI Development (OS4AI)** — um protocolo oficial de engenharia agêntica em `protocol/`.

| Documento | Conteúdo |
|-----------|----------|
| [OPERATING_SYSTEM_FOR_AI_DEVELOPMENT.md](protocol/OPERATING_SYSTEM_FOR_AI_DEVELOPMENT.md) | Visão geral e princípios |
| [AGENT_RULES.md](protocol/AGENT_RULES.md) | Papéis, limites e colaboração |
| [TASK_LIFECYCLE.md](protocol/TASK_LIFECYCLE.md) | Status, transições e metadata |
| [PROJECT_BOOTSTRAP.md](protocol/PROJECT_BOOTSTRAP.md) | Onboarding de novos projetos |
| [DEVELOPMENT_PHILOSOPHY.md](protocol/DEVELOPMENT_PHILOSOPHY.md) | Princípios de engenharia |
| [CONTEXT_INJECTION.md](protocol/CONTEXT_INJECTION.md) | Montagem de contexto |
| [ARCHITECTURE_GUIDELINES.md](protocol/ARCHITECTURE_GUIDELINES.md) | Modularidade e padrões |

**Reutilização:** o protocolo pode ser copiado para qualquer repositório. Qualquer chat, agente ou orquestrador pode seguir as mesmas regras — basta adotar a estrutura `ai/` e os documentos em `protocol/`.

**Agnosticismo:** o PAM implementa o protocolo com [Cursor Python SDK](https://cursor.com/docs/sdk/python), mas OS4AI não depende de Cursor, do PAM ou de qualquer vendor específico. A especificação vive em Markdown; a ferramenta é substituível.

## Projetos configurados

| Projeto    | Repositório                      |
|------------|----------------------------------|
| AuraTime   | `C:\src\projects\auratime`       |
| Nilkplayer | `C:\src\projects\Nilkplayer`     |

## Licença

Uso interno — projetos Franklin.

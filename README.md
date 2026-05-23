# Project Agent Manager (PAM)

## Operating System for AI Development

O **Project Agent Manager** é um controlador Python para orquestrar agentes do [Cursor Python SDK](https://cursor.com/docs/sdk/python) em projetos reais — com planejamento, execução, revisão, memória, contexto, rastreabilidade e sprints pequenas.

Não é só um CLI de prompts: é a camada que organiza **como** agentes trabalham nos seus repositórios (AuraTime, Nilkplayer e outros).

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

## Requisitos

- Python 3.11+
- Chave de API Cursor (`CURSOR_API_KEY`)
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
```

Obtenha a chave em [Cursor Dashboard → Integrations](https://cursor.com/dashboard/integrations).

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

### Exemplos

```powershell
python -m pam.main --list-projects
python -m pam.main plan auratime --task ai/tasks/sprint_001_analyze_project.md
python -m pam.main run auratime --task ai/tasks/minha_tarefa.md
python -m pam.main review nilkplayer
python -m pam.main resume auratime -p "Continue a análise"
python -m pam.main clear-session auratime
```

## Estrutura

```
project_agent_manager/
├── protocol/          # OS4AI — especificação reutilizável (Sprint 5.5)
├── ai/
│   ├── context/       # contexto global PAM
│   ├── memory/        # memória por projeto
│   ├── sessions/      # metadata de sessões agenticas
│   ├── projects/      # YAML por projeto
│   ├── tasks/         # Task Lifecycle (active/completed/blocked/archived)
│   ├── prompts/       # templates plan, run, review
│   ├── agents/        # definições de agentes especializados
│   └── runs/          # logs de execução (local)
├── src/pam/
│   ├── main.py
│   ├── config_loader.py
│   ├── cursor_runner.py
│   ├── context_engine.py
│   ├── session_store.py
│   ├── agent_registry.py
│   ├── task_manager.py
│   ├── project_bootstrap.py
│   ├── template_engine.py
│   ├── templates/
│   └── models.py
└── README.md
```

Detalhes de arquitetura: `ai/context/ARCHITECTURE.md`.

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

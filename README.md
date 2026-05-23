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
| `clear-session` | — | Remove metadata de sessão (preserva `ai/runs/`) |

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
├── ai/
│   ├── context/       # contexto global PAM
│   ├── memory/        # memória por projeto
│   ├── sessions/      # metadata de sessões agenticas
│   ├── projects/      # YAML por projeto
│   ├── tasks/         # tarefas Markdown
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
│   └── models.py
└── README.md
```

Detalhes de arquitetura: `ai/context/ARCHITECTURE.md`.

## Projetos configurados

| Projeto    | Repositório                      |
|------------|----------------------------------|
| AuraTime   | `C:\src\projects\auratime`       |
| Nilkplayer | `C:\src\projects\Nilkplayer`     |

## Licença

Uso interno — projetos Franklin.

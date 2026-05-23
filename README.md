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
| **Sessões** | `ai/sessions/` — metadata de agentes (base Sprint 2) |
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
| `resume` | — | Localiza sessão salva (stub; execução na Sprint 3) |

O **Context Engine** injeta automaticamente `ai/context/` e `ai/memory/<projeto>/` no início de cada prompt.

### Exemplos

```powershell
python -m pam.main --list-projects
python -m pam.main plan auratime --task ai/tasks/sprint_001_analyze_project.md
python -m pam.main run auratime --task ai/tasks/minha_tarefa.md
python -m pam.main review nilkplayer
python -m pam.main resume auratime
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
│   └── runs/          # logs de execução (local)
├── src/pam/
│   ├── main.py
│   ├── config_loader.py
│   ├── cursor_runner.py
│   ├── context_engine.py
│   ├── session_store.py
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

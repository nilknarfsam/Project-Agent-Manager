# Project Agent Manager (PAM)

Controlador agentico central para os projetos do Franklin, usando o [Cursor Python SDK](https://cursor.com/docs/sdk/python).

O PAM orquestra fluxos agenticos (planejar, executar e revisar) em repositórios como **AuraTime** e **Nilkplayer**, mantendo configurações, tarefas e histórico de execuções em uma estrutura modular.

## Objetivo

Este projeto é o hub que:

- Carrega configurações por projeto (YAML em `ai/projects/`)
- Dispara agentes Cursor locais via `cursor-sdk`
- Organiza prompts, tarefas e logs em `ai/`
- Expõe uma CLI simples para automação local

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

## Configuração da API key

1. Copie `.env.example` para `.env`
2. Cole sua `CURSOR_API_KEY` no `.env`
3. O PAM carrega automaticamente via `python-dotenv` ao iniciar a CLI

Alternativa sem arquivo: defina a variável no shell:

```powershell
$env:CURSOR_API_KEY = "sua-chave"
```

## Uso

Defina `PYTHONPATH` para incluir `src` e execute a CLI:

```powershell
$env:PYTHONPATH = "src"
python -m pam.main --list-projects
```

### Fluxo plan / run / review

| Comando | Modo SDK | Comportamento |
|---------|----------|---------------|
| `plan`  | `plan`   | Análise e planejamento — o agente não deve alterar arquivos |
| `run`   | `agent`  | Execução da tarefa com permissão para editar o repositório |
| `review`| `agent`  | Revisão de código/estado com prompt dedicado de review |

Cada execução grava logs em `ai/runs/` (`.md` legível + `.json` estruturado), com timestamp no nome do arquivo.

### Exemplos

Listar projetos:

```powershell
python -m pam.main --list-projects
```

Planejar com tarefa em arquivo:

```powershell
python -m pam.main plan auratime --task ai/tasks/sprint_001_analyze_project.md
```

Executar uma tarefa:

```powershell
python -m pam.main run auratime --task ai/tasks/minha_tarefa.md
```

Revisar o repositório:

```powershell
python -m pam.main review nilkplayer
```

Instruções extras no prompt:

```powershell
python -m pam.main plan auratime --task ai/tasks/sprint_001_analyze_project.md -p "Foque em testes e CI"
```

## Estrutura

```
project_agent_manager/
├── ai/
│   ├── projects/    # YAML por projeto (auratime, nilkplayer, ...)
│   ├── tasks/       # tarefas em Markdown
│   ├── prompts/     # templates plan, run, review
│   └── runs/        # logs de execução (ignorados no git)
├── src/pam/
│   ├── main.py           # CLI (argparse)
│   ├── config_loader.py  # leitura dos YAMLs
│   ├── cursor_runner.py  # integração com cursor-sdk
│   └── models.py         # dataclasses compartilhadas
├── requirements.txt
├── .env.example
├── CHANGELOG.md
└── README.md
```

## Projetos configurados

| Projeto    | Repositório                      |
|------------|----------------------------------|
| AuraTime   | `C:\src\projects\auratime`       |
| Nilkplayer | `C:\src\projects\Nilkplayer`     |

Novos projetos: crie `ai/projects/<nome>.yaml` com `name`, `repo_path`, `default_runtime`, `default_model` e `description`.

## Licença

Uso interno — projetos Franklin.

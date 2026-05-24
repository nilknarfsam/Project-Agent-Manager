# Onboarding de projetos

Guia para integrar projetos existentes ou criar novos com a estrutura **OS4AI** (Operating System for AI Development).

## O que é onboarding?

Onboarding é o processo de preparar um repositório para trabalhar com o PAM:

- Criar pastas `ai/` (context, memory, tasks, sessions, …)
- Copiar protocolo, agentes e prompts
- Registrar o projeto em `ai/projects/<nome>.yaml` no PAM
- Gerar documentação inicial

## Onboard de projeto existente

Para repositórios que **já existem** no disco:

```powershell
$env:PYTHONPATH = "src"
python -m pam.main onboard "C:\src\projects\meu-app"
```

### Opções

| Flag | Efeito |
|------|--------|
| `--project-name slug` | Define o nome do projeto (padrão: nome da pasta) |
| `--force` | Sobrescreve templates existentes |

### O que é criado

```text
meu-app/
├── ai/
│   ├── context/       ← ARCHITECTURE, ROADMAP, STACK, …
│   ├── memory/<slug>/ ← DECISIONS, PATTERNS, LEARNINGS
│   ├── tasks/         ← active, completed, blocked, archived
│   ├── sessions/
│   ├── agents/        ← cópia dos agentes PAM
│   └── prompts/       ← plan, run, review
├── protocol/          ← cópia do OS4AI
└── README_PAM.md      ← se README.md já existir
```

### Preservação de conteúdo

Por padrão, arquivos existentes **não são sobrescritos**. Use `--force` apenas quando quiser regenerar templates.

### Via GUI

1. Abra `python -m pam.main gui`
2. Selecione ou informe a pasta na sidebar
3. Marque `--force` se necessário
4. Clique em **Executar onboard**

## Create-project (projeto novo)

Para criar um projeto **PAM-native** do zero (estrutura sem código de app):

```powershell
python -m pam.main create-project python log-analyzer
python -m pam.main create-project flutter auratime
python -m pam.main create-project electron project-manager
python -m pam.main create-project python my-app --path D:\dev\projects
```

### Stacks disponíveis

| Stack | Uso típico |
|-------|------------|
| `python` | APIs, scripts, automação |
| `flutter` | Apps mobile multiplataforma |
| `electron` | Apps desktop com web tech |

O diretório padrão é o pai dos projetos já configurados (ex.: `C:\src\projects`).

## Estrutura OS4AI

Após onboarding, o projeto segue o protocolo OS4AI:

| Pasta | Função |
|-------|--------|
| `ai/context/` | Contexto global do projeto |
| `ai/memory/<projeto>/` | Memória persistente entre sprints |
| `ai/tasks/` | Tarefas com lifecycle |
| `ai/sessions/` | Sessões de agentes |
| `ai/agents/` | Papéis especializados |
| `ai/prompts/` | Templates de comando |
| `protocol/` | Regras e filosofia OS4AI |

## Registro no PAM

O PAM cria `ai/projects/<slug>.yaml` no **repositório do PAM** (não no projeto onboarded):

```yaml
name: meu-app
repo_path: C:\src\projects\meu-app
default_runtime: local
default_model: ...
description: ...
```

Isso permite que `plan`, `run`, `gui`, etc. encontrem o projeto.

## Boas práticas

### Antes do onboard

1. **Commit ou backup** — o onboard cria muitos arquivos
2. **Defina o slug** — nome curto e consistente (`auratime`, não `AuraTime-v2`)
3. **Verifique o caminho** — `repo_path` deve existir no disco

### Depois do onboard

1. **Preencha `ai/context/`** — arquitetura, stack, sprint atual
2. **Execute um `plan`** de teste — valide que o contexto injeta corretamente
3. **Crie a primeira task** — `ai/tasks/active/` ou via `plan --task`
4. **Configure chaves** — Cursor obrigatório; Gemini recomendado

### Para equipes

- Padronize o protocolo em todos os repos
- Use o mesmo conjunto de agentes (`ai/agents/`)
- Documente decisões em `ai/memory/<projeto>/DECISIONS.md`
- Revise `CURRENT_SPRINT.md` a cada sprint

## Problemas comuns

| Problema | Solução |
|----------|---------|
| Projeto não aparece em `--list-projects` | Verifique `ai/projects/<slug>.yaml` no PAM |
| `repo_path` inválido | Corrija o caminho no YAML |
| Templates duplicados | Use `--force` com cuidado ou limpe manualmente |
| README sobrescrito | Sem `--force`, o PAM cria `README_PAM.md` |

## Próximo passo

- [Primeiros passos](getting_started.md)
- [Instalação](installation.md)
- [Ciclo de vida de tasks](tasks_lifecycle.md)

# Primeiros passos

Bem-vindo ao **Project Agent Manager (PAM)** — o sistema que organiza como agentes de IA trabalham nos seus projetos de software.

## O que é o PAM?

O PAM é um **controlador Python** para orquestrar agentes especializados em repositórios reais. Ele não substitui o Cursor, o Gemini ou qualquer IDE: ele **coordena** planejamento, execução, revisão, memória, contexto e rastreabilidade.

Pense no PAM como a **camada operacional** entre você (arquiteto ou desenvolvedor) e os agentes de IA.

## Operating System for AI Development (OS4AI)

O PAM implementa o conceito de **Sistema Operacional para Desenvolvimento com IA**:

| Analogia | No PAM |
|----------|--------|
| Processos | Agentes especializados (`architect`, `implementer`, `reviewer`, …) |
| Memória | `ai/memory/<projeto>/` — decisões, padrões, aprendizados |
| Contexto | `ai/context/` — arquitetura, roadmap, sprint atual |
| Tarefas | `ai/tasks/` — lifecycle com `TASK-XXXX` |
| Logs | `ai/runs/` — rastreabilidade de cada execução |
| Sessões | `ai/sessions/` — retomada de conversas com agentes |

O protocolo completo está em `protocol/` e pode ser adotado em qualquer repositório, independentemente da ferramenta de IA.

## Filosofia do sistema

1. **Sprints pequenas** — entregas rastreáveis, uma de cada vez.
2. **Agentes com papéis claros** — cada um faz uma coisa bem feita.
3. **Contexto explícito** — nada de “memória mágica”; tudo documentado em arquivos.
4. **Rastreabilidade** — cada execução gera log; cada task tem histórico.
5. **Modularidade** — CLI, GUI, providers e pipelines são camadas separadas.
6. **Pragmatismo** — Cursor para código; Gemini para análise leve; híbrido quando fizer sentido.

## Visão geral

```
Você (arquiteto)
       │
       ▼
   PAM (CLI ou GUI)
       │
       ├── Context Engine ──► ai/context + ai/memory
       ├── Task Manager ────► TASK-XXXX + lifecycle
       ├── Agent Registry ──► ai/agents/
       ├── Providers ───────► Cursor / Gemini / …
       └── Pipeline Engine ─► multi-agente sequencial
       │
       ▼
   Repositório do projeto
```

## Agentic Workbench for Software Architects

A interface gráfica (GUI) do PAM foi pensada como um **Agentic Workbench** — um painel de trabalho para arquitetos de software, não uma IDE completa. Você seleciona projetos, monta contexto, escolhe agentes e acompanha logs — sem editar código dentro do PAM.

## Primeiros passos

### 1. Instalar

Siga o guia [Instalação](installation.md).

### 2. Configurar chaves

Configure `CURSOR_API_KEY` (obrigatória para plan/run/review) e, opcionalmente, `GEMINI_API_KEY`.

### 3. Cadastrar ou integrar um projeto

- Projeto existente: `python -m pam.main onboard C:\caminho\do\projeto`
- Projeto novo: `python -m pam.main create-project python meu-app`

### 4. Executar o fluxo básico

```powershell
$env:PYTHONPATH = "src"
python -m pam.main plan meu-projeto --task ai/tasks/minha_tarefa.md
python -m pam.main run meu-projeto --task TASK-0001
python -m pam.main review meu-projeto --task TASK-0001
```

### 5. Abrir a GUI (opcional)

```powershell
python -m pam.main gui
```

## Fluxo básico: ideia → sprint → agente → revisão

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│  Ideia  │───►│ Sprint  │───►│  Agente  │───►│ Revisão  │
│         │    │ (task)  │    │ (plan/   │    │ (review) │
│         │    │         │    │  run)    │    │          │
└─────────┘    └─────────┘    └──────────┘    └──────────┘
     │              │              │               │
     ▼              ▼              ▼               ▼
  Documento    TASK-XXXX      ai/runs/        status: done
  em Markdown  planned →      log salvo       memória
               running →
               reviewed
```

1. **Ideia** — descreva o objetivo em um arquivo Markdown (`ai/tasks/` ou legado).
2. **Sprint / Task** — o PAM cria `TASK-XXXX` com status e histórico.
3. **Agente** — `plan` analisa; `run` implementa; agente especializado conforme o comando.
4. **Revisão** — `review` valida qualidade; task vai para `done`.

## Próximos guias

| Guia | Conteúdo |
|------|----------|
| [Instalação](installation.md) | Python, venv, chaves, problemas comuns |
| [GUI Workbench](gui_workbench.md) | Interface gráfica completa |
| [Onboarding](onboarding.md) | Integrar projetos ao OS4AI |
| [FAQ](faq.md) | Perguntas frequentes |

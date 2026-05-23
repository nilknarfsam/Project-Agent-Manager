# Arquitetura — Project Agent Manager

## Posicionamento

O **Project Agent Manager (PAM)** é um **Operating System for AI Development**: um sistema operacional agentico para desenvolvimento com IA.

Não é apenas um wrapper de API. É a camada que organiza como agentes trabalham em projetos reais — com contexto, memória, sessões e rastreabilidade.

## Camadas

```
┌─────────────────────────────────────────┐
│  CLI (pam.main)                         │  ← camada de controle
│  plan · run · review · resume           │
├─────────────────────────────────────────┤
│  PAM Core                               │
│  context_engine · session_store         │
│  cursor_runner · config_loader          │
├─────────────────────────────────────────┤
│  Cursor Python SDK                      │  ← motor agentico
│  Agent · Agent.resume · LocalAgent      │
├─────────────────────────────────────────┤
│  Repositórios dos projetos              │  ← workspace real
│  (auratime, nilkplayer, …)              │
└─────────────────────────────────────────┘
```

## Diretórios `ai/`

| Diretório | Função |
|-----------|--------|
| `ai/context/` | Contexto global do PAM — arquitetura, roadmap, sprint atual, stack, issues |
| `ai/memory/<projeto>/` | Memória por projeto — decisões, padrões, aprendizados |
| `ai/sessions/` | Histórico e metadata de agentes (`agent_id`, runs, modo, tarefa) |
| `ai/projects/` | Configuração YAML por projeto |
| `ai/tasks/` | Tarefas em Markdown para plan/run/review |
| `ai/prompts/` | Templates de prompt por comando |
| `ai/runs/` | Logs de execução (artefatos locais) |

## Fluxo de uma execução

1. CLI carrega projeto (`ai/projects/<nome>.yaml`).
2. **Context Engine** monta bloco com `ai/context/` + `ai/memory/<projeto>/`.
3. Prompt = contexto + template + tarefa opcional.
4. **Cursor Runner** envia ao SDK (`plan` ou `agent`).
5. Resultado em `ai/runs/`; metadata de sessão em `ai/sessions/` (Sprint 2+).
6. Futuro: `resume` retoma via `Agent.resume(agent_id)`.

## Princípios

- Sprints pequenas e rastreáveis.
- Sem UI na fase inicial — CLI primeiro.
- Secrets fora do repositório (`.env`, `.gitignore`).
- Compatibilidade: comandos existentes não quebram ao evoluir sessões.

# Project Bootstrap — Onboarding de projetos

Guia para adotar o protocolo OS4AI em um repositório novo ou existente.

---

## 1. Objetivo

Permitir que **qualquer projeto** — com ou sem PAM — opere com o mesmo padrão de contexto, memória, tasks, sessões e agentes.

---

## 2. Pré-requisitos

- Repositório Git inicializado
- `.gitignore` configurado (`.env`, `.venv`, artefatos locais)
- Decisão sobre idioma principal da documentação (`ai/context/`)

---

## 3. Estrutura padrão

Criar na raiz do repositório (ou no monorepo do pacote):

```
<projeto>/
├── ai/
│   ├── context/           # contexto global do projeto
│   │   ├── ARCHITECTURE.md
│   │   ├── ROADMAP.md
│   │   ├── CURRENT_SPRINT.md
│   │   ├── KNOWN_ISSUES.md
│   │   └── STACK.md
│   ├── memory/
│   │   └── <projeto>/     # ou nome curto do pacote
│   │       ├── DECISIONS.md
│   │       ├── PATTERNS.md
│   │       └── LEARNINGS.md
│   ├── tasks/
│   │   ├── active/
│   │   ├── completed/
│   │   ├── blocked/
│   │   └── archived/
│   ├── sessions/          # metadata JSON (geralmente gitignored)
│   ├── agents/            # definições de papéis (opcional: copiar do PAM)
│   ├── prompts/           # templates plan/run/review (opcional)
│   ├── projects/          # YAML de config (se usar PAM)
│   └── runs/              # logs locais (gitignored)
├── protocol/              # opcional: cópia dos docs OS4AI
├── README.md
├── CHANGELOG.md
└── ...
```

---

## 4. ai/context/

Contexto **global e estável** do projeto. Arquivos recomendados:

| Arquivo | Conteúdo |
|---------|----------|
| `ARCHITECTURE.md` | Camadas, módulos, fluxos principais |
| `ROADMAP.md` | Fases, sprints futuras, visão |
| `CURRENT_SPRINT.md` | Sprint ativa, entregas, critérios de aceite |
| `KNOWN_ISSUES.md` | Bugs conhecidos, limitações, débitos |
| `STACK.md` | Linguagens, frameworks, versões |

**Regras:**

- Atualizar `CURRENT_SPRINT.md` a cada sprint.
- Não duplicar conteúdo de memória — contexto = “estado do sistema”; memória = “decisões ao longo do tempo”.

---

## 5. ai/memory/

Memória **por projeto ou submódulo**:

| Arquivo | Conteúdo |
|---------|----------|
| `DECISIONS.md` | ADRs leves — o que foi decidido e por quê |
| `PATTERNS.md` | Convenções de código adotadas |
| `LEARNINGS.md` | Retrospectivas, incidentes, lições |

**Regras:**

- Append ou seções datadas — preservar histórico.
- Agentes leem no início de cada execução (via Context Engine ou manualmente).

---

## 6. ai/tasks/

Sistema de tasks conforme [TASK_LIFECYCLE.md](./TASK_LIFECYCLE.md).

Bootstrap mínimo:

```powershell
mkdir ai\tasks\active, ai\tasks\completed, ai\tasks\blocked, ai\tasks\archived
```

Primeira task sugerida: análise inicial (`plan`) documentada como `TASK-0001`.

---

## 7. ai/sessions/

Armazena metadata para retomada de agentes:

```json
{
  "project": "meu_projeto",
  "agent_id": "...",
  "agent_name": "architect",
  "mode": "plan",
  "task": "TASK-0001",
  "created_at": "...",
  "updated_at": "..."
}
```

**Recomendação:** adicionar `ai/sessions/*.json` ao `.gitignore` — IDs de sessão são locais e efêmeros.

---

## 8. ai/agents/

Copiar definições do PAM ou criar papéis customizados:

```
ai/agents/
├── architect.md
├── implementer.md
├── reviewer.md
├── test_writer.md
├── docs_writer.md
└── release_manager.md
```

Cada arquivo: nome, responsabilidade, limites, estilo, critérios, quando atuar.

Referência normativa: [AGENT_RULES.md](./AGENT_RULES.md).

---

## 9. README.md

Seções mínimas recomendadas:

1. **O que é o projeto**
2. **Requisitos e instalação**
3. **Uso / comandos**
4. **Estrutura `ai/`** — link para protocolo
5. **AI Engineering Protocol** — menção ao OS4AI (ver README do PAM)

---

## 10. CHANGELOG.md

Seguir [Keep a Changelog](https://keepachangelog.com/):

- Versões semver
- Seções Added / Changed / Fixed / Removed
- Entradas por sprint quando aplicável

---

## 11. ROADMAP

Pode viver em `ai/context/ROADMAP.md` (preferido no protocolo) ou `ROADMAP.md` na raiz para visibilidade pública.

Conteúdo: fases, sprints concluídas e planejadas, dependências entre entregas.

---

## 12. Integração com PAM

1. Clonar ou referenciar `project_agent_manager`.
2. Criar `ai/projects/<nome>.yaml` apontando para o path do repositório:

```yaml
name: meu_projeto
path: C:\src\projects\meu_projeto
description: Descrição curta
```

3. Configurar `CURSOR_API_KEY` no `.env` do PAM.
4. Executar:

```powershell
python -m pam.main plan meu_projeto --agent architect --task ai/tasks/minha_primeira_task.md
```

---

## 13. Bootstrap sem PAM (chat manual)

1. Criar estrutura `ai/` conforme seções acima.
2. Copiar `protocol/` para o repositório ou linkar este repositório.
3. Em cada chat/sessão, colar:
   - Conteúdo relevante de `ai/context/`
   - Memória do projeto
   - Definição do agente (`ai/agents/<papel>.md`)
   - Task atual (`ai/tasks/...`)
4. Atualizar tasks e memória manualmente após cada entrega.

---

## 14. Boas práticas de onboarding

| Prática | Detalhe |
|---------|---------|
| Sprint zero | Primeira sprint = bootstrap + análise (`architect`) |
| Tasks pequenas | Primeiras 3 tasks devem caber em uma sessão cada |
| Memória desde o dia 1 | Registrar primeira decisão em `DECISIONS.md` |
| Não commitar runs/sessions | Apenas código, docs e tasks versionadas |
| Protocolo visível | Link `protocol/` no README |
| Idioma consistente | PT ou EN em todo `ai/context/` |

---

## 15. Checklist de bootstrap

```
[ ] Estrutura ai/ criada
[ ] ai/context/ preenchido (mínimo ARCHITECTURE + CURRENT_SPRINT)
[ ] ai/memory/<projeto>/ inicializado
[ ] ai/tasks/ com subpastas
[ ] ai/agents/ (cópia ou custom)
[ ] README com seção de protocolo
[ ] CHANGELOG iniciado
[ ] .gitignore para .env, sessions, runs
[ ] Primeira task TASK-0001 ou equivalente
[ ] (Opcional) YAML em ai/projects/ para PAM
```

---

## 16. Evolução

Após bootstrap:

1. Executar sprint 1 via `plan` → `run` → `review`.
2. Atualizar memória e CHANGELOG.
3. Marcar sprint concluída em `CURRENT_SPRINT.md`.
4. Repetir com escopo incremental.

Este documento é o ponto de entrada para novos projetos no ecossistema OS4AI / PAM.

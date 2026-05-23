# Operating System for AI Development

**Protocolo oficial de engenharia agêntica do Project Agent Manager (PAM)**

Versão do protocolo: **0.6.5** (Sprint 5.5)  
Status: **fundacional** — reutilizável em qualquer projeto, chat ou agente

---

## 1. Visão geral

O **Operating System for AI Development (OS4AI)** é um conjunto de convenções, estruturas e fluxos que transformam desenvolvimento assistido por IA em um processo **previsível, rastreável e colaborativo**.

Não é uma ferramenta específica. É o **sistema operacional conceitual** sobre o qual ferramentas (como o PAM com Cursor SDK) executam agentes especializados em repositórios reais.

### O que o protocolo resolve

| Problema comum | Resposta do protocolo |
|----------------|----------------------|
| Contexto perdido entre chats | Persistência em `ai/context/`, `ai/memory/` e sessões |
| Agentes sem papel definido | Agentes especializados com limites claros |
| Tarefas sem rastreio | Task Lifecycle com ID, status e histórico |
| Mudanças grandes e arriscadas | Sprints pequenas e diffs mínimos |
| Falta de padrão entre projetos | Bootstrap e guidelines reutilizáveis |

### Princípio central

> **IA como sistema colaborativo**, não como atalho isolado. Cada execução deixa rastro; cada decisão pode ser recuperada; cada agente sabe o que fazer — e o que **não** fazer.

---

## 2. Filosofia do PAM

O PAM materializa este protocolo como controlador Python. A filosofia subjacente:

1. **CLI primeiro** — controle explícito antes de UI.
2. **Markdown como contrato** — tarefas, contexto e memória legíveis por humanos e agentes.
3. **Separação plan / run / review** — pensar, executar e validar são fases distintas.
4. **Agnosticismo de runtime** — o protocolo funciona com Cursor SDK, outros SDKs ou chats manuais.
5. **Evolução incremental** — sprints pequenas; compatibilidade retroativa com comandos existentes.

Documento complementar: [DEVELOPMENT_PHILOSOPHY.md](./DEVELOPMENT_PHILOSOPHY.md).

---

## 3. Conceito: Operating System for AI Development

Analogia com um SO tradicional:

| SO tradicional | OS4AI |
|----------------|-------|
| Kernel | Protocolo + Context Engine |
| Processos | Agentes especializados |
| Memória | `ai/memory/<projeto>/` |
| Sistema de arquivos | Estrutura `ai/` padronizada |
| Scheduler | Task Lifecycle + sprints |
| Logs | `ai/runs/`, histórico de tasks |
| Sessões de usuário | `ai/sessions/` + `Agent.resume()` |

O OS4AI **não substitui** Git, CI ou editores. Organiza **como agentes interagem** com o repositório dentro dessas ferramentas.

---

## 4. Arquitetura modular

```
┌──────────────────────────────────────────────────────────┐
│  Camada de controle (CLI / orquestrador)                 │
│  plan · run · review · resume · tasks · agents           │
├───────────────────────────────────────────────────────────│
│  Camada de protocolo (este diretório protocol/)          │
│  regras · lifecycle · bootstrap · guidelines             │
├──────────────────────────────────────────────────────────┤
│  Camada de contexto (Context Engine)                     │
│  ai/context/ · ai/memory/ · ai/agents/ · ai/prompts/   │
├──────────────────────────────────────────────────────────┤
│  Camada de persistência                                  │
│  ai/tasks/ · ai/sessions/ · ai/runs/                     │
├──────────────────────────────────────────────────────────┤
│  Camada de execução (SDK / runtime agêntico)             │
│  Cursor SDK · outros motores compatíveis                 │
├──────────────────────────────────────────────────────────┤
│  Repositório alvo (workspace real do projeto)            │
└──────────────────────────────────────────────────────────┘
```

Cada camada tem responsabilidade única. Mudanças em uma camada não devem quebrar as demais sem versionamento explícito.

Detalhes: [ARCHITECTURE_GUIDELINES.md](./ARCHITECTURE_GUIDELINES.md).

---

## 5. Agentes especializados

Agentes são **papéis operacionais**, não personas genéricas. Cada um possui responsabilidade, limites, critérios de qualidade e momentos de atuação.

| Agente | Papel principal | Comando padrão |
|--------|-----------------|----------------|
| `architect` | Planejamento e arquitetura | `plan` |
| `implementer` | Implementação de código | `run` |
| `reviewer` | Revisão e qualidade | `review` |
| `test_writer` | Testes automatizados | `run` (sob demanda) |
| `docs_writer` | Documentação | `run` (sob demanda) |
| `release_manager` | Checklist de release | `plan` / `run` (sob demanda) |

Definições completas: [AGENT_RULES.md](./AGENT_RULES.md) e `ai/agents/*.md`.

### Colaboração entre agentes

Fluxo recomendado para uma entrega:

```
architect (plan) → implementer (run) → reviewer (review) → docs_writer (opcional) → release_manager (opcional)
```

Handoffs explícitos via tasks (`TASK-XXXX`) e memória do projeto.

---

## 6. Persistência de contexto

Contexto não vive apenas no chat. Vive em arquivos versionáveis:

| Local | Conteúdo |
|-------|----------|
| `ai/context/` | Arquitetura, roadmap, sprint, stack, issues |
| `ai/memory/<projeto>/` | Decisões, padrões, aprendizados |
| `ai/agents/` | Definição de papéis |
| `ai/prompts/` | Templates por comando |

Montagem e prioridade: [CONTEXT_INJECTION.md](./CONTEXT_INJECTION.md).

---

## 7. Lifecycle de tasks

Toda tarefa gerenciada possui identidade (`TASK-XXXX`), metadata JSON, histórico de transições e pasta por estado.

**Status oficiais:** `planned` · `approved` · `running` · `reviewed` · `done` · `blocked` · `cancelled`

Documento completo: [TASK_LIFECYCLE.md](./TASK_LIFECYCLE.md).

---

## 8. Sprints pequenas

Entregas são **incrementais e versionadas**:

- Uma sprint = um objetivo claro, critérios de aceite e escopo limitado.
- Documentada em `ai/context/CURRENT_SPRINT.md` e refletida no `CHANGELOG.md`.
- Preferir várias sprints pequenas a uma mudança monolítica.
- Ao concluir: marcar sprint, atualizar roadmap, registrar aprendizados em memória.

---

## 9. Rastreabilidade

Cada execução deve ser recuperável:

| Artefato | Função |
|----------|--------|
| `ai/runs/` | Log de execução (prompt, modo, agente, timestamp) |
| `ai/sessions/<projeto>.json` | `agent_id` para retomada |
| `ai/tasks/TASK-XXXX.json` | Status, agente, histórico |
| `CHANGELOG.md` | Histórico de versões do sistema/projeto |

Regra: **se não está registrado, não aconteceu** — para fins de auditoria agêntica.

---

## 10. Memória

Memória por projeto em `ai/memory/<projeto>/`:

- **DECISIONS.md** — decisões arquiteturais e trade-offs.
- **PATTERNS.md** — padrões adotados no código.
- **LEARNINGS.md** — lições de sprints e incidentes.

Agentes **leem** memória no início; **escrevem** apenas quando a tarefa pede ou ao fechar sprint.

---

## 11. Sessões

Sessões conectam execuções discretas em uma conversa contínua:

1. `plan`, `run` ou `review` cria/atualiza `ai/sessions/<projeto>.json`.
2. Campo `agent_id` permite `Agent.resume()` (ou equivalente no runtime).
3. `resume` reinjeta contexto atualizado + instrução adicional.
4. `clear-session` remove metadata; `cwd `ai/runs/`.

Sessão ≠ task: uma sessão pode abranger várias tasks; uma task pode ser retomada em sessões diferentes.

---

## 12. Plan / Run / Review

Três modos operacionais obrigatórios:

| Modo | Objetivo | Altera código? | Agente padrão |
|------|----------|------------------|---------------|
| **Plan** | Analisar e planejar | Não | architect |
| **Run** | Implementar tarefa | Sim (escopo da task) | implementer |
| **Review** | Avaliar qualidade | Não (relatório) | reviewer |

Templates em `ai/prompts/plan_prompt.md`, `run_prompt.md`, `review_prompt.md`.

**Nunca pular plan** para mudanças arquiteturais. **Nunca pular review** antes de fechar sprint crítica.

---

## 13. Princípios obrigatórios

Todo agente, chat ou contribuidor que adote este protocolo deve:

1. **Respeitar limites do agente** — architect não implementa; reviewer não faz push.
2. **Manter diffs pequenos** — uma task, um propósito.
3. **Preservar compatibilidade** — não quebrar comandos, paths ou tasks legadas.
4. **Documentar decisões** — memória e CHANGELOG quando relevante.
5. **Usar tasks gerenciadas** — `TASK-XXXX` para trabalho rastreável.
6. **Injetar contexto** — ler `ai/context/` e memória antes de agir.
7. **Registrar execuções** — runs e histórico de status.
8. **Evitar secrets no repo** — `.env`, credenciais fora do Git.
9. **Ser agnóstico de ferramenta** — protocolo > vendor lock-in.
10. **Priorizar clareza** — docs legíveis valem mais que automação prematura.

---

## 14. Documentos do protocolo

| Documento | Conteúdo |
|-----------|----------|
| [OPERATING_SYSTEM_FOR_AI_DEVELOPMENT.md](./OPERATING_SYSTEM_FOR_AI_DEVELOPMENT.md) | Este documento — visão e princípios |
| [AGENT_RULES.md](./AGENT_RULES.md) | Papéis, limites e colaboração |
| [TASK_LIFECYCLE.md](./TASK_LIFECYCLE.md) | Status, transições, metadata |
| [PROJECT_BOOTSTRAP.md](./PROJECT_BOOTSTRAP.md) | Onboarding de novos projetos |
| [DEVELOPMENT_PHILOSOPHY.md](./DEVELOPMENT_PHILOSOPHY.md) | Princípios de engenharia |
| [CONTEXT_INJECTION.md](./CONTEXT_INJECTION.md) | Montagem de contexto |
| [ARCHITECTURE_GUIDELINES.md](./ARCHITECTURE_GUIDELINES.md) | Modularidade e padrões |

---

## 15. Adoção em outros projetos

1. Copie a estrutura `ai/` conforme [PROJECT_BOOTSTRAP.md](./PROJECT_BOOTSTRAP.md).
2. Adote ou adapte os documentos em `protocol/`.
3. Configure seu orquestrador (PAM ou manual) para injetar contexto.
4. Defina agentes em `ai/agents/` — podem ser os padrões do PAM.
5. Execute sprints pequenas com tasks rastreáveis.

O PAM é a **referência de implementação**; o protocolo é a **especificação reutilizável**.

---

## 16. Referência PAM

Implementação de referência: repositório `project_agent_manager`.

- CLI: `python -m pam.main`
- Context Engine: `src/pam/context_engine.py`
- Task Manager: `src/pam/task_manager.py`
- Agent Registry: `src/pam/agent_registry.py`

Para uso operacional imediato, consulte também o [README.md](../README.md) na raiz do projeto.

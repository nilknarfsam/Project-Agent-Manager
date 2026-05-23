# Development Philosophy — Filosofia de desenvolvimento

Princípios orientadores para engenharia agêntica no protocolo OS4AI / PAM.

Estes princípios aplicam-se a **humanos e agentes**. Violá-los aumenta risco, débito técnico e perda de contexto.

---

## 1. Mudanças pequenas

> **Prefira dez commits pequenos a um commit gigante.**

- Cada task deve ter escopo delimitado e critérios de aceite verificáveis.
- Refatorações amplas exigem sprint dedicada e plano do architect.
- Diffs grandes dificultam review, rollback e rastreabilidade.

**Na prática:** se a task cresceu, divida em `TASK-0002`, `TASK-0003`.

---

## 2. Estabilidade

> **Comandos e contratos existentes não quebram silenciosamente.**

- Evolução incremental com compatibilidade retroativa.
- Paths legados (`ai/tasks/sprint_001_*.md`) permanecem válidos.
- Novas features são aditivas; breaking changes exigem versão major e CHANGELOG explícito.

**Na prática:** antes de renomear pastas ou comandos, documente migração.

---

## 3. Arquitetura limpa

> **Cada módulo faz uma coisa; cada camada conhece apenas a adjacent.**

Camadas do OS4AI:

- **Controle** — CLI, orquestração
- **Protocolo** — regras e documentação
- **Contexto** — injeção de memória e docs
- **Persistência** — tasks, sessions, runs
- **Runtime** — SDK agêntico
- **Workspace** — repositório alvo

**Na prática:** lógica de negócio do projeto alvo não vaza para o PAM; o PAM não implementa features do projeto alvo.

---

## 4. Rastreabilidade

> **Se não está registrado, não aconteceu.**

Artefatos de rastreio:

- Tasks com histórico de status
- Logs em `ai/runs/`
- Sessões em `ai/sessions/`
- CHANGELOG e memória de decisões

**Na prática:** ao fechar task, atualizar status; ao decidir arquitetura, registrar em `DECISIONS.md`.

---

## 5. Sem mudanças gigantes

> **Sprints pequenas vencem big bang.**

- Uma sprint = um objetivo mensurável.
- Critérios de aceite claros antes de `run`.
- Entregas parciais são preferíveis a “quase pronto” por semanas.

**Na prática:** `CURRENT_SPRINT.md` cabe em uma página; se não cabe, a sprint é grande demais.

---

## 6. Evitar acoplamento

> **Protocolo agnóstico; implementação substituível.**

- Documentação em `protocol/` não depende de Cursor SDK.
- Context Engine lê arquivos Markdown — qualquer runtime pode fazer o mesmo.
- Agentes são arquivos `.md`, não código proprietário.

**Na prática:** ao integrar nova ferramenta, adapte o runner — não reescreva o protocolo.

---

## 7. Contexto persistente

> **O chat é efêmero; os arquivos são a fonte de verdade.**

- Contexto global: `ai/context/`
- Memória por projeto: `ai/memory/`
- Definições de agente: `ai/agents/`

**Na prática:** nunca confie apenas na janela de contexto do LLM; injete ou leia arquivos.

---

## 8. IA como sistema colaborativo

> **Agentes são papéis em um time, não oráculos solitários.**

- architect planeja; implementer codifica; reviewer valida.
- Humano aprova, desbloqueia e faz deploy.
- Handoffs explícitos via tasks e notas no histórico.

**Na prática:** um chat “faz tudo” é anti-padrão; prefira sequência plan → run → review.

---

## 9. Revisão contínua

> **Review não é luxo — é gate de qualidade.**

- Toda entrega significativa passa por reviewer (humano ou agente).
- Blockers devem ser resolvidos antes de `done`.
- Retrospectiva alimenta `LEARNINGS.md`.

**Na prática:** sprint não fecha sem review e CHANGELOG atualizado quando aplicável.

---

## 10. Resumo dos mandamentos

| # | Princípio | Pergunta de verificação |
|---|-----------|-------------------------|
| 1 | Mudanças pequenas | Esta task cabe em um diff reviewável? |
| 2 | Estabilidade | Quebrei algum comando ou path existente? |
| 3 | Arquitetura limpa | Esta responsabilidade está na camada certa? |
| 4 | Rastreabilidade | Status, run e decisão estão registrados? |
| 5 | Sem big bang | Posso entregar valor parcial hoje? |
| 6 | Baixo acoplamento | O protocolo ainda funciona sem esta ferramenta? |
| 7 | Contexto persistente | Li e atualizei os arquivos certos? |
| 8 | Colaboração | O próximo agente sabe o que fazer? |
| 9 | Revisão contínua | Passou por review antes de done? |

---

## 11. Relação com outros documentos

- Visão operacional: [OPERATING_SYSTEM_FOR_AI_DEVELOPMENT.md](./OPERATING_SYSTEM_FOR_AI_DEVELOPMENT.md)
- Regras de agentes: [AGENT_RULES.md](./AGENT_RULES.md)
- Padrões técnicos: [ARCHITECTURE_GUIDELINES.md](./ARCHITECTURE_GUIDELINES.md)

Esta filosofia é **normativa**. Desvios devem ser conscientes, documentados e temporários.

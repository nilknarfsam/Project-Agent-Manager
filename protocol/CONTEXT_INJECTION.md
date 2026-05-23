# Context Injection — Montagem e prioridade de contexto

Especificação de como o contexto é consolidado e injetado em prompts agênticos no protocolo OS4AI / PAM.

---

## 1. Objetivo

Garantir que cada execução (`plan`, `run`, `review`, `resume`) receba **informação suficiente e ordenada** para decisões corretas — sem depender da memória efêmera do chat.

---

## 2. Fontes de contexto

| Fonte | Path | Escopo |
|-------|------|--------|
| Contexto global | `ai/context/*.md` | Projeto/sistema inteiro |
| Memória do projeto | `ai/memory/<projeto>/*.md` | Decisões e padrões locais |
| Definição do agente | `ai/agents/<agente>.md` | Papel e limites |
| Template de comando | `ai/prompts/<modo>_prompt.md` | Instruções do modo |
| Tarefa | `ai/tasks/...` ou `TASK-XXXX.md` | Escopo da execução |
| Instrução adicional | CLI `-p` / prompt do usuário | Complemento pontual |

---

## 3. Ordem de montagem (prioridade)

Do **mais estável** ao **mais específico**:

```
1. Contexto global PAM/projeto     (ai/context/)
2. Memória do projeto              (ai/memory/<projeto>/)
3. Definição do agente             (ai/agents/<agente>.md)
4. Template do comando             (ai/prompts/plan|run|review_prompt.md)
5. Corpo da tarefa                 (ai/tasks/TASK-XXXX.md ou legado)
6. Instrução adicional do usuário  (-p ou mensagem)
```

**Regra de conflito:** níveis mais específicos **não invalidam** níveis inferiores, mas **refinam** o escopo. Se a tarefa contradiz memória, o agente deve **sinalizar conflito** em vez de ignorar silenciosamente.

---

## 4. Context Engine (implementação PAM)

Módulo: `src/pam/context_engine.py`

### Arquivos globais lidos (ordem fixa)

1. `ARCHITECTURE.md`
2. `ROADMAP.md`
3. `CURRENT_SPRINT.md`
4. `KNOWN_ISSUES.md`
5. `STACK.md`

### Arquivos de memória por projeto (ordem fixa)

1. `DECISIONS.md`
2. `PATTERNS.md`
3. `LEARNINGS.md`

### Formato de saída

Bloco Markdown consolidado:

```markdown
# Contexto consolidado (Project Agent Manager)

## Contexto PAM (global)

### Global — Arquitetura (PAM)
...

## Memória do projeto (auratime)

### auratime — Decisões
...
```

Arquivos ausentes ou vazios são **omitidos** — não geram erro.

---

## 5. Injeção do agente

Após o bloco de contexto, o **Agent Registry** carrega `ai/agents/<agente>.md`.

Ordem no prompt final (PAM):

```
[Contexto consolidado]
[Definição do agente]
[Template plan/run/review]
[Tarefa]
[Instrução -p opcional]
```

Isso garante que limites do agente (ex.: “não alterar arquivos” no architect) estejam presentes **antes** da tarefa executável.

---

## 6. Memória — leitura vs escrita

| Operação | Quem | Quando |
|----------|------|--------|
| **Leitura** | Context Engine (automático) | Toda execução |
| **Escrita** | Agente ou humano | Fechamento de sprint, ADR, aprendizado |

Agentes **não devem** reescrever memória inteira — append em seções datadas ou bullets.

---

## 7. Tasks no contexto

Tasks fornecem **escopo imediato**:

- Título, objetivo, critérios de aceite
- Referências a arquivos ou módulos
- Restrições (“não alterar lógica principal”)

Resolução de path:

- `TASK-0001` → busca em `ai/tasks/{active,completed,blocked,archived}/`
- Caminho relativo legado → usado diretamente

Metadata JSON (`TASK-0001.json`) **não** é injetada por padrão no prompt — o `.md` é o contrato humano; o JSON é para o Task Manager.

---

## 8. Prompts (templates)

Templates em `ai/prompts/`:

| Arquivo | Modo | Comportamento esperado |
|---------|------|------------------------|
| `plan_prompt.md` | plan | Análise sem editar arquivos |
| `run_prompt.md` | run | Implementação no escopo |
| `review_prompt.md` | review | Relatório sem alterações |

Templates são **curtos e estáveis**. Detalhes de sprint vivem em `CURRENT_SPRINT.md`, não no template.

---

## 9. Sessões e retomada

`resume` reinjeta contexto **atualizado** (contexto + memória podem ter mudado desde a sessão anterior) e envia ao `agent_id` salvo.

Metadata em `ai/sessions/<projeto>.json`:

- `agent_id` — continuidade conversacional
- `agent_name` — papel para fallback de definição
- `task`, `mode` — última execução

Contexto da sessão anterior **não** substitui arquivos — arquivos prevalecem.

---

## 10. Prioridade explícita (resumo)

| Prioridade | Elemento | Motivo |
|------------|----------|--------|
| Alta | Limites do agente | Segurança operacional |
| Alta | KNOWN_ISSUES, DECISIONS | Evitar regressões |
| Média | CURRENT_SPRINT, task | Escopo atual |
| Média | PATTERNS, STACK | Consistência técnica |
| Baixa | ROADMAP, LEARNINGS | Orientação de longo prazo |
| Variável | `-p` usuário | Override pontual — usar com cuidado |

---

## 11. Implementação manual (sem PAM)

Em chat ou outro IDE:

1. Colar seções relevantes de `ai/context/` (não necessariamente todas).
2. Colar memória do projeto se existir.
3. Colar definição do agente escolhido.
4. Colar enunciado da task.
5. Indicar modo: plan / run / review.

Checklist mínimo antes de enviar prompt:

```
[ ] CURRENT_SPRINT.md incluído ou resumido
[ ] Agente correto para o modo
[ ] Task com critérios de aceite
[ ] KNOWN_ISSUES consultado se for run/review
```

---

## 12. Anti-padrões

| Anti-padrão | Problema | Correção |
|-------------|----------|----------|
| Prompt só com a task | Perde arquitetura e decisões | Injetar contexto global |
| Context dump sem ordem | Modelo ignora partes críticas | Seguir ordem da seção 3 |
| Agente errado no modo | architect implementa código | Usar `--agent` correto |
| Memória desatualizada | Agente repete erros | Atualizar DECISIONS/LEARNINGS |
| Task gigante no prompt | Estoura contexto | Dividir tasks |

---

## 13. Referências

- Implementação: `src/pam/context_engine.py`, `src/pam/agent_registry.py`, `src/pam/cursor_runner.py`
- Filosofia: [DEVELOPMENT_PHILOSOPHY.md](./DEVELOPMENT_PHILOSOPHY.md)
- Bootstrap: [PROJECT_BOOTSTRAP.md](./PROJECT_BOOTSTRAP.md)

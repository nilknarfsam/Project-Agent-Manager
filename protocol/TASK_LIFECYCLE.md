# Task Lifecycle — Ciclo de vida de tarefas

Especificação oficial do sistema de tasks gerenciadas do protocolo OS4AI / PAM.

---

## 1. Objetivo

Garantir que todo trabalho agêntico rastreável possua:

- **Identidade única** (`TASK-XXXX`)
- **Status explícito** com transições válidas
- **Metadata estruturada** (JSON)
- **Histórico imutável** de mudanças de status
- **Localização por pasta** conforme estado

---

## 2. Estrutura de arquivos

```
ai/tasks/
├── active/           # planned, approved, running, reviewed
├── completed/        # done
├── blocked/          # blocked
├── archived/         # cancelled
├── .task_counter     # contador sequencial (interno)
├── TASK-0001.md      # corpo da tarefa (Markdown)
└── TASK-0001.json    # metadata (JSON)
```

Cada task gerenciada possui par **`.md` + `.json`** com o mesmo stem (`TASK-0001`).

### Arquivo Markdown (`.md`)

Contém o enunciado humano-legível:

- Título e objetivo
- Critérios de aceite
- Escopo e restrições
- Referências a contexto ou decisões

### Arquivo JSON (`.json`)

Metadata machine-readable. Campos oficiais:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `task_id` | string | Formato `TASK-XXXX` (4 dígitos) |
| `title` | string | Título curto |
| `project` | string | Nome do projeto (ex.: `auratime`) |
| `status` | string | Status atual (ver seção 3) |
| `agent` | string | Agente associado (ex.: `architect`) |
| `created_at` | string | ISO 8601 UTC |
| `updated_at` | string | ISO 8601 UTC |
| `history` | array | Lista de eventos (ver seção 6) |

Exemplo de metadata:

```json
{
  "task_id": "TASK-0001",
  "title": "Analisar estrutura do projeto",
  "project": "auratime",
  "status": "planned",
  "agent": "architect",
  "created_at": "2026-05-23T12:00:00+00:00",
  "updated_at": "2026-05-23T12:00:00+00:00",
  "history": [
    {
      "status": "planned",
      "timestamp": "2026-05-23T12:00:00+00:00",
      "note": "Criada via plan"
    }
  ]
}
```

---

## 3. Status oficiais

| Status | Significado | Pasta |
|--------|-------------|-------|
| `planned` | Tarefa criada, aguardando aprovação ou execução | `active/` |
| `approved` | Aprovada para execução | `active/` |
| `running` | Em execução (`run` em andamento) | `active/` |
| `reviewed` | Implementação concluída, aguardando review formal | `active/` |
| `done` | Concluída e validada | `completed/` |
| `blocked` | Impedida por dependência ou decisão externa | `blocked/` |
| `cancelled` | Cancelada, não será executada | `archived/` |

---

## 4. Transições

### Diagrama

```
                    ┌──────────┐
                    │ planned  │
                    └────┬─────┘
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
     ┌──────────┐  ┌──────────┐  ┌───────────┐
     │ approved │  │ blocked  │  │ cancelled │
     └────┬─────┘  └──────────┘  └───────────┘
          │
          ▼
     ┌──────────┐
     │ running  │
     └────┬─────┘
          │
          ▼
     ┌──────────┐
     │ reviewed │
     └────┬─────┘
          │
          ▼
     ┌──────────┐
     │   done   │
     └──────────┘
```

### Transições automáticas (PAM)

| Evento | De → Para |
|--------|-----------|
| `plan --task ...` | (criação) → `planned` |
| `run --task TASK-XXXX` (início) | → `running` |
| `run --task TASK-XXXX` (fim) | → `reviewed` |
| `review --task TASK-XXXX` (fim) | → `done` |

### Transições manuais (CLI)

| Comando | Efeito |
|---------|--------|
| `approve-task TASK-XXXX` | → `approved` |
| `complete-task TASK-XXXX` | → `done` |
| `block-task TASK-XXXX` | → `blocked` |
| `cancel-task TASK-XXXX` | → `cancelled` |

### Regras de transição

1. Toda mudança de status **atualiza** `updated_at` e **append** em `history`.
2. Mudança de status **move** o par `.md`/`.json` para a pasta correspondente.
3. Status inválidos são rejeitados — apenas os sete oficiais são aceitos.
4. `task_id` é imutável após criação.
5. Transições manuais podem ser usadas para corrigir fluxo ou pular etapas com intenção explícita (ex.: `complete-task` direto de `approved`).

---

## 5. Identificação e resolução

### Formato de ID

- Padrão: `TASK-` + 4 dígitos (`TASK-0001`, `TASK-0042`)
- Case-insensitive na entrada; normalizado para uppercase internamente.

### Referência em comandos

```powershell
# Por ID
python -m pam.main run auratime --task TASK-0001

# Por caminho legado (compatibilidade)
python -m pam.main plan auratime --task ai/tasks/sprint_001_analyze_project.md
```

Arquivos legados fora da estrutura `TASK-XXXX` continuam válidos. No `plan`, o PAM pode criar automaticamente um `TASK-XXXX` em `active/`.

---

## 6. Histórico (`history`)

Cada entrada no array `history`:

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `status` | string | sim | Novo status |
| `timestamp` | string | sim | ISO 8601 UTC |
| `note` | string | não | Motivo ou origem (comando, agente) |
| `agent` | string | não | Agente no momento da transição |

Regras:

- **Append-only** — entradas não são editadas ou removidas.
- Ordem cronológica crescente.
- Fonte de verdade para auditoria de progresso.

---

## 7. Movimentação de tasks

Ao mudar status, o sistema:

1. Valida o novo status.
2. Atualiza metadata JSON.
3. Adiciona entrada em `history`.
4. Move `TASK-XXXX.md` e `TASK-XXXX.json` para subpasta correta.

Mapeamento status → pasta:

| Status | Subpasta |
|--------|----------|
| `planned`, `approved`, `running`, `reviewed` | `active/` |
| `done` | `completed/` |
| `blocked` | `blocked/` |
| `cancelled` | `archived/` |

---

## 8. Comandos de consulta

```powershell
python -m pam.main tasks
python -m pam.main tasks --project auratime
python -m pam.main task-status TASK-0001
```

Saída de `task-status` inclui: ID, título, projeto, status, agente, timestamps e histórico resumido.

---

## 9. Boas práticas

| Prática | Motivo |
|---------|--------|
| Uma task = um objetivo | Diffs pequenos e review focado |
| Critérios de aceite no `.md` | Reviewer valida objetivamente |
| Aprovar antes de runs críticos | Controle humano em mudanças sensíveis |
| Bloquear em vez de cancelar | Preserva intenção para retomada |
| Registrar nota no histórico | Contexto para próximo agente |

---

## 10. Adoção sem PAM

Projetos que não usam o PAM podem adotar manualmente:

1. Criar estrutura de pastas em `ai/tasks/`.
2. Usar pares `.md`/`.json` com os campos oficiais.
3. Mover arquivos ao mudar status.
4. Referenciar `TASK-XXXX` em prompts e commits.

O protocolo é **independente da ferramenta**; o PAM automatiza este documento.

# Ciclo de vida de tasks

O PAM gerencia tarefas com identidade única, status rastreável e histórico completo — o **Task Lifecycle System**.

## Identidade: TASK-XXXX

Toda tarefa gerenciada recebe um ID sequencial:

```text
TASK-0001
TASK-0002
TASK-0042
```

Formato fixo: `TASK-` + 4 dígitos. Gerado automaticamente pelo `task_manager.py`.

Cada task possui dois arquivos:

```text
ai/tasks/active/TASK-0001.md    ← descrição (Markdown)
ai/tasks/active/TASK-0001.json  ← metadata (JSON)
```

## Status oficiais

| Status | Significado | Pasta |
|--------|-------------|-------|
| `planned` | Criada, aguardando aprovação | `active/` |
| `approved` | Aprovada para execução | `active/` |
| `running` | Em execução (`run` iniciado) | `active/` |
| `reviewed` | Executada, aguardando revisão final | `active/` |
| `done` | Concluída com sucesso | `completed/` |
| `blocked` | Bloqueada (erro ou dependência) | `blocked/` |
| `cancelled` | Cancelada | `archived/` |

## Fluxo automático

```
planned ──► running ──► reviewed ──► done
   │            │           │
   │            ▼           │
   │         blocked        │
   │                        │
   └──────► cancelled ◄────┘
```

| Comando | Transição automática |
|---------|---------------------|
| `plan --task ...` | Cria task → `planned` |
| `run --task TASK-XXXX` | Início → `running`; fim → `reviewed` |
| `review --task TASK-XXXX` | Fim → `done` |
| `pipeline ... TASK-XXXX` | `running` → `reviewed`/`done`/`blocked` conforme resultado |

## Transições manuais

```powershell
python -m pam.main approve-task TASK-0001
python -m pam.main complete-task TASK-0001
python -m pam.main block-task TASK-0001
python -m pam.main cancel-task TASK-0001
```

## Metadata JSON

Exemplo simplificado de `TASK-0001.json`:

```json
{
  "task_id": "TASK-0001",
  "title": "Implementar login",
  "project": "auratime",
  "status": "reviewed",
  "agent": "implementer",
  "created_at": "2026-05-23T10:00:00+00:00",
  "updated_at": "2026-05-23T12:30:00+00:00",
  "history": [
    {
      "timestamp": "2026-05-23T10:00:00+00:00",
      "from_status": null,
      "to_status": "planned",
      "message": "task created"
    }
  ],
  "pipeline_history": []
}
```

### Campos principais

| Campo | Descrição |
|-------|-----------|
| `task_id` | Identificador único |
| `title` | Título extraído do Markdown |
| `project` | Nome do projeto PAM |
| `status` | Status atual |
| `agent` | Agente associado |
| `history` | Log de mudanças de status |
| `pipeline_history` | Steps de pipeline executados |

## pipeline_history

Quando um **pipeline** processa uma task, cada step é registrado:

```json
{
  "pipeline_name": "default_pipeline",
  "agent": "architect",
  "status": "success",
  "started_at": "2026-05-23T10:00:00+00:00",
  "finished_at": "2026-05-23T10:05:00+00:00",
  "summary": "Resumo do step...",
  "run_path": "ai/runs/pipelines/...",
  "provider": "gemini",
  "model": "gemini-2.5-pro"
}
```

Campos `provider` e `model` foram adicionados com Runtime Profiles (Sprint 9).

## Organização de pastas

```text
ai/tasks/
├── active/       ← planned, approved, running, reviewed
├── completed/    ← done
├── blocked/      ← blocked
├── archived/     ← cancelled
└── .task_counter ← contador sequencial
```

Ao mudar de status, os arquivos `.md` e `.json` **movem automaticamente** para a pasta correta.

## Comandos úteis

```powershell
python -m pam.main tasks
python -m pam.main tasks --project auratime
python -m pam.main task-status TASK-0001
```

Na GUI: aba **Tasks** → selecione o projeto → **Atualizar tasks**.

## Arquivos legados

Arquivos como `ai/tasks/sprint_001_analyze_project.md` (sem `TASK-XXXX`) continuam válidos. No `plan`, o PAM cria automaticamente um `TASK-XXXX` em `active/` com o conteúdo copiado.

## Boas práticas

1. **Uma task = uma entrega pequena** — alinhado à filosofia de sprints pequenas.
2. **Título claro no Markdown** — vira o `title` da metadata.
3. **Use `task-status`** antes de reexecutar — evite duplicar trabalho.
4. **Consulte `pipeline_history`** — saiba o que cada agente já fez.

## Próximo passo

- [Pipelines](pipelines.md)
- [Primeiros passos](getting_started.md)
- [Onboarding](onboarding.md)

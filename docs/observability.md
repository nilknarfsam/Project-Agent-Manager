# Observabilidade e Métricas

Fundação de observabilidade do **Project Agent Manager** — registro local de execuções, agregações básicas e painel na GUI, sem banco de dados externo.

## Visão geral

Cada execução relevante do PAM gera um **evento** em arquivos JSONL mensais:

```
ai/metrics/events_YYYYMM.jsonl
```

Exemplo: `ai/metrics/events_202605.jsonl` para maio de 2026.

Comandos instrumentados:

| Comando | Quando registra |
|---------|-----------------|
| `plan` | Após persistir run em `ai/runs/` |
| `run` | Idem |
| `review` | Idem |
| `resume` | Idem (sucesso ou falha) |
| `pipeline` | Por step (Cursor/Gemini) + evento consolidado do pipeline |
| `ai-summary` | Após chamada Gemini |
| `ai-tasks` | Idem |
| `ai-docs` | Idem |

## Campos do evento

Cada linha JSONL contém:

| Campo | Descrição |
|-------|-----------|
| `event_id` | UUID único |
| `timestamp` | ISO 8601 UTC |
| `project` | Slug do projeto |
| `command` | Comando executado (`plan`, `run`, `pipeline`, `ai-summary`, …) |
| `agent` | Agente PAM, quando aplicável |
| `provider` | `cursor`, `gemini`, `mixed`, … |
| `model` | Modelo usado |
| `task_id` | TASK-XXXX, quando aplicável |
| `status` | Status textual da execução |
| `duration_ms` | Duração em milissegundos |
| `success` | `true` / `false` |
| `error_summary` | Resumo sanitizado (sem chaves) |
| `run_file` | Caminho do log em `ai/runs/` |
| `pipeline_name` | Nome do pipeline, quando aplicável |

**Nunca são salvos:** prompts completos, conteúdo de contexto, chaves de API ou tokens.

## Privacidade

O módulo `metrics_store.py` aplica sanitização antes de gravar:

- Padrões de API key, secret, token e password são substituídos por `[REDACTED]`
- `error_summary` é truncado (máx. 500 caracteres)
- Apenas metadados operacionais — não há dump de conversas ou código

Arquivos de eventos ficam no `.gitignore` (`ai/metrics/events_*.jsonl`); apenas a estrutura de pastas é versionada.

## CLI — comando `metrics`

```powershell
$env:PYTHONPATH = "src"

# Resumo completo
python -m pam.main metrics

# Filtrar por projeto
python -m pam.main metrics --project auratime

# Limitar últimas execuções exibidas
python -m pam.main metrics --last 10
```

Saída inclui:

- Total de execuções
- Sucessos e falhas
- Duração média
- Contagem por projeto, provider e agente
- Lista das últimas execuções

## GUI — aba Observabilidade

No **Agentic Workbench** (`python -m pam.main gui`):

1. Abra a aba **Observabilidade**
2. Selecione um projeto na barra lateral (opcional — filtra métricas)
3. Clique em **Atualizar**

Painéis: resumo numérico, tabelas de providers/agentes e últimas execuções.

## Módulos

| Módulo | Responsabilidade |
|--------|------------------|
| `metrics_store.py` | Gravação e leitura JSONL, sanitização |
| `observability_service.py` | Agregações e formatação de relatórios |

Integração mínima em:

- `cursor_runner.py` — runs Cursor (plan/run/review/resume/steps)
- `pipeline_engine.py` — steps Gemini + evento consolidado de pipeline
- `ai_service.py` — comandos `ai-*`

## Limitações atuais (Sprint 13)

- **Armazenamento local apenas** — arquivos JSONL, sem banco de dados
- **Sem custos reais** — duração sim, tokens/custo por provider ainda não
- **Sem exportação** — Prometheus, Grafana ou cloud não integrados
- **Agregação em memória** — leitura linear de todos os JSONL ao consultar
- **Steps de pipeline** — cada step gera evento; pipeline consolidado gera evento adicional
- **Gemini em pipeline** — duração medida localmente; Cursor usa `duration_ms` do SDK

## Custos futuros (roadmap)

Planejado para sprints posteriores:

- Contagem de tokens por provider/modelo
- Estimativa de custo (USD) com tabelas configuráveis
- Dashboard histórico e alertas de falha
- Exportação para ferramentas externas (OpenTelemetry, etc.)
- Retenção e rotação automática de arquivos antigos

## Boas práticas

1. Execute `metrics` periodicamente para acompanhar saúde operacional
2. Use `--project` ao analisar um repositório específico
3. Combine com logs em `ai/runs/` para investigar falhas (evento aponta `run_file`)
4. Não commite arquivos `events_*.jsonl` — contêm metadados operacionais locais

## Referências

- [Arquitetura](architecture.md)
- [Providers](providers.md)
- [Pipelines](pipelines.md)
- [GUI Workbench](gui_workbench.md)

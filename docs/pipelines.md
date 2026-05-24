# Pipelines multi-agente

O PAM orquestra **pipelines sequenciais** de agentes especializados — cada um executa em ordem, passando contexto acumulado ao próximo.

## Conceito

Em vez de um único agente fazer tudo, um **pipeline** define uma sequência de papéis:

```text
architect → implementer → reviewer → test_writer → docs_writer → release_manager
```

Cada step é um agente com prompt, provider e modelo próprios (via [Runtime Profiles](runtime_profiles.md)).

## Multi-agent orchestration

| Princípio | Descrição |
|-----------|-----------|
| **Sequencial** | Um agente por vez — sem paralelismo (por enquanto) |
| **Especialização** | Cada agente tem papel definido em `ai/agents/` |
| **Contexto acumulado** | Resumo de cada step vai para o próximo |
| **Rastreabilidade** | Logs em `ai/runs/pipelines/` + `pipeline_history` na task |

## Executar um pipeline

```powershell
$env:PYTHONPATH = "src"

# Pipeline padrão
python -m pam.main pipeline auratime TASK-0001

# Pipeline específico
python -m pam.main pipeline auratime TASK-0001 --pipeline default_pipeline

# Retomar a partir de um step
python -m pam.main pipeline auratime TASK-0001 --from-step reviewer
```

## Pipeline padrão

Arquivo: `ai/pipelines/default_pipeline.yaml`

```yaml
name: default_pipeline
description: >-
  Pipeline sequencial padrão — architect → implementer → reviewer →
  test_writer → docs_writer → release_manager.

steps:
  - architect
  - implementer
  - reviewer
  - test_writer
  - docs_writer
  - release_manager
```

### Papel de cada agente no pipeline

| Step | Agente | Função típica |
|------|--------|---------------|
| 1 | `architect` | Análise e planejamento |
| 2 | `implementer` | Implementação no código |
| 3 | `reviewer` | Revisão de qualidade |
| 4 | `test_writer` | Cenários e testes |
| 5 | `docs_writer` | Documentação |
| 6 | `release_manager` | Checklist de release |

## Contexto acumulado

```
Step 1 (architect)
   │
   ▼ resumo salvo
Step 2 (implementer) ← recebe resumo do step 1 + task original
   │
   ▼ resumo salvo
Step 3 (reviewer) ← recebe resumos acumulados
   ...
```

Limite de contexto acumulado: ~12.000 caracteres (truncamento automático).

Cada resumo individual: até ~2.000 caracteres.

## Definir pipelines customizados

Crie um novo arquivo em `ai/pipelines/`:

```yaml
name: meu_pipeline
description: Pipeline focado em qualidade.

steps:
  - architect
  - implementer
  - reviewer
```

Execute com:

```powershell
python -m pam.main pipeline meu-projeto TASK-0001 --pipeline meu_pipeline
```

## Logs e resultados

Após a execução:

| Artefato | Local |
|----------|-------|
| Log por step | `ai/runs/pipelines/` |
| Resultado consolidado | `.json` + `.md` no mesmo diretório |
| Histórico na task | `pipeline_history` em `TASK-XXXX.json` |

Exemplo de log no terminal:

```text
[pipeline] Step 1/6: architect (default_pipeline / TASK-0001) [provider=gemini, model=gemini-2.5-pro]
[pipeline] Step 2/6: implementer ... [provider=cursor, model=...]
```

## Integração com Task Lifecycle

| Evento | Efeito na task |
|--------|----------------|
| Pipeline inicia | Status → `running` |
| Step `reviewer` concluído | Status → `reviewed` |
| Pipeline com sucesso | Status → `done` |
| Falha em algum step | Status → `blocked` |

## Runtime híbrido em pipelines

Com [Runtime Profiles](runtime_profiles.md), steps leves usam Gemini e implementação usa Cursor — otimizando custo sem perder capacidade de editar código.

## Comandos single-agent vs pipeline

| Abordagem | Quando usar |
|-----------|-------------|
| `plan` / `run` / `review` | Tarefa simples, um agente, controle fino |
| `pipeline` | Entrega completa, múltiplos papéis, fluxo padronizado |

Ambos coexistem — pipelines **não substituem** comandos single-agent.

## Próximo passo

- [Runtime Profiles](runtime_profiles.md)
- [Ciclo de vida de tasks](tasks_lifecycle.md)
- [Providers](providers.md)

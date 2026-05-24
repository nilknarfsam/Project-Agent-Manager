# Providers de IA

O PAM suporta múltiplos **providers** (fornecedores de modelos de IA). Cada um tem um papel diferente no ecossistema — nenhum substitui completamente o outro.

## Visão geral

```
                    ┌─────────────┐
                    │     PAM     │
                    │   Router    │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │   Cursor   │  │   Gemini   │  │  OpenAI /  │
    │    SDK     │  │    API     │  │ Anthropic  │
    │  (ativo)   │  │  (ativo)   │  │ (futuro)   │
    └────────────┘  └────────────┘  └────────────┘
```

## Cursor

**Papel principal:** edição real de código, refactors, sessões persistentes.

| Aspecto | Detalhe |
|---------|---------|
| Comandos | `plan`, `run`, `review`, `resume`, `pipeline` (steps Cursor) |
| Modos SDK | `plan` (análise) e `agent` (implementação) |
| Sessões | `Agent.resume()` — retomada de conversas |
| Chave | `CURSOR_API_KEY` |
| Custo | Conforme plano Cursor |

**Quando usar:** sempre que o agente precisa **ler e modificar** arquivos no repositório.

## Gemini

**Papel principal:** tarefas leves — análise, sumarização, sugestão de tasks, rascunho de docs.

| Aspecto | Detalhe |
|---------|---------|
| Comandos | `ai-summary`, `ai-tasks`, `ai-docs` |
| Pipeline | Steps leves (`architect`, `reviewer`, `docs_writer`, …) |
| Modelos | `gemini-2.5-flash` (rápido), `gemini-2.5-pro` (profundo) |
| Chave | `GEMINI_API_KEY` |
| Custo | Pay-per-use na API Google |

**Quando usar:** análise de contexto, brainstorming de tasks, documentação preliminar — **sem editar código**.

## OpenAI

**Status:** reservado para implementação futura.

| Aspecto | Detalhe |
|---------|---------|
| Chave | `OPENAI_API_KEY` (já preparada no `.env.example`) |
| Uso previsto | Provider alternativo para agentes leves ou chat |

Configure a chave com `set-key openai` — ainda não é usada em runtime.

## Anthropic

**Status:** reservado para implementação futura.

| Aspecto | Detalhe |
|---------|---------|
| Chave | `ANTHROPIC_API_KEY` |
| Uso previsto | Provider alternativo (Claude) para análise ou código |

## Quando usar cada um

| Cenário | Provider recomendado |
|---------|---------------------|
| Implementar feature no código | **Cursor** |
| Planejar arquitetura (sem editar) | **Gemini** (leve) ou **Cursor** (plan) |
| Revisar qualidade do código | **Cursor** (review) ou **Gemini** (análise) |
| Sugerir lista de tasks | **Gemini** (`ai-tasks`) |
| Rascunho de documentação | **Gemini** (`ai-docs`) |
| Pipeline completo com código | **Híbrido** (ver abaixo) |

## Runtime híbrido

O PAM permite **misturar providers** no mesmo pipeline via [Runtime Profiles](runtime_profiles.md):

```yaml
architect:
  provider: gemini        # análise barata
  model: gemini-2.5-pro

implementer:
  provider: cursor        # edição real
  mode: deep_agent

reviewer:
  provider: gemini
  model: gemini-2.5-flash
```

Benefício: **architect** e **reviewer** no Gemini (rápido/barato); **implementer** no Cursor (capacidade de editar).

## Custos e otimização

| Estratégia | Efeito |
|------------|--------|
| Gemini Flash para steps leves | Menor custo por token |
| Gemini Pro só onde precisa de profundidade | Balance qualidade/custo |
| Cursor apenas para implementação | Evita chamadas caras desnecessárias |
| Context Builder seletivo | Menos tokens por prompt |
| Sprints pequenas | Menos retrabalho e reexecuções |

## Roteamento automático

O `provider_router.py` roteia por **tipo de tarefa** (comandos `ai-*`):

| Tipo | Provider |
|------|----------|
| `analysis`, `summarize`, `docs`, `tasks` | Gemini |
| `code_edit`, `plan`, `run`, `review`, `pipeline` | Cursor |

Para pipelines, o roteamento por **agente** usa `runtime_profiles.py` → `route_agent()`.

## Configuração de chaves

```powershell
python -m pam.main set-key cursor
python -m pam.main set-key gemini
python -m pam.main settings
```

Ou pela GUI → aba **Configurações**.

Chaves ficam **apenas** no `.env` local — nunca em JSON, logs completos ou repositório.

## Próximo passo

- [Runtime Profiles](runtime_profiles.md)
- [Pipelines](pipelines.md)
- [Instalação](installation.md)

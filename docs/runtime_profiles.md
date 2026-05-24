# Runtime Profiles

**Runtime Profiles** permitem definir **provider, modelo e modo** por agente — habilitando pipelines híbridos com otimização de custo e performance.

## O que são?

Cada agente especializado (`architect`, `implementer`, `reviewer`, …) pode usar um runtime diferente. A configuração fica em YAML, sem alterar código.

Arquivo padrão:

```text
ai/runtime_profiles/default_profiles.yaml
```

## Exemplo completo

```yaml
architect:
  provider: gemini
  model: gemini-2.5-pro

implementer:
  provider: cursor
  mode: deep_agent

reviewer:
  provider: gemini
  model: gemini-2.5-flash

test_writer:
  provider: gemini
  model: gemini-2.5-flash

docs_writer:
  provider: gemini
  model: gemini-2.5-flash

release_manager:
  provider: gemini
  model: gemini-2.5-pro
```

## Campos do profile

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `provider` | Sim | `cursor`, `gemini`, `openai` ou `anthropic` |
| `model` | Não | Modelo do provider (ex.: `gemini-2.5-flash`) |
| `mode` | Não | Modo Cursor (ex.: `deep_agent` → mapeado para `agent`) |

## Provider por agente

| Agente | Provider padrão | Motivo |
|--------|-----------------|--------|
| `architect` | Gemini Pro | Planejamento analítico, sem editar código |
| `implementer` | Cursor | Único com capacidade de editar o repositório |
| `reviewer` | Gemini Flash | Revisão rápida e econômica |
| `test_writer` | Gemini Flash | Geração de cenários de teste |
| `docs_writer` | Gemini Flash | Rascunho de documentação |
| `release_manager` | Gemini Pro | Checklist de release com atenção |

## Fallback seguro

Se um agente **não tiver** entrada no YAML:

```
→ provider: cursor
→ mode: agent (padrão legado)
```

Comportamento idêntico ao PAM antes dos Runtime Profiles — **nada quebra**.

Se o provider configurado **falhar** (chave ausente, API indisponível):

- Mensagem amigável com instruções (`set-key`, etc.)
- Demais comandos e agentes continuam funcionando

## Otimização custo / performance

| Técnica | Como |
|---------|------|
| Flash para steps repetitivos | `reviewer`, `test_writer`, `docs_writer` |
| Pro só para decisões críticas | `architect`, `release_manager` |
| Cursor só no implementer | Edição real onde importa |
| Ajuste fino via YAML | Edite `default_profiles.yaml` sem redeploy |

## Como o PAM resolve o profile

```
Pipeline step: architect
       │
       ▼
provider_router.route_agent("architect")
       │
       ▼
runtime_profiles.get_agent_profile("architect")
       │
       ▼
{ provider: gemini, model: gemini-2.5-pro }
       │
       ▼
Execução via GeminiProvider (step leve)
```

Logs de pipeline e `pipeline_history` registram `provider` e `model` por step.

## Visualização na GUI

A aba **Runtime Profiles** (somente leitura) mostra:

- Agente
- Provider atual
- Modelo atual

Clique em **Atualizar profiles** após editar o YAML.

## Editar profiles

1. Abra `ai/runtime_profiles/default_profiles.yaml`
2. Ajuste provider/model/mode do agente desejado
3. Salve o arquivo
4. Execute pipeline ou atualize a GUI

Não é necessário reiniciar o PAM — profiles são carregados a cada execução.

## Providers suportados em pipeline

| Provider | Status em pipeline |
|----------|-------------------|
| `cursor` | ✅ Ativo |
| `gemini` | ✅ Ativo |
| `openai` | 🔜 Futuro |
| `anthropic` | 🔜 Futuro |

## Próximo passo

- [Providers](providers.md)
- [Pipelines](pipelines.md)
- [Arquitetura](architecture.md)

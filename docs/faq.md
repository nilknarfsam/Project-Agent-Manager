# Perguntas frequentes (FAQ)

Respostas diretas às dúvidas mais comuns sobre o PAM.

---

## O PAM substitui o Cursor?

**Não.** O PAM **orquestra** o Cursor (e outros providers). Você continua precisando do Cursor SDK para editar código, executar `plan`/`run`/`review` e pipelines com o agente implementer.

O PAM adiciona: tasks rastreáveis, contexto estruturado, agentes especializados, pipelines sequenciais e uma interface de workbench.

---

## O PAM é uma IDE?

**Não.** O PAM não edita código, não tem debugger e não substitui VS Code ou Cursor.

A GUI é um **Agentic Workbench** — painel para selecionar projetos, montar contexto, executar agentes e acompanhar logs. Para editar código, use **Abrir no Cursor** ou **Abrir no VS Code** na sidebar.

---

## Posso usar só Gemini?

**Parcialmente.** Comandos `ai-summary`, `ai-tasks`, `ai-docs` e steps leves de pipeline funcionam só com Gemini.

Para **implementar código** no repositório (`run`, step `implementer`), você precisa do **Cursor**. Sem `CURSOR_API_KEY`, o núcleo de execução agentica não funciona.

---

## Preciso saber programar?

**Ajuda, mas não é obrigatório para começar.**

- **Arquitetos** podem usar a GUI para `plan`, montar contexto e revisar logs sem escrever Python.
- **Desenvolvedores** se beneficiam da CLI, customização de pipelines e integração com o fluxo Git.

Conhecimento básico de linha de comando e Markdown é recomendado.

---

## O PAM funciona com outros providers?

**Hoje:** Cursor (ativo) e Gemini (ativo).

**Preparado para o futuro:** OpenAI e Anthropic têm variáveis no `.env` e suporte em `settings`, mas ainda não estão integrados em runtime.

A arquitetura de [Runtime Profiles](runtime_profiles.md) foi desenhada para adicionar providers sem reescrever o core.

---

## O PAM é open source?

Consulte a licença no repositório. Atualmente o README indica **uso interno** — verifique com os mantenedores antes de distribuir ou comercializar.

A documentação em `docs/` e o protocolo em `protocol/` foram escritos para facilitar adoção por comunidades no futuro.

---

## Posso criar meus próprios agentes?

**Sim.** Adicione um arquivo Markdown em `ai/agents/`:

```text
ai/agents/meu_agente.md
```

Depois use:

```powershell
python -m pam.main plan meu-projeto --agent meu_agente
```

Para pipelines, inclua o agente em `ai/pipelines/*.yaml` e, se quiser, configure um [Runtime Profile](runtime_profiles.md).

---

## Qual a diferença entre Context Engine e Context Builder?

| | Context Engine | Context Builder |
|---|----------------|-----------------|
| **Automático** | Sim — injeta em todo prompt | Não — você escolhe |
| **Fonte** | `ai/context/` + `ai/memory/` | Arquivos do repositório |
| **Uso** | Sempre ativo | Ad hoc, via GUI |

---

## O que é TASK-XXXX?

Identificador único de tarefas gerenciadas pelo PAM. Veja [Ciclo de vida de tasks](tasks_lifecycle.md).

---

## Como retomar uma conversa com o agente?

Após `plan`, `run` ou `review` bem-sucedido:

```powershell
python -m pam.main resume meu-projeto -p "Continue de onde parou"
```

O PAM usa `Agent.resume()` com o `agent_id` salvo em `ai/sessions/`.

---

## O pipeline executa agentes em paralelo?

**Não.** Pipelines são **sequenciais** — um agente por vez. Paralelismo é planejado para versões futuras.

---

## Onde ficam os logs?

```text
ai/runs/              ← comandos single-agent
ai/runs/pipelines/    ← steps de pipeline
```

Cada execução gera `.json` + `.md` com prompt, resultado e metadata.

---

## Como reportar problemas ou sugerir melhorias?

Abra uma issue no repositório ou contate os mantenedores do projeto. Inclua:

- Comando executado
- Trecho relevante do log (`ai/runs/`)
- Versão do Python e sistema operacional

---

## Próximo passo

- [Primeiros passos](getting_started.md)
- [Instalação](installation.md)
- [Arquitetura](architecture.md)

# Agentic Workbench (GUI)

A interface gráfica do PAM — o **Agentic Workbench** — é um painel de trabalho para arquitetos de software. Ela complementa a CLI sem duplicar lógica: todos os comandos delegam aos mesmos handlers Python.

> **Importante:** o PAM não é uma IDE. Você não edita código dentro da GUI — apenas orquestra agentes, tasks e contexto.

## Como abrir

```powershell
$env:PYTHONPATH = "src"
python -m pam.main gui
```

<!-- Screenshot futura: visão geral do workbench -->
<!-- ![Agentic Workbench](../docs/assets/workbench_overview.png) -->

## Layout da interface

A janela está organizada em três zonas principais:

```
┌──────────────────┬────────────────────────────────────────┐
│                  │  [Operações] [Tasks] [Context Builder] │
│    SIDEBAR       │  [Runtime Profiles] [Config] [Logs]    │
│    Projetos      │                                        │
│                  │         ÁREA CENTRAL (abas)            │
│                  │                                        │
├──────────────────┴────────────────────────────────────────┤
│              PAINEL INFERIOR — Saída / log                │
└───────────────────────────────────────────────────────────┘
```

## Barra lateral (sidebar)

Painel esquerdo com tudo relacionado ao **projeto ativo**:

| Elemento | Função |
|----------|--------|
| **Lista de projetos** | Projetos cadastrados em `ai/projects/` |
| **Atualizar** | Recarrega a lista de projetos |
| **Abrir pasta…** | Seletor de diretório no disco |
| **Executar onboard** | Aplica estrutura OS4AI na pasta selecionada |
| **Abrir no Cursor** | Abre o repo no Cursor (`cursor <caminho>`) |
| **Abrir no VS Code** | Abre o repo no VS Code (`code <caminho>`) |
| **--force** | Sobrescreve templates no onboard |
| **Pasta para onboard** | Caminho alvo do onboard |

Ao selecionar um projeto, o caminho do repositório aparece abaixo da lista.

## Aba Operações

O coração da execução agentica:

| Campo | Descrição |
|-------|-----------|
| **Comando** | `plan`, `run`, `review` ou `resume` |
| **Agente** | Opcional — vazio usa o padrão do comando |
| **Task** | Caminho manual ou seletor de arquivo `.md` |
| **Prompt extra** | Instruções adicionais (equivalente a `-p` na CLI) |
| **Executar** | Dispara o comando em thread separada |

A saída aparece no painel inferior em tempo real.

## Aba Tasks

Lista tarefas do **lifecycle PAM** (`ai/tasks/`) filtradas pelo projeto selecionado:

- ID (`TASK-XXXX`)
- Título
- Status
- Agente

Clique em uma task para preencher automaticamente o campo Task na aba Operações.

## Aba Context Builder

Monte pacotes de contexto a partir de arquivos do repositório. Veja o guia completo em [Context Builder](context_builder.md).

## Aba Runtime Profiles

Visualização **somente leitura** dos profiles de runtime por agente:

- Agente
- Provider (Cursor, Gemini, …)
- Modelo

Configuração em `ai/runtime_profiles/default_profiles.yaml`. Detalhes em [Runtime Profiles](runtime_profiles.md).

## Aba Configurações

Gerenciamento seguro de chaves de API:

- Status mascarado por provider (Cursor, Gemini, OpenAI, Anthropic)
- Botões para inserir/atualizar chave com campo password
- Valores salvos apenas em `.env` local (gitignored)

## Aba Logs

Controles do painel de saída:

- **Limpar log** — apaga o conteúdo do painel inferior
- **Rolar para o fim** — vai ao final do log

A saída em tempo real fica sempre visível no **painel inferior**, independentemente da aba ativa.

## Abrir no Cursor / VS Code

Dois atalhos na sidebar abrem o repositório do projeto selecionado no editor externo:

```text
cursor C:\caminho\do\projeto
code C:\caminho\do\projeto
```

Se o comando não estiver no PATH, a GUI exibe uma mensagem amigável com instruções de instalação do shell command.

## Dicas de uso

1. **Selecione o projeto** na sidebar antes de executar comandos.
2. **Use Tasks** para navegar entre tarefas existentes sem digitar caminhos.
3. **Monte contexto** no Context Builder e use “Usar no próximo prompt” antes de `plan` ou `run`.
4. **Acompanhe o log** inferior — erros e caminhos de arquivos aparecem lá.
5. **Configure chaves** na aba Configurações antes da primeira execução.

## Próximo passo

- [Context Builder](context_builder.md)
- [Providers](providers.md)
- [Primeiros passos](getting_started.md)

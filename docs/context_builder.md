# Context Builder

O **Context Builder** permite selecionar arquivos do repositório do projeto e montar um **pacote de contexto** em Markdown — pronto para enviar aos agentes via prompt extra.

Disponível na aba **Context Builder** da GUI (`python -m pam.main gui`).

## Para que serve?

Agentes trabalham melhor quando recebem contexto relevante e delimitado. Em vez de copiar arquivos manualmente, você:

1. Navega pela árvore de arquivos do projeto
2. Seleciona o que importa
3. Gera um markdown consolidado
4. Anexa ao próximo comando (`plan`, `run`, etc.)

## Como selecionar arquivos

### Atualizar a árvore

1. Selecione um projeto na **barra lateral**
2. Abra a aba **Context Builder**
3. Clique em **Atualizar árvore**

A árvore lista arquivos e pastas do repositório, ignorando automaticamente pastas pesadas.

### Adicionar ao contexto

1. Selecione um **arquivo** ou **pasta** na árvore
2. Clique em **Adicionar selecionado**
   - **Arquivo** — adiciona apenas aquele arquivo
   - **Pasta** — adiciona todos os arquivos dentro dela (respeitando filtros)

O contador “Selecionados: N arquivo(s)” atualiza a cada adição.

### Limpar contexto

Clique em **Limpar contexto** para zerar a seleção e o preview.

## Pastas ignoradas automaticamente

Para evitar lentidão e contexto inflado, estas pastas são excluídas:

| Pasta | Motivo |
|-------|--------|
| `.git` | Controle de versão |
| `.venv` | Ambiente Python |
| `node_modules` | Dependências Node |
| `build`, `dist` | Artefatos de build |
| `.dart_tool` | Flutter/Dart |
| `.gradle` | Android/Java |
| `android/build` | Build Android |
| `ios/Pods` | Dependências iOS |
| `__pycache__` | Cache Python |

## Visualização do contexto montado

O painel direito mostra o **preview** do markdown gerado em tempo real, conforme você adiciona arquivos.

Formato do arquivo gerado:

```markdown
# Generated Context

Projeto: nome-do-projeto

Arquivos incluídos:
- src/main.py
- README.md

Conteúdo:

## src/main.py

```text
(conteúdo do arquivo)
```
```

## Salvar contexto gerado

Clique em **Salvar contexto gerado** para persistir em:

```text
ai/context/generated/context_YYYYMMDD_HHMMSS.md
```

Útil para reutilizar, compartilhar ou auditar o que foi enviado aos agentes.

## Anexar ao prompt

Clique em **Usar no próximo prompt**:

1. O markdown é copiado para o campo **Prompt extra** na aba Operações
2. A GUI muda automaticamente para a aba Operações
3. Execute `plan`, `run` ou outro comando normalmente

Se já houver texto no prompt extra, o contexto é **anexado** com separador `---`.

## Limites de contexto

| Limite | Valor |
|--------|-------|
| Tamanho máximo do pacote | ~120.000 caracteres |
| Comportamento ao exceder | Truncamento com aviso; arquivos restantes omitidos |

Arquivos binários ou com encoding não UTF-8 são marcados como omitidos — não quebram o pacote.

## Boas práticas

### Faça

- Selecione apenas arquivos **relevantes** para a task atual
- Prefira módulos pequenos (um serviço, um componente) em vez de pastas inteiras
- Use o Context Builder **antes** de `plan` para dar visão ao architect
- Salve contextos importantes para auditoria

### Evite

- Adicionar a raiz inteira do projeto
- Incluir pastas de dependências (já filtradas, mas cuidado com pastas customizadas grandes)
- Repetir o mesmo contexto gigante em todo comando (custo e ruído)
- Confiar em arquivos gerados automaticamente (`package-lock.json`, etc.) sem necessidade

## Relação com o Context Engine

| Módulo | Função |
|--------|--------|
| **Context Engine** | Injeta automaticamente `ai/context/` e `ai/memory/<projeto>/` em todo prompt |
| **Context Builder** | Monta pacotes **ad hoc** a partir de arquivos que você escolhe |

Os dois se **complementam** — não se substituem.

## Próximo passo

- [GUI Workbench](gui_workbench.md)
- [Providers](providers.md)
- [Arquitetura](architecture.md)

# Architecture Guidelines — Diretrizes de arquitetura

Padrões de modularidade, organização, naming e versionamento para projetos que adotam o protocolo OS4AI / PAM.

---

## 1. Objetivo

Manter codebases **legíveis, evolutivos e desacoplados** — tanto no PAM quanto nos repositórios gerenciados por agentes.

---

## 2. Modularidade

### Camadas do PAM (referência)

```
src/pam/
├── main.py              # CLI — parsing, roteamento de comandos
├── config_loader.py     # YAML de projetos, paths
├── context_engine.py    # Montagem de contexto
├── agent_registry.py    # Carregamento de agentes
├── task_manager.py      # Task Lifecycle
├── session_store.py     # Persistência de sessões
├── cursor_runner.py     # Integração SDK
└── models.py            # Tipos compartilhados
```

**Regra:** cada módulo expõe uma responsabilidade. CLI não contém lógica de SDK; Task Manager não monta prompts.

### Projetos alvo

- Separar domínio, infraestrutura e interface (adaptar ao stack).
- Evitar “god modules” — arquivos > 500 linhas são candidatos a divisão planificada.

---

## 3. Separação de responsabilidades

| Componente | Responsabilidade | Não deve |
|------------|------------------|----------|
| CLI | Argumentos, help, exit codes | Lógica de negócio do projeto alvo |
| Context Engine | Ler e formatar Markdown | Executar agentes |
| Task Manager | CRUD e lifecycle de tasks | Injetar prompts |
| Session Store | JSON de sessão | Gerenciar tasks |
| Cursor Runner | SDK, modos plan/agent | Parsear CLI |
| Agent Registry | Validar e carregar `.md` | Alterar definições em runtime |

---

## 4. Organização de diretórios

### PAM / protocolo

```
project_agent_manager/
├── protocol/           # Especificação OS4AI (este sprint)
├── ai/                 # Dados operacionais do PAM
├── src/pam/            # Código Python
├── README.md
└── CHANGELOG.md
```

### Projeto gerenciado (bootstrap)

Ver [PROJECT_BOOTSTRAP.md](./PROJECT_BOOTSTRAP.md).

**Regra:** código de produção separado de `ai/` — `ai/` é meta-camada agêntica, não substitui `src/`, `lib/`, etc.

---

## 5. Naming conventions

### Tasks

- ID: `TASK-` + 4 dígitos zero-padded (`TASK-0001`)
- Filename: mesmo stem para `.md` e `.json`
- Títulos: imperativo curto (“Adicionar validação de email”)

### Agentes

- Slug lowercase: `architect`, `implementer`, `test_writer`
- Arquivo: `ai/agents/<slug>.md`

### Contexto e memória

- UPPERCASE para arquivos canônicos: `ARCHITECTURE.md`, `DECISIONS.md`
- Nomes fixos — Context Engine depende deles

### Código Python (PAM)

- snake_case para módulos e funções
- PascalCase para classes (`TaskManager`, `ContextEngine`)
- Constantes em UPPER_SNAKE: `TASK_STATUSES`, `GLOBAL_CONTEXT_FILES`

### Projetos YAML

- `ai/projects/<nome_projeto>.yaml` — nome alinhado ao slug usado na CLI

---

## 6. Versionamento

### Semver

- **MAJOR** — breaking changes em CLI, protocolo ou estrutura `ai/tasks/`
- **MINOR** — novas features compatíveis (agentes, comandos)
- **PATCH** — docs, fixes, ajustes internos

Registrar em `CHANGELOG.md` e, quando aplicável, `src/pam/__init__.py`.

### Protocolo

- Versão do protocolo documentada em `OPERATING_SYSTEM_FOR_AI_DEVELOPMENT.md`
- Sprints documentais podem bump patch (ex.: 0.6.5) sem alterar código

---

## 7. Padrões de código

### Python (PAM)

- Python 3.11+
- Type hints em APIs públicas
- Docstrings em módulos e classes principais
- `from __future__ import annotations` onde adotado

### Markdown (protocolo e ai/)

- Um H1 por documento
- Tabelas para referência rápida
- Exemplos de comando em blocos copiáveis
- Links relativos entre docs do `protocol/`

### JSON (tasks, sessions)

- UTF-8, indent 2 espaços
- Timestamps ISO 8601 UTC
- Campos oficiais estáveis — novos campos são aditivos

---

## 8. Compatibilidade e evolução

| Mudança | Estratégia |
|---------|-------------
| Novo status de task | Adicionar ao enum + pasta; documentar em TASK_LIFECYCLE |
| Novo agente | Arquivo em `ai/agents/` + registro; sem alterar existentes |
| Novo arquivo de contexto | Estender `GLOBAL_CONTEXT_FILES` com fallback gracioso |
| Path legado | Manter resolução dual (ID + path antigo) |

**Nunca** remover suporte a tasks legadas sem sprint de migração documentada.

---

## 9. Segurança e secrets

- `.env` na raiz — nunca commitado
- `ai/sessions/`, `ai/runs/` — gitignore recomendado
- Agentes não leem `.env` para incluir em prompts
- API keys apenas via variáveis de ambiente no runtime

---

## 10. Testes e qualidade

- Testes focados em comportamento (Task Manager, Context Engine, resolução de paths)
- Reviewer agente ou humano antes de merge em mudanças de core
- Sem testes triviais que apenas espelham implementação

---

## 11. Documentação como contrato

| Artefato | Contrato com |
|----------|--------------|
| `protocol/` | Humanos, agentes, outros runtimes |
| `ai/context/` | Context Engine |
| `ai/agents/` | Agent Registry |
| `ai/prompts/` | Cursor Runner |
| README | Operadores humanos |

Código e docs devem **concordar**. Divergência = bug de documentação ou de implementação.

---

## 12. Checklist de arquitetura (nova feature)

```
[ ] Responsabilidade única identificada
[ ] Módulo/diretório correto
[ ] Naming alinhado às convenções
[ ] Compatibilidade retroativa preservada
[ ] CHANGELOG e protocolo atualizados se contrato mudou
[ ] Sem acoplamento desnecessário ao SDK
[ ] Secrets fora do repo
```

---

## 13. Referências cruzadas

- Visão geral: [OPERATING_SYSTEM_FOR_AI_DEVELOPMENT.md](./OPERATING_SYSTEM_FOR_AI_DEVELOPMENT.md)
- Filosofia: [DEVELOPMENT_PHILOSOPHY.md](./DEVELOPMENT_PHILOSOPHY.md)
- Contexto: [CONTEXT_INJECTION.md](./CONTEXT_INJECTION.md)
- Implementação PAM: `ai/context/ARCHITECTURE.md`

Estas guidelines evoluem com o protocolo. Propostas de mudança passam por sprint documentada e review.

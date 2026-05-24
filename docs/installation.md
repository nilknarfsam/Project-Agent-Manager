# Instalação

Guia passo a passo para configurar o PAM no seu ambiente de desenvolvimento.

## Requisitos

| Item | Versão / detalhe |
|------|------------------|
| Python | 3.11 ou superior |
| Sistema operacional | Windows, macOS ou Linux |
| Git | Recomendado (para clonar o repositório) |
| Cursor | Conta com API key (para plan/run/review/pipeline) |
| Gemini | Opcional (para comandos `ai-*` e runtime híbrido) |

## 1. Clonar ou obter o projeto

```powershell
cd C:\src\projects
git clone <url-do-repositorio> project_agent_manager
cd project_agent_manager
```

## 2. Ambiente virtual (venv)

Recomendamos usar um ambiente virtual isolado:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows PowerShell
# source .venv/bin/activate   # macOS / Linux
```

## 3. Dependências (requirements)

```powershell
pip install -r requirements.txt
```

Pacotes principais:

| Pacote | Função |
|--------|--------|
| `cursor-sdk` | Integração com Cursor Python SDK |
| `python-dotenv` | Leitura do arquivo `.env` |
| `pyyaml` | Pipelines e configurações YAML |
| `google-genai` | Provider Gemini |

## 4. Configurar o `.env`

Copie o exemplo e edite com suas chaves:

```powershell
copy .env.example .env
```

**Nunca commite o arquivo `.env`** — ele está no `.gitignore`.

Conteúdo típico (use placeholders reais):

```env
CURSOR_API_KEY=sua_chave_cursor_aqui
GEMINI_API_KEY=sua_chave_gemini_aqui
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Onde obter as chaves

| Provider | Onde obter |
|----------|------------|
| **Cursor** | [Cursor Dashboard → Integrations](https://cursor.com/dashboard/integrations) |
| **Gemini** | [Google AI Studio](https://aistudio.google.com/apikey) |
| **OpenAI** | [platform.openai.com](https://platform.openai.com/) (reservado para futuro) |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/) (reservado para futuro) |

### Configurar via CLI (recomendado)

Entrada oculta — a chave não aparece no terminal:

```powershell
$env:PYTHONPATH = "src"
python -m pam.main set-key cursor
python -m pam.main set-key gemini
python -m pam.main settings
```

## 5. Cursor SDK

O PAM usa o [Cursor Python SDK](https://cursor.com/docs/sdk/python) para:

- `plan` — modo planejamento (sem editar arquivos)
- `run` — modo agente (implementação)
- `review` — revisão estruturada
- `resume` — retomada de sessão
- Steps de pipeline no provider Cursor

Certifique-se de que o repositório do projeto existe no disco e o caminho em `ai/projects/<nome>.yaml` está correto.

## 6. Gemini API

Gemini é **opcional** mas recomendado para:

- Comandos `ai-summary`, `ai-tasks`, `ai-docs`
- Agentes leves em pipelines híbridos (ex.: `architect`, `reviewer`)

Sem `GEMINI_API_KEY`, esses comandos falham com mensagem amigável — o restante do PAM continua funcionando.

## 7. Comandos iniciais

```powershell
$env:PYTHONPATH = "src"

# Listar projetos cadastrados
python -m pam.main --list-projects

# Listar agentes disponíveis
python -m pam.main agents

# Abrir interface gráfica
python -m pam.main gui
```

## 8. Problemas comuns

### `ModuleNotFoundError: No module named 'pam'`

Defina o PYTHONPATH antes de executar:

```powershell
$env:PYTHONPATH = "src"
```

Ou instale o pacote em modo editável (se configurado no projeto):

```powershell
pip install -e .
```

### `CURSOR_API_KEY não configurada`

Execute `python -m pam.main set-key cursor` ou edite `.env` manualmente.

### `Repositório do projeto não encontrado`

Verifique o caminho em `ai/projects/<nome>.yaml` → campo `repo_path`.

### Comando `cursor` ou `code` não encontrado (GUI)

Instale o **Shell Command** no Cursor ou VS Code:

- Cursor: Command Palette → “Install 'cursor' command”
- VS Code: Command Palette → “Shell Command: Install 'code' command”

### Tkinter não disponível (GUI)

No Windows, Tkinter vem com Python padrão. Em algumas distribuições Linux:

```bash
sudo apt install python3-tk
```

### Erro de encoding ao ler arquivos

O PAM espera arquivos de texto em UTF-8. Converta arquivos legados se necessário.

## Próximo passo

Continue com [Primeiros passos](getting_started.md) ou [Onboarding de projetos](onboarding.md).

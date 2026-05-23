# Stack — PAM

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.11+ |
| CLI | argparse |
| SDK agentico | [cursor-sdk](https://cursor.com/docs/sdk/python) |
| Config | YAML (`pyyaml`) |
| Env | python-dotenv |
| Formato de docs | Markdown em `ai/` |
| Versionamento | Git + GitHub |

## Estrutura de código

```
src/pam/
  main.py           # CLI
  config_loader.py  # projetos YAML
  cursor_runner.py  # Cursor SDK + sessões (hooks)
  context_engine.py # contexto consolidado
  session_store.py  # metadata em ai/sessions/
  models.py         # dataclasses
```

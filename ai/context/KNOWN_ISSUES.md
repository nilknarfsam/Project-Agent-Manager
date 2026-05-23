# Known Issues

## PAM

- Runtime `cloud` não implementado no `cursor_runner`.
- Context Engine injeta texto estático; não há ranking ou limite de tokens ainda.

## Cursor SDK (retomada de sessão)

Conforme [documentação do Cursor Python SDK](https://cursor.com/docs/sdk/python):

- **`agent.model` pode ser `None` ao retomar** se o modelo não for informado nas opções de resume.
- **MCP inline não é preservado** ao retomar um agente — configurações MCP precisam ser reaplicadas se necessário.
- **Execução cloud** ainda não implementada no PAM (apenas runtime local).

## Operacional

- Requer `CURSOR_API_KEY` em `.env` para plan/run/review/resume.
- Caminhos de `repo_path` nos YAMLs são absolutos (Windows); ajustar por máquina.
- JSON corrompido em `ai/sessions/` exige `clear-session` antes de nova execução.

# Known Issues

## PAM

- `resume` ainda não executa o agente — apenas localiza e exibe metadata de sessão.
- Sessões não usam `Agent.resume()` até Sprint 3.
- Runtime `cloud` não implementado no `cursor_runner`.
- Context Engine injeta texto estático; não há ranking ou limite de tokens ainda.

## Operacional

- Requer `CURSOR_API_KEY` em `.env` para plan/run/review.
- Caminhos de `repo_path` nos YAMLs são absolutos (Windows); ajustar por máquina.

# Repository Guidelines

## Project Structure & Module Organization

This repository contains a FastAPI/PostgreSQL backend and a Telegram bot:

- `backend/` — API routes (`api.py`), database schema/migrations (`*.sql`),
  scheduled pipeline (`dailypipeline.py`), and seed scripts.
- `frontend/` — Telegram application entry point (`main.py`), handlers,
  keyboards, API client, and configuration.
- `docker-compose.*.yml` — local, staging, and production service definitions.
- `README.md` — environment setup and deployment notes.

There is no dedicated test suite currently; keep new tests close to the code or
under a future `tests/` directory rather than adding ad-hoc scripts to the root.

## Build, Test, and Development Commands

Use the repository root unless noted otherwise:

```powershell
docker compose -f .\docker-compose.local.yml up --build
python -m py_compile backend\api.py frontend\handlers\*.py
Set-Location backend; python seed_demo_tracking.py --district "TO RANTAU PRAPAT" --sites RNT001,RNT002
```

The first command starts PostgreSQL, seeds development data, and runs services.
The second catches Python syntax errors. The demo seeder writes aggregate
tracking rows only; it does not create tickets.

## Coding Style & Naming Conventions

Use Python 3.12-compatible code, four-space indentation, and PEP 8 naming:
`snake_case` for functions/variables, `PascalCase` for Pydantic models, and
uppercase constants. Keep handlers thin and put backend calls in
`frontend/api_client.py`. Preserve parameterized SQL (`%s`) and schema-qualified
table names. Run `git diff --check` before submitting changes.

## Testing Guidelines

No framework or coverage threshold is configured. At minimum, run `py_compile`
for modified Python files and exercise affected API/bot flows against the local
Compose stack. Add deterministic tests when introducing non-trivial business
logic.

## Commit & Pull Request Guidelines

Recent commits use short, lowercase Conventional Commit-style subjects such as
`feat: add management view`, `refactor: ...`, and `chore: ...`. Keep commits
focused. Pull requests should describe behavior changes, configuration or
migration steps, validation commands, and screenshots for Telegram UI changes.

## Security & Configuration

Never commit `.env` files, tokens, passwords, or production data. Use the
provided `.env.*.example` files, and keep development database settings
separate from staging/production credentials.

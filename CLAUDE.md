# CLAUDE.md

## Project Overview

Django REST Framework project with Clean Architecture (DDD) pattern. Two apps: `users` and `books`.

## Architecture

Each app follows 4-layer structure inside `apps/<app>/`:
- `domain/` — Pure Python entities, exceptions (no framework imports)
- `application/` — Services, abstract interfaces (imports domain only)
- `infrastructure/` — Django ORM models, repositories (imports domain + application)
- `presentation/` — DRF views, serializers, permissions, urls (imports all layers)

**Import rule:** Inner layers never import from outer layers.

Root-level `models.py` and `managers.py` in each app are proxy re-exports for Django model discovery — do not remove them.

## Commands

All commands use `uv` (not pip):

```bash
make install          # uv sync --all-extras
make run              # runserver 0.0.0.0:8000
make test             # uv run pytest -v
make migrate          # makemigrations + migrate
make lint             # ruff check apps/
```

## Tech Stack

- Python 3.12+, Django 5.1, DRF 3.15
- JWT auth (simplejwt), PostgreSQL (psycopg3)
- drf-spectacular (Swagger/ReDoc), django-filter
- pytest + pytest-django + factory-boy for testing

## API Endpoints

- `/api/users/` — User registration, auth, profile
- `/api/books/` — Book CRUD with filtering
- `/api/docs/` — Swagger UI
- `/api/redoc/` — ReDoc
- `/admin/` — Django admin

## Testing

```bash
uv run pytest -v                              # all tests
uv run pytest apps/books/tests/ -v            # single app
uv run pytest -v --cov=apps --cov-report=term-missing  # with coverage
```

Settings module: `config.settings` (set via DJANGO_SETTINGS_MODULE in pyproject.toml).

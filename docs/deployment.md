# Deployment (Production)

**Complete guide** for deploying the project to a production environment.

## Docker Setup

### Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System libraries (PostgreSQL client)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

# Install uv and dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN uv sync --frozen --no-dev

COPY . .

RUN uv run python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

### docker-compose.yml

```yaml
version: "3.8"

services:
  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: drf_db
      POSTGRES_USER: drf_user
      POSTGRES_PASSWORD: your_secure_password
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env

volumes:
  postgres_data:
  redis_data:
```

### Starting Up

```bash
# Configure the .env file
cp .env.example .env
# Update the values in .env for production

# Start with Docker
docker-compose up -d --build

# Run migrations
docker-compose exec web uv run python manage.py migrate --no-input

# Create superuser
docker-compose exec web uv run python manage.py createsuperuser
```

## Environment Variables (Production)

| Variable | Description | Production example |
|----------|-------------|-------------------|
| `DJANGO_ENV` | Environment name | `production` |
| `SECRET_KEY` | Django secret key (50+ characters) | `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed domains | `api.example.com,www.example.com` |
| `DB_NAME` | PostgreSQL database name | `drf_production` |
| `DB_USER` | PostgreSQL user | `drf_prod_user` |
| `DB_PASSWORD` | PostgreSQL password | Strong password |
| `DB_HOST` | Database host | `db` (Docker) or RDS URL |
| `DB_PORT` | Database port | `5432` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `CORS_ALLOWED_ORIGINS` | Frontend URLs | `https://app.example.com` |

> **Important:** Never commit `SECRET_KEY` to git. The `.env` file should be in `.gitignore`.

## PostgreSQL Setup (without Docker)

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE drf_production;
CREATE USER drf_prod_user WITH PASSWORD 'your_secure_password';
ALTER ROLE drf_prod_user SET client_encoding TO 'utf8';
ALTER ROLE drf_prod_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE drf_prod_user SET timezone TO 'Asia/Tashkent';
GRANT ALL PRIVILEGES ON DATABASE drf_production TO drf_prod_user;
\q

# Test the connection
psql -U drf_prod_user -d drf_production -h localhost
```

## Redis Setup (without Docker)

```bash
# Install
sudo apt install redis-server

# Start
sudo systemctl start redis
sudo systemctl enable redis

# Test
redis-cli ping    # Should respond with PONG
```

Redis is used for two purposes in the project:
- **Cache:** Caching frequently requested data
- **Sessions:** Storing user sessions

## Gunicorn Configuration

```bash
# Simple startup
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Recommended for production
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile /var/log/gunicorn/access.log \
  --error-logfile /var/log/gunicorn/error.log
```

**Number of workers:** Calculate using the formula `(2 * CPU_CORES) + 1`.
For example, for a 2-core server: `(2 * 2) + 1 = 5` workers.

## Security Checklist

The following settings are automatically enabled in production via `config/settings/production.py`:

| Setting | Value | Description |
|---------|-------|-------------|
| `DEBUG` | `False` | Debug mode disabled |
| `SECURE_SSL_REDIRECT` | `True` | HTTP → HTTPS redirect |
| `SECURE_HSTS_SECONDS` | `31536000` | HSTS — 1 year |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` | Subdomains also use HTTPS |
| `SESSION_COOKIE_SECURE` | `True` | Session cookie HTTPS only |
| `CSRF_COOKIE_SECURE` | `True` | CSRF cookie HTTPS only |
| `X_FRAME_OPTIONS` | `DENY` | Clickjacking protection |
| `CORS_ALLOW_ALL_ORIGINS` | `False` | Only specified origins allowed |

> These settings are automatically activated when `DJANGO_ENV=production` is set.

## CI/CD Pipeline (GitHub Actions)

`.github/workflows/ci.yml` example:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:6-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Python setup
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Lint check
        run: uv run ruff check apps/

      - name: Run tests
        env:
          DJANGO_ENV: development
          SECRET_KEY: test-secret-key-for-ci
          DB_NAME: test_db
          DB_USER: test_user
          DB_PASSWORD: test_pass
          DB_HOST: localhost
          DB_PORT: 5432
          REDIS_URL: redis://localhost:6379/0
        run: uv run pytest -v --cov=apps
```

## Static Files

```bash
# Collect static
uv run python manage.py collectstatic --noinput

# Static files are collected to STATIC_ROOT = BASE_DIR / "staticfiles"
# Serve them via Nginx or CDN
```

Nginx example:
```nginx
location /static/ {
    alias /app/staticfiles/;
}
```

## Migration (Production)

```bash
# With Docker
docker-compose exec web uv run python manage.py migrate --no-input

# Without Docker
DJANGO_ENV=production uv run python manage.py migrate --no-input
```

> **Important:** Don't run `makemigrations` in production — only `migrate`.
> Create migration files in development and deploy them via git.

## Backup

```bash
# PostgreSQL backup
pg_dump -U drf_prod_user drf_production > backup_$(date +%Y%m%d).sql

# Restore
psql -U drf_prod_user drf_production < backup_20240115.sql
```

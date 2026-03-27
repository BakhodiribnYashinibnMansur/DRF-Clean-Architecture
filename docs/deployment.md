# Deployment (Production ga Chiqarish)

**Loyihani production muhitga deploy qilish** uchun to'liq yo'riqnoma.

## Docker Setup

### Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Tizim kutubxonalari (PostgreSQL client)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

# uv o'rnatish va dependencylar
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

### Ishga tushirish

```bash
# .env faylini sozlash
cp .env.example .env
# .env ichidagi qiymatlarni production uchun o'zgartiring

# Docker bilan ishga tushirish
docker-compose up -d --build

# Migratsiyalar
docker-compose exec web uv run python manage.py migrate --no-input

# Superuser yaratish
docker-compose exec web uv run python manage.py createsuperuser
```

## Environment Variables (Production)

| O'zgaruvchi | Tavsif | Production misol |
|------------|--------|-----------------|
| `DJANGO_ENV` | Muhit nomi | `production` |
| `SECRET_KEY` | Django maxfiy kalit (50+ belgi) | `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | Debug rejim | `False` |
| `ALLOWED_HOSTS` | Ruxsat etilgan domenlar | `api.example.com,www.example.com` |
| `DB_NAME` | PostgreSQL database nomi | `drf_production` |
| `DB_USER` | PostgreSQL foydalanuvchi | `drf_prod_user` |
| `DB_PASSWORD` | PostgreSQL parol | Kuchli parol |
| `DB_HOST` | Database host | `db` (Docker) yoki RDS URL |
| `DB_PORT` | Database port | `5432` |
| `REDIS_URL` | Redis ulanish URL | `redis://redis:6379/0` |
| `CORS_ALLOWED_ORIGINS` | Frontend URL lari | `https://app.example.com` |

> **Muhim:** `SECRET_KEY` ni hech qachon git ga commit qilmang. `.env` fayli `.gitignore` da bo'lishi kerak.

## PostgreSQL Setup (Docker siz)

```bash
# PostgreSQL o'rnatish (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib

# Database va user yaratish
sudo -u postgres psql
CREATE DATABASE drf_production;
CREATE USER drf_prod_user WITH PASSWORD 'your_secure_password';
ALTER ROLE drf_prod_user SET client_encoding TO 'utf8';
ALTER ROLE drf_prod_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE drf_prod_user SET timezone TO 'Asia/Tashkent';
GRANT ALL PRIVILEGES ON DATABASE drf_production TO drf_prod_user;
\q

# Ulanishni tekshirish
psql -U drf_prod_user -d drf_production -h localhost
```

## Redis Setup (Docker siz)

```bash
# O'rnatish
sudo apt install redis-server

# Ishga tushirish
sudo systemctl start redis
sudo systemctl enable redis

# Tekshirish
redis-cli ping    # PONG javob berishi kerak
```

Loyihada Redis ikki maqsadda ishlatiladi:
- **Cache:** Tez-tez so'raladigan ma'lumotlarni keshlash
- **Sessions:** Foydalanuvchi sessiyalarini saqlash

## Gunicorn Konfiguratsiyasi

```bash
# Oddiy ishga tushirish
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Production uchun tavsiya
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile /var/log/gunicorn/access.log \
  --error-logfile /var/log/gunicorn/error.log
```

**Workers soni:** `(2 * CPU_CORES) + 1` formulasi bilan hisoblang.
Masalan, 2 yadroli server uchun: `(2 * 2) + 1 = 5` worker.

## Security Checklist

Production muhitda quyidagi sozlamalar `config/settings/production.py` da avtomatik yoqiladi:

| Sozlama | Qiymat | Tavsif |
|---------|--------|--------|
| `DEBUG` | `False` | Debug rejim o'chirilgan |
| `SECURE_SSL_REDIRECT` | `True` | HTTP → HTTPS ga yo'naltirish |
| `SECURE_HSTS_SECONDS` | `31536000` | HSTS — 1 yil |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` | Subdomenlar ham HTTPS |
| `SESSION_COOKIE_SECURE` | `True` | Session cookie faqat HTTPS |
| `CSRF_COOKIE_SECURE` | `True` | CSRF cookie faqat HTTPS |
| `X_FRAME_OPTIONS` | `DENY` | Clickjacking himoyasi |
| `CORS_ALLOW_ALL_ORIGINS` | `False` | Faqat belgilangan originlar |

> `DJANGO_ENV=production` o'rnatilganda bu sozlamalar avtomatik faollashadi.

## CI/CD Pipeline (GitHub Actions)

`.github/workflows/ci.yml` misoli:

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

      - name: uv o'rnatish
        uses: astral-sh/setup-uv@v4

      - name: Dependencies o'rnatish
        run: uv sync --all-extras

      - name: Lint tekshirish
        run: uv run ruff check apps/

      - name: Testlarni ishga tushirish
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

## Static Fayllar

```bash
# Collect static
uv run python manage.py collectstatic --noinput

# Static fayllar STATIC_ROOT = BASE_DIR / "staticfiles" ga yig'iladi
# Nginx yoki CDN orqali xizmat ko'rsating
```

Nginx misoli:
```nginx
location /static/ {
    alias /app/staticfiles/;
}
```

## Migration (Production)

```bash
# Docker bilan
docker-compose exec web uv run python manage.py migrate --no-input

# Docker siz
DJANGO_ENV=production uv run python manage.py migrate --no-input
```

> **Muhim:** Production da `makemigrations` ishlatmang — faqat `migrate`.
> Migration fayllarini development da yaratib, git orqali deploy qiling.

## Backup

```bash
# PostgreSQL backup
pg_dump -U drf_prod_user drf_production > backup_$(date +%Y%m%d).sql

# Restore
psql -U drf_prod_user drf_production < backup_20240115.sql
```

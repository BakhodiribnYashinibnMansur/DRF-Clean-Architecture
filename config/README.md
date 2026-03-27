# Config — Django Project Configuration

## Vazifasi

Django loyihasining markaziy konfiguratsiyasi. Settings, URL routing, WSGI/ASGI.

## Fayllar

### `settings/` — Environment-based Settings

```
settings/
├── __init__.py      # DJANGO_ENV ga qarab dev yoki prod yuklaydi
├── base.py          # Umumiy sozlamalar (DRF, JWT, Redis, DB, CORS)
├── development.py   # DEBUG=True, CORS_ALLOW_ALL
└── production.py    # DEBUG=False, SSL, HSTS, Secure Cookies
```

**`base.py`** asosiy sozlamalar:
- `AUTH_USER_MODEL = "users.CustomUser"` — email-based auth
- `REST_FRAMEWORK` — JWT auth, pagination (10), filtering, throttling
- `SIMPLE_JWT` — access: 30 min, refresh: 7 kun
- `CACHES` — Redis (django-redis)
- `SESSION_ENGINE` — Redis-based sessions
- `SPECTACULAR_SETTINGS` — Swagger konfiguratsiya
- `DATABASES` — PostgreSQL (env variables orqali)

**`development.py`**: Debug rejim, CORS cheklovsiz.

**`production.py`**: SSL redirect, HSTS, secure cookies, strict CORS.

### `urls.py` — Root URL Routing
```
/admin/              → Django Admin
/api/users/          → apps.users.presentation.urls
/api/books/          → apps.books.presentation.urls
/api/schema/         → OpenAPI schema (JSON)
/api/docs/           → Swagger UI
/api/redoc/          → ReDoc
```

### `wsgi.py` / `asgi.py`
Production server entry pointlari (Gunicorn, Uvicorn uchun).

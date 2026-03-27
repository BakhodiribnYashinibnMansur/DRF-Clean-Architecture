# Troubleshooting

**Common errors** and their solutions.

## PostgreSQL Issues

### "could not connect to server" / "Connection refused"

**Cause:** PostgreSQL server is not running.

**Solution:**
```bash
# Check status
sudo systemctl status postgresql

# Start
sudo systemctl start postgresql

# With Docker
docker-compose up -d db
```

Check `DB_HOST` and `DB_PORT` in `.env`.

### "FATAL: password authentication failed"

**Cause:** Incorrect `DB_USER` or `DB_PASSWORD`.

**Solution:**
```bash
# Check .env
cat .env | grep DB_

# Try connecting directly to the database
psql -U drf_user -d drf_db -h localhost
```

### "database does not exist"

**Cause:** Database has not been created yet.

**Solution:**
```bash
# Create via PostgreSQL
sudo -u postgres createdb drf_db

# Or inside psql
sudo -u postgres psql -c "CREATE DATABASE drf_db;"
```

### "relation does not exist"

**Cause:** Migrations have not been applied.

**Solution:**
```bash
make migrate
# or
uv run python manage.py makemigrations && uv run python manage.py migrate
```

## Redis Issues

### "Error connecting to Redis" / "Connection refused"

**Cause:** Redis server is not running.

**Solution:**
```bash
# Check status
sudo systemctl status redis

# Start
sudo systemctl start redis

# With Docker
docker-compose up -d redis

# Test
redis-cli ping    # Should respond with PONG
```

Check `REDIS_URL` in `.env` (default: `redis://127.0.0.1:6379/0`).

### "NOAUTH Authentication required"

**Cause:** Redis is password-protected.

**Solution:**
```bash
# Add password to .env
REDIS_URL=redis://:your_password@127.0.0.1:6379/0
```

### Running without Redis

If Redis is down, cache and sessions won't work. Temporary solution —
change the cache backend in `config/settings/base.py`:

```python
# Temporary (development only!)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
```

> **Important:** This is for development only. Redis must be used in production.

## JWT Token Issues

### "Authentication credentials were not provided" (401)

**Cause:** `Authorization` header is missing or has incorrect format.

**Solution:**
```bash
# Correct format
curl -H "Authorization: Bearer eyJ0eXAi..."

# Incorrect formats:
# curl -H "Authorization: eyJ0eXAi..."        # Missing "Bearer" keyword
# curl -H "Authorization: bearer eyJ0eXAi..."  # Lowercase "b"
# curl -H "Auth: Bearer eyJ0eXAi..."           # Wrong header name
```

### "Given token not valid for any token type" (401)

**Cause:** Access token has expired (30 minutes).

**Solution:**
```bash
# Get a new access token using the refresh token
curl -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAi..."}'
```

### "Token is invalid or expired" (refresh token)

**Cause:** Refresh token has expired (7 days).

**Solution:** Log in again:
```bash
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your_password"}'
```

### "No active account found with the given credentials"

**Cause:** Email or password is incorrect, or `is_active=False`.

**Solution:**
1. Verify the email is spelled correctly
2. Check the password (case-sensitive)
3. Check the user's `is_active` status from admin panel:
```bash
uv run python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.filter(email='user@example.com').first()
print(f'Found: {user is not None}')
if user: print(f'is_active: {user.is_active}')
"
```

## Migration Issues

### "No changes detected"

**Cause:** No model changes or the app is not in `INSTALLED_APPS`.

**Solution:**
```bash
# Check INSTALLED_APPS (config/settings/base.py)
# Should contain "apps.books.apps.BooksConfig" and "apps.users.apps.UsersConfig"

# Try specifying the app name explicitly
uv run python manage.py makemigrations books
uv run python manage.py makemigrations users
```

### "Conflicting migrations"

**Cause:** Two people created migrations at the same time.

**Solution:**
```bash
uv run python manage.py makemigrations --merge
```

### "django.db.utils.ProgrammingError: relation already exists"

**Cause:** Migration and DB state are out of sync.

**Solution:**
```bash
# Be careful — this marks the migration as applied
uv run python manage.py migrate --fake
```

> **Warning:** Only use `--fake` when you are absolutely certain.

### Proxy model migration error

**Cause:** `apps/books/models.py` is not importing from `infrastructure/models.py`.

**Solution:** Check the proxy file:
```python
# apps/books/models.py — correct format:
from apps.books.infrastructure.models import Book
__all__ = ["Book"]
```

## Permission Issues

### "You do not have permission to perform this action" (403)

**Cause:** The user does not have sufficient permissions.

| Scenario | Solution |
|----------|----------|
| Update/delete book | Must be the owner or admin |
| User manage (list, create, delete) | Must be admin (`is_staff=True`) |
| User manage (retrieve, update) | Must be admin or the same user |
| Profile | Must be authenticated |

### "Method not allowed" (405)

**Cause:** The endpoint doesn't support this HTTP method.

For example:
- `DELETE /api/users/profile/` — profile only supports `GET`, `PATCH`
- `POST /api/books/1/` — detail endpoint doesn't support `POST`

## General Django Errors

### "ImproperlyConfigured: The SECRET_KEY setting must not be empty"

**Cause:** `.env` file is missing or `SECRET_KEY` is empty.

**Solution:**
```bash
cp .env.example .env
# Fill in the SECRET_KEY in .env
```

### "ModuleNotFoundError: No module named '...'"

**Cause:** Python package is not installed.

**Solution:**
```bash
make install
# or
uv sync --all-extras
```

### "DisallowedHost at /"

**Cause:** Server hostname is not in `ALLOWED_HOSTS`.

**Solution:**
```bash
# Add to .env
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

## Throttling (429 Too Many Requests)

**Cause:** Request count exceeded the limit.

| User type | Limit |
|-----------|-------|
| Anonymous | 100 requests/hour |
| Authenticated | 1000 requests/hour |

**Solution:**
1. Wait (limit resets every hour)
2. Authenticate (to avoid the anonymous limit)
3. Disable throttle for development (not recommended)

## Debugging Methods

```bash
# Django shell — interactive inspection
make shell
# or
uv run python manage.py shell

# Django admin panel
# http://localhost:8000/admin/ (with superuser)

# Swagger UI — interactive API test
# http://localhost:8000/api/docs/

# Run tests with detailed output
pytest -v --tb=long

# Only failed tests
pytest --lf -v

# Development mode — detailed error pages
# In .env: DJANGO_ENV=development
```

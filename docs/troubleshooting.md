# Muammolarni Hal Qilish (Troubleshooting)

**Ko'p uchraydigan xatolar** va ularning yechimlari.

## PostgreSQL Muammolari

### "could not connect to server" / "Connection refused"

**Sabab:** PostgreSQL serveri ishlamayapti.

**Yechim:**
```bash
# Holatni tekshirish
sudo systemctl status postgresql

# Ishga tushirish
sudo systemctl start postgresql

# Docker bilan
docker-compose up -d db
```

`.env` dagi `DB_HOST` va `DB_PORT` ni tekshiring.

### "FATAL: password authentication failed"

**Sabab:** Noto'g'ri `DB_USER` yoki `DB_PASSWORD`.

**Yechim:**
```bash
# .env ni tekshiring
cat .env | grep DB_

# Bazaga to'g'ridan-to'g'ri ulanib ko'ring
psql -U drf_user -d drf_db -h localhost
```

### "database does not exist"

**Sabab:** Database hali yaratilmagan.

**Yechim:**
```bash
# PostgreSQL ga kirib yaratish
sudo -u postgres createdb drf_db

# yoki psql ichida
sudo -u postgres psql -c "CREATE DATABASE drf_db;"
```

### "relation does not exist"

**Sabab:** Migratsiyalar qo'llanilmagan.

**Yechim:**
```bash
make migrate
# yoki
python manage.py makemigrations && python manage.py migrate
```

## Redis Muammolari

### "Error connecting to Redis" / "Connection refused"

**Sabab:** Redis serveri ishlamayapti.

**Yechim:**
```bash
# Holatni tekshirish
sudo systemctl status redis

# Ishga tushirish
sudo systemctl start redis

# Docker bilan
docker-compose up -d redis

# Tekshirish
redis-cli ping    # PONG javob berishi kerak
```

`.env` dagi `REDIS_URL` ni tekshiring (default: `redis://127.0.0.1:6379/0`).

### "NOAUTH Authentication required"

**Sabab:** Redis parol bilan himoyalangan.

**Yechim:**
```bash
# .env da parolni qo'shing
REDIS_URL=redis://:your_password@127.0.0.1:6379/0
```

### Redis o'chirilgan holatda ishlash

Redis o'chirilsa, cache va sessionlar ishlamaydi. Vaqtinchalik yechim —
`config/settings/base.py` da cache backend ni o'zgartirish:

```python
# Vaqtinchalik (faqat development uchun!)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
```

> **Muhim:** Bu faqat development uchun. Production da Redis ishlatilishi shart.

## JWT Token Muammolari

### "Authentication credentials were not provided" (401)

**Sabab:** `Authorization` header yo'q yoki noto'g'ri format.

**Yechim:**
```bash
# To'g'ri format
curl -H "Authorization: Bearer eyJ0eXAi..."

# Noto'g'ri formatlar:
# curl -H "Authorization: eyJ0eXAi..."        # "Bearer" so'zi yo'q
# curl -H "Authorization: bearer eyJ0eXAi..."  # "b" kichik harf
# curl -H "Auth: Bearer eyJ0eXAi..."           # Noto'g'ri header nomi
```

### "Given token not valid for any token type" (401)

**Sabab:** Access token muddati tugagan (30 daqiqa).

**Yechim:**
```bash
# Refresh token bilan yangi access token olish
curl -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAi..."}'
```

### "Token is invalid or expired" (refresh token)

**Sabab:** Refresh token muddati tugagan (7 kun).

**Yechim:** Qaytadan login qilish:
```bash
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your_password"}'
```

### "No active account found with the given credentials"

**Sabab:** Email yoki parol noto'g'ri, yoki `is_active=False`.

**Yechim:**
1. Email to'g'ri yozilganini tekshiring
2. Parolni tekshiring (case-sensitive)
3. Admin paneldan foydalanuvchining `is_active` holatini tekshiring:
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.filter(email='user@example.com').first()
print(f'Topildi: {user is not None}')
if user: print(f'is_active: {user.is_active}')
"
```

## Migration Muammolari

### "No changes detected"

**Sabab:** Model o'zgarish yo'q yoki app `INSTALLED_APPS` da yo'q.

**Yechim:**
```bash
# INSTALLED_APPS ni tekshiring (config/settings/base.py)
# "apps.books.apps.BooksConfig" va "apps.users.apps.UsersConfig" bo'lishi kerak

# App nomini aniq ko'rsatib ko'ring
python manage.py makemigrations books
python manage.py makemigrations users
```

### "Conflicting migrations"

**Sabab:** Bir vaqtda ikki kishi migration yaratdi.

**Yechim:**
```bash
python manage.py makemigrations --merge
```

### "django.db.utils.ProgrammingError: relation already exists"

**Sabab:** Migration va DB holati mos kelmaydi.

**Yechim:**
```bash
# Ehtiyot bo'ling — bu migration ni qo'llanildi deb belgilaydi
python manage.py migrate --fake
```

> **Ogohlantirish:** `--fake` faqat ishonchingiz komil bo'lganda ishlatilsin.

### Proxy model migration xatosi

**Sabab:** `apps/books/models.py` fayli `infrastructure/models.py` dan import qilmayapti.

**Yechim:** Proxy faylni tekshiring:
```python
# apps/books/models.py — to'g'ri ko'rinishi:
from apps.books.infrastructure.models import Book
__all__ = ["Book"]
```

## Permission Muammolari

### "You do not have permission to perform this action" (403)

**Sabab:** Foydalanuvchining ruxsati yetarli emas.

| Holat | Yechim |
|-------|--------|
| Kitob o'zgartirish/o'chirish | Owner yoki admin bo'lish kerak |
| User manage (list, create, delete) | Admin (`is_staff=True`) bo'lish kerak |
| User manage (retrieve, update) | Admin yoki o'sha user bo'lish kerak |
| Profil | Autentifikatsiya qilingan bo'lish kerak |

### "Method not allowed" (405)

**Sabab:** Endpoint bu HTTP methodini qo'llab-quvvatlamaydi.

Masalan:
- `DELETE /api/users/profile/` — profile faqat `GET`, `PATCH` qo'llab-quvvatlaydi
- `POST /api/books/1/` — detail endpoint `POST` qo'llab-quvvatlamaydi

## Umumiy Django Xatolari

### "ImproperlyConfigured: The SECRET_KEY setting must not be empty"

**Sabab:** `.env` fayli yo'q yoki `SECRET_KEY` bo'sh.

**Yechim:**
```bash
cp .env.example .env
# .env ichidagi SECRET_KEY ni to'ldiring
```

### "ModuleNotFoundError: No module named '...'"

**Sabab:** Python kutubxona o'rnatilmagan.

**Yechim:**
```bash
make install
# yoki
pip install -r requirements.txt
```

### "DisallowedHost at /"

**Sabab:** `ALLOWED_HOSTS` da server host nomi yo'q.

**Yechim:**
```bash
# .env da qo'shing
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

## Throttling (429 Too Many Requests)

**Sabab:** So'rovlar soni limitdan oshdi.

| Foydalanuvchi turi | Limit |
|-------------------|-------|
| Anonim | 100 so'rov/soat |
| Autentifikatsiya qilingan | 1000 so'rov/soat |

**Yechim:**
1. Kutish (limit har soatda yangilanadi)
2. Autentifikatsiya qilish (anonim limitdan qochish uchun)
3. Development uchun throttle o'chirish (tavsiya etilmaydi)

## Debug Qilish Usullari

```bash
# Django shell — interaktiv tekshirish
make shell
# yoki
python manage.py shell

# Django admin panel
# http://localhost:8000/admin/ (superuser bilan)

# Swagger UI — interaktiv API test
# http://localhost:8000/api/docs/

# Testlarni batafsil ishga tushirish
pytest -v --tb=long

# Faqat muvaffaqiyatsiz testlar
pytest --lf -v

# Development rejim — batafsil xato sahifalari
# .env da: DJANGO_ENV=development
```

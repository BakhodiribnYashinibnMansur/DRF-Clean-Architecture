# Ma'lumotlar Bazasi (Database)

**PostgreSQL 16** — asosiy ma'lumotlar bazasi. **Redis 6.x** — cache va sessionlar uchun.

## ER Diagramma

```
+-------------------------+           +-------------------------+
|    users_customuser     |           |       books_book        |
+-------------------------+           +-------------------------+
| id         BIGSERIAL PK |<---+     | id         BIGSERIAL PK |
| email      VARCHAR UQ   |    +-----| created_by_id BIGINT FK |
| password   VARCHAR(128) |          | title      VARCHAR(255) |
| first_name VARCHAR(150) |          | author     VARCHAR(255) |
| last_name  VARCHAR(150) |          | isbn       VARCHAR(13) UQ|
| bio        TEXT          |          | published_date DATE     |
| date_of_birth DATE NULL  |          | page_count INTEGER      |
| is_active  BOOLEAN       |          | language   VARCHAR(50)  |
| is_staff   BOOLEAN       |          | genre      VARCHAR(20)  |
| is_superuser BOOLEAN     |          | description TEXT        |
| date_joined TIMESTAMPTZ  |          | created_at TIMESTAMPTZ  |
| last_login TIMESTAMPTZ   |          | updated_at TIMESTAMPTZ  |
+-------------------------+           +-------------------------+
```

**Aloqa:** `books_book.created_by_id` → `users_customuser.id` (ForeignKey, ON DELETE SET NULL)

## Jadvallar Tavsifi

### `users_customuser`

Django `AbstractUser` dan meros olgan. `username` olib tashlangan — `email` asosiy identifikator.

| Ustun | Turi | Null | Default | Constraint | Tavsif |
|-------|------|------|---------|------------|--------|
| `id` | BigAutoField | Yo'q | auto | PRIMARY KEY | Avtomatik ID |
| `email` | EmailField | Yo'q | — | UNIQUE | Login uchun email |
| `password` | CharField(128) | Yo'q | — | — | Hashed parol (bcrypt) |
| `first_name` | CharField(150) | Yo'q | `""` | — | Ism |
| `last_name` | CharField(150) | Yo'q | `""` | — | Familiya |
| `bio` | TextField | Yo'q | `""` | — | Biografiya (ixtiyoriy) |
| `date_of_birth` | DateField | Ha | `NULL` | — | Tug'ilgan sana |
| `is_active` | BooleanField | Yo'q | `True` | — | Aktiv holat |
| `is_staff` | BooleanField | Yo'q | `False` | — | Admin panelga kirish |
| `is_superuser` | BooleanField | Yo'q | `False` | — | To'liq huquq |
| `date_joined` | DateTimeField | Yo'q | `auto_now_add` | — | Ro'yxatdan o'tgan vaqt |
| `last_login` | DateTimeField | Ha | `NULL` | — | Oxirgi kirish vaqti |

**Ordering:** `-date_joined` (eng yangi birinchi)

### `books_book`

| Ustun | Turi | Null | Default | Constraint | Tavsif |
|-------|------|------|---------|------------|--------|
| `id` | BigAutoField | Yo'q | auto | PRIMARY KEY | Avtomatik ID |
| `title` | CharField(255) | Yo'q | — | — | Kitob nomi |
| `author` | CharField(255) | Yo'q | — | — | Muallif ismi |
| `isbn` | CharField(13) | Yo'q | — | UNIQUE, RegexValidator | ISBN (10 yoki 13 raqam) |
| `published_date` | DateField | Yo'q | — | — | Nashr sanasi |
| `page_count` | PositiveIntegerField | Yo'q | — | >= 0 | Sahifalar soni |
| `language` | CharField(50) | Yo'q | `"English"` | — | Til |
| `genre` | CharField(20) | Yo'q | `"other"` | choices, db_index | Janr (14 ta tanlov) |
| `description` | TextField | Yo'q | `""` | — | Tavsif (ixtiyoriy) |
| `created_by_id` | ForeignKey | Ha | `NULL` | FK → users_customuser | Yaratuvchi |
| `created_at` | DateTimeField | Yo'q | `auto_now_add` | — | Yaratilgan vaqt |
| `updated_at` | DateTimeField | Yo'q | `auto_now` | — | O'zgartirilgan vaqt |

**Ordering:** `-created_at` (eng yangi birinchi)

**ISBN Validator:**
```python
regex = r"^\d{10}(\d{3})?$"
# To'g'ri: "1234567890" (10 raqam), "1234567890123" (13 raqam)
# Noto'g'ri: "123", "ISBN-10", "12345678901" (11 raqam)
```

## Genre Turlari

| Qiymat | Ko'rinishi |
|--------|-----------|
| `fiction` | Fiction |
| `non_fiction` | Non-Fiction |
| `science` | Science |
| `technology` | Technology |
| `history` | History |
| `biography` | Biography |
| `philosophy` | Philosophy |
| `poetry` | Poetry |
| `romance` | Romance |
| `thriller` | Thriller |
| `fantasy` | Fantasy |
| `mystery` | Mystery |
| `self_help` | Self-Help |
| `other` | Other |

## Indexlar

### `books_book` indexlari

| Index nomi | Ustun(lar) | Turi | Sabab |
|-----------|-----------|------|-------|
| `idx_book_isbn` | `isbn` | B-tree | ISBN bo'yicha tez qidirish |
| `idx_book_author` | `author` | B-tree | Muallif bo'yicha filtrlash |
| `idx_book_created` | `-created_at` | B-tree (desc) | Default ordering tezlashtirish |
| `books_book_genre_...` | `genre` | B-tree | Genre bo'yicha filtrlash (`db_index=True`) |
| `books_book_isbn_key` | `isbn` | UNIQUE | Takrorlanmas ISBN |

### `users_customuser` indexlari

| Index nomi | Ustun(lar) | Turi |
|-----------|-----------|------|
| `users_customuser_pkey` | `id` | PRIMARY KEY |
| `users_customuser_email_key` | `email` | UNIQUE |

## On Delete Xatti-harakatlari

| Aloqa | On Delete | Natija |
|-------|-----------|--------|
| `Book.created_by` → `CustomUser` | `SET_NULL` | User o'chirilsa, kitob qoladi (`created_by = NULL`) |
| `User.groups` (M2M) | `CASCADE` | User o'chirilsa, guruh aloqasi ham o'chadi |
| `User.user_permissions` (M2M) | `CASCADE` | User o'chirilsa, ruxsat aloqasi ham o'chadi |

## Django Tizim Jadvallari

Loyihada avtomatik yaratilgan jadvallar:

| Jadval | Vazifa |
|--------|--------|
| `django_migrations` | Qo'llanilgan migration'lar tarixi |
| `django_content_type` | Model turlari registri |
| `django_admin_log` | Admin panel amallar logi |
| `django_session` | Sessiya ma'lumotlari (Redis bilan ishlatilmaydi) |
| `auth_group` | Foydalanuvchi guruhlari |
| `auth_permission` | Ruxsatlar |
| `auth_group_permissions` | Guruh-ruxsat M2M |
| `users_customuser_groups` | User-guruh M2M |
| `users_customuser_user_permissions` | User-ruxsat M2M |

## Migration Strategiyasi

### Lokal muhitda

```bash
# Model o'zgartirgandan keyin:
make makemigrations    # Migration fayllarini yaratish
make migrate           # Bazaga qo'llash (makemigrations + migrate)
```

### Production muhitda

```bash
python manage.py migrate --no-input
```

### Muhim qoidalar

1. Migration fayllarini **git ga commit** qiling
2. `infrastructure/models.py` ni o'zgartirgandan keyin, proxy `models.py` ham ishlashini tekshiring
3. Conflict bo'lsa: `python manage.py makemigrations --merge`
4. Katta migratsiyalarni squash qilish: `python manage.py squashmigrations <app_label>`

## Redis (Cache va Sessions)

Redis ma'lumotlar bazasi emas — **cache** va **session** uchun ishlatiladi:

```python
# config/settings/base.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
```

Redis o'chirilsa, cache va sessionlar yo'qoladi, lekin asosiy ma'lumotlar PostgreSQL da saqlanib qoladi.

# Database

**PostgreSQL 16** — primary database. **Redis 6.x** — for cache and sessions.

## ER Diagram

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

**Relationship:** `books_book.created_by_id` → `users_customuser.id` (ForeignKey, ON DELETE SET NULL)

## Table Descriptions

### `users_customuser`

Inherits from Django `AbstractUser`. `username` is removed — `email` is the primary identifier.

| Column | Type | Null | Default | Constraint | Description |
|--------|------|------|---------|------------|-------------|
| `id` | BigAutoField | No | auto | PRIMARY KEY | Auto-generated ID |
| `email` | EmailField | No | — | UNIQUE | Login email |
| `password` | CharField(128) | No | — | — | Hashed password (bcrypt) |
| `first_name` | CharField(150) | No | `""` | — | First name |
| `last_name` | CharField(150) | No | `""` | — | Last name |
| `bio` | TextField | No | `""` | — | Biography (optional) |
| `date_of_birth` | DateField | Yes | `NULL` | — | Date of birth |
| `is_active` | BooleanField | No | `True` | — | Active status |
| `is_staff` | BooleanField | No | `False` | — | Admin panel access |
| `is_superuser` | BooleanField | No | `False` | — | Full permissions |
| `date_joined` | DateTimeField | No | `auto_now_add` | — | Registration timestamp |
| `last_login` | DateTimeField | Yes | `NULL` | — | Last login timestamp |

**Ordering:** `-date_joined` (newest first)

### `books_book`

| Column | Type | Null | Default | Constraint | Description |
|--------|------|------|---------|------------|-------------|
| `id` | BigAutoField | No | auto | PRIMARY KEY | Auto-generated ID |
| `title` | CharField(255) | No | — | — | Book title |
| `author` | CharField(255) | No | — | — | Author name |
| `isbn` | CharField(13) | No | — | UNIQUE, RegexValidator | ISBN (10 or 13 digits) |
| `published_date` | DateField | No | — | — | Publication date |
| `page_count` | PositiveIntegerField | No | — | >= 0 | Number of pages |
| `language` | CharField(50) | No | `"English"` | — | Language |
| `genre` | CharField(20) | No | `"other"` | choices, db_index | Genre (14 choices) |
| `description` | TextField | No | `""` | — | Description (optional) |
| `created_by_id` | ForeignKey | Yes | `NULL` | FK → users_customuser | Creator |
| `created_at` | DateTimeField | No | `auto_now_add` | — | Creation timestamp |
| `updated_at` | DateTimeField | No | `auto_now` | — | Last update timestamp |

**Ordering:** `-created_at` (newest first)

**ISBN Validator:**
```python
regex = r"^\d{10}(\d{3})?$"
# Valid: "1234567890" (10 digits), "1234567890123" (13 digits)
# Invalid: "123", "ISBN-10", "12345678901" (11 digits)
```

## Genre Types

| Value | Display |
|-------|---------|
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

## Indexes

### `books_book` indexes

| Index name | Column(s) | Type | Reason |
|------------|-----------|------|--------|
| `idx_book_isbn` | `isbn` | B-tree | Fast lookup by ISBN |
| `idx_book_author` | `author` | B-tree | Filter by author |
| `idx_book_created` | `-created_at` | B-tree (desc) | Speed up default ordering |
| `books_book_genre_...` | `genre` | B-tree | Filter by genre (`db_index=True`) |
| `books_book_isbn_key` | `isbn` | UNIQUE | Unique ISBN constraint |

### `users_customuser` indexes

| Index name | Column(s) | Type |
|------------|-----------|------|
| `users_customuser_pkey` | `id` | PRIMARY KEY |
| `users_customuser_email_key` | `email` | UNIQUE |

## On Delete Behaviors

| Relationship | On Delete | Result |
|-------------|-----------|--------|
| `Book.created_by` → `CustomUser` | `SET_NULL` | If user is deleted, the book remains (`created_by = NULL`) |
| `User.groups` (M2M) | `CASCADE` | If user is deleted, group associations are also deleted |
| `User.user_permissions` (M2M) | `CASCADE` | If user is deleted, permission associations are also deleted |

## Django System Tables

Auto-generated tables in the project:

| Table | Purpose |
|-------|---------|
| `django_migrations` | Applied migrations history |
| `django_content_type` | Model type registry |
| `django_admin_log` | Admin panel action log |
| `django_session` | Session data (not used with Redis) |
| `auth_group` | User groups |
| `auth_permission` | Permissions |
| `auth_group_permissions` | Group-permission M2M |
| `users_customuser_groups` | User-group M2M |
| `users_customuser_user_permissions` | User-permission M2M |

## Migration Strategy

### Local environment

```bash
# After modifying a model:
make makemigrations    # Generate migration files
make migrate           # Apply to database (makemigrations + migrate)
```

### Production environment

```bash
uv run python manage.py migrate --no-input
```

### Important rules

1. **Commit** migration files to git
2. After modifying `infrastructure/models.py`, verify the proxy `models.py` still works
3. If there's a conflict: `uv run python manage.py makemigrations --merge`
4. To squash large migrations: `uv run python manage.py squashmigrations <app_label>`

## Redis (Cache and Sessions)

Redis is not a database — it's used for **cache** and **sessions**:

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

If Redis goes down, cache and sessions are lost, but core data remains safe in PostgreSQL.

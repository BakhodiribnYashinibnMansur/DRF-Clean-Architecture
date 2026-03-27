# API Misollar (curl)

**Barcha misollar** `curl` buyrug'i bilan ko'rsatilgan. Base URL: `http://localhost:8000`

## JWT Token Flow (To'liq Jarayon)

```
1. Register → user ma'lumotlari + tokens
2. Login   → access + refresh token
3. So'rov  → Authorization: Bearer <access_token>
4. Yangilash → refresh token bilan yangi access olish
```

### 1-qadam: Ro'yxatdan o'tish

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "first_name": "Ali",
    "last_name": "Valiyev",
    "password": "StrongPass123!",
    "password_confirm": "StrongPass123!"
  }'
```

Javob (201 Created):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "Ali",
    "last_name": "Valiyev",
    "full_name": "Ali Valiyev",
    "bio": "",
    "date_of_birth": null,
    "date_joined": "2024-01-15T10:30:00+05:00"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
  }
}
```

### 2-qadam: Login (Token olish)

```bash
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPass123!"
  }'
```

Javob (200 OK):
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

> `access` token — 30 daqiqa amal qiladi.
> `refresh` token — 7 kun amal qiladi.

### 3-qadam: Token ishlatish

Har bir himoyalangan so'rovda `Authorization` headerini qo'shing:

```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi..."
```

> **Muhim:** `Bearer` so'zi kerak, `B` katta harf bilan.

### 4-qadam: Token yangilash

Access token muddati tugaganda, refresh token bilan yangi access oling:

```bash
curl -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
  }'
```

Javob (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

> `ROTATE_REFRESH_TOKENS=True` — har safar yangi refresh token ham beriladi.

---

## Users — Profile Endpointlari

### Profilni ko'rish

```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer <access_token>"
```

### Profilni o'zgartirish

```bash
curl -X PATCH http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alisher",
    "bio": "Backend dasturchi",
    "date_of_birth": "1995-03-15"
  }'
```

> `email` va `date_joined` o'zgartirib bo'lmaydi (read-only).

### Parolni o'zgartirish

```bash
curl -X PUT http://localhost:8000/api/users/change-password/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "StrongPass123!",
    "new_password": "NewSecure456!",
    "new_password_confirm": "NewSecure456!"
  }'
```

Javob (200 OK):
```json
{
  "message": "Password changed successfully.",
  "tokens": {
    "refresh": "eyJ0eXAi...",
    "access": "eyJ0eXAi..."
  }
}
```

> Parol o'zgartirilgandan keyin **yangi tokenlar** qaytariladi.

---

## Users — Management Endpointlari (Admin)

### Barcha foydalanuvchilar ro'yxati (faqat admin)

```bash
curl -X GET http://localhost:8000/api/users/manage/ \
  -H "Authorization: Bearer <admin_access_token>"
```

Javob (200 OK):
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "admin@example.com",
      "first_name": "Admin",
      "last_name": "User",
      "is_active": true,
      "is_staff": true,
      "date_joined": "2024-01-01T00:00:00+05:00"
    },
    {
      "id": 2,
      "email": "user@example.com",
      "first_name": "Ali",
      "last_name": "Valiyev",
      "is_active": true,
      "is_staff": false,
      "date_joined": "2024-01-15T10:30:00+05:00"
    }
  ]
}
```

### Foydalanuvchi yaratish (faqat admin)

```bash
curl -X POST http://localhost:8000/api/users/manage/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "first_name": "Yangi",
    "last_name": "Foydalanuvchi",
    "is_active": true,
    "is_staff": false
  }'
```

### Foydalanuvchini ko'rish (admin yoki o'zi)

```bash
curl -X GET http://localhost:8000/api/users/manage/2/ \
  -H "Authorization: Bearer <access_token>"
```

### Foydalanuvchini o'chirish (faqat admin)

```bash
curl -X DELETE http://localhost:8000/api/users/manage/2/ \
  -H "Authorization: Bearer <admin_access_token>"
```

Javob: `204 No Content`

---

## Books Endpointlari

### Kitoblar ro'yxati (autentifikatsiya shart emas)

```bash
curl -X GET http://localhost:8000/api/books/
```

Javob (200 OK):
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Clean Code",
      "author": "Robert C. Martin",
      "isbn": "9780132350884",
      "genre": "technology",
      "language": "English",
      "published_date": "2008-08-01",
      "page_count": 464,
      "created_by": {
        "id": 1,
        "email": "user@example.com"
      },
      "created_at": "2024-01-15T12:00:00+05:00"
    }
  ]
}
```

### Kitob yaratish (autentifikatsiya kerak)

```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "published_date": "2008-08-01",
    "page_count": 464,
    "language": "English",
    "genre": "technology",
    "description": "A Handbook of Agile Software Craftsmanship."
  }'
```

Javob (201 Created):
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "9780132350884",
  "genre": "technology",
  "language": "English",
  "published_date": "2008-08-01",
  "page_count": 464,
  "description": "A Handbook of Agile Software Craftsmanship.",
  "created_by": {
    "id": 1,
    "email": "user@example.com"
  },
  "created_at": "2024-01-15T12:00:00+05:00",
  "updated_at": "2024-01-15T12:00:00+05:00"
}
```

### Kitobni ko'rish

```bash
curl -X GET http://localhost:8000/api/books/1/
```

### Kitobni yangilash (owner yoki admin)

```bash
curl -X PATCH http://localhost:8000/api/books/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Yangilangan tavsif."
  }'
```

### Kitobni o'chirish (owner yoki admin)

```bash
curl -X DELETE http://localhost:8000/api/books/1/ \
  -H "Authorization: Bearer <access_token>"
```

Javob: `204 No Content`

---

## Filtrlash va Qidirish

### Filtrlash misollari

```bash
# Nomi bo'yicha (case-insensitive, partial match)
curl "http://localhost:8000/api/books/?title=python"

# Muallif bo'yicha
curl "http://localhost:8000/api/books/?author=martin"

# Janr bo'yicha (aniq qiymat)
curl "http://localhost:8000/api/books/?genre=fiction"

# Til bo'yicha (case-insensitive, aniq)
curl "http://localhost:8000/api/books/?language=english"

# Nashr sanasi oralig'i
curl "http://localhost:8000/api/books/?published_after=2020-01-01&published_before=2023-12-31"

# Sahifalar soni oralig'i
curl "http://localhost:8000/api/books/?min_pages=100&max_pages=500"

# Bir nechta filterni birlashtirish
curl "http://localhost:8000/api/books/?genre=technology&min_pages=200&ordering=title"
```

### Qidirish (Search)

`title`, `author`, `isbn` ichidan qidiradi:

```bash
curl "http://localhost:8000/api/books/?search=clean+code"
```

### Saralash (Ordering)

```bash
# Nomi bo'yicha (A → Z)
curl "http://localhost:8000/api/books/?ordering=title"

# Nashr sanasi bo'yicha (eng yangisi birinchi)
curl "http://localhost:8000/api/books/?ordering=-published_date"

# Sahifalar soni bo'yicha
curl "http://localhost:8000/api/books/?ordering=page_count"
```

Mavjud ordering maydonlari: `title`, `author`, `published_date`, `page_count`, `created_at`

### Pagination

Har bir sahifada **10 ta** natija. Keyingi sahifaga o'tish:

```bash
curl "http://localhost:8000/api/books/?page=2"
```

Javob formati:
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/books/?page=3",
  "previous": "http://localhost:8000/api/books/?page=1",
  "results": [...]
}
```

---

## Xato Javoblari

### 400 Bad Request — Validatsiya xatosi

```json
{
  "isbn": ["ISBN must be 10 or 13 digits."],
  "page_count": ["This field is required."]
}
```

### 401 Unauthorized — Token yo'q yoki muddati tugagan

```json
{
  "detail": "Authentication credentials were not provided."
}
```

yoki:

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

### 403 Forbidden — Ruxsat yo'q

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found — Mavjud emas

```json
{
  "detail": "Not found."
}
```

### 429 Too Many Requests — Throttling

```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

Throttling limitlari:
- Anonim: **100 so'rov/soat**
- Autentifikatsiya qilingan: **1000 so'rov/soat**

---

## API Hujjatlari

| URL | Tavsif |
|-----|--------|
| `/api/docs/` | Swagger UI — interaktiv API tester |
| `/api/redoc/` | ReDoc — chiroyli API hujjati |
| `/api/schema/` | OpenAPI schema (JSON) |

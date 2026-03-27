# API Examples (curl)

**All examples** are shown using the `curl` command. Base URL: `http://localhost:8000`

## JWT Token Flow (Complete Process)

```
1. Register → user data + tokens
2. Login   → access + refresh token
3. Request → Authorization: Bearer <access_token>
4. Refresh → get new access token using refresh token
```

### Step 1: Register

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

Response (201 Created):
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

### Step 2: Login (Obtain Token)

```bash
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPass123!"
  }'
```

Response (200 OK):
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

> `access` token — valid for 30 minutes.
> `refresh` token — valid for 7 days.

### Step 3: Using the Token

Include the `Authorization` header in every protected request:

```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi..."
```

> **Important:** The `Bearer` keyword is required, with a capital `B`.

### Step 4: Refresh Token

When the access token expires, use the refresh token to obtain a new access token:

```bash
curl -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
  }'
```

Response (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

> `ROTATE_REFRESH_TOKENS=True` — a new refresh token is also issued each time.

---

## Users — Profile Endpoints

### View Profile

```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer <access_token>"
```

### Update Profile

```bash
curl -X PATCH http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alisher",
    "bio": "Backend developer",
    "date_of_birth": "1995-03-15"
  }'
```

> `email` and `date_joined` cannot be changed (read-only).

### Change Password

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

Response (200 OK):
```json
{
  "message": "Password changed successfully.",
  "tokens": {
    "refresh": "eyJ0eXAi...",
    "access": "eyJ0eXAi..."
  }
}
```

> After changing the password, **new tokens** are returned.

---

## Users — Management Endpoints (Admin)

### List All Users (admin only)

```bash
curl -X GET http://localhost:8000/api/users/manage/ \
  -H "Authorization: Bearer <admin_access_token>"
```

Response (200 OK):
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

### Create User (admin only)

```bash
curl -X POST http://localhost:8000/api/users/manage/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "first_name": "New",
    "last_name": "User",
    "is_active": true,
    "is_staff": false
  }'
```

### View User (admin or self)

```bash
curl -X GET http://localhost:8000/api/users/manage/2/ \
  -H "Authorization: Bearer <access_token>"
```

### Delete User (admin only)

```bash
curl -X DELETE http://localhost:8000/api/users/manage/2/ \
  -H "Authorization: Bearer <admin_access_token>"
```

Response: `204 No Content`

---

## Books Endpoints

### List Books (authentication not required)

```bash
curl -X GET http://localhost:8000/api/books/
```

Response (200 OK):
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

### Create Book (authentication required)

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

Response (201 Created):
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

### View Book

```bash
curl -X GET http://localhost:8000/api/books/1/
```

### Update Book (owner or admin)

```bash
curl -X PATCH http://localhost:8000/api/books/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description."
  }'
```

### Delete Book (owner or admin)

```bash
curl -X DELETE http://localhost:8000/api/books/1/ \
  -H "Authorization: Bearer <access_token>"
```

Response: `204 No Content`

---

## Filtering and Search

### Filtering Examples

```bash
# By title (case-insensitive, partial match)
curl "http://localhost:8000/api/books/?title=python"

# By author
curl "http://localhost:8000/api/books/?author=martin"

# By genre (exact match)
curl "http://localhost:8000/api/books/?genre=fiction"

# By language (case-insensitive, exact)
curl "http://localhost:8000/api/books/?language=english"

# Published date range
curl "http://localhost:8000/api/books/?published_after=2020-01-01&published_before=2023-12-31"

# Page count range
curl "http://localhost:8000/api/books/?min_pages=100&max_pages=500"

# Combining multiple filters
curl "http://localhost:8000/api/books/?genre=technology&min_pages=200&ordering=title"
```

### Search

Searches across `title`, `author`, `isbn`:

```bash
curl "http://localhost:8000/api/books/?search=clean+code"
```

### Ordering

```bash
# By title (A → Z)
curl "http://localhost:8000/api/books/?ordering=title"

# By published date (newest first)
curl "http://localhost:8000/api/books/?ordering=-published_date"

# By page count
curl "http://localhost:8000/api/books/?ordering=page_count"
```

Available ordering fields: `title`, `author`, `published_date`, `page_count`, `created_at`

### Pagination

Each page contains **10** results. To navigate to the next page:

```bash
curl "http://localhost:8000/api/books/?page=2"
```

Response format:
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/books/?page=3",
  "previous": "http://localhost:8000/api/books/?page=1",
  "results": [...]
}
```

---

## Error Responses

### 400 Bad Request — Validation Error

```json
{
  "isbn": ["ISBN must be 10 or 13 digits."],
  "page_count": ["This field is required."]
}
```

### 401 Unauthorized — Token missing or expired

```json
{
  "detail": "Authentication credentials were not provided."
}
```

or:

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

### 403 Forbidden — Permission denied

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found — Resource does not exist

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

Throttling limits:
- Anonymous: **100 requests/hour**
- Authenticated: **1000 requests/hour**

---

## API Documentation

| URL | Description |
|-----|-------------|
| `/api/docs/` | Swagger UI — interactive API tester |
| `/api/redoc/` | ReDoc — clean API documentation |
| `/api/schema/` | OpenAPI schema (JSON) |

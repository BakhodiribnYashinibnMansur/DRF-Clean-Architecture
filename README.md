# DRF Book Management API

A production-grade REST API built with Django REST Framework and **Clean Architecture** pattern.

---

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12+ | Core language |
| Django | 5.1 | Web framework |
| DRF | 3.15 | REST API |
| PostgreSQL | 16 | Database |
| Redis | 6.x | Cache + Sessions |
| SimpleJWT | 5.3 | JWT Authentication |
| drf-spectacular | 0.27 | Swagger / OpenAPI |
| django-filter | 24.3 | Filtering |
| django-cors-headers | 4.4 | CORS |
| Gunicorn | 22.0 | Production server |
| pytest | 8.x | Testing |
| factory-boy | 3.3 | Test fixtures |

---

## Project Structure

```
DRF/
├── config/                          # Django configuration
│   ├── settings/
│   │   ├── base.py                  # Shared settings (DB, JWT, DRF, Cache)
│   │   ├── development.py           # Development (DEBUG=True, CORS_ALLOW_ALL)
│   │   └── production.py            # Production (SSL, HSTS, Secure cookies)
│   ├── urls.py                      # Root URL router
│   ├── wsgi.py                      # WSGI (for gunicorn)
│   └── asgi.py                      # ASGI (for async servers)
│
├── apps/
│   ├── users/                       # User app (auth, profile, CRUD)
│   │   ├── domain/
│   │   │   ├── entities.py          # UserEntity dataclass (pure Python)
│   │   │   └── exceptions.py        # UserNotFoundError, UserAlreadyExistsError
│   │   ├── application/
│   │   │   ├── services.py          # UserService (register, auth, profile)
│   │   │   └── interfaces.py        # AbstractUserRepository (interface)
│   │   ├── infrastructure/
│   │   │   ├── models.py            # CustomUser model (email-based auth)
│   │   │   ├── managers.py          # CustomUserManager
│   │   │   └── repositories.py      # DjangoUserRepository
│   │   ├── presentation/
│   │   │   ├── views.py             # RegisterView, ProfileView, ChangePasswordView, UserViewSet
│   │   │   ├── serializers.py       # 5 serializers (Registration, Profile, List, Detail, ChangePassword)
│   │   │   ├── permissions.py       # IsOwnerOrReadOnly, IsAdminOrSelf
│   │   │   └── urls.py              # Auth + user endpoints
│   │   ├── admin.py
│   │   └── tests/                   # Domain, Service, Repo, Model, Serializer, View tests
│   │
│   └── books/                       # Book app (CRUD, filter, search)
│       ├── domain/
│       │   ├── entities.py          # BookEntity dataclass + Genre enum
│       │   └── exceptions.py        # BookNotFoundError, DuplicateISBNError
│       ├── application/
│       │   ├── services.py          # BookService (CRUD + ISBN validation)
│       │   └── interfaces.py        # AbstractBookRepository
│       ├── infrastructure/
│       │   ├── models.py            # Book model (title, author, isbn, genre...)
│       │   └── repositories.py      # DjangoBookRepository
│       ├── presentation/
│       │   ├── views.py             # BookViewSet (full CRUD + filtering)
│       │   ├── serializers.py       # BookListSerializer, BookDetailSerializer
│       │   ├── permissions.py       # IsAdminOrReadOnly, IsOwnerOrAdmin
│       │   ├── filters.py           # BookFilter (django-filter)
│       │   └── urls.py              # Book routes (DefaultRouter)
│       ├── admin.py
│       └── tests/
│
├── conftest.py                      # Shared pytest fixtures
├── setup.cfg                        # Pytest configuration
├── requirements.txt                 # Dependencies
├── Makefile                         # Dev commands
├── .env                             # Environment variables (local)
└── .env.example                     # .env template
```

---

## Clean Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Presentation Layer                      │
│         (Views, Serializers, URLs, Permissions)           │
├──────────────────────────────────────────────────────────┤
│                    Application Layer                       │
│              (Services, Interfaces/Contracts)              │
├──────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                     │
│           (Django Models, Repositories, Managers)          │
├──────────────────────────────────────────────────────────┤
│                      Domain Layer                          │
│          (Entities, Exceptions — pure Python)              │
└──────────────────────────────────────────────────────────┘
```

**Rule:** Inner layers never import from outer layers. Dependencies flow inward only.

### Request Flow

```
HTTP Request
    │
    ▼
Presentation Layer (View)
    │── Serializer validates request data
    │
    ▼
Application Layer (Service)
    │── Executes business logic and rules
    │── Calls repository through interface
    │
    ▼
Infrastructure Layer (Repository)
    │── Interacts with DB via Django ORM
    │── Converts between Domain Entity ↔ Django Model
    │
    ▼
Domain Layer (Entity)
    │── Pure Python dataclass
    │── Framework-independent
    │
    ▼
HTTP Response (Serialized JSON)
```

---

## Models

### CustomUser

| Field | Type | Description |
|-------|------|-------------|
| `id` | AutoField | Primary key |
| `email` | EmailField (unique) | Login identifier (replaces username) |
| `first_name` | CharField | First name |
| `last_name` | CharField | Last name |
| `bio` | TextField | Biography (optional) |
| `date_of_birth` | DateField | Date of birth (optional) |
| `is_active` | BooleanField | Active status |
| `is_staff` | BooleanField | Admin status |
| `date_joined` | DateTimeField | Registration timestamp |
| `last_login` | DateTimeField | Last login timestamp |

> `USERNAME_FIELD = "email"` — authentication is email-based.

### Book

| Field | Type | Description |
|-------|------|-------------|
| `id` | AutoField | Primary key |
| `title` | CharField(255) | Book title |
| `author` | CharField | Author name |
| `isbn` | CharField(13, unique) | ISBN (10-13 digits, regex validated) |
| `published_date` | DateField | Publication date |
| `page_count` | PositiveIntegerField | Number of pages |
| `language` | CharField | Language (default: "English") |
| `genre` | CharField(choices) | Genre |
| `description` | TextField | Description (optional) |
| `created_by` | ForeignKey(User) | Creator (nullable) |
| `created_at` | DateTimeField | Creation timestamp |
| `updated_at` | DateTimeField | Last update timestamp |

**Genre choices:** `fiction`, `non_fiction`, `science`, `technology`, `history`, `biography`, `philosophy`, `poetry`, `romance`, `thriller`, `fantasy`, `mystery`, `self_help`, `other`

---

## Authentication (JWT)

The project uses **JWT (JSON Web Token)** authentication via `djangorestframework-simplejwt`.

### How It Works

```
1. User logs in (email + password)
        │
        ▼
2. Server returns a JWT token pair:
   {
     "access": "...",      ← valid for 30 minutes
     "refresh": "..."      ← valid for 7 days
   }
        │
        ▼
3. Access token is sent with every request:
   Authorization: Bearer <access_token>
        │
        ▼
4. When access token expires, use refresh token to get a new one
        │
        ▼
5. Refresh token is rotated (old token gets blacklisted)
```

### JWT Configuration

| Parameter | Value |
|-----------|-------|
| Access token lifetime | 30 minutes |
| Refresh token lifetime | 7 days |
| Token rotation | Yes (new refresh token on each refresh) |
| Blacklisting | Yes (old tokens are invalidated) |
| Header format | `Authorization: Bearer <token>` |

---

## API Endpoints & Request/Response Examples

### 1. Register

```
POST /api/users/register/
Content-Type: application/json
Auth: Not required
```

**Request:**
```json
{
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "StrongPass123!",
    "password_confirm": "StrongPass123!"
}
```

**Response (201 Created):**
```json
{
    "user": {
        "id": 1,
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "bio": "",
        "date_of_birth": null,
        "date_joined": "2025-03-27T12:00:00Z"
    },
    "tokens": {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

**Errors:**
```json
// 400 — passwords don't match
{
    "password_confirm": ["Passwords do not match."]
}

// 400 — email already exists
{
    "email": ["user with this email already exists."]
}

// 400 — password too simple
{
    "password": ["This password is too common."]
}
```

---

### 2. Login (Obtain Token)

```
POST /api/users/token/
Content-Type: application/json
Auth: Not required
```

**Request:**
```json
{
    "email": "john@example.com",
    "password": "StrongPass123!"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error (401 Unauthorized):**
```json
{
    "detail": "No active account found with the given credentials"
}
```

---

### 3. Refresh Token

```
POST /api/users/token/refresh/
Content-Type: application/json
Auth: Not required
```

**Request:**
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error (401):**
```json
{
    "detail": "Token is blacklisted",
    "code": "token_not_valid"
}
```

---

### 4. Get Profile

```
GET /api/users/profile/
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "bio": "",
    "date_of_birth": null,
    "date_joined": "2025-03-27T12:00:00Z"
}
```

**Error (401):**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

---

### 5. Update Profile

```
PATCH /api/users/profile/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "bio": "Backend developer",
    "date_of_birth": "1995-06-15"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "bio": "Backend developer",
    "date_of_birth": "1995-06-15",
    "date_joined": "2025-03-27T12:00:00Z"
}
```

---

### 6. Change Password

```
PUT /api/users/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "old_password": "StrongPass123!",
    "new_password": "NewPass456!",
    "new_password_confirm": "NewPass456!"
}
```

**Response (200 OK):**
```json
{
    "detail": "Password updated successfully.",
    "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

**Errors:**
```json
// 400 — wrong old password
{
    "old_password": ["Old password is incorrect."]
}

// 400 — passwords don't match
{
    "new_password_confirm": ["Passwords do not match."]
}
```

---

### 7. List Users (Admin Only)

```
GET /api/users/manage/
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/users/manage/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "email": "admin@example.com",
            "first_name": "Admin",
            "last_name": "User",
            "is_active": true,
            "is_staff": true,
            "date_joined": "2025-03-20T10:00:00Z"
        },
        {
            "id": 2,
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "is_active": true,
            "is_staff": false,
            "date_joined": "2025-03-27T12:00:00Z"
        }
    ]
}
```

**Error (403 — not admin):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

### 8. User Detail (Admin or Self)

```
GET /api/users/manage/2/
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 2,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "bio": "Backend developer",
    "date_of_birth": "1995-06-15",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-03-27T12:00:00Z",
    "last_login": "2025-03-27T14:30:00Z"
}
```

---

### 9. Create User (Admin Only)

```
POST /api/users/manage/
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "password": "SecurePass789!",
    "password_confirm": "SecurePass789!"
}
```

**Response (201 Created):**
```json
{
    "id": 3,
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "full_name": "Jane Smith",
    "bio": "",
    "date_of_birth": null,
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-03-27T15:00:00Z",
    "last_login": null
}
```

---

### 10. Delete User (Admin Only)

```
DELETE /api/users/manage/3/
Authorization: Bearer <admin_access_token>
```

**Response (204 No Content):**
```
(empty response)
```

---

### 11. List Books

```
GET /api/books/
Auth: Optional (anonymous users get read-only access)
```

**Response (200 OK):**
```json
{
    "count": 50,
    "next": "http://localhost:8000/api/books/?page=2",
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
                "email": "admin@example.com"
            },
            "created_at": "2025-03-27T12:00:00Z"
        },
        {
            "id": 2,
            "title": "The Pragmatic Programmer",
            "author": "David Thomas",
            "isbn": "9780135957059",
            "genre": "technology",
            "language": "English",
            "published_date": "2019-09-23",
            "page_count": 352,
            "created_by": {
                "id": 2,
                "email": "john@example.com"
            },
            "created_at": "2025-03-27T11:30:00Z"
        }
    ]
}
```

---

### 12. Filtering & Searching Books

```bash
# By title (case-insensitive)
GET /api/books/?title=clean

# By author (partial match)
GET /api/books/?author=martin

# By genre (exact match)
GET /api/books/?genre=technology

# By language (case-insensitive)
GET /api/books/?language=english

# By date range
GET /api/books/?published_after=2020-01-01&published_before=2023-12-31

# By page count range
GET /api/books/?min_pages=100&max_pages=500

# Full-text search (searches title, author, isbn)
GET /api/books/?search=pragmatic

# Ordering (prefix - for descending)
GET /api/books/?ordering=-published_date
GET /api/books/?ordering=title
GET /api/books/?ordering=-page_count

# Combined filters
GET /api/books/?genre=technology&language=english&ordering=-created_at&search=code
```

---

### 13. Create Book

```
POST /api/books/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "title": "Design Patterns",
    "author": "Gang of Four",
    "isbn": "9780201633610",
    "published_date": "1994-10-31",
    "page_count": 395,
    "language": "English",
    "genre": "technology",
    "description": "Elements of Reusable Object-Oriented Software"
}
```

**Response (201 Created):**
```json
{
    "id": 3,
    "title": "Design Patterns",
    "author": "Gang of Four",
    "isbn": "9780201633610",
    "published_date": "1994-10-31",
    "page_count": 395,
    "language": "English",
    "genre": "technology",
    "description": "Elements of Reusable Object-Oriented Software",
    "created_by": {
        "id": 2,
        "email": "john@example.com"
    },
    "created_at": "2025-03-27T16:00:00Z",
    "updated_at": "2025-03-27T16:00:00Z"
}
```

**Errors:**
```json
// 400 — ISBN already exists
{
    "isbn": ["book with this isbn already exists."]
}

// 400 — invalid ISBN format
{
    "isbn": ["ISBN must be 10-13 digits."]
}

// 401 — not authenticated
{
    "detail": "Authentication credentials were not provided."
}
```

---

### 14. Book Detail

```
GET /api/books/3/
Auth: Optional
```

**Response (200 OK):**
```json
{
    "id": 3,
    "title": "Design Patterns",
    "author": "Gang of Four",
    "isbn": "9780201633610",
    "published_date": "1994-10-31",
    "page_count": 395,
    "language": "English",
    "genre": "technology",
    "description": "Elements of Reusable Object-Oriented Software",
    "created_by": {
        "id": 2,
        "email": "john@example.com"
    },
    "created_at": "2025-03-27T16:00:00Z",
    "updated_at": "2025-03-27T16:00:00Z"
}
```

**Error (404):**
```json
{
    "detail": "Not found."
}
```

---

### 15. Update Book (Owner or Admin)

```
PATCH /api/books/3/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "page_count": 400,
    "description": "Updated description"
}
```

**Response (200 OK):**
```json
{
    "id": 3,
    "title": "Design Patterns",
    "author": "Gang of Four",
    "isbn": "9780201633610",
    "published_date": "1994-10-31",
    "page_count": 400,
    "language": "English",
    "genre": "technology",
    "description": "Updated description",
    "created_by": {
        "id": 2,
        "email": "john@example.com"
    },
    "created_at": "2025-03-27T16:00:00Z",
    "updated_at": "2025-03-27T16:30:00Z"
}
```

**Error (403 — not owner):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

### 16. Delete Book (Owner or Admin)

```
DELETE /api/books/3/
Authorization: Bearer <access_token>
```

**Response (204 No Content):**
```
(empty response)
```

---

## Permissions

| Endpoint | Anonymous | Authenticated | Owner | Admin |
|----------|-----------|---------------|-------|-------|
| `POST /api/users/register/` | Yes | Yes | Yes | Yes |
| `POST /api/users/token/` | Yes | Yes | Yes | Yes |
| `POST /api/users/token/refresh/` | Yes | Yes | Yes | Yes |
| `GET /api/users/profile/` | No | Yes (self) | Yes (self) | Yes (self) |
| `PATCH /api/users/profile/` | No | Yes (self) | Yes (self) | Yes (self) |
| `PUT /api/users/change-password/` | No | Yes (self) | Yes (self) | Yes (self) |
| `GET /api/users/manage/` | No | No | No | Yes |
| `POST /api/users/manage/` | No | No | No | Yes |
| `GET /api/users/manage/{id}/` | No | Yes (self) | Yes (self) | Yes |
| `PUT/PATCH /api/users/manage/{id}/` | No | Yes (self) | Yes (self) | Yes |
| `DELETE /api/users/manage/{id}/` | No | No | No | Yes |
| `GET /api/books/` | Yes (read) | Yes | Yes | Yes |
| `POST /api/books/` | No | Yes | Yes | Yes |
| `GET /api/books/{id}/` | Yes (read) | Yes | Yes | Yes |
| `PUT/PATCH /api/books/{id}/` | No | No | Yes | Yes |
| `DELETE /api/books/{id}/` | No | No | Yes | Yes |

---

## Rate Limiting (Throttling)

| Type | Limit |
|------|-------|
| Anonymous users | 100 requests / hour |
| Authenticated users | 1000 requests / hour |

**Error (429 Too Many Requests):**
```json
{
    "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

---

## Pagination

All list endpoints use **PageNumberPagination** with 10 items per page.

```json
{
    "count": 50,
    "next": "http://localhost:8000/api/books/?page=2",
    "previous": null,
    "results": [...]
}
```

```bash
GET /api/books/?page=1    # Page 1 (items 1-10)
GET /api/books/?page=2    # Page 2 (items 11-20)
GET /api/books/?page=5    # Page 5 (items 41-50)
```

---

## Common Error Formats

### 400 Bad Request (Validation Error)
```json
{
    "field_name": ["Error message."],
    "another_field": ["Another error."]
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 429 Too Many Requests
```json
{
    "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

---

## API Documentation

| URL | Description |
|-----|-------------|
| `/api/schema/` | OpenAPI schema (JSON) |
| `/api/docs/` | Swagger UI (interactive) |
| `/api/redoc/` | ReDoc (clean format) |
| `/admin/` | Django Admin panel |

---

## Environment Variables

```bash
# Django
DJANGO_ENV=development          # development | production
SECRET_KEY=change-me            # Django secret key
DEBUG=True                      # True | False
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
DB_NAME=drf_db
DB_USER=drf_user
DB_PASSWORD=drf_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://:password@127.0.0.1:6379/0

# CORS (for production)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

---

## Getting Started

```bash
# 1. Clone the repository
git clone <repo-url>
cd DRF

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
make install
# or: pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run database migrations
make migrate
# or: python manage.py migrate

# 6. Create admin user
make superuser
# or: python manage.py createsuperuser

# 7. Start the server
make run
# or: python manage.py runserver 0.0.0.0:8000
```

---

## Tests

```bash
# Run all tests
make test
# or: pytest

# Result:
# 143 tests passed
```

### Test Statistics

```
143 tests
├── Domain tests      — 21 (pure unit, no DB)
├── Service tests     — 20 (mocked repository)
├── Repository tests  — 24 (integration, real DB)
├── Model tests       — 19 (Django ORM)
├── Serializer tests  — 21 (DRF validation)
└── View tests        — 38 (HTTP endpoints, permissions)
```

---

## Usage Examples (cURL)

```bash
# 1. Register
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
# Save the access token from the response

# 3. View profile
curl http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer <access_token>"

# 4. Create a book
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Crash Course",
    "author": "Eric Matthes",
    "isbn": "9781593279288",
    "published_date": "2019-05-03",
    "page_count": 544,
    "genre": "technology",
    "language": "English"
  }'

# 5. Filter books
curl "http://localhost:8000/api/books/?genre=technology&ordering=-created_at"

# 6. Refresh token
curl -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

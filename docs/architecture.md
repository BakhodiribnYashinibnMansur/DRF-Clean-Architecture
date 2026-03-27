# Clean Architecture — Deep Dive

**Project architecture** — built on Clean Architecture proposed by Robert C. Martin (Uncle Bob).

## What is Clean Architecture?

Clean Architecture is a principle of separating application code into **layers**, making each layer
**independent** from the others. The fundamental rule:

> Inner layers **never** import from outer layers.
> Dependencies flow only **from outside to inside**.

## Layer Diagram

```
+------------------------------------------------------+
|  Presentation Layer (DRF Views, Serializers, URLs)   |
|  +------------------------------------------------+  |
|  |  Infrastructure Layer (Django ORM, Repositories)|  |
|  |  +------------------------------------------+  |  |
|  |  |  Application Layer (Services, Interfaces)|  |  |
|  |  |  +------------------------------------+  |  |  |
|  |  |  |  Domain Layer (Entities, Exceptions)|  |  |  |
|  |  |  +------------------------------------+  |  |  |
|  |  +------------------------------------------+  |  |
|  +------------------------------------------------+  |
+------------------------------------------------------+
```

Dependency direction:

```
Presentation → Infrastructure → Application → Domain
     |               |               |            |
  outermost       outer           inner       innermost
```

## Layer Responsibilities and Boundaries

### 1. Domain Layer (innermost)

**Purpose:** Answers the questions "What is a Book?", "What is a User?"

| File | Purpose |
|------|---------|
| `entities.py` | `BookEntity`, `UserEntity` — pure Python dataclass |
| `exceptions.py` | `BookNotFoundError`, `DuplicateISBNError`, `UserNotFoundError`, etc. |

**Import rule:**
```
domain/ → imports nothing
         (only Python stdlib: dataclasses, datetime, enum, typing)
```

**Why it's needed:**
1. Fully independent of the framework — doesn't matter if it's Django, Flask, or FastAPI
2. Easiest to test — no DB needed, no mocks needed
3. All business concepts are gathered in one place

### 2. Application Layer

**Purpose:** Answers "How is a book created?", "What are the business rules?"

| File | Purpose |
|------|---------|
| `interfaces.py` | `AbstractBookRepository`, `AbstractUserRepository` — ABC interface |
| `services.py` | `BookService`, `UserService` — business logic |

**Import rule:**
```
application/ → imports only from domain/
```

**Dependency Injection:** The service doesn't create the repository itself — it receives it from outside:
```python
class BookService:
    def __init__(self, repository: AbstractBookRepository):
        self._repo = repository
```

### 3. Infrastructure Layer

**Purpose:** Answers "How is data stored?"

| File | Purpose |
|------|---------|
| `models.py` | `Book`, `CustomUser` — Django ORM models |
| `repositories.py` | `DjangoBookRepository`, `DjangoUserRepository` — concrete implementation |
| `managers.py` | `CustomUserManager` — only in users app |

**Import rule:**
```
infrastructure/ → imports from domain/ and application/
                  uses Django ORM
```

**Entity Mapping:** The repository converts between domain entity and ORM model:
```python
# ORM model → Domain Entity
def _to_entity(self, book: Book) -> BookEntity:
    return BookEntity(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        ...
    )
```

### 4. Presentation Layer (outermost)

**Purpose:** Answers "How does the API work?"

| File | Purpose |
|------|---------|
| `views.py` | `BookViewSet`, `RegisterView`, `UserProfileView` — API endpoints |
| `serializers.py` | `BookListSerializer`, `BookDetailSerializer` — data validation |
| `permissions.py` | `IsOwnerOrAdmin`, `IsAdminOrSelf` — permissions |
| `filters.py` | `BookFilter` — 8 filters (books only) |
| `urls.py` | URL routing (DefaultRouter) |

**Import rule:**
```
presentation/ → can import from all layers
```

## Request Lifecycle

Book creation example (`POST /api/books/`):

```
HTTP Request (POST /api/books/)
        |
        v
config/urls.py → apps/books/presentation/urls.py
        |
        v
BookViewSet.create() — permission check:
  - IsAuthenticated() → is the user logged in?
        |
        v
BookDetailSerializer.is_valid() — data validation:
  - title, author, isbn, published_date, page_count required
  - isbn format: 10 or 13 digits
        |
        v
BookViewSet.perform_create() — business rules:
  - BookService → does the ISBN already exist? (DuplicateISBNError)
  - serializer.save(created_by=request.user)
        |
        v
Book.objects.create() — Django ORM → PostgreSQL
        |
        v
BookDetailSerializer(book) — prepare response
        |
        v
HTTP Response (201 Created + JSON)
```

## Data Flow

Data format at each stage during book creation:

| Stage | Data format |
|-------|-------------|
| HTTP Request | JSON: `{"title": "...", "isbn": "...", ...}` |
| Serializer validation | Python dict: `validated_data` |
| Service layer | `BookEntity(title="...", isbn="...", ...)` |
| Repository | `Book(title="...", isbn="...", ...)` — ORM model |
| PostgreSQL | SQL INSERT — written to `books_book` table |
| Response | JSON: `{"id": 1, "title": "...", "created_by": {...}, ...}` |

## Dependency Injection Explained

**Problem:** If the service directly uses `DjangoBookRepository`, testing it would require a **real DB**.

**Solution:** Bind through abstraction:

```python
# In view — real repository
service = BookService(repository=DjangoBookRepository())

# In test — mock repository
mock_repo = MagicMock(spec=AbstractBookRepository)
service = BookService(repository=mock_repo)
```

This approach is the **D** in **SOLID** — Dependency Inversion Principle.

## ADR: Why Clean Architecture?

**Problem:** In traditional Django projects, "fat views" or "fat models" antipatterns emerge — business logic gets tangled inside views.py or models.py.

**Decision:** The Clean Architecture 4-layer pattern was adopted.

| Feature | Traditional Django | Clean Architecture |
|---------|-------------------|-------------------|
| Business logic location | views.py or models.py | services.py |
| Test speed | Slow (always needs DB) | Fast (domain/service without DB) |
| Framework coupling | High | Low (domain layer is independent) |
| Code replaceability | Difficult | Easy (through interfaces) |
| For new developers | Complex | Structured, understandable |

**Result:** Each layer is tested independently. Domain and service tests **don't use a database** — fast and reliable.

## Proxy Model Mechanism

Django expects to find models in the `apps/<app>/models.py` file. But our models are located in `infrastructure/models.py`.

**Solution:** Root-level `models.py` simply re-exports:

```python
# apps/books/models.py (proxy)
from apps.books.infrastructure.models import Book

__all__ = ["Book"]
```

This preserves the Clean Architecture structure without breaking Django's model discovery mechanism.

## Folder Structure

```
apps/books/
├── domain/              # Pure Python — no framework
│   ├── entities.py      # BookEntity dataclass
│   └── exceptions.py    # BookNotFoundError, DuplicateISBNError
├── application/         # Business logic
│   ├── interfaces.py    # AbstractBookRepository (ABC)
│   └── services.py      # BookService
├── infrastructure/      # Django ORM
│   ├── models.py        # Book model
│   └── repositories.py  # DjangoBookRepository
├── presentation/        # REST API
│   ├── views.py         # BookViewSet
│   ├── serializers.py   # BookListSerializer, BookDetailSerializer
│   ├── permissions.py   # IsOwnerOrAdmin
│   ├── filters.py       # BookFilter
│   └── urls.py          # Router
├── tests/               # 6 test files
├── models.py            # Proxy → infrastructure/models.py
└── admin.py             # Django admin
```

> For more details, read the `README.md` inside each layer.

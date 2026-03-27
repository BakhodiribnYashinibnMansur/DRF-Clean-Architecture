# Clean Architecture — Chuqur Tushuncha

**Loyiha arxitekturasi** — Robert C. Martin (Uncle Bob) tomonidan taklif qilingan Clean Architecture asosida qurilgan.

## Clean Architecture Nima?

Clean Architecture — dastur kodini **layerlarga** (qatlamlarga) ajratib, har bir layerni
boshqalaridan **mustaqil** qilish tamoyili. Asosiy qoida:

> Ichki layerlar tashqi layerlardan **hech qachon** import qilmaydi.
> Bog'liqlik faqat **tashqaridan ichkariga** yo'naladi.

## Layer Diagrammasi

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

Bog'liqlik yo'nalishi:

```
Presentation → Infrastructure → Application → Domain
     |               |               |            |
  tashqi          tashqi          ichki        eng ichki
```

## Layer Vazifalari va Chegaralari

### 1. Domain Layer (eng ichki)

**Vazifasi:** "Kitob nima?", "Foydalanuvchi nima?" degan savollarga javob beradi.

| Fayl | Vazifa |
|------|--------|
| `entities.py` | `BookEntity`, `UserEntity` — pure Python dataclass |
| `exceptions.py` | `BookNotFoundError`, `DuplicateISBNError`, `UserNotFoundError` va boshqalar |

**Import qoidasi:**
```
domain/ → hech narsadan import qilmaydi
         (faqat Python stdlib: dataclasses, datetime, enum, typing)
```

**Nima uchun kerak:**
1. Frameworkdan to'liq mustaqil — Django, Flask, FastAPI farqi yo'q
2. Test qilish eng oson — DB kerak emas, mock kerak emas
3. Barcha biznes tushunchalari bir joyda jamlangan

### 2. Application Layer

**Vazifasi:** "Kitob qanday yaratiladi?", "Biznes qoidalari nima?" degan savollarga javob beradi.

| Fayl | Vazifa |
|------|--------|
| `interfaces.py` | `AbstractBookRepository`, `AbstractUserRepository` — ABC interfeys |
| `services.py` | `BookService`, `UserService` — biznes logika |

**Import qoidasi:**
```
application/ → faqat domain/ dan import qiladi
```

**Dependency Injection:** Service o'zi repository yaratmaydi — tashqaridan oladi:
```python
class BookService:
    def __init__(self, repository: AbstractBookRepository):
        self._repo = repository
```

### 3. Infrastructure Layer

**Vazifasi:** "Ma'lumot qanday saqlanadi?" degan savolga javob beradi.

| Fayl | Vazifa |
|------|--------|
| `models.py` | `Book`, `CustomUser` — Django ORM modellari |
| `repositories.py` | `DjangoBookRepository`, `DjangoUserRepository` — konkret realizatsiya |
| `managers.py` | `CustomUserManager` — faqat users app da |

**Import qoidasi:**
```
infrastructure/ → domain/ va application/ dan import qiladi
                  Django ORM ishlatadi
```

**Entity Mapping:** Repository domain entity va ORM model o'rtasida konvertatsiya qiladi:
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

### 4. Presentation Layer (eng tashqi)

**Vazifasi:** "API qanday ishlaydi?" degan savolga javob beradi.

| Fayl | Vazifa |
|------|--------|
| `views.py` | `BookViewSet`, `RegisterView`, `UserProfileView` — API endpointlar |
| `serializers.py` | `BookListSerializer`, `BookDetailSerializer` — ma'lumot validatsiya |
| `permissions.py` | `IsOwnerOrAdmin`, `IsAdminOrSelf` — ruxsatlar |
| `filters.py` | `BookFilter` — 8 ta filter (faqat books) |
| `urls.py` | URL routing (DefaultRouter) |

**Import qoidasi:**
```
presentation/ → barcha layerlardan import qilishi mumkin
```

## Request Lifecycle (So'rov Hayot Sikli)

Kitob yaratish misoli (`POST /api/books/`):

```
HTTP Request (POST /api/books/)
        |
        v
config/urls.py → apps/books/presentation/urls.py
        |
        v
BookViewSet.create() — permission tekshiruvi:
  - IsAuthenticated() → foydalanuvchi tizimga kirganmi?
        |
        v
BookDetailSerializer.is_valid() — ma'lumot validatsiya:
  - title, author, isbn, published_date, page_count majburiy
  - isbn format: 10 yoki 13 raqam
        |
        v
BookViewSet.perform_create() — biznes qoidalar:
  - BookService → ISBN allaqachon mavjudmi? (DuplicateISBNError)
  - serializer.save(created_by=request.user)
        |
        v
Book.objects.create() — Django ORM → PostgreSQL
        |
        v
BookDetailSerializer(book) — response tayyorlash
        |
        v
HTTP Response (201 Created + JSON)
```

## Data Flow (Ma'lumot Oqimi)

Kitob yaratishda har bir bosqichdagi ma'lumot formati:

| Bosqich | Ma'lumot formati |
|---------|-----------------|
| HTTP Request | JSON: `{"title": "...", "isbn": "...", ...}` |
| Serializer validation | Python dict: `validated_data` |
| Service layer | `BookEntity(title="...", isbn="...", ...)` |
| Repository | `Book(title="...", isbn="...", ...)` — ORM model |
| PostgreSQL | SQL INSERT — `books_book` jadvaliga yoziladi |
| Response | JSON: `{"id": 1, "title": "...", "created_by": {...}, ...}` |

## Dependency Injection Tushuntirishi

**Muammo:** Agar service to'g'ridan-to'g'ri `DjangoBookRepository` ishlatsa,
uni test qilishda **haqiqiy DB** kerak bo'ladi.

**Yechim:** Abstraktsiya orqali bog'lash:

```python
# View da — haqiqiy repository
service = BookService(repository=DjangoBookRepository())

# Test da — mock repository
mock_repo = MagicMock(spec=AbstractBookRepository)
service = BookService(repository=mock_repo)
```

Bu yondashuv **SOLID** tamoyilining **D** harfi — Dependency Inversion Principle.

## ADR: Nima Uchun Clean Architecture?

**Muammo:** An'anaviy Django loyihalarda "fat views" yoki "fat models" antipattern
paydo bo'ladi — biznes logika views.py yoki models.py ichida chalkashib ketadi.

**Qaror:** Clean Architecture 4-layer pattern qo'llanildi.

| Xususiyat | An'anaviy Django | Clean Architecture |
|-----------|-----------------|-------------------|
| Biznes logika joyi | views.py yoki models.py | services.py |
| Test tezligi | Sekin (har doim DB kerak) | Tez (domain/service DB siz) |
| Framework bog'liqligi | Yuqori | Past (domain layer mustaqil) |
| Kodni almashtirish | Qiyin | Oson (interface orqali) |
| Yangi dasturchi uchun | Murakkab | Strukturali, tushunarli |

**Natija:** Har bir layer mustaqil test qilinadi. Domain va service testlari
**database ishlatmaydi** — tezkor va ishonchli.

## Proxy Model Mexanizmi

Django modellarni topish uchun `apps/<app>/models.py` faylini kutadi.
Lekin bizning modellar `infrastructure/models.py` da joylashgan.

**Yechim:** Root-level `models.py` faqat re-export qiladi:

```python
# apps/books/models.py (proxy)
from apps.books.infrastructure.models import Book

__all__ = ["Book"]
```

Bu Django'ning model discovery mexanizmini buzmasdan, Clean Architecture
strukturasini saqlash imkonini beradi.

## Papka Strukturasi

```
apps/books/
├── domain/              # Pure Python — framework yo'q
│   ├── entities.py      # BookEntity dataclass
│   └── exceptions.py    # BookNotFoundError, DuplicateISBNError
├── application/         # Biznes logika
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
├── tests/               # 6 ta test fayli
├── models.py            # Proxy → infrastructure/models.py
└── admin.py             # Django admin
```

> Batafsil ma'lumot uchun har bir layer ichidagi `README.md` ni o'qing.

# Books App

**Kitoblarni boshqarish** — yaratish, o'qish, yangilash, o'chirish (CRUD).

## Vazifasi

Books app "Kitoblar bilan nima qilish mumkin?" degan savolga javob beradi.
To'liq REST API orqali kitoblarni boshqarish, filtrlash, qidirish va saralash.

## Asosiy Xususiyatlar

- To'liq CRUD API (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`)
- 8 ta filter: `title`, `author`, `genre`, `language`, `published_after`, `published_before`, `min_pages`, `max_pages`
- Search: `title`, `author`, `isbn` bo'yicha qidirish
- Ordering: 5 ta maydon bo'yicha saralash
- Pagination: sahifada 10 ta natija
- Permissions: faqat owner yoki admin o'zgartirishi/o'chirishi mumkin

## Book Entity

| Maydon | Turi | Tavsif |
|--------|------|--------|
| `id` | BigAutoField | Avtomatik ID |
| `title` | CharField(255) | Kitob nomi |
| `author` | CharField(255) | Muallif ismi |
| `isbn` | CharField(13) | ISBN — unique, 10 yoki 13 raqam |
| `published_date` | DateField | Nashr sanasi |
| `page_count` | PositiveIntegerField | Sahifalar soni |
| `language` | CharField(50) | Til (default: `"English"`) |
| `genre` | CharField(20) | Janr — 14 ta tanlov (default: `"other"`) |
| `description` | TextField | Tavsif (ixtiyoriy) |
| `created_by` | ForeignKey(User) | Yaratuvchi (nullable) |
| `created_at` | DateTimeField | Yaratilgan vaqt (auto) |
| `updated_at` | DateTimeField | O'zgartirilgan vaqt (auto) |

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

## API Endpointlari

| Method | URL | Permission | Tavsif |
|--------|-----|-----------|--------|
| `GET` | `/api/books/` | Hamma | Kitoblar ro'yxati (filtrlash, search, pagination) |
| `POST` | `/api/books/` | Authenticated | Yangi kitob yaratish |
| `GET` | `/api/books/{id}/` | Hamma | Bitta kitobni ko'rish |
| `PUT` | `/api/books/{id}/` | Owner / Admin | To'liq yangilash |
| `PATCH` | `/api/books/{id}/` | Owner / Admin | Qisman yangilash |
| `DELETE` | `/api/books/{id}/` | Owner / Admin | O'chirish |

## Clean Architecture Layerlari

```
books/
├── domain/          # BookEntity, Genre, Exceptions
├── application/     # BookService, AbstractBookRepository
├── infrastructure/  # Book ORM model, DjangoBookRepository
├── presentation/    # BookViewSet, Serializers, Filters, Permissions
└── tests/           # 6 ta test fayli
```

> Har bir layer haqida batafsil — mos papkadagi `README.md` ni o'qing.

## Users App Bilan Aloqa

- `Book.created_by` → `CustomUser` (ForeignKey)
- `on_delete=SET_NULL` — user o'chirilsa, kitob qoladi (`created_by = NULL`)
- `related_name="books"` — `user.books.all()` orqali userning barcha kitoblarini olish mumkin

## Testlar

| Test fayli | Layer | DB kerakmi? |
|-----------|-------|-------------|
| `test_domain.py` | Domain | Yo'q |
| `test_services.py` | Application | Yo'q (mock) |
| `test_repositories.py` | Infrastructure | Ha |
| `test_models.py` | Infrastructure | Ha |
| `test_serializers.py` | Presentation | Ha |
| `test_views.py` | Presentation | Ha |

```bash
pytest apps/books/tests/ -v
```

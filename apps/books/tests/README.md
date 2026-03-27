# Tests — Book App

Har bir Clean Architecture layer uchun alohida test fayli.

## Test fayllari

| Fayl | Layer | Type | DB kerakmi? |
|------|-------|------|-------------|
| `test_domain.py` | Domain | Unit test | Yo'q |
| `test_services.py` | Application | Unit test (mock) | Yo'q |
| `test_repositories.py` | Infrastructure | Integration test | Ha |
| `test_models.py` | Infrastructure | Integration test | Ha |
| `test_serializers.py` | Presentation | Integration test | Ha |
| `test_views.py` | Presentation | Integration test | Ha |

## Layer bo'yicha test strategiyasi

### `test_domain.py` — Pure Unit Tests
- Entity yaratish va default qiymatlar
- Genre enum values va str conversion
- Exception instantiation
- **DB ishlatilmaydi, mock ishlatilmaydi** — eng tez testlar

### `test_services.py` — Service Tests (Mock Repository)
- `BookService.create_book()` — muvaffaqiyatli yaratish
- `BookService.create_book()` — duplicate ISBN → `DuplicateISBNError`
- `BookService.get_book()` — topilmasa → `BookNotFoundError`
- `BookService.update_book()` — ISBN conflict tekshiruvi
- `BookService.delete_book()` — mavjud emas → xato
- **Repository mock qilinadi** — DB yo'q, tez ishlaydi

### `test_repositories.py` — Repository Integration Tests
- `create()` → DB da saqlanishi
- `get_by_id()` → to'g'ri entity qaytishi
- `update()` → field lar yangilanishi
- `delete()` → DB dan o'chirilishi
- `exists_by_isbn()` → True/False, exclude_id bilan
- **Real PostgreSQL ishlatiladi**

### `test_models.py` — ORM Model Tests
- Model yaratish, `__str__`, ordering
- ISBN validator, uniqueness constraint
- Genre TextChoices, auto timestamps
- `created_by` nullable

### `test_serializers.py` — Serializer Tests
- BookListSerializer: description yo'qligi, created_by format
- BookDetailSerializer: barcha fieldlar, timestamps
- Validation: required fields, invalid ISBN format

### `test_views.py` — API Endpoint Tests
- **CRUD**: list, create, retrieve, update, delete
- **Permissions**: owner, admin, boshqa user, unauthenticated
- **Filtering**: genre, author
- **Search**: title bo'yicha
- **Pagination**: 10 ta per page
- **Ordering**: title bo'yicha

## Ishga tushirish

```bash
pytest -v                           # Barcha testlar
pytest apps/books/tests/ -v         # Faqat books testlari
pytest apps/books/tests/test_domain.py -v   # Faqat domain testlari
pytest apps/books/tests/test_services.py -v # Faqat service testlari
```

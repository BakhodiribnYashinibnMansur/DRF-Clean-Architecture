# Application Layer (books)

**Biznes logika qatlami** — Use Case / Service pattern.

## Vazifasi

Application layer "Kitob bilan nima qilish mumkin?" savoliga javob beradi.
CRUD operatsiyalarini boshqaradi va biznes qoidalarini tekshiradi.

## Fayllar

### `interfaces.py` — Repository Interface (ABC)
```python
class AbstractBookRepository(ABC):
    def get_by_id(self, book_id: int) -> Optional[BookEntity]: ...
    def create(self, entity: BookEntity) -> BookEntity: ...
    def update(self, entity: BookEntity) -> BookEntity: ...
    def delete(self, book_id: int) -> None: ...
    def exists_by_isbn(self, isbn: str, exclude_id: Optional[int] = None) -> bool: ...
```

Bu **abstract class** — qanday database ishlatilishini bilmaydi.
Faqat "nima qilish kerak"ni belgilaydi. Konkret implementatsiya
`infrastructure/repositories.py` da bo'ladi.

### `services.py` — Business Logic Service
```python
class BookService:
    def __init__(self, repository: AbstractBookRepository):
        self._repo = repository

    def create_book(self, entity: BookEntity) -> BookEntity:
        if self._repo.exists_by_isbn(entity.isbn):
            raise DuplicateISBNError(...)
        return self._repo.create(entity)

    def get_book(self, book_id: int) -> BookEntity: ...
    def update_book(self, entity: BookEntity) -> BookEntity: ...
    def delete_book(self, book_id: int) -> None: ...
```

`BookService` — asosiy biznes logika:
- Kitob yaratishdan oldin ISBN unikal ekanligini tekshiradi
- Kitob topilmasa `BookNotFoundError` ko'taradi
- Repository orqali database bilan ishlaydi (Dependency Injection)

## Import qoidasi

```
application/ → faqat domain/ dan import qiladi
               (entities, exceptions)
```

**Django, DRF, ORM — hech biri import qilinmaydi.**

## Nima uchun kerak?

1. **Dependency Inversion** — service database haqida bilmaydi, faqat interface biladi
2. **Test qilish oson** — `mock_repo = MagicMock(spec=AbstractBookRepository)` bilan test
3. **Biznes qoidalari bir joyda** — ISBN uniqueness, permission logic shu yerda
4. **Almashtirish mumkin** — PostgreSQL o'rniga MongoDB ishlatsa, faqat repository o'zgaradi

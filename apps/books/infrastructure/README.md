# Infrastructure Layer (books)

**Database va ORM qatlami** — Django-specific implementatsiya.

## Vazifasi

Infrastructure layer "Ma'lumot qayerda va qanday saqlanadi?" savoliga javob beradi.
Domain entity'larni database jadvallariga map qiladi.

## Fayllar

### `models.py` — Django ORM Model
```python
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True, validators=[isbn_validator])
    genre = models.CharField(choices=Genre.choices, ...)
    created_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=SET_NULL, ...)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Bu **Django ORM model** — `books_book` jadvaliga map bo'ladi.
Validators, indexes, Meta class — hammasi shu yerda.

> **Muhim**: App root dagi `apps/books/models.py` — bu proxy fayl.
> U faqat `from apps.books.infrastructure.models import Book` qiladi.
> Django'ning model discovery mexanizmi ishlashi uchun kerak.

### `repositories.py` — Concrete Repository
```python
class DjangoBookRepository(AbstractBookRepository):
    def _to_entity(self, model: Book) -> BookEntity:
        """ORM model → Domain entity"""
        return BookEntity(id=model.id, title=model.title, ...)

    def _to_model_kwargs(self, entity: BookEntity) -> dict:
        """Domain entity → ORM field dict"""
        return {"title": entity.title, "isbn": entity.isbn, ...}

    def create(self, entity: BookEntity) -> BookEntity:
        model = Book.objects.create(**self._to_model_kwargs(entity))
        return self._to_entity(model)

    def get_by_id(self, book_id: int) -> Optional[BookEntity]:
        try:
            return self._to_entity(Book.objects.get(id=book_id))
        except Book.DoesNotExist:
            return None
```

`DjangoBookRepository` — `AbstractBookRepository` ni implement qiladi.
**Ikki yo'nalishli mapping** qiladi:
- `_to_entity()`: Django model → pure Python dataclass
- `_to_model_kwargs()`: Python dataclass → Django model fields

## Import qoidasi

```
infrastructure/ → domain/ va application/ dan import qiladi
                  (BookEntity, Genre, AbstractBookRepository)
                → Django ORM dan import qiladi
                  (models, django.db, django.conf)
```

## Nima uchun kerak?

1. **Database abstraction** — ORM logikasi bir joyda to'plangan
2. **Mapping** — domain entity va ORM model orasidagi aloqa aniq
3. **Almashtirish mumkin** — `MongoBookRepository`, `InMemoryBookRepository` yozsa, faqat shu layer o'zgaradi
4. **Migration xavfsizligi** — proxy `models.py` tufayli Django migrations buzilmaydi

# Domain Layer (books)

**Eng ichki layer** — frameworkdan to'liq mustaqil.

## Vazifasi

Domain layer "Kitob nima?" degan savolga javob beradi.
Bu yerda **hech qanday Django yoki DRF import yo'q** — faqat pure Python.

## Fayllar

### `entities.py` — Domain Entity
```python
@dataclass
class BookEntity:
    title: str
    author: str
    isbn: str
    published_date: date
    page_count: int
    language: str = "English"
    genre: Genre = Genre.OTHER
    ...
```

`BookEntity` — kitobning biznes modeli. Bu **Django ORM model emas**.
Dataclass sifatida yaratilgan — sodda, yengil, frameworksiz ishlaydi.

`Genre` — pure Python `str, Enum`. Django `TextChoices` emas, lekin
qiymatlari bir xil (`"fiction"`, `"technology"`, va h.k.).

### `exceptions.py` — Domain Exceptions
```python
class BookNotFoundError(Exception): ...
class DuplicateISBNError(Exception): ...
class BookPermissionDeniedError(Exception): ...
```

Biznes qoidalari buzilganda ishlatiladi. Masalan:
- ISBN allaqachon mavjud → `DuplicateISBNError`
- Kitob topilmadi → `BookNotFoundError`

## Import qoidasi

```
domain/ → hech narsadan import qilmaydi
         (faqat Python stdlib: dataclasses, datetime, enum, typing)
```

## Nima uchun kerak?

1. **Frameworkdan mustaqil** — Django o'rniga Flask, FastAPI ishlatsa ham, domain o'zgarmaydi
2. **Test qilish oson** — database kerak emas, mock kerak emas
3. **Business logic markazi** — barcha biznes tushunchalari bir joyda

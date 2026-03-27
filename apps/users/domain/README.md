# Domain Layer (users)

**Eng ichki layer** — frameworkdan to'liq mustaqil.

## Vazifasi

User domain "Foydalanuvchi nima?" savoliga javob beradi.
Django `AbstractUser`, `auth` moduli — bularning hech biri bu yerda yo'q.

## Fayllar

### `entities.py` — Domain Entity
```python
@dataclass
class UserEntity:
    email: str
    first_name: str = ""
    last_name: str = ""
    bio: str = ""
    date_of_birth: Optional[date] = None
    id: Optional[int] = None
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False
    date_joined: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
```

`UserEntity` — foydalanuvchining biznes modeli. Django `User` model emas.
`full_name` property — biznes logika (ism + familiya birlashtirish).

### `exceptions.py` — Domain Exceptions
```python
class UserNotFoundError(Exception): ...     # User topilmadi
class InvalidPasswordError(Exception): ...  # Parol noto'g'ri
class DuplicateEmailError(Exception): ...   # Email allaqachon mavjud
```

## Import qoidasi

```
domain/ → hech narsadan import qilmaydi (faqat Python stdlib)
```

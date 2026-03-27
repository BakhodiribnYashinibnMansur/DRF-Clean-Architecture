# Application Layer (users)

**Biznes logika qatlami** — Use Case / Service pattern.

## Vazifasi

"Foydalanuvchi bilan nima qilish mumkin?" — registratsiya, login, profil o'zgartirish,
parol almashtirish. Barcha biznes qoidalari shu yerda.

## Fayllar

### `interfaces.py` — Repository Interface (ABC)
```python
class AbstractUserRepository(ABC):
    def get_by_id(self, user_id: int) -> Optional[UserEntity]: ...
    def get_by_email(self, email: str) -> Optional[UserEntity]: ...
    def create_user(self, email: str, password: str, **kwargs) -> UserEntity: ...
    def update(self, user_id: int, **kwargs) -> UserEntity: ...
    def delete(self, user_id: int) -> None: ...
    def exists_by_email(self, email: str) -> bool: ...
    def check_password(self, user_id: int, password: str) -> bool: ...
    def set_password(self, user_id: int, new_password: str) -> None: ...
```

### `services.py` — Business Logic Service
```python
class UserService:
    def register_user(self, email, password, **kwargs) -> UserEntity:
        # Email unikal ekanligini tekshiradi
        if self._repo.exists_by_email(email):
            raise DuplicateEmailError(...)
        return self._repo.create_user(...)

    def change_password(self, user_id, old_password, new_password):
        # Eski parolni tekshiradi, keyin yangisini o'rnatadi
        if not self._repo.check_password(user_id, old_password):
            raise InvalidPasswordError(...)
        self._repo.set_password(user_id, new_password)
```

## Import qoidasi

```
application/ → faqat domain/ dan import qiladi
               (UserEntity, UserNotFoundError, InvalidPasswordError, DuplicateEmailError)
```

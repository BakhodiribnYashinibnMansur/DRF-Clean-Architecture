# Tests — Users App

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
- UserEntity yaratish va default qiymatlar
- `full_name` property (ikkala ism, faqat biri, bo'sh)
- `__str__` → email
- Exception instantiation

### `test_services.py` — Service Tests (Mock Repository)
- `register_user()` — muvaffaqiyatli + duplicate email
- `get_user()` / `get_user_by_email()` — topilsa / topilmasa
- `change_password()` — to'g'ri parol / noto'g'ri parol / user yo'q
- `update_profile()` / `delete_user()`

### `test_repositories.py` — Repository Integration Tests
- `create_user()` → DB da yaratilishi, entity qaytishi
- `get_by_id()` / `get_by_email()` → topilsa / topilmasa
- `check_password()` → to'g'ri / noto'g'ri / user yo'q
- `set_password()` → parol o'zgarishi
- `exists_by_email()` / `delete()`

### `test_models.py` — ORM Model Tests
- User yaratish, email normalization
- Superuser yaratish va validation
- `full_name` property, `__str__`
- USERNAME_FIELD = "email", username yo'qligi

### `test_serializers.py` — Serializer Tests
- Registration: valid data, duplicate email, password mismatch, weak password
- Profile: field presence, email read-only
- ChangePassword: wrong old, mismatch, success

### `test_views.py` — API Endpoint Tests
- **Register**: success, duplicate, invalid
- **Profile**: get, update, email immutability
- **UserViewSet**: admin CRUD, non-admin restrictions
- **ChangePassword**: success, wrong old, unauthenticated
- **Token**: obtain, invalid credentials, refresh

## Ishga tushirish

```bash
pytest apps/users/tests/ -v         # Barcha user testlari
pytest apps/users/tests/test_services.py -v  # Faqat service testlari
```

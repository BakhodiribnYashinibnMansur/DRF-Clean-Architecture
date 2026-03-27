# Infrastructure Layer (users)

**Database va ORM qatlami** — Django-specific implementatsiya.

## Vazifasi

User ma'lumotlarini PostgreSQL da saqlash va olish.
Django `AbstractUser`, `BaseUserManager` — shu yerda.

## Fayllar

### `models.py` — Django ORM Model
```python
class CustomUser(AbstractUser):
    username = None                    # Username o'chirilgan
    email = models.EmailField(unique=True)  # Email = login
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    USERNAME_FIELD = "email"           # Auth uchun email ishlatiladi
    objects = CustomUserManager()      # Custom manager
```

> **Proxy**: App root dagi `apps/users/models.py` faqat shu fayldan re-export qiladi.
> `AUTH_USER_MODEL = "users.CustomUser"` ishlashi uchun kerak.

### `managers.py` — Custom User Manager
```python
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)   # Domain qismini lowercase
        user = self.model(email=email, **extra_fields)
        user.set_password(password)            # Parolni hash qiladi
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # is_staff=True, is_superuser=True bo'lishi shart
        ...
```

### `repositories.py` — Concrete Repository
```python
class DjangoUserRepository(AbstractUserRepository):
    def _to_entity(self, model: CustomUser) -> UserEntity:
        """ORM model → Domain entity mapping"""

    def create_user(self, email, password, **kwargs) -> UserEntity:
        model = CustomUser.objects.create_user(email=email, password=password, **kwargs)
        return self._to_entity(model)

    def check_password(self, user_id, password) -> bool:
        model = CustomUser.objects.get(id=user_id)
        return model.check_password(password)

    def set_password(self, user_id, new_password):
        model = CustomUser.objects.get(id=user_id)
        model.set_password(new_password)
        model.save(update_fields=["password"])
```

## Import qoidasi

```
infrastructure/ → domain/ (UserEntity)
                → application/ (AbstractUserRepository)
                → Django (AbstractUser, BaseUserManager, models)
```

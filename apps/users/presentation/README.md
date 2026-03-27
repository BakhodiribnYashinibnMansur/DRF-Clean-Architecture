# Presentation Layer (users)

**API qatlami** — DRF-specific kod. Tashqi dunyo bilan aloqa.

## Vazifasi

User API endpointlari — registratsiya, login, profil boshqarish, admin CRUD.

## Fayllar

### `views.py` — API Views

**RegisterView** (`POST /api/users/register/`)
```python
class RegisterView(CreateAPIView):
    permission_classes = [AllowAny]  # Hamma ro'yxatdan o'ta oladi
    # Muvaffaqiyatli bo'lsa → user data + JWT tokens qaytaradi
```

**UserProfileView** (`GET/PATCH /api/users/profile/`)
```python
class UserProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user  # Faqat o'zini ko'radi/o'zgartiradi
```

**UserViewSet** (`/api/users/manage/` — admin CRUD)
```python
class UserViewSet(ModelViewSet):
    # Admin: barcha userlarni CRUD qila oladi
    # Oddiy user: faqat o'zini ko'radi/o'zgartiradi
    def get_permissions(self):
        if self.action in ["list", "create", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated(), IsAdminOrSelf()]
```

**ChangePasswordView** (`PUT /api/users/change-password/`)
```python
class ChangePasswordView(UpdateAPIView):
    # Eski parolni tekshiradi → yangi JWT tokens qaytaradi
```

### `serializers.py` — 5 ta serializer

| Serializer | Vazifasi |
|-----------|----------|
| `UserRegistrationSerializer` | Register: email, password, password_confirm |
| `UserProfileSerializer` | Profil: email (read-only), first_name, last_name, bio |
| `UserListSerializer` | Admin list: compact (7 field) |
| `UserDetailSerializer` | Admin detail: to'liq (11 field) |
| `ChangePasswordSerializer` | Parol: old_password, new_password, new_password_confirm |

### `permissions.py` — Access Control

| Permission | Qoida |
|-----------|-------|
| `IsOwnerOrReadOnly` | O'qish — hamma. Yozish — faqat egasi |
| `IsAdminOrSelf` | Admin — hamma. Oddiy user — faqat o'zi |

### `urls.py` — URL Routing
```python
POST   token/              → JWT token olish (login)
POST   token/refresh/      → Token yangilash
POST   register/           → Ro'yxatdan o'tish
GET    profile/            → Profil ko'rish
PATCH  profile/            → Profil o'zgartirish
PUT    change-password/    → Parol o'zgartirish
       manage/             → User CRUD (router)
```

## Import qoidasi

```
presentation/ → barcha layerlardan import qilishi mumkin
```

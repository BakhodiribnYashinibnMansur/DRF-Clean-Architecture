# Users App

**Foydalanuvchilarni boshqarish** — ro'yxatdan o'tish, autentifikatsiya, profil boshqarish, admin CRUD.

## Vazifasi

Users app "Foydalanuvchilar bilan nima qilish mumkin?" degan savolga javob beradi.
Email-based autentifikatsiya, JWT tokenlar, profil boshqarish va admin panel.

## Asosiy Xususiyatlar

- Email-based authentication (username yo'q)
- JWT token: access (30 daqiqa), refresh (7 kun)
- Ro'yxatdan o'tishda avtomatik JWT token qaytarish
- Profil ko'rish va o'zgartirish
- Parol o'zgartirish (eski parol tekshiruvi bilan, yangi tokenlar qaytarish)
- Admin: barcha foydalanuvchilar CRUD

## User Entity

| Maydon | Turi | Tavsif |
|--------|------|--------|
| `id` | BigAutoField | Avtomatik ID |
| `email` | EmailField | Login uchun email (unique) |
| `password` | CharField(128) | Hashed parol (bcrypt) |
| `first_name` | CharField(150) | Ism |
| `last_name` | CharField(150) | Familiya |
| `bio` | TextField | Biografiya (ixtiyoriy) |
| `date_of_birth` | DateField | Tug'ilgan sana (ixtiyoriy, nullable) |
| `is_active` | BooleanField | Aktiv holat (default: `True`) |
| `is_staff` | BooleanField | Admin panelga kirish (default: `False`) |
| `is_superuser` | BooleanField | To'liq huquq (default: `False`) |
| `date_joined` | DateTimeField | Ro'yxatdan o'tgan vaqt (auto) |
| `last_login` | DateTimeField | Oxirgi kirish vaqti (nullable) |

## Authentication Flow

```
1. Register:  POST /api/users/register/      → user + tokens
2. Login:     POST /api/users/token/          → {access, refresh}
3. So'rov:    Authorization: Bearer <access>
4. Yangilash: POST /api/users/token/refresh/  → {access}
5. Parol:     PUT /api/users/change-password/ → yangi tokens
```

## Permission Tizimi

| Endpoint | Anonim | Authenticated | Admin |
|----------|--------|---------------|-------|
| `POST /register/` | Ha | Ha | Ha |
| `POST /token/` | Ha | Ha | Ha |
| `POST /token/refresh/` | Ha | Ha | Ha |
| `GET /profile/` | Yo'q | O'zini | O'zini |
| `PATCH /profile/` | Yo'q | O'zini | O'zini |
| `PUT /change-password/` | Yo'q | O'zini | O'zini |
| `GET /manage/` | Yo'q | Yo'q | Ha (hammasini) |
| `POST /manage/` | Yo'q | Yo'q | Ha |
| `GET /manage/{id}/` | Yo'q | O'zini | Ha (hammasini) |
| `PUT /manage/{id}/` | Yo'q | O'zini | Ha (hammasini) |
| `PATCH /manage/{id}/` | Yo'q | O'zini | Ha (hammasini) |
| `DELETE /manage/{id}/` | Yo'q | Yo'q | Ha |

## Serializer Turlari

| Serializer | Vazifasi | Ishlatilish joyi |
|-----------|---------|-----------------|
| `UserRegistrationSerializer` | Ro'yxatdan o'tish (email, password, password_confirm) | `POST /register/` |
| `UserProfileSerializer` | Profil ko'rish/o'zgartirish (email read-only) | `GET/PATCH /profile/` |
| `UserListSerializer` | Foydalanuvchilar ro'yxati (kompakt) | `GET /manage/` |
| `UserDetailSerializer` | Batafsil ko'rish/o'zgartirish (admin) | `GET/PUT/PATCH /manage/{id}/` |
| `ChangePasswordSerializer` | Parol o'zgartirish (old + new + confirm) | `PUT /change-password/` |

## API Endpointlari

### Autentifikatsiya

| Method | URL | Permission | Tavsif |
|--------|-----|-----------|--------|
| `POST` | `/api/users/register/` | AllowAny | Ro'yxatdan o'tish |
| `POST` | `/api/users/token/` | AllowAny | JWT token olish (login) |
| `POST` | `/api/users/token/refresh/` | AllowAny | Token yangilash |

### Profil

| Method | URL | Permission | Tavsif |
|--------|-----|-----------|--------|
| `GET` | `/api/users/profile/` | Authenticated | O'z profilini ko'rish |
| `PATCH` | `/api/users/profile/` | Authenticated | O'z profilini o'zgartirish |
| `PUT` | `/api/users/change-password/` | Authenticated | Parolni o'zgartirish |

### Foydalanuvchi Boshqarish (Admin)

| Method | URL | Permission | Tavsif |
|--------|-----|-----------|--------|
| `GET` | `/api/users/manage/` | Admin | Barcha userlar ro'yxati |
| `POST` | `/api/users/manage/` | Admin | Yangi user yaratish |
| `GET` | `/api/users/manage/{id}/` | Admin / O'zi | Userni ko'rish |
| `PUT` | `/api/users/manage/{id}/` | Admin / O'zi | To'liq yangilash |
| `PATCH` | `/api/users/manage/{id}/` | Admin / O'zi | Qisman yangilash |
| `DELETE` | `/api/users/manage/{id}/` | Admin | Userni o'chirish |

## Clean Architecture Layerlari

```
users/
├── domain/          # UserEntity, Exceptions
├── application/     # UserService, AbstractUserRepository
├── infrastructure/  # CustomUser ORM, CustomUserManager, DjangoUserRepository
├── presentation/    # Views, Serializers, Permissions, URLs
└── tests/           # 6 ta test fayli
```

> Har bir layer haqida batafsil — mos papkadagi `README.md` ni o'qing.

## CustomUserManager

Django'ning standart `UserManager` username ishlatadi. Loyihada email asosiy
identifikator bo'lgani uchun, `CustomUserManager` yaratilgan:

- `create_user(email, password, **extra_fields)` — email normalize, parol hash
- `create_superuser(email, password, **extra_fields)` — `is_staff=True`, `is_superuser=True` tekshiruvi

## Parol Validatsiyasi

Django'ning 4 ta built-in validatori ishlatiladi:

1. **UserAttributeSimilarityValidator** — email/ism ga o'xshash parol taqiqlangan
2. **MinimumLengthValidator** — kamida 8 belgi
3. **CommonPasswordValidator** — keng tarqalgan parollar taqiqlangan
4. **NumericPasswordValidator** — faqat raqamdan iborat parol taqiqlangan

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
pytest apps/users/tests/ -v
```

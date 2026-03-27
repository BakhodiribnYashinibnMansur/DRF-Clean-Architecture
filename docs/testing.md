# Test Strategiyasi

**143 ta test**, barcha o'tadi. Har bir app da **6 ta test fayli** — layer bo'yicha ajratilgan.

## Umumiy Statistika

| Kategoriya | Testlar soni | DB kerakmi? |
|-----------|-------------|-------------|
| Domain tests | 21 | Yo'q |
| Service tests | 20 | Yo'q |
| Repository tests | 24 | Ha |
| Model tests | 19 | Ha |
| Serializer tests | 21 | Ha |
| View tests | 38 | Ha |
| **Jami** | **143** | |

## Layer Bo'yicha Test Strategiyasi

### 1. Domain Tests (`test_domain.py`)

**Nima test qilinadi:** Entity yaratish, property'lar, enum qiymatlari, exceptionlar.

**DB:** kerak emas | **Mock:** kerak emas | **Tezligi:** eng tez

```python
def test_book_entity_default_values():
    book = BookEntity(
        title="Test",
        author="Author",
        isbn="1234567890",
        published_date=date(2024, 1, 1),
        page_count=100,
    )
    assert book.language == "English"
    assert book.genre == Genre.OTHER
    assert book.description == ""

def test_genre_enum_values():
    assert Genre.FICTION == "fiction"
    assert Genre.TECHNOLOGY == "technology"

def test_book_not_found_error():
    with pytest.raises(BookNotFoundError):
        raise BookNotFoundError("Kitob topilmadi")
```

### 2. Service Tests (`test_services.py`)

**Nima test qilinadi:** Biznes logika — yaratish, yangilash, o'chirish, validatsiya.

**DB:** kerak emas | **Mock:** Ha (repository) | **Tezligi:** tez

```python
@pytest.fixture
def mock_repo():
    return MagicMock(spec=AbstractBookRepository)

@pytest.fixture
def service(mock_repo):
    return BookService(repository=mock_repo)

def test_create_book_success(service, mock_repo, sample_entity):
    mock_repo.exists_by_isbn.return_value = False
    mock_repo.create.return_value = sample_entity

    result = service.create_book(sample_entity)

    mock_repo.exists_by_isbn.assert_called_once_with(sample_entity.isbn)
    mock_repo.create.assert_called_once_with(sample_entity)
    assert result == sample_entity

def test_create_book_duplicate_isbn(service, mock_repo, sample_entity):
    mock_repo.exists_by_isbn.return_value = True

    with pytest.raises(DuplicateISBNError):
        service.create_book(sample_entity)
```

### 3. Repository Tests (`test_repositories.py`)

**Nima test qilinadi:** ORM operatsiyalari, entity mapping, DB integratsiya.

**DB:** ha | **Mock:** yo'q | **Tezligi:** o'rtacha

```python
@pytest.mark.django_db
def test_create_and_get_book(book_data):
    repo = DjangoBookRepository()
    entity = BookEntity(**book_data)

    created = repo.create(entity)
    assert created.id is not None
    assert created.title == entity.title

    fetched = repo.get_by_id(created.id)
    assert fetched.isbn == entity.isbn
```

### 4. Model Tests (`test_models.py`)

**Nima test qilinadi:** Django model validatsiya, `__str__`, Meta options, constraintlar.

**DB:** ha | **Mock:** yo'q

```python
@pytest.mark.django_db
def test_book_str(book):
    assert str(book) == "Clean Code by Robert C. Martin"

@pytest.mark.django_db
def test_isbn_unique_constraint(user, book_data):
    Book.objects.create(created_by=user, **book_data)
    with pytest.raises(IntegrityError):
        Book.objects.create(created_by=user, **book_data)
```

### 5. Serializer Tests (`test_serializers.py`)

**Nima test qilinadi:** DRF data validatsiya, field presence, read-only fields.

**DB:** ha (model instance kerak) | **Mock:** yo'q

```python
@pytest.mark.django_db
def test_registration_password_mismatch():
    data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "StrongPass123!",
        "password_confirm": "DifferentPass456!",
    }
    serializer = UserRegistrationSerializer(data=data)
    assert not serializer.is_valid()
    assert "password_confirm" in serializer.errors
```

### 6. View Tests (`test_views.py`)

**Nima test qilinadi:** HTTP endpointlar, permissionlar, filtrlash, pagination.

**DB:** ha | **Mock:** yo'q | **Tezligi:** eng sekin (to'liq HTTP cycle)

```python
@pytest.mark.django_db
def test_create_book_authenticated(auth_client, book_data):
    response = auth_client.post(reverse("books:book-list"), book_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == book_data["title"]

@pytest.mark.django_db
def test_create_book_unauthenticated(api_client, book_data):
    response = api_client.post(reverse("books:book-list"), book_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_update_book_not_owner(auth_client, book, second_user):
    # Boshqa userning kitobini o'zgartirish — 403
    book.created_by = second_user
    book.save()
    response = auth_client.patch(
        reverse("books:book-detail", args=[book.id]),
        {"title": "Hacked"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
```

## Shared Fixtures (`conftest.py`)

| Fixture | Qaytaradi | Tavsif |
|---------|----------|--------|
| `api_client` | `APIClient` | Autentifikatsiyasiz API client |
| `user_data` | `dict` | Valid user ma'lumotlari |
| `create_user` | factory function | User yaratish uchun factory |
| `user` | `CustomUser` | Oddiy (non-admin) foydalanuvchi |
| `admin_user` | `CustomUser` | Admin foydalanuvchi (`is_staff=True`) |
| `auth_client` | `APIClient` | Oddiy user JWT tokeni bilan |
| `admin_client` | `APIClient` | Admin JWT tokeni bilan |
| `book_data` | `dict` | Valid kitob ma'lumotlari |
| `book` | `Book` | DB dagi kitob (user yaratgan) |
| `second_user` | `CustomUser` | Permission test uchun ikkinchi user |

## Mock vs Real DB Qoidalari

| Layer | Mock | Real DB | Sabab |
|-------|------|---------|-------|
| Domain | Yo'q | Yo'q | Pure Python, framework yo'q |
| Service | Ha (repository) | Yo'q | Biznes logikani izolyatsiya qilish |
| Repository | Yo'q | Ha | ORM integratsiyani tekshirish |
| Model | Yo'q | Ha | Django model xatti-harakati |
| Serializer | Yo'q | Ha | Validation + model instance |
| View | Yo'q | Ha | To'liq HTTP cycle |

> **Qoida:** Agar layerda Django ORM ishlatilsa — real DB kerak.
> Agar pure Python yoki mock bilan ishlasa — DB kerak emas.

## Coverage Maqsadlari

- **Umumiy:** 90%+ coverage
- **Domain/Service:** 100% (kichik, muhim kod)
- **View testlari:** barcha permission kombinatsiyalari qamrab olinishi kerak

Coverage tekshirish:
```bash
make test-cov    # pytest --cov=apps --cov-report=term-missing
```

## Test Buyruqlari

```bash
# Barcha testlar
make test                                        # pytest -v

# Faqat bitta app testlari
pytest apps/books/tests/ -v
pytest apps/users/tests/ -v

# Faqat bitta test fayli
pytest apps/books/tests/test_services.py -v

# Nomi bo'yicha filtrlash
pytest -k "test_create" -v

# Faqat domain testlari (DB siz, eng tez)
pytest -k "test_domain" -v

# Coverage bilan
pytest --cov=apps --cov-report=term-missing -v

# Batafsil xato ma'lumoti
pytest -v --tb=long
```

## Yangi Test Yozish Qoidalari

1. Har bir layer uchun **alohida test fayli** — `test_<layer>.py`
2. Har bir test uchun kamida **happy path + xato holat**
3. Domain va Service testlari **DB ishlatmasligi** kerak
4. `@pytest.mark.django_db` faqat DB kerak bo'lganda qo'shiladi
5. `conftest.py` dagi shared fixturelardan foydalaning
6. Test nomlarida nima test qilinayotgani aniq bo'lsin: `test_create_book_duplicate_isbn`

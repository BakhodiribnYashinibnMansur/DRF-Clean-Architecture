# Test Strategy

**143 tests**, all passing. Each app has **6 test files** — separated by layer.

## Overall Statistics

| Category | Test count | DB required? |
|----------|-----------|-------------|
| Domain tests | 21 | No |
| Service tests | 20 | No |
| Repository tests | 24 | Yes |
| Model tests | 19 | Yes |
| Serializer tests | 21 | Yes |
| View tests | 38 | Yes |
| **Total** | **143** | |

## Test Strategy by Layer

### 1. Domain Tests (`test_domain.py`)

**What's tested:** Entity creation, properties, enum values, exceptions.

**DB:** not required | **Mock:** not required | **Speed:** fastest

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
        raise BookNotFoundError("Book not found")
```

### 2. Service Tests (`test_services.py`)

**What's tested:** Business logic — create, update, delete, validation.

**DB:** not required | **Mock:** Yes (repository) | **Speed:** fast

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

**What's tested:** ORM operations, entity mapping, DB integration.

**DB:** yes | **Mock:** no | **Speed:** medium

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

**What's tested:** Django model validation, `__str__`, Meta options, constraints.

**DB:** yes | **Mock:** no

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

**What's tested:** DRF data validation, field presence, read-only fields.

**DB:** yes (model instance needed) | **Mock:** no

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

**What's tested:** HTTP endpoints, permissions, filtering, pagination.

**DB:** yes | **Mock:** no | **Speed:** slowest (full HTTP cycle)

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
    # Trying to modify another user's book — 403
    book.created_by = second_user
    book.save()
    response = auth_client.patch(
        reverse("books:book-detail", args=[book.id]),
        {"title": "Hacked"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
```

## Shared Fixtures (`conftest.py`)

| Fixture | Returns | Description |
|---------|---------|-------------|
| `api_client` | `APIClient` | Unauthenticated API client |
| `user_data` | `dict` | Valid user data |
| `create_user` | factory function | Factory for creating users |
| `user` | `CustomUser` | Regular (non-admin) user |
| `admin_user` | `CustomUser` | Admin user (`is_staff=True`) |
| `auth_client` | `APIClient` | Regular user with JWT token |
| `admin_client` | `APIClient` | Admin with JWT token |
| `book_data` | `dict` | Valid book data |
| `book` | `Book` | Book in DB (created by user) |
| `second_user` | `CustomUser` | Second user for permission tests |

## Mock vs Real DB Rules

| Layer | Mock | Real DB | Reason |
|-------|------|---------|--------|
| Domain | No | No | Pure Python, no framework |
| Service | Yes (repository) | No | Isolate business logic |
| Repository | No | Yes | Verify ORM integration |
| Model | No | Yes | Django model behavior |
| Serializer | No | Yes | Validation + model instance |
| View | No | Yes | Full HTTP cycle |

> **Rule:** If the layer uses Django ORM — real DB is required.
> If it works with pure Python or mocks — no DB needed.

## Coverage Goals

- **Overall:** 90%+ coverage
- **Domain/Service:** 100% (small, critical code)
- **View tests:** all permission combinations should be covered

Check coverage:
```bash
make test-cov    # pytest --cov=apps --cov-report=term-missing
```

## Test Commands

```bash
# All tests
make test                                        # pytest -v

# Only one app's tests
pytest apps/books/tests/ -v
pytest apps/users/tests/ -v

# Only one test file
pytest apps/books/tests/test_services.py -v

# Filter by name
pytest -k "test_create" -v

# Only domain tests (no DB, fastest)
pytest -k "test_domain" -v

# With coverage
pytest --cov=apps --cov-report=term-missing -v

# Detailed error info
pytest -v --tb=long
```

## Rules for Writing New Tests

1. A **separate test file** for each layer — `test_<layer>.py`
2. At least **happy path + error case** for each test
3. Domain and Service tests **must not use DB**
4. `@pytest.mark.django_db` only when DB is needed
5. Use shared fixtures from `conftest.py`
6. Test names should clearly state what is being tested: `test_create_book_duplicate_isbn`

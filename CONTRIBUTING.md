# Contributing

**How to contribute to the project** — rules and guidelines.

## Running the Project Locally

```bash
# 1. Clone the repository
git clone <repository-url>
cd DRF

# 2. Create the .env file
cp .env.example .env
# Edit the values in .env

# 3. Install dependencies
uv sync --all-extras

# 4. Database migrations
make migrate

# 5. Create superuser
make superuser

# 6. Start the server
make run
```

## Git Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code. Direct push is prohibited |
| `develop` | Integration branch. All features are merged here |
| `feature/*` | New functionality. Example: `feature/add-category-filter` |
| `fix/*` | Bug fixes. Example: `fix/isbn-validation-error` |
| `docs/*` | Documentation. Example: `docs/add-api-examples` |

### Creating a Branch

```bash
# New branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

## Commit Conventions

### Format

```
type(scope): short description
```

### Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New functionality | `feat(books): add genre filtering endpoint` |
| `fix` | Bug fix | `fix(users): validate email before registration` |
| `refactor` | Code rewrite (no functionality change) | `refactor(books): move validation to service layer` |
| `test` | Add or modify tests | `test(users): add password change edge cases` |
| `docs` | Documentation | `docs: add API examples` |
| `chore` | Technical tasks (config, dependencies) | `chore: update pyproject.toml` |

### Scope Types

| Scope | Description |
|-------|-------------|
| `books` | Books app |
| `users` | Users app |
| `config` | Configuration (settings, urls) |
| `docs` | Documentation |

### Examples

```bash
git commit -m "feat(books): add published_year filter"
git commit -m "fix(users): handle duplicate email on registration"
git commit -m "test(books): add ISBN uniqueness test cases"
git commit -m "docs: update API endpoint documentation"
```

## Pull Request Rules

### Creating a PR

1. Use a clear branch name (`feature/add-genre-filter`, `fix/isbn-bug`)
2. Include the following in the PR description:
   - **What was changed** — brief description
   - **Why** — the problem or requirement
   - **How it was tested** — tests, manual verification

### PR Merge Rules

- At least **1 approval** required
- All **tests must pass** (`pytest`)
- **Lint check** must pass (`ruff check apps/`)
- No merge conflicts

## Code Standards

### Python Style

- **Linter:** `ruff` (check with `make lint`)
- **Formatter:** `ruff format` or project standards
- **Type hints:** required in domain and application layers
- **Docstring:** for every class and public method

### Import Order

```python
# 1. Python stdlib
from dataclasses import dataclass
from datetime import date

# 2. Third-party
from rest_framework import viewsets
from django.db import models

# 3. Local imports
from apps.books.domain.entities import BookEntity
from apps.books.application.services import BookService
```

## Clean Architecture Rules

### Layer Dependencies

```
Domain          ← imports nothing
Application     ← only from Domain
Infrastructure  ← from Domain and Application
Presentation    ← from all layers
```

### Import Rules Table

| Layer | CAN import | CANNOT import |
|-------|-----------|---------------|
| Domain | Python stdlib | Django, DRF, Application, Infrastructure, Presentation |
| Application | Domain | Django, DRF, Infrastructure, Presentation |
| Infrastructure | Domain, Application, Django ORM | DRF, Presentation |
| Presentation | Everything | — |

> **Important:** Breaking this rule leads to architecture violations.

## Adding a New Feature (7 Steps)

For example, adding a `Category` entity:

### Step 1: Domain Layer
```python
# domain/entities.py
@dataclass
class CategoryEntity:
    name: str
    id: Optional[int] = None
```

```python
# domain/exceptions.py
class CategoryNotFoundError(Exception): ...
class DuplicateCategoryError(Exception): ...
```

### Step 2: Application Layer
```python
# application/interfaces.py
class AbstractCategoryRepository(ABC):
    @abstractmethod
    def get_by_id(self, category_id: int) -> Optional[CategoryEntity]: ...
    @abstractmethod
    def create(self, entity: CategoryEntity) -> CategoryEntity: ...
```

```python
# application/services.py
class CategoryService:
    def __init__(self, repository: AbstractCategoryRepository):
        self._repo = repository
```

### Step 3: Infrastructure Layer
```python
# infrastructure/models.py
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
```

```python
# infrastructure/repositories.py
class DjangoCategoryRepository(AbstractCategoryRepository):
    def get_by_id(self, category_id): ...
    def create(self, entity): ...
```

### Step 4: Presentation Layer
- `serializers.py` — `CategorySerializer`
- `views.py` — `CategoryViewSet`
- `permissions.py` — if needed
- `urls.py` — router registration

### Step 5: Proxy Model
```python
# apps/<app>/models.py
from apps.<app>.infrastructure.models import Category
```

### Step 6: Tests
- `test_domain.py` — entity and exception tests
- `test_services.py` — service tests with mock repository
- `test_repositories.py` — integration tests with real DB
- `test_models.py` — ORM model tests
- `test_serializers.py` — serializer validation tests
- `test_views.py` — HTTP endpoint tests

### Step 7: Documentation
- Update layer READMEs
- Add API endpoints to main README

## Test Writing Rules

1. A **separate test file** for each layer (`test_<layer>.py`)
2. At least **happy path + error case** for each test
3. Domain and Service tests **must not use DB**
4. `@pytest.mark.django_db` only when DB is needed
5. Use shared fixtures from `conftest.py`
6. Test names should be clear: `test_create_book_duplicate_isbn`

### Running Tests

```bash
make test           # All tests
make test-cov       # With coverage
pytest -k "test_create" -v   # By name
```

## Useful Commands

```bash
uv sync --all-extras # Install dependencies
make run             # Development server
make migrate         # Migrations
make test            # Tests
make test-cov        # Test coverage
make lint            # Ruff lint
make shell           # Django shell
make superuser       # Create superuser
make flush           # Clear database
```

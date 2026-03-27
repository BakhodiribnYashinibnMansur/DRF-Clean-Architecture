# Loyihaga Hissa Qo'shish (Contributing)

**Loyihaga qanday hissa qo'shish mumkin** — qoidalar va yo'riqnomalar.

## Loyihani Lokal Ishga Tushirish

```bash
# 1. Repository ni clone qiling
git clone <repository-url>
cd DRF

# 2. .env faylini yarating
cp .env.example .env
# .env ichidagi qiymatlarni o'zgartiring

# 3. Dependencylarni o'rnating
uv sync --all-extras

# 4. Database migratsiyalari
make migrate

# 5. Superuser yarating
make superuser

# 6. Serverni ishga tushiring
make run
```

## Git Branching Strategiyasi

| Branch | Vazifasi |
|--------|---------|
| `main` | Production-ready kod. To'g'ridan-to'g'ri push qilish taqiqlangan |
| `develop` | Integration branch. Barcha feature'lar bu yerga merge qilinadi |
| `feature/*` | Yangi funksionallik. Masalan: `feature/add-category-filter` |
| `fix/*` | Xato tuzatish. Masalan: `fix/isbn-validation-error` |
| `docs/*` | Dokumentatsiya. Masalan: `docs/add-api-examples` |

### Branch yaratish

```bash
# develop dan yangi branch
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

## Commit Konventsiyalari

### Format

```
type(scope): qisqa tavsif
```

### Commit turlari

| Type | Tavsif | Misol |
|------|--------|-------|
| `feat` | Yangi funksionallik | `feat(books): add genre filtering endpoint` |
| `fix` | Xato tuzatish | `fix(users): validate email before registration` |
| `refactor` | Kod qayta yozish (funksionallik o'zgarmaydi) | `refactor(books): move validation to service layer` |
| `test` | Test qo'shish yoki o'zgartirish | `test(users): add password change edge cases` |
| `docs` | Dokumentatsiya | `docs: add API examples` |
| `chore` | Texnik ishlar (config, dependency) | `chore: update pyproject.toml` |

### Scope turlari

| Scope | Tavsif |
|-------|--------|
| `books` | Books app |
| `users` | Users app |
| `config` | Konfiguratsiya (settings, urls) |
| `docs` | Dokumentatsiya |

### Misollar

```bash
git commit -m "feat(books): add published_year filter"
git commit -m "fix(users): handle duplicate email on registration"
git commit -m "test(books): add ISBN uniqueness test cases"
git commit -m "docs: update API endpoint documentation"
```

## Pull Request Qoidalari

### PR yaratish

1. Branch nomini tushunarli qiling (`feature/add-genre-filter`, `fix/isbn-bug`)
2. PR tavsifida quyidagilarni yozing:
   - **Nima o'zgartirildi** — qisqacha tavsif
   - **Nima uchun** — muammo yoki talab
   - **Qanday test qilindi** — testlar, qo'lda tekshirish

### PR merge qoidalari

- Kamida **1 ta approval** kerak
- Barcha **testlar o'tishi** shart (`pytest`)
- **Lint tekshiruvi** o'tishi shart (`ruff check apps/`)
- Merge conflict bo'lmasligi kerak

## Kod Yozish Standartlari

### Python Style

- **Linter:** `ruff` (`make lint` bilan tekshiring)
- **Formatter:** `ruff format` yoki loyiha standartlari
- **Type hints:** domain va application layerlarda majburiy
- **Docstring:** har bir class va public method uchun

### Import tartibi

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

## Clean Architecture Qoidalari

### Layer bog'liqliklari

```
Domain          ← hech narsadan import qilmaydi
Application     ← faqat Domain dan
Infrastructure  ← Domain va Application dan
Presentation    ← barcha layerlardan
```

### Import qilish qoidalari jadvali

| Layer | Import qilishi MUMKIN | Import qilishi MUMKIN EMAS |
|-------|----------------------|---------------------------|
| Domain | Python stdlib | Django, DRF, Application, Infrastructure, Presentation |
| Application | Domain | Django, DRF, Infrastructure, Presentation |
| Infrastructure | Domain, Application, Django ORM | DRF, Presentation |
| Presentation | Hammasi | — |

> **Muhim:** Bu qoidani buzish arxitektura buzilishiga olib keladi.

## Yangi Feature Qo'shish (7 Bosqich)

Masalan, `Category` entity qo'shmoqchisiz:

### 1-bosqich: Domain Layer
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

### 2-bosqich: Application Layer
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

### 3-bosqich: Infrastructure Layer
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

### 4-bosqich: Presentation Layer
- `serializers.py` — `CategorySerializer`
- `views.py` — `CategoryViewSet`
- `permissions.py` — kerak bo'lsa
- `urls.py` — router registratsiya

### 5-bosqich: Proxy Model
```python
# apps/<app>/models.py
from apps.<app>.infrastructure.models import Category
```

### 6-bosqich: Testlar
- `test_domain.py` — entity va exception testlari
- `test_services.py` — mock repository bilan service testlari
- `test_repositories.py` — real DB bilan integration testlari
- `test_models.py` — ORM model testlari
- `test_serializers.py` — serializer validatsiya testlari
- `test_views.py` — HTTP endpoint testlari

### 7-bosqich: Dokumentatsiya
- Layer README'larini yangilang
- API endpointlarni asosiy README ga qo'shing

## Test Yozish Qoidalari

1. Har bir layer uchun **alohida test fayli** (`test_<layer>.py`)
2. Har bir test uchun kamida **happy path + xato holat**
3. Domain va Service testlari **DB ishlatmasligi** kerak
4. `@pytest.mark.django_db` faqat DB kerak bo'lganda
5. `conftest.py` dagi shared fixturelardan foydalaning
6. Test nomlari aniq bo'lsin: `test_create_book_duplicate_isbn`

### Testlarni ishga tushirish

```bash
make test           # Barcha testlar
make test-cov       # Coverage bilan
pytest -k "test_create" -v   # Nomi bo'yicha
```

## Foydali Buyruqlar

```bash
uv sync --all-extras # Dependencylar o'rnatish
make run             # Development server
make migrate         # Migratsiyalar
make test            # Testlar
make test-cov        # Test coverage
make lint            # Ruff lint
make shell           # Django shell
make superuser       # Superuser yaratish
make flush           # Database tozalash
```

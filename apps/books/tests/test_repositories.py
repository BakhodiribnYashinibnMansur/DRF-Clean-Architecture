# ============================================
# Book Repository Integration Tests
# Tests the DjangoBookRepository against a real database.
# Verifies ORM operations and entity mapping.
# ============================================

from datetime import date

import pytest

from apps.books.domain.entities import BookEntity, Genre
from apps.books.infrastructure.models import Book
from apps.books.infrastructure.repositories import DjangoBookRepository


@pytest.fixture
def repo():
    """Return a DjangoBookRepository instance."""
    return DjangoBookRepository()


@pytest.fixture
def sample_entity(user):
    """Return a sample BookEntity for testing."""
    return BookEntity(
        title="Repo Test Book",
        author="Repo Author",
        isbn="1111111111",
        published_date=date(2020, 6, 15),
        page_count=300,
        language="English",
        genre=Genre.SCIENCE,
        description="A book for repo testing.",
        created_by_id=user.id,
    )


@pytest.mark.django_db
class TestDjangoBookRepositoryCreate:
    """Tests for DjangoBookRepository.create()."""

    def test_create_persists_to_db(self, repo, sample_entity):
        """create() should persist the book to the database."""
        result = repo.create(sample_entity)

        assert result.id is not None
        assert result.title == "Repo Test Book"
        assert result.isbn == "1111111111"
        assert result.genre == Genre.SCIENCE
        assert Book.objects.filter(isbn="1111111111").exists()

    def test_create_sets_timestamps(self, repo, sample_entity):
        """create() should auto-populate created_at and updated_at."""
        result = repo.create(sample_entity)

        assert result.created_at is not None
        assert result.updated_at is not None


@pytest.mark.django_db
class TestDjangoBookRepositoryRead:
    """Tests for DjangoBookRepository.get_by_id() and get_all()."""

    def test_get_by_id_returns_entity(self, repo, sample_entity):
        """get_by_id() should return a BookEntity for an existing book."""
        created = repo.create(sample_entity)

        result = repo.get_by_id(created.id)

        assert result is not None
        assert result.title == "Repo Test Book"
        assert isinstance(result, BookEntity)

    def test_get_by_id_returns_none_for_missing(self, repo):
        """get_by_id() should return None for a non-existent ID."""
        result = repo.get_by_id(99999)
        assert result is None

    def test_get_all_returns_list(self, repo, sample_entity):
        """get_all() should return a list of BookEntity objects."""
        repo.create(sample_entity)

        results = repo.get_all()

        assert len(results) >= 1
        assert all(isinstance(r, BookEntity) for r in results)


@pytest.mark.django_db
class TestDjangoBookRepositoryUpdate:
    """Tests for DjangoBookRepository.update()."""

    def test_update_modifies_fields(self, repo, sample_entity):
        """update() should modify the book's fields in the database."""
        created = repo.create(sample_entity)
        created.title = "Updated Title"

        result = repo.update(created)

        assert result.title == "Updated Title"
        db_book = Book.objects.get(id=created.id)
        assert db_book.title == "Updated Title"


@pytest.mark.django_db
class TestDjangoBookRepositoryDelete:
    """Tests for DjangoBookRepository.delete()."""

    def test_delete_removes_from_db(self, repo, sample_entity):
        """delete() should remove the book from the database."""
        created = repo.create(sample_entity)

        repo.delete(created.id)

        assert not Book.objects.filter(id=created.id).exists()


@pytest.mark.django_db
class TestDjangoBookRepositoryExistsByIsbn:
    """Tests for DjangoBookRepository.exists_by_isbn()."""

    def test_exists_by_isbn_returns_true(self, repo, sample_entity):
        """exists_by_isbn() should return True when ISBN exists."""
        repo.create(sample_entity)

        assert repo.exists_by_isbn("1111111111") is True

    def test_exists_by_isbn_returns_false(self, repo):
        """exists_by_isbn() should return False when ISBN doesn't exist."""
        assert repo.exists_by_isbn("9999999999") is False

    def test_exists_by_isbn_excludes_id(self, repo, sample_entity):
        """exists_by_isbn() should exclude the specified ID."""
        created = repo.create(sample_entity)

        # Same ISBN but excluded ID — should return False
        assert repo.exists_by_isbn("1111111111", exclude_id=created.id) is False
        # Same ISBN without exclusion — should return True
        assert repo.exists_by_isbn("1111111111") is True

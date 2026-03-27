# ============================================
# Book Service Layer Tests
# Unit tests with mocked repository.
# Tests business logic without touching the database.
# ============================================

from datetime import date
from unittest.mock import MagicMock

import pytest

from apps.books.application.interfaces import AbstractBookRepository
from apps.books.application.services import BookService
from apps.books.domain.entities import BookEntity, Genre
from apps.books.domain.exceptions import BookNotFoundError, DuplicateISBNError


@pytest.fixture
def mock_repo():
    """Return a mocked AbstractBookRepository."""
    return MagicMock(spec=AbstractBookRepository)


@pytest.fixture
def service(mock_repo):
    """Return a BookService with a mocked repository."""
    return BookService(repository=mock_repo)


@pytest.fixture
def sample_entity():
    """Return a sample BookEntity for testing."""
    return BookEntity(
        title="Test Book",
        author="Test Author",
        isbn="1234567890",
        published_date=date(2020, 1, 1),
        page_count=200,
        genre=Genre.TECHNOLOGY,
    )


class TestBookServiceCreate:
    """Tests for BookService.create_book()."""

    def test_create_book_success(self, service, mock_repo, sample_entity):
        """create_book should call repo.create when ISBN is unique."""
        mock_repo.exists_by_isbn.return_value = False
        mock_repo.create.return_value = sample_entity

        result = service.create_book(sample_entity)

        mock_repo.exists_by_isbn.assert_called_once_with(sample_entity.isbn)
        mock_repo.create.assert_called_once_with(sample_entity)
        assert result == sample_entity

    def test_create_book_duplicate_isbn_raises_error(self, service, mock_repo, sample_entity):
        """create_book should raise DuplicateISBNError when ISBN exists."""
        mock_repo.exists_by_isbn.return_value = True

        with pytest.raises(DuplicateISBNError, match="already exists"):
            service.create_book(sample_entity)

        mock_repo.create.assert_not_called()


class TestBookServiceGet:
    """Tests for BookService.get_book()."""

    def test_get_book_success(self, service, mock_repo, sample_entity):
        """get_book should return the entity when found."""
        mock_repo.get_by_id.return_value = sample_entity

        result = service.get_book(1)

        mock_repo.get_by_id.assert_called_once_with(1)
        assert result == sample_entity

    def test_get_book_not_found_raises_error(self, service, mock_repo):
        """get_book should raise BookNotFoundError when not found."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(BookNotFoundError, match="not found"):
            service.get_book(999)


class TestBookServiceUpdate:
    """Tests for BookService.update_book()."""

    def test_update_book_success(self, service, mock_repo, sample_entity):
        """update_book should call repo.update when ISBN doesn't conflict."""
        sample_entity.id = 1
        mock_repo.exists_by_isbn.return_value = False
        mock_repo.update.return_value = sample_entity

        result = service.update_book(sample_entity)

        mock_repo.exists_by_isbn.assert_called_once_with(sample_entity.isbn, exclude_id=1)
        mock_repo.update.assert_called_once_with(sample_entity)
        assert result == sample_entity

    def test_update_book_duplicate_isbn_raises_error(self, service, mock_repo, sample_entity):
        """update_book should raise DuplicateISBNError when ISBN conflicts."""
        sample_entity.id = 1
        mock_repo.exists_by_isbn.return_value = True

        with pytest.raises(DuplicateISBNError):
            service.update_book(sample_entity)

        mock_repo.update.assert_not_called()


class TestBookServiceDelete:
    """Tests for BookService.delete_book()."""

    def test_delete_book_success(self, service, mock_repo, sample_entity):
        """delete_book should call repo.delete when book exists."""
        mock_repo.get_by_id.return_value = sample_entity

        service.delete_book(1)

        mock_repo.delete.assert_called_once_with(1)

    def test_delete_book_not_found_raises_error(self, service, mock_repo):
        """delete_book should raise BookNotFoundError when book doesn't exist."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(BookNotFoundError):
            service.delete_book(999)

        mock_repo.delete.assert_not_called()


class TestBookServiceGetAll:
    """Tests for BookService.get_all_books()."""

    def test_get_all_books(self, service, mock_repo, sample_entity):
        """get_all_books should return list from repository."""
        mock_repo.get_all.return_value = [sample_entity]

        result = service.get_all_books()

        mock_repo.get_all.assert_called_once()
        assert len(result) == 1
        assert result[0] == sample_entity

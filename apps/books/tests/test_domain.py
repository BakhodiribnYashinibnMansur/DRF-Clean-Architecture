# ============================================
# Book Domain Layer Tests
# Pure unit tests — no database, no Django.
# Tests entity creation, Genre enum, and domain exceptions.
# ============================================

from datetime import date

from apps.books.domain.entities import BookEntity, Genre
from apps.books.domain.exceptions import (
    BookNotFoundError,
    BookPermissionDeniedError,
    DuplicateISBNError,
)


class TestBookEntity:
    """Tests for the BookEntity dataclass."""

    def test_create_entity_with_required_fields(self):
        """BookEntity should be creatable with just the required fields."""
        entity = BookEntity(
            title="Test Book",
            author="Test Author",
            isbn="1234567890",
            published_date=date(2020, 1, 1),
            page_count=200,
        )
        assert entity.title == "Test Book"
        assert entity.author == "Test Author"
        assert entity.isbn == "1234567890"
        assert entity.page_count == 200

    def test_default_field_values(self):
        """BookEntity should have correct default values."""
        entity = BookEntity(
            title="Test",
            author="Author",
            isbn="1234567890",
            published_date=date(2020, 1, 1),
            page_count=100,
        )
        assert entity.language == "English"
        assert entity.genre == Genre.OTHER
        assert entity.description == ""
        assert entity.id is None
        assert entity.created_by_id is None
        assert entity.created_at is None
        assert entity.updated_at is None

    def test_entity_str_representation(self):
        """BookEntity __str__ should return 'title by author'."""
        entity = BookEntity(
            title="Clean Code",
            author="Robert Martin",
            isbn="1234567890",
            published_date=date(2020, 1, 1),
            page_count=400,
        )
        assert str(entity) == "Clean Code by Robert Martin"

    def test_entity_with_all_fields(self):
        """BookEntity should accept all optional fields."""
        entity = BookEntity(
            title="Full Book",
            author="Full Author",
            isbn="9781234567890",
            published_date=date(2023, 6, 15),
            page_count=350,
            language="Uzbek",
            genre=Genre.TECHNOLOGY,
            description="A great book.",
            id=42,
            created_by_id=7,
        )
        assert entity.id == 42
        assert entity.language == "Uzbek"
        assert entity.genre == Genre.TECHNOLOGY
        assert entity.created_by_id == 7


class TestGenreEnum:
    """Tests for the Genre enum."""

    def test_genre_values(self):
        """Genre enum should contain all expected values."""
        assert Genre.FICTION.value == "fiction"
        assert Genre.TECHNOLOGY.value == "technology"
        assert Genre.SCIENCE.value == "science"
        assert Genre.OTHER.value == "other"

    def test_genre_is_string_enum(self):
        """Genre members should be usable as strings."""
        assert Genre.FICTION == "fiction"
        assert isinstance(Genre.FICTION, str)

    def test_genre_count(self):
        """Genre should have 14 members."""
        assert len(Genre) == 14

    def test_genre_from_value(self):
        """Genre should be constructable from a string value."""
        genre = Genre("technology")
        assert genre == Genre.TECHNOLOGY


class TestBookExceptions:
    """Tests for domain exception classes."""

    def test_book_not_found_error(self):
        """BookNotFoundError should be instantiable with a message."""
        error = BookNotFoundError("Book 42 not found")
        assert str(error) == "Book 42 not found"
        assert isinstance(error, Exception)

    def test_duplicate_isbn_error(self):
        """DuplicateISBNError should be instantiable with a message."""
        error = DuplicateISBNError("ISBN 123 exists")
        assert str(error) == "ISBN 123 exists"

    def test_permission_denied_error(self):
        """BookPermissionDeniedError should be an Exception."""
        error = BookPermissionDeniedError("Not allowed")
        assert isinstance(error, Exception)

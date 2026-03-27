# ============================================
# Book Model Tests
# Tests for book creation, validation, and model behavior.
# ============================================

import pytest
from django.core.exceptions import ValidationError

from apps.books.models import Book


@pytest.mark.django_db
class TestBookModel:
    """Tests for the Book model."""

    def test_create_book(self, book):
        """Book should be created with correct field values."""
        assert book.title == "Clean Code"
        assert book.author == "Robert C. Martin"
        assert book.isbn == "9780132350884"
        assert book.page_count == 464
        assert book.genre == "technology"

    def test_book_str_representation(self, book):
        """Book __str__ should return 'title by author'."""
        assert str(book) == "Clean Code by Robert C. Martin"

    def test_book_ordering(self, db, user):
        """Books should be ordered by -created_at (newest first)."""
        book1 = Book.objects.create(
            title="First",
            author="Author A",
            isbn="1234567890",
            published_date="2020-01-01",
            page_count=100,
            created_by=user,
        )
        book2 = Book.objects.create(
            title="Second",
            author="Author B",
            isbn="1234567890123",
            published_date="2021-01-01",
            page_count=200,
            created_by=user,
        )
        books = list(Book.objects.all())
        assert books[0] == book2  # Newer book first
        assert books[1] == book1

    def test_genre_choices(self):
        """Genre TextChoices should contain expected values."""
        genre_values = [choice[0] for choice in Book.Genre.choices]
        assert "fiction" in genre_values
        assert "technology" in genre_values
        assert "science" in genre_values

    def test_isbn_validator_rejects_invalid(self, db, user):
        """ISBN with wrong format should fail model validation."""
        book = Book(
            title="Bad ISBN",
            author="Author",
            isbn="ABC123",  # Invalid ISBN format
            published_date="2020-01-01",
            page_count=100,
            created_by=user,
        )
        with pytest.raises(ValidationError):
            book.full_clean()

    def test_isbn_uniqueness(self, book, user):
        """Duplicate ISBN should raise an error."""
        with pytest.raises(Exception):  # IntegrityError
            Book.objects.create(
                title="Duplicate",
                author="Author",
                isbn=book.isbn,  # Same ISBN
                published_date="2021-01-01",
                page_count=100,
                created_by=user,
            )

    def test_book_created_by_can_be_null(self, db):
        """Book should allow created_by to be null (anonymous addition)."""
        book = Book.objects.create(
            title="No Author Track",
            author="Unknown",
            isbn="9876543210",
            published_date="2020-01-01",
            page_count=50,
            created_by=None,
        )
        assert book.created_by is None

    def test_auto_timestamps(self, book):
        """created_at and updated_at should be auto-populated."""
        assert book.created_at is not None
        assert book.updated_at is not None

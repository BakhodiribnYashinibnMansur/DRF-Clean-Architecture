# ============================================
# Book Serializer Tests
# Tests for book data validation and serialization.
# ============================================

import pytest

from apps.books.models import Book
from apps.books.presentation.serializers import BookDetailSerializer, BookListSerializer


@pytest.mark.django_db
class TestBookListSerializer:
    """Tests for the BookListSerializer."""

    def test_list_serializer_excludes_description(self, book):
        """List serializer should not include the description field."""
        serializer = BookListSerializer(book)
        assert "description" not in serializer.data

    def test_list_serializer_includes_created_by(self, book):
        """List serializer should show created_by as {id, email}."""
        serializer = BookListSerializer(book)
        assert serializer.data["created_by"]["email"] == book.created_by.email

    def test_list_serializer_null_created_by(self, db):
        """created_by should be None when no user is associated."""
        book = Book.objects.create(
            title="No Owner",
            author="Author",
            isbn="1111111111",
            published_date="2020-01-01",
            page_count=100,
            created_by=None,
        )
        serializer = BookListSerializer(book)
        assert serializer.data["created_by"] is None


@pytest.mark.django_db
class TestBookDetailSerializer:
    """Tests for the BookDetailSerializer."""

    def test_detail_serializer_includes_description(self, book):
        """Detail serializer should include the description field."""
        serializer = BookDetailSerializer(book)
        assert "description" in serializer.data

    def test_detail_serializer_includes_timestamps(self, book):
        """Detail serializer should include created_at and updated_at."""
        serializer = BookDetailSerializer(book)
        assert "created_at" in serializer.data
        assert "updated_at" in serializer.data

    def test_valid_book_data(self, book_data):
        """Valid book data should pass serializer validation."""
        serializer = BookDetailSerializer(data=book_data)
        assert serializer.is_valid(), serializer.errors

    def test_missing_required_fields(self):
        """Missing required fields should fail validation."""
        serializer = BookDetailSerializer(data={})
        assert not serializer.is_valid()
        assert "title" in serializer.errors
        assert "author" in serializer.errors
        assert "isbn" in serializer.errors

    def test_invalid_isbn_format(self, book_data):
        """Invalid ISBN format should fail validation."""
        book_data["isbn"] = "INVALID"
        serializer = BookDetailSerializer(data=book_data)
        assert not serializer.is_valid()
        assert "isbn" in serializer.errors

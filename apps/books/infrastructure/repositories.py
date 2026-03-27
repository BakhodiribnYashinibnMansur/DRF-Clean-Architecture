# ============================================
# Book Repository (Infrastructure Layer)
# Concrete implementation of AbstractBookRepository using Django ORM.
# Maps between BookEntity (domain) and Book (ORM model).
# ============================================

from typing import Optional

from apps.books.application.interfaces import AbstractBookRepository
from apps.books.domain.entities import BookEntity, Genre
from apps.books.infrastructure.models import Book


class DjangoBookRepository(AbstractBookRepository):
    """
    Django ORM implementation of the book repository.
    Handles all database operations and maps between
    domain entities and ORM model instances.
    """

    @staticmethod
    def _to_entity(model: Book) -> BookEntity:
        """Convert a Django ORM Book instance to a domain BookEntity."""
        return BookEntity(
            id=model.id,
            title=model.title,
            author=model.author,
            isbn=model.isbn,
            published_date=model.published_date,
            page_count=model.page_count,
            language=model.language,
            genre=Genre(model.genre),
            description=model.description,
            created_by_id=model.created_by_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model_kwargs(entity: BookEntity) -> dict:
        """Convert a domain BookEntity to a dict of ORM model field values."""
        return {
            "title": entity.title,
            "author": entity.author,
            "isbn": entity.isbn,
            "published_date": entity.published_date,
            "page_count": entity.page_count,
            "language": entity.language,
            "genre": entity.genre.value if isinstance(entity.genre, Genre) else entity.genre,
            "description": entity.description,
            "created_by_id": entity.created_by_id,
        }

    def get_by_id(self, book_id: int) -> Optional[BookEntity]:
        """Retrieve a book by primary key. Returns None if not found."""
        try:
            model = Book.objects.select_related("created_by").get(id=book_id)
            return self._to_entity(model)
        except Book.DoesNotExist:
            return None

    def get_all(self) -> list[BookEntity]:
        """Retrieve all books ordered by creation date (newest first)."""
        return [
            self._to_entity(model)
            for model in Book.objects.select_related("created_by").all()
        ]

    def create(self, entity: BookEntity) -> BookEntity:
        """Create a new book record in the database."""
        model = Book.objects.create(**self._to_model_kwargs(entity))
        return self._to_entity(model)

    def update(self, entity: BookEntity) -> BookEntity:
        """Update an existing book record in the database."""
        Book.objects.filter(id=entity.id).update(**self._to_model_kwargs(entity))
        # Re-fetch to get updated timestamps
        model = Book.objects.select_related("created_by").get(id=entity.id)
        return self._to_entity(model)

    def delete(self, book_id: int) -> None:
        """Delete a book record from the database."""
        Book.objects.filter(id=book_id).delete()

    def exists_by_isbn(self, isbn: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a book with the given ISBN exists, optionally excluding one book."""
        qs = Book.objects.filter(isbn=isbn)
        if exclude_id is not None:
            qs = qs.exclude(id=exclude_id)
        return qs.exists()

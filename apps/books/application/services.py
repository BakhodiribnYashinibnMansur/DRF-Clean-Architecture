# ============================================
# Book Service (Application Layer)
# Orchestrates business logic for book operations.
# Depends only on the domain layer and repository interface.
# ============================================

from typing import Optional

from apps.books.application.interfaces import AbstractBookRepository
from apps.books.domain.entities import BookEntity
from apps.books.domain.exceptions import BookNotFoundError, DuplicateISBNError


class BookService:
    """
    Service class that encapsulates book business logic.
    Uses a repository (injected via constructor) for persistence,
    keeping business rules independent of the storage mechanism.
    """

    def __init__(self, repository: AbstractBookRepository):
        self._repo = repository

    def create_book(self, entity: BookEntity) -> BookEntity:
        """
        Create a new book after validating business rules.
        Raises DuplicateISBNError if the ISBN already exists.
        """
        if self._repo.exists_by_isbn(entity.isbn):
            raise DuplicateISBNError(f"A book with ISBN '{entity.isbn}' already exists.")
        return self._repo.create(entity)

    def get_book(self, book_id: int) -> BookEntity:
        """
        Retrieve a book by ID.
        Raises BookNotFoundError if the book does not exist.
        """
        book = self._repo.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError(f"Book with ID {book_id} not found.")
        return book

    def get_all_books(self) -> list[BookEntity]:
        """Retrieve all books."""
        return self._repo.get_all()

    def update_book(self, entity: BookEntity) -> BookEntity:
        """
        Update an existing book after validating business rules.
        Raises DuplicateISBNError if the ISBN conflicts with another book.
        """
        if self._repo.exists_by_isbn(entity.isbn, exclude_id=entity.id):
            raise DuplicateISBNError(f"A book with ISBN '{entity.isbn}' already exists.")
        return self._repo.update(entity)

    def delete_book(self, book_id: int) -> None:
        """
        Delete a book by ID.
        Raises BookNotFoundError if the book does not exist.
        """
        book = self._repo.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError(f"Book with ID {book_id} not found.")
        self._repo.delete(book_id)

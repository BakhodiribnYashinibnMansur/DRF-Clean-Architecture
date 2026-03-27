# ============================================
# Book Repository Interface (Application Layer)
# Abstract base class defining the contract for book persistence.
# Infrastructure layer implements this — domain/services depend on it.
# ============================================

from abc import ABC, abstractmethod
from typing import Optional

from apps.books.domain.entities import BookEntity


class AbstractBookRepository(ABC):
    """
    Abstract repository interface for Book persistence.
    Defines the contract that any concrete repository must implement.
    This allows the service layer to remain infrastructure-agnostic.
    """

    @abstractmethod
    def get_by_id(self, book_id: int) -> Optional[BookEntity]:
        """Retrieve a book entity by its primary key. Returns None if not found."""
        ...

    @abstractmethod
    def get_all(self) -> list[BookEntity]:
        """Retrieve all book entities."""
        ...

    @abstractmethod
    def create(self, entity: BookEntity) -> BookEntity:
        """Persist a new book entity and return it with generated fields (id, timestamps)."""
        ...

    @abstractmethod
    def update(self, entity: BookEntity) -> BookEntity:
        """Update an existing book entity and return the updated version."""
        ...

    @abstractmethod
    def delete(self, book_id: int) -> None:
        """Delete a book by its primary key."""
        ...

    @abstractmethod
    def exists_by_isbn(self, isbn: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a book with the given ISBN exists. Optionally exclude a specific book ID."""
        ...

# ============================================
# Book Domain Entities
# Pure Python — NO Django/DRF imports.
# Represents the core business concept of a Book.
# ============================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class Genre(str, Enum):
    """
    Predefined genre categories for books.
    Pure Python enum — mirrors ORM TextChoices values
    but has zero framework dependency.
    """

    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE = "science"
    TECHNOLOGY = "technology"
    HISTORY = "history"
    BIOGRAPHY = "biography"
    PHILOSOPHY = "philosophy"
    POETRY = "poetry"
    ROMANCE = "romance"
    THRILLER = "thriller"
    FANTASY = "fantasy"
    MYSTERY = "mystery"
    SELF_HELP = "self_help"
    OTHER = "other"


@dataclass
class BookEntity:
    """
    Domain entity representing a Book.
    Framework-independent — used by services and repositories
    for business logic without ORM coupling.

    Attributes:
        title: Book title.
        author: Author's full name.
        isbn: International Standard Book Number (10 or 13 digits).
        published_date: Date when the book was published.
        page_count: Total number of pages.
        language: Language the book is written in.
        genre: Book genre from predefined Genre enum.
        description: Optional detailed description.
        id: Database primary key (None for unsaved entities).
        created_by_id: ID of the user who added this book.
        created_at: Timestamp of record creation.
        updated_at: Timestamp of last update.
    """

    title: str
    author: str
    isbn: str
    published_date: date
    page_count: int
    language: str = "English"
    genre: Genre = Genre.OTHER
    description: str = ""
    id: Optional[int] = None
    created_by_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"

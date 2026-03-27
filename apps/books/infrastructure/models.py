# ============================================
# Book ORM Model (Infrastructure Layer)
# Django-specific model definition.
# Maps to the PostgreSQL 'books_book' table.
# ============================================

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from apps.books.domain.entities import Genre as DomainGenre

# Single source of truth: domain Genre enum.
# Labels are an infrastructure concern (UI display).
GENRE_CHOICES = [
    (DomainGenre.FICTION.value, "Fiction"),
    (DomainGenre.NON_FICTION.value, "Non-Fiction"),
    (DomainGenre.SCIENCE.value, "Science"),
    (DomainGenre.TECHNOLOGY.value, "Technology"),
    (DomainGenre.HISTORY.value, "History"),
    (DomainGenre.BIOGRAPHY.value, "Biography"),
    (DomainGenre.PHILOSOPHY.value, "Philosophy"),
    (DomainGenre.POETRY.value, "Poetry"),
    (DomainGenre.ROMANCE.value, "Romance"),
    (DomainGenre.THRILLER.value, "Thriller"),
    (DomainGenre.FANTASY.value, "Fantasy"),
    (DomainGenre.MYSTERY.value, "Mystery"),
    (DomainGenre.SELF_HELP.value, "Self-Help"),
    (DomainGenre.OTHER.value, "Other"),
]


class Book(models.Model):
    """
    Django ORM model representing a book entity.
    This is the infrastructure-layer persistence model.
    Business logic lives in the service layer (application/).

    Fields:
        title: Book title (max 255 chars).
        author: Author's full name.
        isbn: International Standard Book Number (unique, 10 or 13 digits).
        published_date: Date when the book was published.
        page_count: Total number of pages.
        language: Language the book is written in.
        genre: Book genre from predefined choices.
        description: Optional detailed description.
        created_by: The user who added this book to the system.
        created_at: Timestamp of record creation (auto-set).
        updated_at: Timestamp of last update (auto-set).
    """

    # ISBN validator — accepts 10 or 13 digit ISBNs
    isbn_validator = RegexValidator(
        regex=r"^\d{10}(\d{3})?$",
        message="ISBN must be 10 or 13 digits.",
    )

    title = models.CharField("title", max_length=255)
    author = models.CharField("author", max_length=255)
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        unique=True,
        validators=[isbn_validator],
        help_text="Enter a 10 or 13 digit ISBN number.",
    )
    published_date = models.DateField("published date")
    page_count = models.PositiveIntegerField("page count")
    language = models.CharField("language", max_length=50, default="English")
    genre = models.CharField(
        "genre",
        max_length=20,
        choices=GENRE_CHOICES,
        default=DomainGenre.OTHER.value,
        db_index=True,
    )
    description = models.TextField("description", blank=True, default="")

    # Track which user added this book
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
        verbose_name="created by",
    )

    # Timestamps
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        verbose_name = "book"
        verbose_name_plural = "books"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["isbn"], name="idx_book_isbn"),
            models.Index(fields=["author"], name="idx_book_author"),
            models.Index(fields=["-created_at"], name="idx_book_created"),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"

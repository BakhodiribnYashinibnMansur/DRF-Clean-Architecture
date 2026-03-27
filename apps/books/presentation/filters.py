# ============================================
# Book Filters (Presentation Layer)
# Django-filter FilterSet for advanced book querying.
# Supports text search, genre, date range, and page count range.
# ============================================

import django_filters

from apps.books.infrastructure.models import Book


class BookFilter(django_filters.FilterSet):
    """
    FilterSet for the Book model.

    Supported filters:
        - title: Case-insensitive partial match (e.g., ?title=python)
        - author: Case-insensitive partial match (e.g., ?author=tolkien)
        - genre: Exact match from Genre choices (e.g., ?genre=fiction)
        - language: Case-insensitive exact match (e.g., ?language=english)
        - published_after: Books published on or after this date (e.g., ?published_after=2020-01-01)
        - published_before: Books published on or before this date (e.g., ?published_before=2023-12-31)
        - min_pages: Minimum page count (e.g., ?min_pages=100)
        - max_pages: Maximum page count (e.g., ?max_pages=500)
    """

    title = django_filters.CharFilter(
        lookup_expr="icontains",
        help_text="Filter by title (case-insensitive, partial match).",
    )
    author = django_filters.CharFilter(
        lookup_expr="icontains",
        help_text="Filter by author name (case-insensitive, partial match).",
    )
    genre = django_filters.ChoiceFilter(
        choices=Book.Genre.choices,
        help_text="Filter by genre (exact match).",
    )
    language = django_filters.CharFilter(
        lookup_expr="iexact",
        help_text="Filter by language (case-insensitive, exact match).",
    )
    published_after = django_filters.DateFilter(
        field_name="published_date",
        lookup_expr="gte",
        help_text="Books published on or after this date (YYYY-MM-DD).",
    )
    published_before = django_filters.DateFilter(
        field_name="published_date",
        lookup_expr="lte",
        help_text="Books published on or before this date (YYYY-MM-DD).",
    )
    min_pages = django_filters.NumberFilter(
        field_name="page_count",
        lookup_expr="gte",
        help_text="Minimum page count.",
    )
    max_pages = django_filters.NumberFilter(
        field_name="page_count",
        lookup_expr="lte",
        help_text="Maximum page count.",
    )

    class Meta:
        model = Book
        fields = ["genre", "language"]

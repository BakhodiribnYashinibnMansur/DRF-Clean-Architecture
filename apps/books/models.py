# ============================================
# Proxy re-export for Django model discovery.
# The actual model lives in infrastructure/models.py.
# This file exists so Django's app loader can find the Book model
# via the standard apps.books.models path.
# ============================================

from apps.books.infrastructure.models import Book  # noqa: F401

__all__ = ["Book"]

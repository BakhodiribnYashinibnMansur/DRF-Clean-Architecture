# ============================================
# Book Domain Exceptions
# Pure Python — business rule violation errors.
# ============================================


class BookNotFoundError(Exception):
    """Raised when a book with the given ID does not exist."""

    pass


class DuplicateISBNError(Exception):
    """Raised when attempting to create/update a book with an ISBN that already exists."""

    pass


class BookPermissionDeniedError(Exception):
    """Raised when a user lacks permission to modify a book."""

    pass

# ============================================
# User Domain Exceptions
# Pure Python — business rule violation errors.
# ============================================


class UserNotFoundError(Exception):
    """Raised when a user with the given ID does not exist."""


class InvalidPasswordError(Exception):
    """Raised when the provided password is incorrect."""


class DuplicateEmailError(Exception):
    """Raised when attempting to register with an email that already exists."""

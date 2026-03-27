# ============================================
# User Domain Exceptions
# Pure Python — business rule violation errors.
# ============================================


class UserNotFoundError(Exception):
    """Raised when a user with the given ID does not exist."""

    pass


class InvalidPasswordError(Exception):
    """Raised when the provided password is incorrect."""

    pass


class DuplicateEmailError(Exception):
    """Raised when attempting to register with an email that already exists."""

    pass

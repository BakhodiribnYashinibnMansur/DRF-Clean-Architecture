# ============================================
# User Service (Application Layer)
# Orchestrates business logic for user operations.
# Depends only on the domain layer and repository interface.
# ============================================

from apps.users.application.interfaces import AbstractUserRepository
from apps.users.domain.entities import UserEntity
from apps.users.domain.exceptions import (
    DuplicateEmailError,
    InvalidPasswordError,
    UserNotFoundError,
)


class UserService:
    """
    Service class that encapsulates user business logic.
    Uses a repository (injected via constructor) for persistence,
    keeping business rules independent of the storage mechanism.
    """

    def __init__(self, repository: AbstractUserRepository):
        self._repo = repository

    def register_user(self, email: str, password: str, **kwargs) -> UserEntity:
        """
        Register a new user account.
        Raises DuplicateEmailError if the email is already taken.
        """
        if self._repo.exists_by_email(email):
            raise DuplicateEmailError(f"Email '{email}' is already registered.")
        return self._repo.create_user(email=email, password=password, **kwargs)

    def get_user(self, user_id: int) -> UserEntity:
        """
        Retrieve a user by ID.
        Raises UserNotFoundError if the user does not exist.
        """
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with ID {user_id} not found.")
        return user

    def get_user_by_email(self, email: str) -> UserEntity:
        """
        Retrieve a user by email.
        Raises UserNotFoundError if not found.
        """
        user = self._repo.get_by_email(email)
        if user is None:
            raise UserNotFoundError(f"User with email '{email}' not found.")
        return user

    def update_profile(self, user_id: int, **kwargs) -> UserEntity:
        """Update a user's profile fields."""
        return self._repo.update(user_id, **kwargs)

    def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> None:
        """
        Change a user's password after verifying the old one.
        Raises InvalidPasswordError if the old password is incorrect.
        Raises UserNotFoundError if the user does not exist.
        """
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with ID {user_id} not found.")

        if not self._repo.check_password(user_id, old_password):
            raise InvalidPasswordError("The old password is incorrect.")

        self._repo.set_password(user_id, new_password)

    def delete_user(self, user_id: int) -> None:
        """Delete a user by ID."""
        self._repo.delete(user_id)

# ============================================
# User Repository Interface (Application Layer)
# Abstract base class defining the contract for user persistence.
# Infrastructure layer implements this — domain/services depend on it.
# ============================================

from abc import ABC, abstractmethod
from typing import Optional

from apps.users.domain.entities import UserEntity


class AbstractUserRepository(ABC):
    """
    Abstract repository interface for User persistence.
    Defines the contract that any concrete repository must implement.
    """

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        """Retrieve a user entity by primary key. Returns None if not found."""
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Retrieve a user entity by email. Returns None if not found."""
        ...

    @abstractmethod
    def get_all(self) -> list[UserEntity]:
        """Retrieve all user entities."""
        ...

    @abstractmethod
    def create_user(self, email: str, password: str, **kwargs) -> UserEntity:
        """Create a new user with the given email and hashed password."""
        ...

    @abstractmethod
    def update(self, user_id: int, **kwargs) -> UserEntity:
        """Update user fields and return the updated entity."""
        ...

    @abstractmethod
    def delete(self, user_id: int) -> None:
        """Delete a user by primary key."""
        ...

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Check if a user with the given email exists."""
        ...

    @abstractmethod
    def check_password(self, user_id: int, password: str) -> bool:
        """Verify that the given password matches the user's stored password."""
        ...

    @abstractmethod
    def set_password(self, user_id: int, new_password: str) -> None:
        """Set a new password for the user (hashed before storing)."""
        ...

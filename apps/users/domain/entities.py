# ============================================
# User Domain Entities
# Pure Python — NO Django/DRF imports.
# Represents the core business concept of a User.
# ============================================

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class UserEntity:
    """
    Domain entity representing a User.
    Framework-independent — used by services and repositories
    for business logic without ORM coupling.
    """

    email: str
    first_name: str = ""
    last_name: str = ""
    bio: str = ""
    date_of_birth: date | None = None
    id: int | None = None
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False
    date_joined: datetime | None = None
    last_login: datetime | None = None

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return self.email

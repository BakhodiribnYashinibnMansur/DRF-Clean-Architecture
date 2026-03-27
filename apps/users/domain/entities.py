# ============================================
# User Domain Entities
# Pure Python — NO Django/DRF imports.
# Represents the core business concept of a User.
# ============================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class UserEntity:
    """
    Domain entity representing a User.
    Framework-independent — used by services and repositories
    for business logic without ORM coupling.

    Attributes:
        email: Unique email address (used as login identifier).
        first_name: User's first name.
        last_name: User's last name.
        bio: Optional short biography.
        date_of_birth: Optional date of birth.
        id: Database primary key (None for unsaved entities).
        is_active: Whether the user account is active.
        is_staff: Whether the user can access admin.
        is_superuser: Whether the user has all permissions.
        date_joined: Timestamp of account creation.
        last_login: Timestamp of last login.
    """

    email: str
    first_name: str = ""
    last_name: str = ""
    bio: str = ""
    date_of_birth: Optional[date] = None
    id: Optional[int] = None
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False
    date_joined: Optional[datetime] = None
    last_login: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return self.email

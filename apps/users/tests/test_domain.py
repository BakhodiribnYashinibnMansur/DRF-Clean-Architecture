# ============================================
# User Domain Layer Tests
# Pure unit tests — no database, no Django.
# Tests entity creation and domain exceptions.
# ============================================

from datetime import date

from apps.users.domain.entities import UserEntity
from apps.users.domain.exceptions import (
    DuplicateEmailError,
    InvalidPasswordError,
    UserNotFoundError,
)


class TestUserEntity:
    """Tests for the UserEntity dataclass."""

    def test_create_entity_with_email(self):
        """UserEntity should be creatable with just an email."""
        entity = UserEntity(email="test@example.com")
        assert entity.email == "test@example.com"

    def test_default_field_values(self):
        """UserEntity should have correct default values."""
        entity = UserEntity(email="test@example.com")
        assert entity.first_name == ""
        assert entity.last_name == ""
        assert entity.bio == ""
        assert entity.date_of_birth is None
        assert entity.id is None
        assert entity.is_active is True
        assert entity.is_staff is False
        assert entity.is_superuser is False

    def test_full_name_property(self):
        """full_name should return 'first_name last_name' trimmed."""
        entity = UserEntity(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        assert entity.full_name == "John Doe"

    def test_full_name_with_only_first_name(self):
        """full_name should handle missing last_name."""
        entity = UserEntity(
            email="test@example.com",
            first_name="John",
        )
        assert entity.full_name == "John"

    def test_full_name_with_empty_names(self):
        """full_name should return empty string when both names are empty."""
        entity = UserEntity(email="test@example.com")
        assert entity.full_name == ""

    def test_entity_str_representation(self):
        """UserEntity __str__ should return the email."""
        entity = UserEntity(email="test@example.com")
        assert str(entity) == "test@example.com"

    def test_entity_with_all_fields(self):
        """UserEntity should accept all optional fields."""
        entity = UserEntity(
            email="full@example.com",
            first_name="Jane",
            last_name="Doe",
            bio="A developer.",
            date_of_birth=date(1990, 5, 15),
            id=42,
            is_active=True,
            is_staff=True,
            is_superuser=False,
        )
        assert entity.id == 42
        assert entity.is_staff is True
        assert entity.date_of_birth == date(1990, 5, 15)


class TestUserExceptions:
    """Tests for domain exception classes."""

    def test_user_not_found_error(self):
        """UserNotFoundError should be an Exception with a message."""
        error = UserNotFoundError("User 42 not found")
        assert str(error) == "User 42 not found"
        assert isinstance(error, Exception)

    def test_invalid_password_error(self):
        """InvalidPasswordError should be an Exception."""
        error = InvalidPasswordError("Wrong password")
        assert str(error) == "Wrong password"

    def test_duplicate_email_error(self):
        """DuplicateEmailError should be an Exception."""
        error = DuplicateEmailError("Email exists")
        assert str(error) == "Email exists"

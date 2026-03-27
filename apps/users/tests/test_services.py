# ============================================
# User Service Layer Tests
# Unit tests with mocked repository.
# Tests business logic without touching the database.
# ============================================

from unittest.mock import MagicMock

import pytest

from apps.users.application.interfaces import AbstractUserRepository
from apps.users.application.services import UserService
from apps.users.domain.entities import UserEntity
from apps.users.domain.exceptions import (
    DuplicateEmailError,
    InvalidPasswordError,
    UserNotFoundError,
)


@pytest.fixture
def mock_repo():
    """Return a mocked AbstractUserRepository."""
    return MagicMock(spec=AbstractUserRepository)


@pytest.fixture
def service(mock_repo):
    """Return a UserService with a mocked repository."""
    return UserService(repository=mock_repo)


@pytest.fixture
def sample_entity():
    """Return a sample UserEntity for testing."""
    return UserEntity(
        id=1,
        email="test@example.com",
        first_name="Test",
        last_name="User",
    )


class TestUserServiceRegister:
    """Tests for UserService.register_user()."""

    def test_register_success(self, service, mock_repo, sample_entity):
        """register_user should call repo.create_user when email is unique."""
        mock_repo.exists_by_email.return_value = False
        mock_repo.create_user.return_value = sample_entity

        result = service.register_user(
            email="test@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="User",
        )

        mock_repo.exists_by_email.assert_called_once_with("test@example.com")
        mock_repo.create_user.assert_called_once()
        assert result == sample_entity

    def test_register_duplicate_email_raises_error(self, service, mock_repo):
        """register_user should raise DuplicateEmailError when email exists."""
        mock_repo.exists_by_email.return_value = True

        with pytest.raises(DuplicateEmailError, match="already registered"):
            service.register_user(
                email="taken@example.com",
                password="StrongPass123!",
            )

        mock_repo.create_user.assert_not_called()


class TestUserServiceGet:
    """Tests for UserService.get_user() and get_user_by_email()."""

    def test_get_user_success(self, service, mock_repo, sample_entity):
        """get_user should return the entity when found."""
        mock_repo.get_by_id.return_value = sample_entity

        result = service.get_user(1)

        assert result == sample_entity

    def test_get_user_not_found_raises_error(self, service, mock_repo):
        """get_user should raise UserNotFoundError when not found."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            service.get_user(999)

    def test_get_user_by_email_success(self, service, mock_repo, sample_entity):
        """get_user_by_email should return the entity when found."""
        mock_repo.get_by_email.return_value = sample_entity

        result = service.get_user_by_email("test@example.com")

        assert result == sample_entity

    def test_get_user_by_email_not_found(self, service, mock_repo):
        """get_user_by_email should raise UserNotFoundError when not found."""
        mock_repo.get_by_email.return_value = None

        with pytest.raises(UserNotFoundError):
            service.get_user_by_email("nobody@example.com")


class TestUserServiceChangePassword:
    """Tests for UserService.change_password()."""

    def test_change_password_success(self, service, mock_repo, sample_entity):
        """change_password should call set_password when old password is correct."""
        mock_repo.get_by_id.return_value = sample_entity
        mock_repo.check_password.return_value = True

        service.change_password(1, "OldPass123!", "NewPass456!")

        mock_repo.check_password.assert_called_once_with(1, "OldPass123!")
        mock_repo.set_password.assert_called_once_with(1, "NewPass456!")

    def test_change_password_wrong_old_raises_error(self, service, mock_repo, sample_entity):
        """change_password should raise InvalidPasswordError for wrong old password."""
        mock_repo.get_by_id.return_value = sample_entity
        mock_repo.check_password.return_value = False

        with pytest.raises(InvalidPasswordError, match="incorrect"):
            service.change_password(1, "WrongPass!", "NewPass456!")

        mock_repo.set_password.assert_not_called()

    def test_change_password_user_not_found(self, service, mock_repo):
        """change_password should raise UserNotFoundError when user doesn't exist."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            service.change_password(999, "OldPass!", "NewPass!")


class TestUserServiceUpdateAndDelete:
    """Tests for UserService.update_profile() and delete_user()."""

    def test_update_profile(self, service, mock_repo, sample_entity):
        """update_profile should call repo.update with kwargs."""
        mock_repo.update.return_value = sample_entity

        service.update_profile(1, first_name="Updated")

        mock_repo.update.assert_called_once_with(1, first_name="Updated")

    def test_delete_user(self, service, mock_repo):
        """delete_user should call repo.delete."""
        service.delete_user(1)

        mock_repo.delete.assert_called_once_with(1)

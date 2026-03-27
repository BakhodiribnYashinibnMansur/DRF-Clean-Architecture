# ============================================
# User Repository Integration Tests
# Tests the DjangoUserRepository against a real database.
# Verifies ORM operations and entity mapping.
# ============================================

import pytest

from apps.users.domain.entities import UserEntity
from apps.users.infrastructure.repositories import DjangoUserRepository


@pytest.fixture
def repo():
    """Return a DjangoUserRepository instance."""
    return DjangoUserRepository()


@pytest.mark.django_db
class TestDjangoUserRepositoryCreate:
    """Tests for DjangoUserRepository.create_user()."""

    def test_create_user_returns_entity(self, repo):
        """create_user() should return a UserEntity with correct fields."""
        result = repo.create_user(
            email="repo@example.com",
            password="TestPass123!",
            first_name="Repo",
            last_name="User",
        )

        assert isinstance(result, UserEntity)
        assert result.id is not None
        assert result.email == "repo@example.com"
        assert result.first_name == "Repo"

    def test_create_user_persists_to_db(self, repo):
        """create_user() should persist the user to the database."""
        repo.create_user(
            email="persist@example.com",
            password="TestPass123!",
        )

        assert repo.exists_by_email("persist@example.com") is True


@pytest.mark.django_db
class TestDjangoUserRepositoryRead:
    """Tests for read operations."""

    def test_get_by_id_returns_entity(self, repo):
        """get_by_id() should return a UserEntity for an existing user."""
        created = repo.create_user(email="getme@example.com", password="Pass123!")

        result = repo.get_by_id(created.id)

        assert result is not None
        assert result.email == "getme@example.com"

    def test_get_by_id_returns_none_for_missing(self, repo):
        """get_by_id() should return None for a non-existent user."""
        assert repo.get_by_id(99999) is None

    def test_get_by_email_returns_entity(self, repo):
        """get_by_email() should return a UserEntity."""
        repo.create_user(email="email@example.com", password="Pass123!")

        result = repo.get_by_email("email@example.com")

        assert result is not None
        assert result.email == "email@example.com"

    def test_get_by_email_returns_none_for_missing(self, repo):
        """get_by_email() should return None for non-existent email."""
        assert repo.get_by_email("ghost@example.com") is None

    def test_get_all_returns_list(self, repo):
        """get_all() should return a list of UserEntity objects."""
        repo.create_user(email="all1@example.com", password="Pass123!")
        repo.create_user(email="all2@example.com", password="Pass123!")

        results = repo.get_all()

        assert len(results) >= 2
        assert all(isinstance(r, UserEntity) for r in results)


@pytest.mark.django_db
class TestDjangoUserRepositoryPassword:
    """Tests for password operations."""

    def test_check_password_correct(self, repo):
        """check_password() should return True for correct password."""
        created = repo.create_user(email="pw@example.com", password="MyPass123!")

        assert repo.check_password(created.id, "MyPass123!") is True

    def test_check_password_wrong(self, repo):
        """check_password() should return False for incorrect password."""
        created = repo.create_user(email="pw2@example.com", password="MyPass123!")

        assert repo.check_password(created.id, "WrongPass!") is False

    def test_check_password_nonexistent_user(self, repo):
        """check_password() should return False for non-existent user."""
        assert repo.check_password(99999, "AnyPass!") is False

    def test_set_password(self, repo):
        """set_password() should change the user's password."""
        created = repo.create_user(email="setpw@example.com", password="OldPass123!")

        repo.set_password(created.id, "NewPass456!")

        assert repo.check_password(created.id, "NewPass456!") is True
        assert repo.check_password(created.id, "OldPass123!") is False


@pytest.mark.django_db
class TestDjangoUserRepositoryExistsAndDelete:
    """Tests for exists_by_email() and delete()."""

    def test_exists_by_email_true(self, repo):
        """exists_by_email() should return True when email exists."""
        repo.create_user(email="exists@example.com", password="Pass123!")

        assert repo.exists_by_email("exists@example.com") is True

    def test_exists_by_email_false(self, repo):
        """exists_by_email() should return False when email doesn't exist."""
        assert repo.exists_by_email("nope@example.com") is False

    def test_delete_removes_user(self, repo):
        """delete() should remove the user from the database."""
        created = repo.create_user(email="del@example.com", password="Pass123!")

        repo.delete(created.id)

        assert repo.get_by_id(created.id) is None
        assert repo.exists_by_email("del@example.com") is False

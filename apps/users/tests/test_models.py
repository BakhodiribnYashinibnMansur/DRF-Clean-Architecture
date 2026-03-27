# ============================================
# CustomUser Model Tests
# Tests for user creation, email normalization, and superuser logic.
# ============================================

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestCustomUserModel:
    """Tests for the CustomUser model and CustomUserManager."""

    def test_create_user_with_email(self, create_user):
        """Regular user creation should set correct fields."""
        user = create_user(email="newuser@example.com")
        assert user.email == "newuser@example.com"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_without_email_raises_error(self):
        """Creating a user without email should raise ValueError."""
        with pytest.raises(ValueError, match="The Email field must be set"):
            User.objects.create_user(email="", password="TestPass123!")

    def test_email_normalization(self, create_user):
        """Email domain should be lowercased during creation."""
        user = create_user(email="Test@EXAMPLE.COM")
        assert user.email == "Test@example.com"

    def test_create_superuser(self, db):
        """Superuser should have is_staff=True and is_superuser=True."""
        admin = User.objects.create_superuser(
            email="super@example.com",
            password="SuperPass123!",
            first_name="Super",
            last_name="Admin",
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.is_active is True

    def test_create_superuser_without_is_staff_raises_error(self, db):
        """Superuser with is_staff=False should raise ValueError."""
        with pytest.raises(ValueError, match="is_staff=True"):
            User.objects.create_superuser(
                email="bad@example.com",
                password="TestPass123!",
                first_name="Bad",
                last_name="Admin",
                is_staff=False,
            )

    def test_create_superuser_without_is_superuser_raises_error(self, db):
        """Superuser with is_superuser=False should raise ValueError."""
        with pytest.raises(ValueError, match="is_superuser=True"):
            User.objects.create_superuser(
                email="bad@example.com",
                password="TestPass123!",
                first_name="Bad",
                last_name="Admin",
                is_superuser=False,
            )

    def test_user_str_representation(self, user):
        """User __str__ should return the email address."""
        assert str(user) == user.email

    def test_user_full_name_property(self, create_user):
        """full_name property should return 'first_name last_name'."""
        user = create_user(
            email="full@example.com",
            first_name="John",
            last_name="Doe",
        )
        assert user.full_name == "John Doe"

    def test_user_ordering(self, create_user):
        """Users should be ordered by -date_joined (newest first)."""
        user1 = create_user(email="first@example.com")
        user2 = create_user(email="second@example.com")
        users = list(User.objects.all())
        assert users[0] == user2  # Newer user first
        assert users[1] == user1

    def test_username_field_is_email(self):
        """USERNAME_FIELD should be 'email'."""
        assert User.USERNAME_FIELD == "email"

    def test_user_has_no_username_field(self):
        """CustomUser should not have a username field."""
        assert not hasattr(User, "username") or User.username is None

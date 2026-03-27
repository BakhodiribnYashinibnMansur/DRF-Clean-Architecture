# ============================================
# User Serializer Tests
# Tests for registration validation, profile serialization,
# and password change logic.
# ============================================

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from apps.users.application.services import UserService
from apps.users.infrastructure.repositories import DjangoUserRepository
from apps.users.presentation.serializers import (
    ChangePasswordSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()

factory = APIRequestFactory()


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    """Tests for the UserRegistrationSerializer."""

    def test_valid_registration_data(self):
        """Valid data should pass validation; user creation goes through the service layer."""
        data = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        # User creation is handled by the service layer (not the serializer)
        service = UserService(repository=DjangoUserRepository())
        vd = serializer.validated_data
        entity = service.register_user(
            email=vd["email"],
            password=vd["password"],
            first_name=vd.get("first_name", ""),
            last_name=vd.get("last_name", ""),
        )
        user = User.objects.get(id=entity.id)
        assert user.email == "new@example.com"
        assert user.check_password("StrongPass123!")

    def test_duplicate_email_rejected(self, user):
        """Registration with an existing email should fail."""
        data = {
            "email": user.email,
            "first_name": "Dup",
            "last_name": "User",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_password_mismatch_rejected(self):
        """Mismatched passwords should fail validation."""
        data = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongPass123!",
            "password_confirm": "DifferentPass456!",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "password_confirm" in serializer.errors

    def test_weak_password_rejected(self):
        """A weak/common password should fail Django password validation."""
        data = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "123",
            "password_confirm": "123",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_password_not_in_response(self):
        """Password fields should be write-only (not in serialized output)."""
        user = User.objects.create_user(
            email="new@example.com",
            password="StrongPass123!",
            first_name="New",
            last_name="User",
        )
        output = UserRegistrationSerializer(user).data
        assert "password" not in output
        assert "password_confirm" not in output


@pytest.mark.django_db
class TestUserProfileSerializer:
    """Tests for the UserProfileSerializer."""

    def test_profile_contains_expected_fields(self, user):
        """Profile serializer should return all expected fields."""
        serializer = UserProfileSerializer(user)
        expected_fields = {
            "id", "email", "first_name", "last_name",
            "full_name", "bio", "date_of_birth", "date_joined",
        }
        assert set(serializer.data.keys()) == expected_fields

    def test_email_is_read_only(self, user):
        """Email should not be changeable through the profile serializer."""
        serializer = UserProfileSerializer(
            user,
            data={"email": "hacker@evil.com"},
            partial=True,
        )
        serializer.is_valid()
        # Even if valid, email should remain unchanged
        assert "email" in serializer.Meta.read_only_fields


@pytest.mark.django_db
class TestChangePasswordSerializer:
    """Tests for the ChangePasswordSerializer."""

    def test_wrong_old_password_rejected_by_service(self, user):
        """Incorrect old password should be rejected by the service layer."""
        from apps.users.domain.exceptions import InvalidPasswordError

        service = UserService(repository=DjangoUserRepository())
        with pytest.raises(InvalidPasswordError):
            service.change_password(
                user_id=user.id,
                old_password="WrongPassword123!",
                new_password="NewStrongPass456!",
            )

    def test_new_password_mismatch_rejected(self, user):
        """Mismatched new passwords should fail serializer validation."""
        data = {
            "old_password": "StrongPass123!",
            "new_password": "NewPass456!",
            "new_password_confirm": "DifferentPass789!",
        }
        serializer = ChangePasswordSerializer(data=data)
        assert not serializer.is_valid()
        assert "new_password_confirm" in serializer.errors

    def test_valid_password_change(self, user):
        """Valid password change should update the user's password via service."""
        data = {
            "old_password": "StrongPass123!",
            "new_password": "NewStrongPass456!",
            "new_password_confirm": "NewStrongPass456!",
        }
        serializer = ChangePasswordSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        service = UserService(repository=DjangoUserRepository())
        service.change_password(
            user_id=user.id,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password"],
        )
        user.refresh_from_db()
        assert user.check_password("NewStrongPass456!")

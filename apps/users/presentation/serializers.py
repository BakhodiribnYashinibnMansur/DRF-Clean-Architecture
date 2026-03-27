# ============================================
# User Serializers (Presentation Layer)
# Handles data validation and transformation for User API endpoints.
# Includes registration, profile management, and admin user management.
# ============================================

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates email uniqueness and password strength.
    Returns user data without password on success.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
        help_text="Minimum 8 characters. Must pass Django password validators.",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Must match the password field.",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        """Ensure password and password_confirm match."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        attrs.pop("password_confirm")
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing and updating the authenticated user's profile.
    Email and date_joined are read-only — cannot be changed after registration.
    """

    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "bio",
            "date_of_birth",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "date_joined"]


class UserListSerializer(serializers.ModelSerializer):
    """
    Compact serializer for listing users (admin view).
    Shows essential information without heavy fields.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Full user detail serializer (admin view).
    Allows admins to view and update all user fields including permissions.
    """

    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "bio",
            "date_of_birth",
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing the authenticated user's password.
    Requires the old password for verification and validates the new one.
    """

    old_password = serializers.CharField(
        write_only=True,
        help_text="Current password for verification.",
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
        help_text="New password. Must pass Django password validators.",
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        help_text="Must match the new_password field.",
    )

    def validate(self, attrs):
        """Ensure new passwords match."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        return attrs

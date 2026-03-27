# ============================================
# Custom User Manager (Infrastructure Layer)
# Handles user creation with email as the unique identifier
# instead of the default username field.
# ============================================

from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser model where email is the
    unique identifier for authentication instead of username.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.

        Args:
            email: User's email address (required, used as login identifier).
            password: User's password (will be hashed before storing).
            **extra_fields: Additional fields to set on the user model.

        Raises:
            ValueError: If email is not provided.
        """
        if not email:
            raise ValueError("The Email field must be set")

        # Normalize email — lowercase the domain part
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.
        Ensures is_staff and is_superuser are both True.

        Args:
            email: Superuser's email address.
            password: Superuser's password.
            **extra_fields: Additional fields.

        Raises:
            ValueError: If is_staff or is_superuser is not True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

# ============================================
# Custom User ORM Model (Infrastructure Layer)
# Email-based authentication — no username field.
# Extends Django's AbstractUser for full auth support.
# ============================================

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users.infrastructure.managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Django ORM model for user accounts.
    Uses email as the primary identifier instead of username.
    This is the infrastructure-layer persistence model.

    Fields:
        email: Unique email address used for authentication.
        first_name: User's first name.
        last_name: User's last name.
        bio: Optional short biography.
        date_of_birth: Optional date of birth.
        is_active: Whether the user account is active.
        is_staff: Whether the user can access the admin panel.
        date_joined: Timestamp of account creation (auto-set).
    """

    # Remove the username field — we use email instead
    username = None

    email = models.EmailField(
        "email address",
        unique=True,
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )
    bio = models.TextField("biography", blank=True, default="")
    date_of_birth = models.DateField("date of birth", null=True, blank=True)

    # Use email as the login field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # Attach custom manager
    objects = CustomUserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

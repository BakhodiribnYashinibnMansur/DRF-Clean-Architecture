# ============================================
# Custom User Admin Configuration
# Configures the Django admin interface for the CustomUser model
# with email-based fieldsets (no username).
# ============================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser.
    Replaces username-based fieldsets with email-based ones.
    """

    model = CustomUser

    # List view configuration
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    ]
    list_filter = ["is_staff", "is_active", "date_joined"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]
    list_per_page = 25

    # Detail view fieldsets — organized into logical sections
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {"fields": ("first_name", "last_name", "bio", "date_of_birth")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fieldsets for the "Add User" form
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

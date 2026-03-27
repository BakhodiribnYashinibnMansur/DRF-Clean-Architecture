# ============================================
# Book Admin Configuration
# Full-featured admin interface for managing books.
# ============================================

from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Book model.
    Provides search, filtering, and organized display.
    """

    # List view
    list_display = [
        "title",
        "author",
        "isbn",
        "genre",
        "language",
        "published_date",
        "page_count",
        "created_by",
        "created_at",
    ]
    list_filter = ["genre", "language", "published_date"]
    search_fields = ["title", "author", "isbn"]
    list_per_page = 25
    date_hierarchy = "published_date"

    # Detail view
    readonly_fields = ["created_at", "updated_at", "created_by"]
    fieldsets = (
        (
            "Book Information",
            {"fields": ("title", "author", "isbn", "description")},
        ),
        (
            "Details",
            {"fields": ("published_date", "page_count", "language", "genre")},
        ),
        (
            "Metadata",
            {"fields": ("created_by", "created_at", "updated_at")},
        ),
    )

    def save_model(self, request, obj, form, change):
        """Automatically set created_by to the current admin user on creation."""
        if not change:  # Only on creation, not update
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

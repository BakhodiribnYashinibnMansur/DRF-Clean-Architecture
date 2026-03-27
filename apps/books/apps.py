from django.apps import AppConfig


class BooksConfig(AppConfig):
    """Configuration for the Books application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.books"
    verbose_name = "Books"

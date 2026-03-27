# ============================================
# Shared Test Fixtures
# Provides reusable fixtures for all test modules.
# Includes API client, user creation, and authentication helpers.
# ============================================

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.books.models import Book

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an unauthenticated DRF API test client."""
    return APIClient()


@pytest.fixture
def user_data():
    """Return a dictionary of valid user registration data."""
    return {
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "StrongPass123!",
    }


@pytest.fixture
def create_user(db):
    """
    Factory fixture for creating users.
    Usage: user = create_user(email="user@test.com", password="pass123")
    """

    def _create_user(**kwargs):
        defaults = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "StrongPass123!",
        }
        defaults.update(kwargs)
        password = defaults.pop("password")
        return User.objects.create_user(password=password, **defaults)

    return _create_user


@pytest.fixture
def user(create_user):
    """Return a regular (non-admin) user."""
    return create_user()


@pytest.fixture
def admin_user(create_user):
    """Return an admin (staff) user."""
    return create_user(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def auth_client(api_client, user):
    """Return an API client authenticated as a regular user."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an API client authenticated as an admin user."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def book_data():
    """Return a dictionary of valid book data for creation."""
    return {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "published_date": "2008-08-01",
        "page_count": 464,
        "language": "English",
        "genre": "technology",
        "description": "A Handbook of Agile Software Craftsmanship.",
    }


@pytest.fixture
def book(db, user, book_data):
    """Return a book instance created by the regular user."""
    return Book.objects.create(created_by=user, **book_data)


@pytest.fixture
def second_user(create_user):
    """Return a second regular user for permission testing."""
    return create_user(
        email="second@example.com",
        first_name="Second",
        last_name="User",
    )

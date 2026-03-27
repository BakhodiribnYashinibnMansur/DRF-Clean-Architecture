# ============================================
# Book View Tests
# Tests for book CRUD API endpoints including permissions,
# filtering, search, and pagination.
# ============================================

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.books.models import Book


@pytest.mark.django_db
class TestBookListView:
    """Tests for GET /api/books/"""

    url = reverse("books:book-list")

    def test_list_books_authenticated(self, auth_client, book):
        """Authenticated user should see the list of books."""
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == book.title

    def test_list_books_unauthenticated(self, api_client, book):
        """Unauthenticated user should also be able to list books (read-only)."""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_books_pagination(self, auth_client, user):
        """List should be paginated (default PAGE_SIZE=10)."""
        # Create 15 books
        for i in range(15):
            Book.objects.create(
                title=f"Book {i}",
                author="Author",
                isbn=f"{1000000000 + i}",
                published_date="2020-01-01",
                page_count=100,
                created_by=user,
            )
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 15
        assert len(response.data["results"]) == 10  # First page

    def test_filter_by_genre(self, auth_client, book):
        """Filter by genre should return only matching books."""
        response = auth_client.get(self.url, {"genre": "technology"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

        response = auth_client.get(self.url, {"genre": "fiction"})
        assert response.data["count"] == 0

    def test_filter_by_author(self, auth_client, book):
        """Filter by author (case-insensitive partial match)."""
        response = auth_client.get(self.url, {"author": "martin"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_search_by_title(self, auth_client, book):
        """Search should match against title field."""
        response = auth_client.get(self.url, {"search": "Clean"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_ordering_by_title(self, auth_client, user):
        """Ordering by title should sort books alphabetically."""
        Book.objects.create(
            title="Alpha Book",
            author="Author",
            isbn="1111111111",
            published_date="2020-01-01",
            page_count=100,
            created_by=user,
        )
        Book.objects.create(
            title="Zeta Book",
            author="Author",
            isbn="2222222222",
            published_date="2020-01-01",
            page_count=200,
            created_by=user,
        )
        response = auth_client.get(self.url, {"ordering": "title"})
        titles = [b["title"] for b in response.data["results"]]
        assert titles == sorted(titles)


@pytest.mark.django_db
class TestBookCreateView:
    """Tests for POST /api/books/"""

    url = reverse("books:book-list")

    def test_create_book_authenticated(self, auth_client, book_data):
        """Authenticated user should be able to create a book."""
        response = auth_client.post(self.url, book_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == book_data["title"]
        assert response.data["created_by"] is not None

    def test_create_book_unauthenticated(self, api_client, book_data):
        """Unauthenticated user should get 401."""
        response = api_client.post(self.url, book_data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_book_invalid_data(self, auth_client):
        """Invalid data should return 400."""
        response = auth_client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_book_sets_created_by(self, auth_client, book_data, user):
        """created_by should be automatically set to the requesting user."""
        response = auth_client.post(self.url, book_data, format="json")
        assert response.data["created_by"]["email"] == user.email


@pytest.mark.django_db
class TestBookDetailView:
    """Tests for GET /api/books/{id}/"""

    def test_retrieve_book(self, auth_client, book):
        """Should return full book details including description."""
        url = reverse("books:book-detail", kwargs={"pk": book.id})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == book.title
        assert "description" in response.data

    def test_retrieve_nonexistent_book(self, auth_client):
        """Should return 404 for non-existent book."""
        url = reverse("books:book-detail", kwargs={"pk": 99999})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBookUpdateView:
    """Tests for PUT/PATCH /api/books/{id}/"""

    def test_owner_can_update_book(self, auth_client, book):
        """Book owner should be able to update their book."""
        url = reverse("books:book-detail", kwargs={"pk": book.id})
        response = auth_client.patch(
            url,
            {"title": "Updated Title"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"

    def test_admin_can_update_any_book(self, admin_client, book):
        """Admin should be able to update any book."""
        url = reverse("books:book-detail", kwargs={"pk": book.id})
        response = admin_client.patch(
            url,
            {"title": "Admin Updated"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Admin Updated"

    def test_other_user_cannot_update_book(self, api_client, book, second_user):
        """A different non-admin user should not be able to update the book."""
        refresh = RefreshToken.for_user(second_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("books:book-detail", kwargs={"pk": book.id})
        response = api_client.patch(
            url,
            {"title": "Hacked Title"},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBookDeleteView:
    """Tests for DELETE /api/books/{id}/"""

    def test_owner_can_delete_book(self, auth_client, book):
        """Book owner should be able to delete their book."""
        url = reverse("books:book-detail", kwargs={"pk": book.id})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Book.objects.filter(id=book.id).exists()

    def test_admin_can_delete_any_book(self, admin_client, book):
        """Admin should be able to delete any book."""
        url = reverse("books:book-detail", kwargs={"pk": book.id})
        response = admin_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_other_user_cannot_delete_book(self, api_client, book, second_user):
        """A different non-admin user should not be able to delete the book."""
        refresh = RefreshToken.for_user(second_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("books:book-detail", kwargs={"pk": book.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_delete(self, api_client, book):
        """Unauthenticated user should get 401."""
        url = reverse("books:book-detail", kwargs={"pk": book.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

# ============================================
# User View Tests
# Tests for registration, profile, user CRUD, password change,
# and JWT token endpoints.
# ============================================

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestRegisterView:
    """Tests for POST /api/users/register/"""

    url = reverse("users:register")

    def test_register_success(self, api_client):
        """Successful registration should return 201 with user data and tokens."""
        data = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        assert response.data["user"]["email"] == "new@example.com"

    def test_register_duplicate_email(self, api_client, user):
        """Registration with existing email should return 400."""
        data = {
            "email": user.email,
            "first_name": "Dup",
            "last_name": "User",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_data(self, api_client):
        """Registration with missing fields should return 400."""
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserProfileView:
    """Tests for GET/PATCH /api/users/profile/"""

    url = reverse("users:profile")

    def test_get_profile_authenticated(self, auth_client, user):
        """Authenticated user should get their profile."""
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_get_profile_unauthenticated(self, api_client):
        """Unauthenticated request should return 401."""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, auth_client):
        """PATCH should update editable profile fields."""
        response = auth_client.patch(
            self.url,
            {"first_name": "Updated", "bio": "New bio text."},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"
        assert response.data["bio"] == "New bio text."

    def test_cannot_change_email_via_profile(self, auth_client, user):
        """Email should remain unchanged when trying to update it."""
        original_email = user.email
        auth_client.patch(
            self.url,
            {"email": "hacker@evil.com"},
            format="json",
        )
        user.refresh_from_db()
        assert user.email == original_email


@pytest.mark.django_db
class TestUserViewSet:
    """Tests for /api/users/manage/ (UserViewSet CRUD)."""

    list_url = reverse("users:user-list")

    def _detail_url(self, user_id):
        return reverse("users:user-detail", kwargs={"pk": user_id})

    def test_admin_can_list_users(self, admin_client, user, admin_user):
        """Admin should see all users."""
        response = admin_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        # Should contain at least admin + regular user
        emails = [u["email"] for u in response.data["results"]]
        assert user.email in emails
        assert admin_user.email in emails

    def test_non_admin_cannot_list_users(self, auth_client):
        """Non-admin should get 403 on user list."""
        response = auth_client.get(self.list_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_retrieve_any_user(self, admin_client, user):
        """Admin should be able to retrieve any user's details."""
        response = admin_client.get(self._detail_url(user.id))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_user_can_retrieve_self(self, auth_client, user):
        """Regular user should be able to retrieve their own details."""
        response = auth_client.get(self._detail_url(user.id))
        assert response.status_code == status.HTTP_200_OK

    def test_user_cannot_retrieve_other_user(self, auth_client, admin_user):
        """Regular user should get 404 when accessing another user."""
        response = auth_client.get(self._detail_url(admin_user.id))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_can_update_user(self, admin_client, user):
        """Admin should be able to update any user."""
        response = admin_client.patch(
            self._detail_url(user.id),
            {"first_name": "AdminUpdated"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "AdminUpdated"

    def test_admin_can_delete_user(self, admin_client, create_user):
        """Admin should be able to delete a user."""
        target = create_user(email="todelete@example.com")
        response = admin_client.delete(self._detail_url(target.id))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=target.id).exists()

    def test_non_admin_cannot_delete_user(self, auth_client, user):
        """Non-admin should get 403 when trying to delete."""
        response = auth_client.delete(self._detail_url(user.id))
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestChangePasswordView:
    """Tests for PUT /api/users/change-password/"""

    url = reverse("users:change_password")

    def test_change_password_success(self, auth_client, user):
        """Valid password change should return 200 with new tokens."""
        data = {
            "old_password": "StrongPass123!",
            "new_password": "NewStrongPass456!",
            "new_password_confirm": "NewStrongPass456!",
        }
        response = auth_client.put(self.url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "tokens" in response.data
        # Verify password actually changed
        user.refresh_from_db()
        assert user.check_password("NewStrongPass456!")

    def test_change_password_wrong_old(self, auth_client):
        """Wrong old password should return 400."""
        data = {
            "old_password": "WrongPassword!",
            "new_password": "NewStrongPass456!",
            "new_password_confirm": "NewStrongPass456!",
        }
        response = auth_client.put(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_unauthenticated(self, api_client):
        """Unauthenticated request should return 401."""
        response = api_client.put(self.url, {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenEndpoints:
    """Tests for JWT token obtain and refresh endpoints."""

    obtain_url = reverse("users:token_obtain_pair")
    refresh_url = reverse("users:token_refresh")

    def test_obtain_token_success(self, api_client, user):
        """Valid credentials should return access and refresh tokens."""
        data = {"email": user.email, "password": "StrongPass123!"}
        response = api_client.post(self.obtain_url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_obtain_token_invalid_credentials(self, api_client, user):
        """Invalid credentials should return 401."""
        data = {"email": user.email, "password": "WrongPassword!"}
        response = api_client.post(self.obtain_url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_success(self, api_client, user):
        """Valid refresh token should return a new access token."""
        # First get tokens
        data = {"email": user.email, "password": "StrongPass123!"}
        token_response = api_client.post(self.obtain_url, data, format="json")
        refresh_token = token_response.data["refresh"]

        # Use refresh token
        response = api_client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

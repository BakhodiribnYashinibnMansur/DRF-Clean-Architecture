# ============================================
# User Views (Presentation Layer)
# API endpoints for user registration, profile management,
# admin user CRUD, and password change.
# ============================================

from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.application.services import UserService
from apps.users.domain.exceptions import DuplicateEmailError, InvalidPasswordError
from apps.users.infrastructure.repositories import DjangoUserRepository

from .permissions import IsAdminOrSelf
from .serializers import (
    ChangePasswordSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()


def _get_user_service() -> UserService:
    return UserService(repository=DjangoUserRepository())


class RegisterView(generics.CreateAPIView):
    """
    POST /api/users/register/

    Register a new user account.
    Returns user data along with JWT access and refresh tokens.
    No authentication required.
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        service = _get_user_service()
        try:
            entity = service.register_user(
                email=data["email"],
                password=data["password"],
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
            )
        except DuplicateEmailError:
            raise ValidationError({"email": "This email is already registered."})

        user = User.objects.get(id=entity.id)
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserProfileSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/users/profile/ — Retrieve the authenticated user's profile.
    PATCH /api/users/profile/ — Update the authenticated user's profile.

    Only the authenticated user can view/edit their own profile.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the currently authenticated user."""
        return self.request.user

    def perform_update(self, serializer):
        """Update profile through the service layer."""
        service = _get_user_service()
        service.update_profile(self.request.user.id, **serializer.validated_data)
        serializer.instance.refresh_from_db()


class UserViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for user management.

    - Admin users: Can list, retrieve, update, and delete any user.
    - Non-admin users: Can only retrieve and update their own account.

    Endpoints (via router):
        GET    /api/users/           — List all users (admin only)
        POST   /api/users/           — Create a user (admin only)
        GET    /api/users/{id}/      — Retrieve a user
        PUT    /api/users/{id}/      — Full update a user
        PATCH  /api/users/{id}/      — Partial update a user
        DELETE /api/users/{id}/      — Delete a user (admin only)
    """

    queryset = User.objects.all()

    def get_serializer_class(self):
        """Use compact serializer for list, full serializer for detail."""
        if self.action == "list":
            return UserListSerializer
        return UserDetailSerializer

    def get_permissions(self):
        """
        Permission logic:
        - list, create, destroy: admin only
        - retrieve, update, partial_update: admin or the user themselves
        """
        if self.action in ["list", "create", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated(), IsAdminOrSelf()]

    def get_queryset(self):
        """
        Admin users see all users.
        Non-admin users see only themselves.
        """
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        """Update user through the service layer."""
        service = _get_user_service()
        service.update_profile(serializer.instance.id, **serializer.validated_data)
        serializer.instance.refresh_from_db()

    def perform_destroy(self, instance):
        """Delete user through the service layer."""
        service = _get_user_service()
        service.delete_user(instance.id)


class ChangePasswordView(generics.UpdateAPIView):
    """
    PUT /api/users/change-password/

    Change the authenticated user's password.
    Requires old_password for verification.
    Returns new JWT tokens after successful password change.
    """

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the currently authenticated user."""
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = _get_user_service()
        try:
            service.change_password(
                user_id=request.user.id,
                old_password=serializer.validated_data["old_password"],
                new_password=serializer.validated_data["new_password"],
            )
        except InvalidPasswordError:
            raise ValidationError({"old_password": "Old password is incorrect."})

        refresh = RefreshToken.for_user(request.user)

        return Response(
            {
                "message": "Password changed successfully.",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )

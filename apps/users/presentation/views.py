# ============================================
# User Views (Presentation Layer)
# API endpoints for user registration, profile management,
# admin user CRUD, and password change.
# ============================================

from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsAdminOrSelf
from .serializers import (
    ChangePasswordSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()


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
        user = serializer.save()

        # Generate JWT tokens for the newly registered user
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
        serializer.save()

        # Generate new tokens since the password has changed
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

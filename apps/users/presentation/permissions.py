# ============================================
# User Permissions (Presentation Layer)
# Custom permission classes for user-related API endpoints.
# ============================================

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission:
    - Read access (GET, HEAD, OPTIONS) is allowed for any authenticated user.
    - Write access (PUT, PATCH, DELETE) is only allowed if the object is the requesting user.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in SAFE_METHODS:
            return True
        # Write permissions only for the owner
        return obj == request.user


class IsAdminOrSelf(BasePermission):
    """
    Object-level permission:
    - Admin users can access any user object.
    - Non-admin users can only access their own user object.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user

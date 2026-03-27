# ============================================
# Book Permissions (Presentation Layer)
# Custom permission classes for book-related API endpoints.
# ============================================

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    View-level permission:
    - Read access (GET, HEAD, OPTIONS) is allowed for any authenticated user.
    - Write access (POST, PUT, PATCH, DELETE) is only allowed for admin users.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission:
    - Admin users can modify any book.
    - Non-admin users can only modify books they created.
    - Read access is allowed for everyone.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in SAFE_METHODS:
            return True
        # Write permissions for admin or the book's creator
        return request.user.is_staff or obj.created_by == request.user

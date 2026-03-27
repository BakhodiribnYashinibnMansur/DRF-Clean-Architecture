# ============================================
# Proxy re-export for the custom user manager.
# The actual manager lives in infrastructure/managers.py.
# ============================================

from apps.users.infrastructure.managers import CustomUserManager  # noqa: F401

__all__ = ["CustomUserManager"]

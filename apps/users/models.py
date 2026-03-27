# ============================================
# Proxy re-export for Django model discovery.
# The actual model lives in infrastructure/models.py.
# This file exists so Django's app loader can find the CustomUser model
# via the standard apps.users.models path.
# ============================================

from apps.users.infrastructure.models import CustomUser  # noqa: F401

__all__ = ["CustomUser"]

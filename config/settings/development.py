# ============================================
# Development Settings
# Extends base settings with debug-friendly configuration.
# ============================================

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

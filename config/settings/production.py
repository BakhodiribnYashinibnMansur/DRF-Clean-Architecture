# ============================================
# Production Settings
# Extends base settings with security hardening.
# ============================================

from decouple import Csv, config

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

# ============================================
# Security Hardening
# ============================================
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# CORS — explicit origins only in production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="",
    cast=Csv(),
)

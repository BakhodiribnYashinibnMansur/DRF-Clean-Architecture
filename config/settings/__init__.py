# ============================================
# Settings Module Selector
# Automatically selects development or production settings
# based on the DJANGO_ENV environment variable.
# ============================================

from decouple import config

environment = config("DJANGO_ENV", default="development")

if environment == "production":
    from .production import *  # noqa: F401, F403
else:
    from .development import *  # noqa: F401, F403

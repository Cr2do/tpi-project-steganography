"""
Development settings.
"""
from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = True

SECRET_KEY = "django-insecure-dev-secret-key-change-me-before-production"

ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# CORS — allow everything locally
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# Email — console backend (no real emails sent)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

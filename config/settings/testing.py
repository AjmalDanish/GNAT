"""
Testing Environment Settings.

This module contains configuration overrides specific to the testing environment.
It extends base.py with testing-optimized settings such as:
- In-memory database for fast tests
- Test-specific logging
- Disabled caching
- Simplified email backend
- Faster password hashing
"""

from .base import *  # noqa: F401, F403

# ============================================================================
# Debug Mode
# ============================================================================

DEBUG = True

# ============================================================================
# Database (Testing - In-Memory SQLite)
# ============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": True,
    }
}


# ============================================================================
# Password Hashing (Faster for Tests)
# ============================================================================

# Use fast password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


# ============================================================================
# Email (Testing - In-Memory)
# ============================================================================

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


# ============================================================================
# Caching (Testing - Dummy Cache)
# ============================================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}


# ============================================================================
# Celery (Testing - Eager Mode)
# ============================================================================

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


# ============================================================================
# Logging (Testing - Minimal)
# ============================================================================

LOG_LEVEL = "WARNING"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}


# ============================================================================
# Media/Static Files (Testing - In-Memory)
# ============================================================================

MEDIA_ROOT = "/tmp/test_media/"
STATIC_ROOT = "/tmp/test_static/"


# ============================================================================
# REST Framework (Testing)
# ============================================================================

REST_FRAMEWORK.update(
    {
        # Disable throttling in tests
        "DEFAULT_THROTTLE_CLASSES": [],
        "DEFAULT_THROTTLE_RATES": {},
        # Use simple pagination
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 10,
    }
)


# ============================================================================
# CORS (Testing - Allow All)
# ============================================================================

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


# ============================================================================
# Security (Testing - Relaxed)
# ============================================================================

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False


# ============================================================================
# Test Runner Configuration
# ============================================================================

TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Test database settings
TEST_NON_SERIALIZED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
]

# Speed up tests
SILENCED_SYSTEM_CHECKS = [
    "security.W004",  # SECURE_SSL_REDIRECT = False
    "security.W008",  # SECURE_HSTS_SECONDS = 0
    "security.W012",  # ALLOWED_HOSTS check
]


# ============================================================================
# Internationalization (Testing - Disabled for Speed)
# ============================================================================

USE_I18N = False
USE_L10N = False
USE_TZ = False


# ============================================================================
# Session (Testing - Database-Backed)
# ============================================================================

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 86400


# ============================================================================
# Debug Toolbar (Disabled in Tests)
# ============================================================================

if "debug_toolbar" in INSTALLED_APPS:
    INSTALLED_APPS.remove("debug_toolbar")
if "debug_toolbar.middleware.DebugToolbarMiddleware" in MIDDLEWARE:
    MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")


# ============================================================================
# Django Extensions (Disabled in Tests)
# ============================================================================

if "django_extensions" in INSTALLED_APPS:
    INSTALLED_APPS.remove("django_extensions")


# ============================================================================
# Feature Flags (Testing)
# ============================================================================

FEATURE_JWT_AUTH = False
FEATURE_OAUTH_GOOGLE = False
FEATURE_OAUTH_GITHUB = False
FEATURE_WEBSOCKETS = False
FEATURE_REALTIME_ALERTS = False


# ============================================================================
# Test-Specific Constants
# ============================================================================

# Test data paths
TEST_DATA_DIR = PROJECT_ROOT / "tests" / "fixtures"
TEST_MEDIA_DIR = PROJECT_ROOT / "tests" / "media"

# Create test directories if they don't exist
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
TEST_MEDIA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Internationalization (Testing)
# ============================================================================

LANGUAGE_CODE = "en-us"


# ============================================================================
# Additional Settings
# ============================================================================


# Disable migrations for faster tests
class DisableMigrations:
    """
    Disable migrations for faster tests.

    Usage:
        TEST_RUNNER = "config.settings.testing.DisableMigrations"
    """

    def __contains__(self, item: str) -> bool:
        return True

    def __getitem__(self, item: str) -> list:
        return None


# Uncomment to disable all migrations (uncomment for faster tests)
# MIGRATION_MODULES = DisableMigrations()


# ============================================================================
# pytest-django Configuration
# ============================================================================

# These settings are recognized by pytest-django
PYTEST_TEST_DATABASE_NAME = ":memory:"
PYTEST_CREATE_TEST_DB = True
PYTEST_DONT_DB_RECREATE = False

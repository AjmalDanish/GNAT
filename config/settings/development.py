"""
Development Environment Settings.

This module contains configuration overrides specific to the development environment.
It extends base.py with development-friendly settings such as:
- Debug mode enabled
- Detailed error pages
- Development tools (debug toolbar)
- Relaxed security settings
- Console logging
"""

from .base import *  # noqa: F401, F403

# ============================================================================
# Debug Mode
# ============================================================================

DEBUG = True

# Allow all localhost variations
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "[::1]",  # IPv6 localhost
]

# ============================================================================
# Django Debug Toolbar
# ============================================================================

INSTALLED_APPS.extend(
    [
        "debug_toolbar",
    ]
)

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = [
    "127.0.0.1",
    "::1",
]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
    "SHOW_TEMPLATE_CONTEXT": True,
    "ENABLE_STACKTRACES": True,
    "RESULTS_CACHE_SIZE": 100,
    "SQL_WARNING_THRESHOLD": 100,  # milliseconds
}


# ============================================================================
# Logging (Development - Verbose)
# ============================================================================

LOG_LEVEL = "DEBUG"

# Add console handler for all logs
for logger_config in LOGGING["loggers"].values():
    if "console" not in logger_config.get("handlers", []):
        logger_config.setdefault("handlers", []).append("console")

# Ensure console logs at DEBUG level
LOGGING["handlers"]["console"]["level"] = "DEBUG"


# ============================================================================
# Database (Development)
# ============================================================================

# Display SQL queries in console
if SHOW_SQL_QUERIES:
    LOGGING["loggers"]["django.db.backends"] = {
        "handlers": ["console"],
        "level": "DEBUG",
        "propagate": False,
    }


# ============================================================================
# Email (Development - Console Backend)
# ============================================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ============================================================================
# Security (Development - Relaxed)
# ============================================================================

# Disable SSL redirect in development
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None

# Disable HSTS in development
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Allow insecure cookies in development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Disable cross-origin opener policy
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


# ============================================================================
# Celery (Development)
# ============================================================================

# Run tasks synchronously for easier debugging
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


# ============================================================================
# Static Files (Development - Django Serves)
# ============================================================================

# Whitenoise is still used but with auto-reload
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ============================================================================
# REST Framework (Development)
# ============================================================================

REST_FRAMEWORK.update(
    {
        # Allow browsing API in browser
        "DEFAULT_RENDERER_CLASSES": [
            "rest_framework.renderers.BrowsableAPIRenderer",
            "rest_framework.renderers.JSONRenderer",
        ],
        # Disable throttling in development
        "DEFAULT_THROTTLE_CLASSES": [],
        "DEFAULT_THROTTLE_RATES": {},
        # More detailed error responses
        "DEFAULT_EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    }
)


# ============================================================================
# Django Extensions (Development)
# ============================================================================

DJANGO_EXTENSIONS_EXTENSIONS = [
    "runserver_plus",
    "shell_plus",
    "graph_models",
    "show_urls",
    "describe_form",
    "generate_secret_key",
]


# ============================================================================
# Feature Flags (Development)
# ============================================================================

FEATURE_JWT_AUTH = False
FEATURE_OAUTH_GOOGLE = False
FEATURE_OAUTH_GITHUB = False
FEATURE_WEBSOCKETS = False
FEATURE_REALTIME_ALERTS = False


# ============================================================================
# Testing Configuration
# ============================================================================

# Use test database for testing
TEST_RUNNER = "django.test.runner.DiscoverRunner"


# ============================================================================
# Performance Monitoring (Development)
# ============================================================================

# Enable Django silk for profiling (optional)
if env.bool("DJANGO_SILK_ENABLED", default=False):
    INSTALLED_APPS.append("silk")
    MIDDLEWARE.append("silk.middleware.SilkyMiddleware")
    SILKY_PYTHON_PROFILER_RESULT_PATH = BASE_DIR / ".silk" / "profiler" / "results"


# ============================================================================
# Additional Development Settings
# ============================================================================

# Show deprecation warnings
import warnings

warnings.filterwarnings(
    "default",
    category=DeprecationWarning,
    module="django",
)

# Enable Django debug page
DEBUG_PROPAGATE_EXCEPTIONS = False

# File upload debugging
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

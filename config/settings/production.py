"""
Production Environment Settings.

This module contains configuration overrides specific to the production environment.
It extends base.py with production-grade security and performance settings.

SECURITY NOTES:
- All security settings are enforced
- Debug mode is disabled
- SSL/HTTPS is required
- Cookies are secure
- HSTS is enabled
- Detailed error pages are disabled
"""
from .base import *  # noqa: F401, F403

# ============================================================================
# Debug Mode
# ============================================================================

DEBUG = False

# ALLOWED_HOSTS should be set from environment
# Example: production.example.com,www.production.example.com
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set in production environment")


# ============================================================================
# Security Settings
# ============================================================================

# SSL/HTTPS (Required in production)
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_PRELOAD = True

# Secure Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Referrer Policy
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Additional Security Headers
SECURE_SSL_HOST = True
SECURE_REDIRECT_EXEMPT = []


# ============================================================================
# Email (Production - SMTP)
# ============================================================================

# Ensure email configuration is complete
if not all([EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
    raise ValueError(
        "Email configuration (EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD) "
        "must be set in production"
    )


# ============================================================================
# CORS (Production - Restricted)
# ============================================================================

CORS_ALLOW_ALL_ORIGINS = False

# CORS_ALLOWED_ORIGINS should be set from environment
# Example: https://app.example.com,https://admin.example.com
if not CORS_ALLOWED_ORIGINS:
    raise ValueError("CORS_ALLOWED_ORIGINS must be set in production environment")

# Additional CORS security
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]


# ============================================================================
# Logging (Production - File Only)
# ============================================================================

LOG_LEVEL = "INFO"

# Remove console handler in production
for logger_config in LOGGING["loggers"].values():
    if "console" in logger_config.get("handlers", []):
        logger_config["handlers"].remove("console")

# Add JSON formatter for structured logging
LOGGING["formatters"]["json"] = {
    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
    "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
}

# Add error log handler
LOGGING["handlers"]["error_log"]["level"] = "ERROR"


# ============================================================================
# Static Files (Production - Whitenoise)
# ============================================================================

INSTALLED_APPS.insert(
    INSTALLED_APPS.index("django.contrib.staticfiles") + 1,
    "whitenoise.runserver_nostatic",
)

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.common.CommonMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)

WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False
WHITENOISE_MANIFEST_STRICT = True
WHITENOISE_MAX_AGE = 31536000  # 1 year (with proper cache busting)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ============================================================================
# Database (Production)
# ============================================================================

# Increase connection pool for production
DATABASES["default"]["OPTIONS"] = {
    "connect_timeout": 10,
    "options": "-c statement_timeout=30000",
}

# Enable persistent connections
DATABASES["default"]["CONN_MAX_AGE"] = 600  # 10 minutes


# ============================================================================
# Celery (Production - Redis)
# ============================================================================

CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False


# ============================================================================
# REST Framework (Production)
# ============================================================================

REST_FRAMEWORK.update({
    # Remove browsable API in production
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    # Strict permission checks
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # Enable throttling
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/hour",
    },
    # Use custom exception handler
    "EXCEPTION_HANDLER": "apps.common.exceptions.custom_exception_handler",
})


# ============================================================================
# Session Configuration (Production)
# ============================================================================

SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# ============================================================================
# Sentry (Error Tracking)
# ============================================================================

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        environment=SENTRY_ENVIRONMENT,
        traces_sample_rate=0.1,  # 10% of transactions
        profiles_sample_rate=0.1,
        send_default_pii=False,
        before_send_transaction=lambda event: None,  # Disable transaction sampling
    )


# ============================================================================
# File Upload Limits (Production)
# ============================================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000


# ============================================================================
# Performance Optimization
# ============================================================================

# Disable unnecessary middleware in production
if DEBUG:
    # Ensure debug toolbar is never loaded in production
    if "debug_toolbar" in INSTALLED_APPS:
        INSTALLED_APPS.remove("debug_toolbar")
    if "debug_toolbar.middleware.DebugToolbarMiddleware" in MIDDLEWARE:
        MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")


# ============================================================================
# WSGI Configuration
# ============================================================================

# WSGI application - used by Gunicorn
WSGI_APPLICATION = "config.wsgi.application"


# ============================================================================
# ASGI Configuration (Future: WebSockets)
# ============================================================================

ASGI_APPLICATION = "config.asgi.application"


# ============================================================================
# Monitoring and Metrics
# ============================================================================

# Prometheus metrics (if enabled)
if env.bool("ENABLE_PROMETHEUS_METRICS", default=False):
    INSTALLED_APPS.append("django_prometheus")
    MIDDLEWARE.insert(0, "django_prometheus.middleware.PrometheusBeforeMiddleware")
    MIDDLEWARE.append("django_prometheus.middleware.PrometheusAfterMiddleware")


# ============================================================================
# Content Security Policy (Future Enhancement)
# ============================================================================

# CSP settings can be added via django-csp
# CSP_DEFAULT_SRC = ["'self'"]
# CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'"]
# CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]


# ============================================================================
# Feature Flags (Production)
# ============================================================================

FEATURE_JWT_AUTH = env.bool("FEATURE_JWT_AUTH", default=False)
FEATURE_OAUTH_GOOGLE = env.bool("FEATURE_OAUTH_GOOGLE", default=False)
FEATURE_OAUTH_GITHUB = env.bool("FEATURE_OAUTH_GITHUB", default=False)
FEATURE_WEBSOCKETS = env.bool("FEATURE_WEBSOCKETS", default=False)
FEATURE_REALTIME_ALERTS = env.bool("FEATURE_REALTIME_ALERTS", default=False)


# ============================================================================
# Custom Admin Configuration
# ============================================================================

# Secure admin site
ADMIN_URL = env("ADMIN_URL", default="admin/")
if ADMIN_URL == "admin/":
    import warnings
    warnings.warn(
        "Consider changing ADMIN_URL from default 'admin/' for security",
        UserWarning
    )


# ============================================================================
# Rate Limiting (Optional)
# ============================================================================

RATELIMIT_ENABLE = env.bool("RATELIMIT_ENABLE", default=False)
RATELIMIT_VIEW = env("RATELIMIT_VIEW", default="100/1m")
RATELIMIT_API = env("RATELIMIT_API", default="1000/1h")


# ============================================================================
# Git Revision (Optional)
# ============================================================================

try:
    import subprocess
    GIT_REVISION = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        stderr=subprocess.DEVNULL,
    ).decode("utf-8").strip()
except (subprocess.CalledProcessError, FileNotFoundError):
    GIT_REVISION = "unknown"
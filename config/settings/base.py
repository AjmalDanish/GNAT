"""
Base Django Settings Module.

This module contains all common configuration shared across all environments
(development, production, testing). Environment-specific settings should be
defined in their respective modules.

Architecture:
- Clean Architecture with layered configuration
- Environment-based overrides
- Type-safe configuration loading
- Security-first defaults
"""

import os
from pathlib import Path
from typing import Any

import environ

# ============================================================================
# Path Configuration
# ============================================================================

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Project root directory (for project-level references)
PROJECT_ROOT = BASE_DIR.parent

# Initialize environment
env = environ.Env(
    # Set casting defaults
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    USE_TZ=(bool, True),
    USE_I18N=(bool, True),
    SECURE_SSL_REDIRECT=(bool, True),
    SESSION_COOKIE_SECURE=(bool, True),
    CSRF_COOKIE_SECURE=(bool, True),
    SECURE_HSTS_SECONDS=(int, 31536000),  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS=(bool, True),
    SECURE_HSTS_PRELOAD=(bool, True),
)

# Read .env file
# Priority: .env.local -> .env
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)


# ============================================================================
# Django Core Settings
# ============================================================================

SECRET_KEY: str = env(
    "SECRET_KEY",
    default="django-insecure-change-this-in-production-use-50-characters-minimum",
)

DEBUG: bool = env("DEBUG", default=False)

ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Trusted Origins for CSRF
CSRF_TRUSTED_ORIGINS: list[str] = [
    f"https://{host}" for host in ALLOWED_HOSTS if host not in ["localhost", "127.0.0.1"]
]

# Application definition
INSTALLED_APPS: list[str] = [
    # Django built-in
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "django_filters",
    "corsheaders",
    "django_extensions",
    # Project apps
    "apps.accounts",
    "apps.dashboard",
    "apps.graph_engine",
    "apps.ai_engine",
    "apps.visualization",
    "apps.analytics",
    "apps.reports",
    "apps.notifications",
    "apps.api",
    "apps.common",
]

MIDDLEWARE: list[str] = [
    # Security
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    # Session & Auth
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # SEO
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
]

ROOT_URLCONF: str = "config.urls"

TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Custom context processors
                "apps.common.context_processors.global_settings",
            ],
        },
    },
]

WSGI_APPLICATION: str = "config.wsgi.application"
ASGI_APPLICATION: str = "config.asgi.application"


# ============================================================================
# Internationalization
# ============================================================================

LANGUAGE_CODE: str = env("LANGUAGE_CODE", default="en-us")

TIME_ZONE: str = env("TIME_ZONE", default="UTC")

USE_I18N: bool = env("USE_I18N", default=True)

USE_TZ: bool = env("USE_TZ", default=True)

# Language settings
LANGUAGES: list[tuple[str, str]] = [
    ("en", "English"),
]

# Locale paths
LOCALE_PATHS: list[Path] = [
    BASE_DIR / "locale",
]


# ============================================================================
# Database Configuration
# ============================================================================

DATABASES: dict[str, dict[str, Any]] = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DATABASE_NAME", default="gnat_db"),
        "USER": env("DATABASE_USER", default="gnat_user"),
        "PASSWORD": env("DATABASE_PASSWORD", default=""),
        "HOST": env("DATABASE_HOST", default="localhost"),
        "PORT": env("DATABASE_PORT", default="5432"),
        "CONN_MAX_AGE": 60,  # Persistent connections
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000",  # 30 second query timeout
        },
    }
}

# Default primary key field type
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"


# ============================================================================
# Cache Configuration (Redis)
# ============================================================================

REDIS_URL: str = env("REDIS_URL", default="redis://localhost:6379/0")

CACHES: dict[str, dict[str, Any]] = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 50},
        },
        "KEY_PREFIX": "gnat",
        "TIMEOUT": 300,  # 5 minutes default
    },
    "sessions": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "gnat_session",
        "TIMEOUT": 3600,  # 1 hour
    },
}

# Cache sessions
SESSION_ENGINE: str = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS: str = "sessions"


# ============================================================================
# Password Validation
# ============================================================================

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ============================================================================
# Authentication
# ============================================================================

AUTH_USER_MODEL: str = "accounts.User"

# Session configuration
SESSION_COOKIE_AGE: int = env("SESSION_COOKIE_AGE", default=86400)  # 24 hours
SESSION_SAVE_EVERY_REQUEST: bool = env("SESSION_SAVE_EVERY_REQUEST", default=True)
SESSION_EXPIRE_AT_BROWSER_CLOSE: bool = env("SESSION_EXPIRE_AT_BROWSER_CLOSE", default=False)
SESSION_COOKIE_HTTPONLY: bool = True
SESSION_COOKIE_SAMESITE: str = "Lax"


# ============================================================================
# Static Files Configuration
# ============================================================================

STATIC_URL: str = "/static/"
STATIC_ROOT: str = env("STATIC_ROOT", default=str(PROJECT_ROOT / "staticfiles"))

STATICFILES_DIRS: list[Path] = [
    BASE_DIR / "static",
]

STATICFILES_FINDERS: list[str] = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Media files
MEDIA_URL: str = "/media/"
MEDIA_ROOT: str = env("MEDIA_ROOT", default=str(PROJECT_ROOT / "media"))


# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL: str = env("LOG_LEVEL", default="INFO")
LOG_DIR: Path = Path(env("LOG_ROOT", default=str(PROJECT_ROOT / "logs")))

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
        },
    },
    "filters": {
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "application_log": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "application" / "app.log"),
            "maxBytes": env.int("LOG_FILE_MAX_BYTES", default=10 * 1024 * 1024),  # 10MB
            "backupCount": env.int("LOG_FILE_BACKUP_COUNT", default=10),
            "formatter": "verbose",
        },
        "training_log": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "training" / "training.log"),
            "maxBytes": env.int("LOG_FILE_MAX_BYTES", default=10 * 1024 * 1024),
            "backupCount": env.int("LOG_FILE_BACKUP_COUNT", default=10),
            "formatter": "verbose",
        },
        "prediction_log": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "prediction" / "prediction.log"),
            "maxBytes": env.int("LOG_FILE_MAX_BYTES", default=10 * 1024 * 1024),
            "backupCount": env.int("LOG_FILE_BACKUP_COUNT", default=10),
            "formatter": "verbose",
        },
        "error_log": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "errors" / "errors.log"),
            "maxBytes": env.int("LOG_FILE_MAX_BYTES", default=10 * 1024 * 1024),
            "backupCount": env.int("LOG_FILE_BACKUP_COUNT", default=10),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "application_log"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "application_log", "error_log"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "celery": {
            "handlers": ["console", "application_log"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "application_log", "error_log"],
        "level": LOG_LEVEL,
    },
}


# ============================================================================
# Django REST Framework Configuration
# ============================================================================

REST_FRAMEWORK: dict[str, Any] = {
    # Authentication
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    # Permissions
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # Pagination
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": env.int("DRF_PAGE_SIZE", default=20),
    # Filtering
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Content Negotiation
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    # Parser
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    # Versioning
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    # Throttling
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/hour",
    },
    # Metadata
    "DEFAULT_METADATA_CLASS": "rest_framework.metadata.SimpleMetadata",
    # Exception handling
    "EXCEPTION_HANDLER": "apps.common.exceptions.custom_exception_handler",
}


# ============================================================================
# CORS Configuration
# ============================================================================

CORS_ALLOWED_ORIGINS: list[str] = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://127.0.0.1:3000"],
)

CORS_ALLOW_CREDENTIALS: bool = env("CORS_ALLOW_CREDENTIALS", default=True)

CORS_ALLOW_HEADERS: list[str] = [
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

CORS_ALLOW_METHODS: list[str] = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]


# ============================================================================
# Security Settings
# ============================================================================

# SSL/HTTPS
SECURE_SSL_REDIRECT: bool = env("SECURE_SSL_REDIRECT", default=False)
SECURE_PROXY_SSL_HEADER: tuple[str, str] = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS: int = env.int("SECURE_HSTS_SECONDS", default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = env("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False)
SECURE_HSTS_PRELOAD: bool = env("SECURE_HSTS_PRELOAD", default=False)

# Cookies
SESSION_COOKIE_SECURE: bool = env("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE: bool = env("CSRF_COOKIE_SECURE", default=False)
CSRF_COOKIE_HTTPONLY: bool = True
CSRF_COOKIE_SAMESITE: str = "Lax"

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF: bool = True
SECURE_BROWSER_XSS_FILTER: bool = True
X_FRAME_OPTIONS: str = "DENY"

# CSRF
CSRF_TRUSTED_ORIGINS: list[str] = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[f"http://{host}" for host in ALLOWED_HOSTS],
)

# XSS Protection
SECURE_REFERRER_POLICY: str = "strict-origin-when-cross-origin"


# ============================================================================
# Email Configuration
# ============================================================================

EMAIL_BACKEND: str = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST: str = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT: int = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS: bool = env("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER: str = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD: str = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL: str = env("DEFAULT_FROM_EMAIL", default="noreply@gnat.example.com")
SERVER_EMAIL: str = env("SERVER_EMAIL", default="noreply@gnat.example.com")
ADMINS: list[tuple[str, str]] = [
    ("Admin", email) for email in env.list("ADMINS", default=["admin@example.com"])
]

# Email settings for notifications
EMAIL_SUBJECT_PREFIX: str = "[GNAT] "


# ============================================================================
# Celery Configuration
# ============================================================================

CELERY_BROKER_URL: str = env(
    "CELERY_BROKER_URL", default=env("REDIS_URL", default="redis://localhost:6379/0")
)
CELERY_RESULT_BACKEND: str = env(
    "CELERY_RESULT_BACKEND", default=env("REDIS_URL", default="redis://localhost:6379/0")
)
CELERY_TASK_ALWAYS_EAGER: bool = env("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_ACKS_LATE: bool = env("CELERY_TASK_ACKS_LATE", default=True)
CELERY_WORKER_PREFETCH_MULTIPLIER: int = env.int("CELERY_WORKER_PREFETCH_MULTIPLIER", default=1)
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: bool = env(
    "CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP", default=True
)
CELERY_ACCEPT_CONTENT: list[str] = ["json"]
CELERY_TASK_SERIALIZER: str = "json"
CELERY_RESULT_SERIALIZER: str = "json"
CELERY_TIMEZONE: str = TIME_ZONE
CELERY_TASK_TRACK_STARTED: bool = True
CELERY_TASK_TIME_LIMIT: int = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT: int = 25 * 60  # 25 minutes

# Celery beat schedule (empty in base, override in environment-specific)
CELERY_BEAT_SCHEDULE: dict[str, dict[str, Any]] = {}


# ============================================================================
# File Storage Paths
# ============================================================================

DATA_ROOT: Path = Path(env("DATA_ROOT", default=str(PROJECT_ROOT / "data")))
MODEL_ROOT: Path = Path(env("MODEL_ROOT", default=str(PROJECT_ROOT / "models")))

# Ensure directories exist
DATA_ROOT.mkdir(parents=True, exist_ok=True)
MODEL_ROOT.mkdir(parents=True, exist_ok=True)

# AI Model directories
MODEL_CHECKPOINT_DIR: Path = Path(
    env("MODEL_CHECKPOINT_DIR", default=str(MODEL_ROOT / "checkpoints"))
)
MODEL_EXPORT_DIR: Path = Path(env("MODEL_EXPORT_DIR", default=str(MODEL_ROOT / "exported")))
MODEL_TRAINED_DIR: Path = Path(env("MODEL_TRAINED_DIR", default=str(MODEL_ROOT / "trained")))


# ============================================================================
# AI/ML Configuration
# ============================================================================

# Device configuration
CUDA_VISIBLE_DEVICES: str = env("CUDA_VISIBLE_DEVICES", default="0")
TORCH_DEVICE: str = env("TORCH_DEVICE", default="cuda")

# Training defaults
DEFAULT_EPOCHS: int = env.int("DEFAULT_EPOCHS", default=100)
DEFAULT_BATCH_SIZE: int = env.int("DEFAULT_BATCH_SIZE", default=32)
DEFAULT_LEARNING_RATE: float = env.float("DEFAULT_LEARNING_RATE", default=0.001)
DEFAULT_OPTIMIZER: str = env("DEFAULT_OPTIMIZER", default="adam")


# ============================================================================
# API Configuration
# ============================================================================

API_V1_PREFIX: str = env("API_V1_PREFIX", default="api/v1")


# ============================================================================
# External Services Configuration
# ============================================================================

# OpenCage Geocoding API
OPENCAGE_API_KEY: str = env("OPENCAGE_API_KEY", default="")
OPENCAGE_BASE_URL: str = env("OPENCAGE_BASE_URL", default="https://api.opencagedata.com/geocode/v1")


# ============================================================================
# Sentry Configuration (Optional)
# ============================================================================

SENTRY_DSN: str = env("SENTRY_DSN", default="")
SENTRY_ENVIRONMENT: str = env("SENTRY_ENVIRONMENT", default="production")


# ============================================================================
# Feature Flags
# ============================================================================

FEATURE_JWT_AUTH: bool = env("FEATURE_JWT_AUTH", default=False)
FEATURE_OAUTH_GOOGLE: bool = env("FEATURE_OAUTH_GOOGLE", default=False)
FEATURE_OAUTH_GITHUB: bool = env("FEATURE_OAUTH_GITHUB", default=False)
FEATURE_WEBSOCKETS: bool = env("FEATURE_WEBSOCKETS", default=False)
FEATURE_REALTIME_ALERTS: bool = env("FEATURE_REALTIME_ALERTS", default=False)


# ============================================================================
# Development/Debug Utilities
# ============================================================================

# Show raw SQL queries (set in development overrides)
SHOW_SQL_QUERIES: bool = env("SHOW_SQL_QUERIES", default=False)


# ============================================================================
# Project Metadata
# ============================================================================

PROJECT_NAME: str = "Global Network Anomaly Tracker"
PROJECT_SHORT_NAME: str = "GNAT"
PROJECT_VERSION: str = "1.0.0"
PROJECT_URL: str = "https://github.com/yourusername/Global-Network-Anomaly-Tracker"

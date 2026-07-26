"""
Common Application Configuration.

This application provides:
- Shared utilities
- Logging configuration
- Custom exceptions
- Common validators
- Helper functions
- Mixins
- Decorators

Architecture:
- Reusable components
- No business logic
- Shared across all apps

Status: Phase 1 - App structure created, utilities used throughout
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CommonConfig(AppConfig):
    """
    Configuration class for the common application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
    verbose_name = _("Common Utilities")

    def ready(self) -> None:
        """
        Initialize the application when Django starts.
        """
        # Import signal handlers
        try:
            import apps.common.signals  # noqa: F401
        except ImportError:
            pass

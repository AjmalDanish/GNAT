"""
Notifications Application Configuration.

This application handles:
- Email notifications
- In-app notifications
- Alert management
- Notification preferences
- Delivery tracking

Architecture:
- Multiple notification channels
- Template-based messages
- Celery for async delivery
- User preferences

Status: Phase 1 - App structure created, business logic in Phase 19
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationsConfig(AppConfig):
    """
    Configuration class for the notifications application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    verbose_name = _("Notifications")

    def ready(self) -> None:
        """
        Initialize the application when Django starts.
        """
        # Import signal handlers
        try:
            import apps.notifications.signals  # noqa: F401
        except ImportError:
            pass

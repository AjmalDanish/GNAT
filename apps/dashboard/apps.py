"""
Dashboard Application Configuration.

This application handles:
- Main dashboard interface
- Statistics and KPIs
- Recent analysis display
- System overview
- User activity summary

Architecture:
- Template-based views
- REST API for data
- Chart integration
- Real-time updates (future)

Status: Phase 1 - App structure created, business logic in Phase 17
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DashboardConfig(AppConfig):
    """
    Configuration class for the dashboard application.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
    verbose_name = _("Dashboard")
    
    def ready(self) -> None:
        """
        Initialize the application when Django starts.
        """
        # Import signal handlers
        try:
            import apps.dashboard.signals  # noqa: F401
        except ImportError:
            pass
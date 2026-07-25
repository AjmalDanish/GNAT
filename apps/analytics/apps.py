"""
Analytics Application Configuration.

This application handles:
- Historical analysis
- Report generation
- Trend analysis
- KPI calculations
- Data exports

Architecture:
- Service layer pattern
- Repository pattern
- Celery for background tasks
- Multiple export formats

Status: Phase 1 - App structure created, business logic in Phase 17
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AnalyticsConfig(AppConfig):
    """
    Configuration class for the analytics application.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics"
    verbose_name = _("Analytics")
    
    def ready(self) -> None:
        """
        Initialize the application when Django starts.
        """
        # Import signal handlers
        try:
            import apps.analytics.signals  # noqa: F401
        except ImportError:
            pass
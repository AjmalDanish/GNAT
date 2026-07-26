"""
Reports Application Configuration.

This application handles:
- Report generation
- Multiple export formats (PDF, CSV, JSON, Excel)
- Report scheduling
- Report templates

Architecture:
- Template-based generation
- Celery for background processing
- Storage management
- Email delivery

Status: Phase 1 - App structure created, business logic in Phase 17
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReportsConfig(AppConfig):
    """
    Configuration class for the reports application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reports"
    verbose_name = _("Reports")

    def ready(self) -> None:
        """
        Initialize the application when Django starts.
        """
        # Import signal handlers
        try:
            import apps.reports.signals  # noqa: F401
        except ImportError:
            pass

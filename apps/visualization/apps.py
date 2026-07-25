"""
Visualization Application Configuration.

This application handles:
- Interactive world map visualization
- Network traffic visualization
- Anomaly heatmaps
- Graph rendering
- Chart generation

Architecture:
- Plotly for interactive charts
- GeoJSON for map data
- Template rendering
- REST API for data

Status: Phase 1 - App structure created, business logic in Phase 16
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VisualizationConfig(AppConfig):
    """
    Configuration class for the visualization application.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.visualization"
    verbose_name = _("Visualization")
    
    def ready(self) -> None:
        """
        Initialize the application when Django starts.
        """
        # Import signal handlers
        try:
            import apps.visualization.signals  # noqa: F401
        except ImportError:
            pass
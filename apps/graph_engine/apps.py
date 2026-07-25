"""
Graph Engine Application Configuration.

This application handles:
- Graph generation from network data
- Graph metrics calculation
- Feature engineering
- Graph validation
- Graph utilities

Architecture:
- NetworkX for graph operations
- Service layer pattern
- Repository pattern for data access
- DTO pattern for data transfer

Status: Phase 1 - App structure created, business logic in Phase 3 & 8
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GraphEngineConfig(AppConfig):
    """
    Configuration class for the graph_engine application.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.graph_engine"
    verbose_name = _("Graph Engine")
    
    def ready(self) -> None:
        """
        Initialize the application when Django starts.
        """
        # Import signal handlers
        try:
            import apps.graph_engine.signals  # noqa: F401
        except ImportError:
            pass
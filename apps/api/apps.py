"""
API Application Configuration.

This application handles:
- REST API endpoints
- API versioning
- Request/response serialization
- Authentication for APIs
- Rate limiting

Architecture:
- Django REST Framework
- Viewsets for CRUD operations
- Custom serializers
- API documentation (Swagger/ReDoc)

Status: Phase 1 - App structure created, business logic in Phase 13
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ApiConfig(AppConfig):
    """
    Configuration class for the api application.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
    verbose_name = _("REST API")
    
    def ready(self) -> None:
        """
        Initialize the application when Django starts.
        """
        # Import signal handlers
        try:
            import apps.api.signals  # noqa: F401
        except ImportError:
            pass
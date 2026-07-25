"""
AI Engine Application Configuration.

This application handles:
- AI model management
- Training pipeline
- Inference engine
- Model evaluation
- Feature engineering for ML

Architecture:
- PyTorch for deep learning
- PyTorch Geometric for GNNs
- Service layer pattern
- Repository pattern
- Celery for background tasks

Status: Phase 1 - App structure created, business logic in Phases 5, 6, 7, 11
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AiEngineConfig(AppConfig):
    """
    Configuration class for the ai_engine application.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ai_engine"
    verbose_name = _("AI Engine")
    
    def ready(self) -> None:
        """
        Initialize the application when Django starts.
        """
        # Import signal handlers
        try:
            import apps.ai_engine.signals  # noqa: F401
        except ImportError:
            pass
"""
Accounts Application Configuration.

This application handles:
- User authentication and authorization
- User profiles
- Role-based permissions
- Password management
- Session management

Architecture:
- Custom User model extending AbstractBaseUser
- Profile model for additional user information
- JWT authentication support (future)
- OAuth2 integration (future)

Status: Phase 1 - App structure created, business logic in Phase 11
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    """
    Configuration class for the accounts application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = _("Accounts & Authentication")

    def ready(self) -> None:
        """
        Initialize the application when Django starts.

        This method is called when Django starts and is used for:
        - Importing signal handlers
        - Registering tasks
        - Initializing services
        """
        # Import signal handlers
        try:
            import apps.accounts.signals  # noqa: F401
        except ImportError:
            pass

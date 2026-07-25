"""
Root URL Configuration.

This module defines the main URL routing for the GNAT application.
It follows Django's URL dispatcher pattern and includes all app-specific
URL configurations.

URL Pattern Organization:
- Admin: /admin/
- API: /api/v1/
- Dashboard: /
- Accounts: /accounts/
- Graph Engine: /graph/
- AI Engine: /ai/
- Visualization: /visualization/
- Analytics: /analytics/
- Reports: /reports/
- Notifications: /notifications/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.defaults import page_not_found, server_error, permission_denied
from rest_framework import permissions
from pathlib import Path
from typing import Any

# Conditional import for drf-yasg (API documentation)
try:
    from drf_yasg import openapi
    from drf_yasg.views import get_schema_view
    DRF_YASG_AVAILABLE = True
except ImportError:
    DRF_YASG_AVAILABLE = False

# ============================================================================
# Schema View (Swagger/OpenAPI)
# ============================================================================

if DRF_YASG_AVAILABLE:
    schema_view = get_schema_view(
        openapi.Info(
            title="Global Network Anomaly Tracker API",
            default_version="v1",
            description="""
            The GNAT API provides endpoints for:
            - Network traffic simulation
            - Graph generation and analytics
            - AI-powered anomaly detection
            - Interactive visualization
            - User authentication and authorization
            """,
            terms_of_service="https://www.example.com/terms/",
            contact=openapi.Contact(email="dev@gnat.example.com"),
            license=openapi.License(name="MIT License"),
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )
else:
    schema_view = None


# ============================================================================
# Error Handlers
# ============================================================================

def custom_404_handler(request: Any, exception: Any) -> Any:
    """
    Custom 404 handler.

    Args:
        request: The HTTP request object.
        exception: The exception that triggered the 404.

    Returns:
        The 404 error response.
    """
    return page_not_found(request, exception)


def custom_500_handler(request: Any) -> Any:
    """
    Custom 500 handler.

    Args:
        request: The HTTP request object.

    Returns:
        The 500 error response.
    """
    return server_error(request)


def custom_403_handler(request: Any, exception: Any) -> Any:
    """
    Custom 403 handler.

    Args:
        request: The HTTP request object.
        exception: The exception that triggered the 403.

    Returns:
        The 403 error response.
    """
    return permission_denied(request, exception)


# ============================================================================
# URL Patterns
# ============================================================================

urlpatterns: list[Any] = [
    # Health check endpoint
    path(
        "health/",
        TemplateView.as_view(template_name="health.html"),
        name="health_check",
    ),
    
    # Admin
    path(settings.ADMIN_URL, admin.site.urls),
]

# API Documentation (Swagger/OpenAPI) - only if drf-yasg is available
if DRF_YASG_AVAILABLE:
    urlpatterns.extend([
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "redoc/",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
        path(
            "swagger.json",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
    ])

urlpatterns.extend([
    # API v1
    path("api/v1/", include("apps.api.v1.routers")),
    
    # App-specific URLs (will be implemented in Phase 2+)
    path("", include("apps.dashboard.urls", namespace="dashboard")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("graph/", include("apps.graph_engine.urls", namespace="graph_engine")),
    path("ai/", include("apps.ai_engine.urls", namespace="ai_engine")),
    path(
        "visualization/",
        include("apps.visualization.urls", namespace="visualization"),
    ),
    path("analytics/", include("apps.analytics.urls", namespace="analytics")),
    path("reports/", include("apps.reports.urls", namespace="reports")),
    path(
        "notifications/",
        include("apps.notifications.urls", namespace="notifications"),
    ),
    
    # Common utilities
    path("common/", include("apps.common.urls", namespace="common")),
]

# ============================================================================
# Handler Configuration
# ============================================================================

handler404 = "config.urls.custom_404_handler"
handler500 = "config.urls.custom_500_handler"
handler403 = "config.urls.custom_403_handler"

# ============================================================================
# Static/Media Files (Development Only)
# ============================================================================

if settings.DEBUG:
    # Serve static files in development
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
    
    # Serve media files in development
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    
    # Add Django Debug Toolbar URLs (if enabled)
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        
        urlpatterns.insert(0, path("__debug__/", include(debug_toolbar.urls)))
    
    # Add Django Silk URLs (if enabled)
    if "silk" in settings.INSTALLED_APPS:
        urlpatterns.insert(0, path("silk/", include("silk.urls", namespace="silk")))
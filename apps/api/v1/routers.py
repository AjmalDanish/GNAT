"""
API v1 Router Configuration.

This module defines the API v1 URL patterns using Django REST Framework routers.

Architecture:
- DefaultRouter for automatic viewset routing
- Namespace: api:v1
- Version: v1

Status: Placeholder routers, will be implemented in Phase 13
"""

from django.urls import include, path
from rest_framework import routers
from rest_framework.routers import DefaultRouter

# Create a router and register our ViewSets
router: DefaultRouter = routers.DefaultRouter()

# Register viewsets here (Phase 13)
# router.register(r"users", accounts_views.UserViewSet, basename="user")
# router.register(r"graphs", graph_engine_views.GraphViewSet, basename="graph")
# router.register(r"models", ai_engine_views.ModelViewSet, basename="model")
# router.register(r"predictions", ai_engine_views.PredictionViewSet, basename="prediction")
# router.register(r"datasets", graph_engine_views.DatasetViewSet, basename="dataset")
# router.register(r"analytics", analytics_views.AnalyticsViewSet, basename="analytics")

# Additional API patterns
urlpatterns: list = [
    # Include the router URLs
    path("", include(router.urls)),
    # Additional manual patterns if needed
    # path("health/", views.HealthCheckAPIView.as_view(), name="health_check"),
    # Auth endpoints (if using JWT)
    # path("auth/token/", views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("auth/token/refresh/", views.TokenRefreshView.as_view(), name="token_refresh"),
]

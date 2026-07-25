"""
API v1 Router Configuration.

This module defines the API v1 URL patterns using Django REST Framework routers.

Architecture:
- DefaultRouter for automatic viewset routing
- Namespace: api:v1
- Version: v1

Status: Placeholder routers, will be implemented in Phase 13
"""
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter

# Create a router and register our ViewSets
router: DefaultRouter = routers.DefaultRouter()

# Register viewsets here
# Accounts (Phase 11)
# router.register(r"users", accounts_views.UserViewSet, basename="user")

# Graph Engine (Phase 2 - Partial)
router.register(r"graph/countries", None, basename="country")  # Included from graph_engine
router.register(r"graph/cities", None, basename="city")  # Included from graph_engine
router.register(r"graph/datasets", None, basename="dataset")  # Included from graph_engine
router.register(r"graph/transactions", None, basename="transaction")  # Included from graph_engine
router.register(r"graph/generation", None, basename="generation")  # Included from graph_engine

# AI Engine (Phase 5-7)
# router.register(r"models", ai_engine_views.ModelViewSet, basename="model")
# router.register(r"predictions", ai_engine_views.PredictionViewSet, basename="prediction")

# Analytics (Phase 17)
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
"""
URL Configuration for Graph Engine Application.

This module defines URL patterns for:
- Country management
- City management
- Dataset management
- Transaction viewing
- Dataset generation

Status: Phase 2 - Issue #1
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryViewSet, CityViewSet, DatasetViewSet, TransactionViewSet, DatasetGenerationViewSet

router = DefaultRouter()
router.register(r"countries", CountryViewSet, basename="country")
router.register(r"cities", CityViewSet, basename="city")
router.register(r"datasets", DatasetViewSet, basename="dataset")
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"generation", DatasetGenerationViewSet, basename="generation")

app_name = "graph_engine"

urlpatterns = [
    # API routes
    path("api/v1/", include(router.urls)),
]
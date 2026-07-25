"""
URL Configuration for Graph Engine Application.

This module defines URL patterns for:
- Graph generation
- Graph metrics
- Graph visualization

Status: Placeholder URLs, will be implemented in Phase 3 & 8
"""
from django.urls import path
from . import views

app_name = "graph_engine"

urlpatterns: list = [
    # Graph operations
    # path("generate/", views.GraphGenerateView.as_view(), name="generate"),
    # path("metrics/", views.GraphMetricsView.as_view(), name="metrics"),
    # path("features/", views.GraphFeaturesView.as_view(), name="features"),
]
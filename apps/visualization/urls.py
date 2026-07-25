"""
URL Configuration for Visualization Application.

This module defines URL patterns for:
- World map
- Network graphs
- Heatmaps
- Charts

Status: Placeholder URLs, will be implemented in Phase 16
"""

from django.urls import path

from . import views

app_name = "visualization"

urlpatterns: list = [
    # Map visualization
    # path("map/", views.WorldMapView.as_view(), name="map"),
    # Graph visualization
    # path("graph/<uuid:graph_id>/", views.GraphVisualizationView.as_view(), name="graph"),
    # Heatmap
    # path("heatmap/", views.HeatmapView.as_view(), name="heatmap"),
]

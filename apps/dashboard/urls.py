"""
URL Configuration for Dashboard Application.

This module defines URL patterns for:
- Main dashboard
- Statistics
- KPIs
- Recent activity

Status: Placeholder URLs, will be implemented in Phase 17
"""

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns: list = [
    # Main dashboard
    # path("", views.DashboardView.as_view(), name="home"),
    # Statistics
    # path("stats/", views.StatsView.as_view(), name="stats"),
    # API endpoints (for AJAX)
    # path("api/summary/", views.DashboardSummaryAPIView.as_view(), name="api_summary"),
]

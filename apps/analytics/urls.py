"""
URL Configuration for Analytics Application.

This module defines URL patterns for:
- Historical analysis
- Reports
- Trends
- KPIs

Status: Placeholder URLs, will be implemented in Phase 17
"""

from django.urls import path

from . import views

app_name = "analytics"

urlpatterns: list = [
    # Analysis
    # path("", views.AnalyticsView.as_view(), name="home"),
    # Reports
    # path("reports/", views.ReportsView.as_view(), name="reports"),
    # Trends
    # path("trends/", views.TrendsView.as_view(), name="trends"),
]

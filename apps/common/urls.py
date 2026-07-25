"""
URL Configuration for Common Application.

This module defines URL patterns for:
- Health checks
- System status
- Common utilities

Status: Placeholder URLs
"""

from django.urls import path

from . import views

app_name = "common"

urlpatterns: list = [
    # Health check
    # path("health/", views.HealthCheckView.as_view(), name="health"),
]

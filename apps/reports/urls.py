"""
URL Configuration for Reports Application.

This module defines URL patterns for:
- Report generation
- Report download
- Report history

Status: Placeholder URLs, will be implemented in Phase 17
"""

from django.urls import path

from . import views

app_name = "reports"

urlpatterns: list = [
    # Generate report
    # path("generate/", views.ReportGenerateView.as_view(), name="generate"),
    # Download report
    # path("download/<uuid:report_id>/", views.ReportDownloadView.as_view(), name="download"),
    # Report history
    # path("", views.ReportListView.as_view(), name="list"),
]

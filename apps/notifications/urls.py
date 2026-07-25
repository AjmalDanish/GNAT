"""
URL Configuration for Notifications Application.

This module defines URL patterns for:
- Notification list
- Notification preferences
- Mark as read

Status: Placeholder URLs, will be implemented in Phase 19
"""

from django.urls import path

from . import views

app_name = "notifications"

urlpatterns: list = [
    # Notification list
    # path("", views.NotificationListView.as_view(), name="list"),
    # Preferences
    # path("preferences/", views.NotificationPreferencesView.as_view(), name="preferences"),
    # Actions
    # path("<uuid:notification_id>/read/", views.MarkAsReadView.as_view(), name="mark_read"),
]

"""
URL Configuration for Accounts Application.

This module defines URL patterns for:
- User registration
- Login/logout
- Password reset
- Profile management
- User settings

Status: Placeholder URLs, will be implemented in Phase 11
"""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns: list = [
    # Authentication
    # path("register/", views.UserRegisterView.as_view(), name="register"),
    # path("login/", views.UserLoginView.as_view(), name="login"),
    # path("logout/", views.UserLogoutView.as_view(), name="logout"),
    # Password management
    # path("password/change/", views.PasswordChangeView.as_view(), name="password_change"),
    # path("password/reset/", views.PasswordResetView.as_view(), name="password_reset"),
    # Profile
    # path("profile/", views.ProfileDetailView.as_view(), name="profile"),
    # path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile_edit"),
]

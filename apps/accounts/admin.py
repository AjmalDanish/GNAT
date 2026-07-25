"""
Admin Configuration for Accounts Application.

Status: Placeholder admin, will be implemented in Phase 11
"""
from django.contrib import admin


@admin.register(None)
class UserAdmin(admin.ModelAdmin):
    """User admin placeholder."""
    pass
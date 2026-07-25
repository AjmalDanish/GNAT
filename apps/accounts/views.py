"""
Views for Accounts Application.

Status: Placeholder views, will be implemented in Phase 11
"""

from django.views import View
from django.views.generic import TemplateView
from django.http import HttpResponse


class BaseView(TemplateView):
    """Base view placeholder."""

    pass


def health_check(request: object) -> HttpResponse:
    """Health check endpoint."""
    return HttpResponse("OK", status=200)

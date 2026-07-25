"""
Context Processors for Common Application.

These context processors add common data to template contexts.
"""
from django.conf import settings


def global_settings(request: object) -> dict[str, str]:
    """
    Add global settings to template context.

    Args:
        request: The HTTP request object.

    Returns:
        Dictionary of global settings.
    """
    return {
        "PROJECT_NAME": settings.PROJECT_NAME,
        "PROJECT_SHORT_NAME": settings.PROJECT_SHORT_NAME,
        "PROJECT_VERSION": settings.PROJECT_VERSION,
        "DEBUG": settings.DEBUG,
    }
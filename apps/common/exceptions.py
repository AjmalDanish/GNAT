"""
Custom Exception Handler for REST API.

This module provides custom exception handling for the REST API,
returning consistent error responses across the application.
"""

import logging
from typing import Any

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:
    """
    Custom exception handler for REST API.

    This handler:
    - Logs all exceptions
    - Returns consistent error response format
    - Handles both DRF and Django exceptions
    - Includes request information for debugging

    Args:
        exc: The exception instance.
        context: The context dictionary containing view, request, etc.

    Returns:
        Response object with error details or None for unhandled exceptions.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Use default DRF error response format
        return response

    # Handle non-DRF exceptions
    logger.error(
        f"Unhandled exception: {exc}", exc_info=True, extra={"context": context}
    )

    # Return a generic error response
    return Response(
        {
            "detail": "An internal server error occurred.",
            "error": str(exc) if settings.DEBUG else "Internal error",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

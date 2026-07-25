"""
WSGI Configuration for Production Deployment.

This module configures the WSGI application for production deployment using
Gunicorn or another WSGI server. It follows Django's recommended WSGI setup
for production use.

WSGI (Web Server Gateway Interface) is the Python standard for web servers
to communicate with web applications.

Architecture:
- Django's WSGIHandler serves as the application entry point
- Whitenoise serves static files
- Gunicorn manages worker processes
- Nginx (optional) handles SSL, load balancing, and static file serving

Deployment:
    gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --threads 4 \
        --worker-class gthread \
        --timeout 120 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile - \
        --error-logfile - \
        --log-level info
"""

import os
from typing import Any

from django.core.wsgi import get_wsgi_application

# Set default settings module if not set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# Get the WSGI application
application = get_wsgi_application()

# ============================================================================
# Application Metadata
# ============================================================================

application.gnat_version = "1.0.0"
application.gnat_name = "Global Network Anomaly Tracker"


# ============================================================================
# WSGI Application Wrapper (Optional - for custom middleware)
# ============================================================================


class WSGIApplicationWrapper:
    """
    Wrapper class for the WSGI application to add custom middleware
    at the WSGI level (before Django processes requests).

    This is useful for:
    - Request timing
    - Custom logging
    - Health checks
    - Rate limiting at the WSGI level
    """

    def __init__(self, app: Any) -> None:
        """
        Initialize the WSGI wrapper.

        Args:
            app: The WSGI application to wrap.
        """
        self.app = app

    def __call__(self, environ: dict[str, Any], start_response: Any) -> Any:
        """
        Call the WSGI application.

        Args:
            environ: WSGI environment dictionary.
            start_response: WSGI start_response callable.

        Returns:
            The response from the WSGI application.
        """
        # Add custom WSGI-level middleware here
        # Example: timing, logging, etc.

        return self.app(environ, start_response)


# Uncomment to enable WSGI wrapper
# application = WSGIApplicationWrapper(application)


# ============================================================================
# Health Check Endpoint (Optional - for load balancers)
# ============================================================================


class HealthCheckApplication:
    """
    Simple WSGI application for health checks.

    This can be used by load balancers and orchestrators to verify
    application health without going through Django.

    Usage:
        Map /health to this application in your WSGI server config.
    """

    def __init__(self, app: Any) -> None:
        """
        Initialize the health check application.

        Args:
            app: The main WSGI application.
        """
        self.app = app

    def __call__(self, environ: dict[str, Any], start_response: Any) -> Any:
        """
        Handle the health check request.

        Args:
            environ: WSGI environment dictionary.
            start_response: WSGI start_response callable.

        Returns:
            The health check response.
        """
        if environ.get("PATH_INFO") == "/health":
            status = "200 OK"
            headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", "2"),
            ]
            start_response(status, headers)
            return [b"OK"]

        return self.app(environ, start_response)


# Uncomment to enable health check at WSGI level
# application = HealthCheckApplication(application)


# ============================================================================
# Development Information
# ============================================================================

if __name__ == "__main__":
    """
    Development server startup.

    This allows running the WSGI application directly for testing:
        python config/wsgi.py

    For production deployment, always use Gunicorn or uWSGI.
    """
    import sys
    from wsgiref.simple_server import make_server

    # Override settings for development
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
        print("Running in development mode...")
    else:
        print("Running in production mode...")

    host = os.environ.get("WSGI_HOST", "0.0.0.0")
    port = int(os.environ.get("WSGI_PORT", "8000"))

    print(f"Starting WSGI server on {host}:{port}")

    with make_server(host, port, application) as httpd:
        httpd.serve_forever()

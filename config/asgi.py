"""
ASGI Configuration for Async Support.

This module configures the ASGI application for Django with async support.
ASGI (Asynchronous Server Gateway Interface) enables:

- WebSocket connections
- Server-Sent Events (SSE)
- Async view support
- Long-running connections without blocking

Future Features:
- Real-time anomaly alerts via WebSockets
- Live dashboard updates
- Background task status streaming

Async Server Options:
- Uvicorn: Pure Python ASGI server
- Daphne: Django's recommended ASGI server
- Hypercorn: Supports HTTP/2, WebSockets

Deployment:
    uvicorn config.asgi:application \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 4 \
        --loop uvloop \
        --http httptools \
        --log-level info

Or with Daphne:
    daphne config.asgi:application \
        --bind 0.0.0.0 \
        --port 8000 \
        --workers 4 \
        --access-log - \
        --log-level info
"""

import os
from typing import Any

# Set default settings module if not set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# ============================================================================
# Django ASGI Application
# ============================================================================

from django.core.asgi import get_asgi_application

# Initialize Django ASGI application
django_asgi_app = get_asgi_application()


# ============================================================================
# WebSocket Middleware (Future - for real-time features)
# ============================================================================


class WebSocketMiddleware:
    """
    Middleware for handling WebSocket connections.

    This middleware will be used to handle WebSocket connections
    for real-time features like:
    - Live anomaly alerts
    - Dashboard updates
    - Training progress updates

    Status: PLACEHOLDER - Will be implemented when WebSocket features are added
    """

    def __init__(self, app: Any) -> None:
        """
        Initialize the WebSocket middleware.

        Args:
            app: The ASGI application to wrap.
        """
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> Any:
        """
        Handle ASGI scope, receive, and send.

        Args:
            scope: ASGI scope dictionary.
            receive: ASGI receive callable.
            send: ASGI send callable.

        Returns:
            The response from the ASGI application.
        """
        # WebSocket connection handling will be implemented here
        if scope.get("type") == "websocket":
            # Handle WebSocket connections
            pass

        # Pass non-WebSocket requests to the application
        return await self.app(scope, receive, send)


# ============================================================================
# Lifespan Events (Future - for application startup/shutdown)
# ============================================================================

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: Any) -> Any:
    """
    Manage application lifespan events.

    This is useful for:
    - Database connection initialization
    - Cache warmup
    - Model loading
    - Worker pool initialization

    Args:
        app: The ASGI application.

    Yields:
        None
    """
    # Startup
    print("ASGI application starting up...")

    # Initialize any resources here
    # Example: load AI models, warm up caches, etc.

    yield

    # Shutdown
    print("ASGI application shutting down...")

    # Clean up resources here
    # Example: close database connections, unload models, etc.


# ============================================================================
# Main ASGI Application
# ============================================================================


async def application(scope: dict[str, Any], receive: Any, send: Any) -> Any:
    """
    Main ASGI application entry point.

    This function routes requests to the appropriate handler based on
    the connection type (HTTP, WebSocket, etc.).

    Args:
        scope: ASGI scope dictionary containing request metadata.
        receive: ASGI receive callable for incoming messages.
        send: ASGI send callable for outgoing messages.

    Returns:
        The response from the appropriate handler.
    """
    # Route based on connection type
    if scope["type"] == "http":
        # HTTP requests are handled by Django
        await django_asgi_app(scope, receive, send)

    elif scope["type"] == "websocket":
        # WebSocket connections (future)
        # Currently, we reject WebSocket connections until implemented
        await send(
            {
                "type": "websocket.close",
                "code": 1000,
                "reason": "WebSocket support not yet implemented",
            }
        )

    elif scope["type"] == "lifespan":
        # Lifespan events
        async with lifespan(scope):
            while True:
                message = await receive()
                if message["type"] == "lifespan.shutdown":
                    break

    else:
        # Unsupported connection type
        raise ValueError(f"Unsupported ASGI connection type: {scope['type']}")


# ============================================================================
# Development Server
# ============================================================================

if __name__ == "__main__":
    """
    Development server startup.

    This allows running the ASGI application directly for testing:
        python config/asgi.py

    For production deployment, always use Uvicorn or Daphne.
    """
    import sys

    # Check if uvicorn is available
    try:
        import uvicorn
    except ImportError:
        print("uvicorn is required to run the ASGI server.")
        print("Install it with: pip install uvicorn[standard]")
        sys.exit(1)

    # Override settings for development
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
        print("Running in development mode...")
    else:
        print("Running in production mode...")

    host = os.environ.get("ASGI_HOST", "0.0.0.0")
    port = int(os.environ.get("ASGI_PORT", "8000"))

    # Run with uvicorn
    uvicorn.run(
        "config.asgi:application",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )


# ============================================================================
# Alternative: Using Starlette/FastAPI for WebSockets
# ============================================================================

# Future enhancement: Use Starlette for better WebSocket support
# from starlette.applications import Starlette
# from starlette.routing import Route, WebSocketRoute
# from starlette.middleware import Middleware
# from starlette.middleware.cors import CORSMiddleware

# async def homepage(request):
#     return await django_asgi_app(request.scope, request.receive, request.send)

# routes = [
#     Route("/", homepage),
#     # WebSocket routes will be added here
# ]

# # Alternative ASGI app using Starlette
# starlette_app = Starlette(
#     routes=routes,
#     middleware=[
#         Middleware(CORSMiddleware, allow_origins=["*"]),
#     ],
#     on_startup=[startup],
#     on_shutdown=[shutdown],
# )

"""
Django Settings Package.

This package contains environment-specific Django settings:
- base.py: Common configuration shared across all environments
- development.py: Development environment overrides
- production.py: Production environment overrides (security-focused)
- testing.py: Testing environment overrides (performance-focused)

Usage:
    export DJANGO_SETTINGS_MODULE=config.settings.development
    python manage.py runserver
"""
from typing import Any

# Default to development if not specified
import os
import sys

# This allows Django to find settings via python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
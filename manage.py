#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main() -> None:
    """
    Execute administrative tasks.

    This function serves as the entry point for Django's management commands.
    It sets up the Django settings module and executes the appropriate
    management command.

    Raises:
        ImportError: If Django is not installed or cannot be imported.
        Exception: If an error occurs during command execution.

    Example:
        >>> python manage.py runserver
        >>> python manage.py migrate
        >>> python manage.py createsuperuser
    """
    # Set the default settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Execute the command line utility
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
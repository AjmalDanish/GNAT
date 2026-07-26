"""
Celery Configuration for Background Tasks.

This module configures Celery for asynchronous task processing.
Celery is used for:

- AI model training (long-running tasks)
- Graph generation and analysis
- Batch processing
- Report generation
- Email notifications
- Data ingestion and processing

Architecture:
- Redis as message broker and result backend
- Task serialization via JSON
- Automatic task discovery from apps directory
- Task routing based on task type
- Worker prefetch optimization

Starting Workers:
    celery -A config.celery worker \
        --loglevel=info \
        --concurrency=4 \
        --prefetch-multiplier=1 \
        --max-tasks-per-child=1000

Starting Beat Scheduler:
    celery -A config.celery beat \
        --loglevel=info \
        --scheduler django_celery_beat.schedulers:DatabaseScheduler

Monitoring:
    celery -A config.celery flower \
        --port=5555
"""

import os
from typing import Any

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# ============================================================================
# Celery Application Initialization
# ============================================================================

app = Celery("gnat")

# Load configuration from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed apps
app.autodiscover_tasks(settings.INSTALLED_APPS)


# ============================================================================
# Celery Configuration
# ============================================================================

# Task serialization
app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    # Result backend
    result_backend=settings.CELERY_RESULT_BACKEND,
    result_expires=3600,  # 1 hour
    # Task execution
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_eager_propagates=settings.CELERY_TASK_EAGER_PROPAGATES,
    task_acks_late=settings.CELERY_TASK_ACKS_LATE,
    worker_prefetch_multiplier=settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
    broker_connection_retry_on_startup=settings.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP,
    # Task tracking
    task_track_started=True,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    # Worker settings
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=True,
    worker_proc_alive_timeout=60,
    # Optimization
    broker_connection_retry=True,
    broker_connection_max_retries=5,
    broker_connection_retry_on_startup=True,
)


# ============================================================================
# Task Routing
# ============================================================================

# Route tasks to different queues based on their type
app.conf.task_routes = {
    # AI/ML tasks - high priority, dedicated queue
    "apps.ai_engine.tasks.*": {"queue": "ai_tasks", "priority": 9},
    # Graph processing tasks - high priority, dedicated queue
    "apps.graph_engine.tasks.*": {"queue": "graph_tasks", "priority": 8},
    # Report generation tasks - medium priority
    "apps.reports.tasks.*": {"queue": "reports", "priority": 5},
    # Email notification tasks - low priority
    "apps.notifications.tasks.*": {"queue": "notifications", "priority": 3},
    # Analytics tasks - medium priority
    "apps.analytics.tasks.*": {"queue": "analytics", "priority": 6},
    # Data processing tasks - medium priority
    "apps.common.tasks.*": {"queue": "data", "priority": 4},
    # Default queue
    "celery.*": {"queue": "default", "priority": 1},
}


# ============================================================================
# Task Priority Configuration
# ============================================================================

# Priority levels (lower number = higher priority)
app.conf.task_default_priority = 5
app.conf.task_default_queue = "default"


# ============================================================================
# Beat Schedule (Periodic Tasks)
# ============================================================================

# Example schedule (customize based on requirements)
app.conf.beat_schedule = {
    # Daily cleanup tasks
    "cleanup-old-logs": {
        "task": "apps.common.tasks.cleanup_old_logs",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
    "cleanup-expired-sessions": {
        "task": "apps.common.tasks.cleanup_expired_sessions",
        "schedule": crontab(hour=3, minute=0),  # 3 AM daily
    },
    "generate-daily-report": {
        "task": "apps.analytics.tasks.generate_daily_report",
        "schedule": crontab(hour=6, minute=0),  # 6 AM daily
    },
    # Hourly tasks
    "check-system-health": {
        "task": "apps.common.tasks.check_system_health",
        "schedule": crontab(minute=0),  # Every hour
    },
    "monitor-celery-workers": {
        "task": "apps.common.tasks.monitor_celery_workers",
        "schedule": crontab(minute=30),  # Every 30 minutes
    },
}


# ============================================================================
# Task Result Backend Configuration
# ============================================================================

app.conf.update(
    # Result backend settings
    result_extended=True,
    result_compression="gzip",
    result_backend_transport_options={
        "retry_policy": {
            "timeout": 5.0,
            "max_retries": 3,
        },
    },
)


# ============================================================================
# Worker Configuration
# ============================================================================

app.conf.update(
    # Worker optimization
    worker_send_task_events=True,
    task_send_sent_event=True,
    # Task execution limits
    task_max_retries=3,
    task_default_retry_delay=60,  # seconds
    # Task compression
    task_compression="gzip",
    task_compression_threshold=1024,  # bytes
)


# ============================================================================
# Signals (Task Lifecycle Events)
# ============================================================================

import logging

from celery.signals import (
    task_failure,
    task_postrun,
    task_prerun,
    task_revoked,
    task_success,
    worker_ready,
    worker_shutdown,
)

logger = logging.getLogger(__name__)


@task_prerun.connect
def task_prerun_handler(
    sender: Any = None, task_id: str = None, task: Any = None, **kwargs: Any
) -> None:
    """
    Handle task pre-run signal.

    Args:
        sender: The task sender.
        task_id: The task ID.
        task: The task object.
        **kwargs: Additional keyword arguments.
    """
    logger.info(f"Task {task.name}[{task_id}] started")
    # Additional pre-run logic can be added here


@task_postrun.connect
def task_postrun_handler(
    sender: Any = None,
    task_id: str = None,
    task: Any = None,
    retval: Any = None,
    state: str = None,
    **kwargs: Any,
) -> None:
    """
    Handle task post-run signal.

    Args:
        sender: The task sender.
        task_id: The task ID.
        task: The task object.
        retval: The task return value.
        state: The task state.
        **kwargs: Additional keyword arguments.
    """
    logger.info(f"Task {task.name}[{task_id}] finished with state: {state}")
    # Additional post-run logic can be added here


@task_failure.connect
def task_failure_handler(
    sender: Any = None, task_id: str = None, exception: Any = None, **kwargs: Any
) -> None:
    """
    Handle task failure signal.

    Args:
        sender: The task sender.
        task_id: The task ID.
        exception: The exception that caused the failure.
        **kwargs: Additional keyword arguments.
    """
    logger.error(f"Task {sender.name}[{task_id}] failed: {exception}")
    # Additional failure handling can be added here (alerts, etc.)


@task_success.connect
def task_success_handler(sender: Any = None, result: Any = None, **kwargs: Any) -> None:
    """
    Handle task success signal.

    Args:
        sender: The task sender.
        result: The task result.
        **kwargs: Additional keyword arguments.
    """
    logger.info(f"Task {sender.name} completed successfully")
    # Additional success handling can be added here


@task_revoked.connect
def task_revoked_handler(sender: Any = None, request: Any = None, **kwargs: Any) -> None:
    """
    Handle task revoked signal.

    Args:
        sender: The task sender.
        request: The task request.
        **kwargs: Additional keyword arguments.
    """
    logger.warning(f"Task {sender.name} revoked")
    # Additional revocation handling can be added here


@worker_ready.connect
def worker_ready_handler(sender: Any = None, **kwargs: Any) -> None:
    """
    Handle worker ready signal.

    Args:
        sender: The worker sender.
        **kwargs: Additional keyword arguments.
    """
    logger.info(f"Celery worker {sender.hostname} is ready")
    # Additional worker ready logic can be added here


@worker_shutdown.connect
def worker_shutdown_handler(sender: Any = None, **kwargs: Any) -> None:
    """
    Handle worker shutdown signal.

    Args:
        sender: The worker sender.
        **kwargs: Additional keyword arguments.
    """
    logger.info(f"Celery worker {sender.hostname} is shutting down")
    # Additional worker shutdown logic can be added here


# ============================================================================
# Task Decorators (Custom)
# ============================================================================

from functools import wraps

from celery.exceptions import Retry


def task_with_logging(task_func: Any) -> Any:
    """
    Decorator to add logging to Celery tasks.

    Args:
        task_func: The task function to decorate.

    Returns:
        The decorated task function.
    """

    @wraps(task_func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(f"Starting task: {task_func.__name__}")
        try:
            result = task_func(*args, **kwargs)
            logger.info(f"Completed task: {task_func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Task {task_func.__name__} failed: {e}")
            raise

    return wrapper


def task_with_retry(max_retries: int = 3, countdown: int = 60) -> Any:
    """
    Decorator to add automatic retry to Celery tasks.

    Args:
        max_retries: Maximum number of retries.
        countdown: Seconds between retries.

    Returns:
        The decorator function.
    """

    def decorator(task_func: Any) -> Any:
        @wraps(task_func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            try:
                return task_func(self, *args, **kwargs)
            except Exception as exc:
                logger.warning(f"Task {task_func.__name__} failed, retrying...")
                raise self.retry(exc=exc, max_retries=max_retries, countdown=countdown)

        return wrapper

    return decorator


# ============================================================================
# Debug Task
# ============================================================================


@app.task(bind=True)
def debug_task(self: Any) -> str:
    """
    Debug task for testing Celery configuration.

    Args:
        self: The task instance.

    Returns:
        A debug message.
    """
    logger.info(f"Request: {self.request!r}")
    return f"Debug task executed successfully. Request: {self.request!r}"


# ============================================================================
# Health Check Task
# ============================================================================


@app.task(bind=True, name="config.celery.health_check")
def health_check_task(self: Any) -> dict[str, Any]:
    """
    Health check task for Celery.

    Args:
        self: The task instance.

    Returns:
        Health check status.
    """
    from datetime import datetime

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "task_id": self.request.id,
        "worker": self.request.hostname,
    }


# ============================================================================
# Development Information
# ============================================================================

if __name__ == "__main__":
    """
    Development startup.

    This allows running Celery directly:
        python config/celery.py

    For production, always use the celery command.
    """
    print("Celery configuration loaded successfully.")
    print(f"Broker URL: {app.conf.broker_url}")
    print(f"Result Backend: {app.conf.result_backend}")
    print(f"Timezone: {app.conf.timezone}")
    print(f"Beat Schedule: {len(app.conf.beat_schedule)} periodic tasks")

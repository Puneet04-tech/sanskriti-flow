"""
Celery Worker Configuration
"""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "sanskriti_flow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.workers'])

"""
Celery App Configuration
Vocaply Platform - Day 7

Background task queue for transcription, AI processing, notifications.
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# ============================================
# CELERY APP
# ============================================

celery_app = Celery(
    "vocaply",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.transcription_worker",
        "app.workers.ai_analysis_worker",  # Day 10: AI extraction
    ],
)

# ============================================
# CONFIGURATION
# ============================================

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_time_limit=3600,        # 1 hour hard limit
    task_soft_time_limit=3300,   # 55 min soft limit
    task_acks_late=True,         # Acknowledge after completion
    worker_prefetch_multiplier=1, # Process one at a time
    
    # Retries
    task_default_retry_delay=300,  # 5 minutes
    task_max_retries=3,
    
    # Result backend
    result_expires=86400,  # 24 hours
    result_backend_transport_options={
        "master_name": "mymaster",
    },
    
    # Broker
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    
    # Worker
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (prevent memory leaks)
    worker_disable_rate_limits=False,
)

# ============================================
# BEAT SCHEDULE (Periodic Tasks)
# ============================================

celery_app.conf.beat_schedule = {
    # Cleanup old job results every day at 3 AM
    "cleanup-old-results": {
        "task": "app.workers.transcription_worker.cleanup_old_results",
        "schedule": crontab(hour=3, minute=0),
    },

    # Check for stuck transcription jobs every 10 minutes
    "check-stuck-jobs": {
        "task": "app.workers.transcription_worker.check_stuck_jobs",
        "schedule": crontab(minute="*/10"),
    },

    # Retry AI analyses stuck in 'processing' every 15 minutes
    "retry-stuck-analyses": {
        "task": "app.workers.ai_analysis_worker.retry_stuck_analyses",
        "schedule": crontab(minute="*/15"),
    },
}

# ============================================
# TASK ROUTES (optional - direct tasks to specific queues)
# ============================================

celery_app.conf.task_routes = {
    "app.workers.transcription_worker.*": {"queue": "transcription"},
    "app.workers.ai_analysis_worker.*":   {"queue": "ai"},
}

# ============================================
# LOGGING
# ============================================

celery_app.conf.worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
celery_app.conf.worker_task_log_format = (
    "[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s"
)
"""
Celery Application Configuration for Bondhu AI
Handles background task processing for music/video fetching, sentiment analysis, etc.
"""

from celery import Celery
from celery.schedules import crontab
from core.config import get_config

# Get configuration
config = get_config()

# Create Celery app
celery_app = Celery(
    'bondhu',
    broker=config.celery.broker_url,
    backend=config.celery.result_backend,
    include=[
        'core.tasks.personality',
    ]
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
    
    # Task tracking (DISABLE to reduce Redis operations)
    task_track_started=False,  # Don't track task start events
    task_send_sent_event=False,  # Don't send task sent events
    worker_send_task_events=False,  # Disable worker task events
    
    # Task time limits (5 minutes hard limit, 4 minutes soft limit)
    task_time_limit=300,
    task_soft_time_limit=240,
    
    # Worker configuration
    worker_prefetch_multiplier=1,  # Reduced from 4 to minimize Redis polling
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Broker connection settings (AGGRESSIVE polling reduction for free tier)
    broker_connection_retry_on_startup=True,
    broker_pool_limit=1,  # Minimize connection pool to 1
    broker_heartbeat=0,  # DISABLE heartbeat to reduce polling
    broker_connection_max_retries=3,
    
    # Transport options (reduce Redis polling frequency)
    broker_transport_options={
        'visibility_timeout': 43200,  # 12 hours
        'fanout_prefix': True,
        'fanout_patterns': True,
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.5,
        'interval_max': 3,
        # CRITICAL: Increase sleep time between polls from 0.1s to 5s
        'max_sleep_time': 5,  # Sleep 5 seconds between queue checks
    },
    
    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        'retry_policy': {
            'timeout': 5.0
        }
    },
    
    # CRITICAL: Disable result backend to reduce Redis usage by 50%
    # We can re-enable this when we actually need task results
    # For now, tasks run fire-and-forget style
    task_ignore_result=True,  # Don't store results in Redis
    
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Rate limiting
    task_default_rate_limit='100/m',  # 100 tasks per minute
    
    # Task routes (optional: send specific tasks to specific queues)
    task_routes={
        'core.tasks.music.*': {'queue': 'music'},
        'core.tasks.video.*': {'queue': 'video'},
        'core.tasks.personality.*': {'queue': 'personality'},
    },
    
    # Beat schedule (periodic tasks)
    # WARNING: Each periodic task polls Redis constantly. Only enable tasks that exist!
    beat_schedule={
        # Analyze chat sentiment every hour (DISABLED until we have real users)
        # 'analyze-chat-sentiment-hourly': {
        #     'task': 'core.tasks.personality.analyze_all_users_sentiment',
        #     'schedule': crontab(minute=0),  # Every hour at minute 0
        # },
        
        # NOTE: These tasks don't exist yet - will be added in Days 3-6
        # 'refresh-music-preferences-daily': {
        #     'task': 'core.tasks.music.refresh_all_music_preferences',
        #     'schedule': crontab(hour=3, minute=0),
        # },
        # 'cleanup-expired-cache': {
        #     'task': 'core.tasks.maintenance.cleanup_expired_cache',
        #     'schedule': crontab(hour='*/6', minute=0),
        # },
    },
)

# Task annotations (for specific task configuration)
celery_app.conf.task_annotations = {
    'core.tasks.music.fetch_spotify_preferences': {
        'rate_limit': '10/m',  # Max 10 per minute (Spotify API limit)
    },
    'core.tasks.video.fetch_youtube_preferences': {
        'rate_limit': '20/m',  # Max 20 per minute (YouTube API limit)
    },
}


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery setup."""
    print(f'Request: {self.request!r}')
    return 'Celery is working!'


# Celery signals
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Set up periodic tasks after Celery configuration."""
    print("Celery periodic tasks configured")


if __name__ == '__main__':
    celery_app.start()

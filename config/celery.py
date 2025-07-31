"""
Celery configuration for The Last Neuron project.
"""

import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create Celery app
app = Celery('the_last_neuron')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed Django apps
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'retrain-personality-models': {
        'task': 'apps.ml.tasks.retrain_personality_models',
        'schedule': 72 * 60 * 60,  # Every 72 hours
    },
    'cleanup-old-sessions': {
        'task': 'apps.chat.tasks.cleanup_old_sessions',
        'schedule': 24 * 60 * 60,  # Daily
    },
    'send-proactive-messages': {
        'task': 'apps.chat.tasks.send_proactive_messages',
        'schedule': 30 * 60,  # Every 30 minutes
    },
}

# Celery timezone
app.conf.timezone = 'Asia/Kolkata'

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')

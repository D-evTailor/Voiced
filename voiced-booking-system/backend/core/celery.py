import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

app = Celery('voiceappoint')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'cleanup-expired-tokens': {
        'task': 'apps.users.tasks.cleanup_expired_tokens',
        'schedule': 60.0 * 60.0 * 24.0,  # Daily
    },
    'send-appointment-reminders': {
        'task': 'apps.notifications.tasks.send_appointment_reminders',
        'schedule': 60.0 * 15.0,  # Every 15 minutes
    },
    'update-business-metrics': {
        'task': 'apps.analytics.tasks.update_daily_metrics',
        'schedule': 60.0 * 60.0,  # Hourly
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery functionality."""
    print(f'Request: {self.request!r}')

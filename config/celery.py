import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('library_api')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Explicitly set broker URL
app.conf.broker_url = "redis://localhost:6379/0"
app.conf.result_backend = "redis://localhost:6379/0"

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'check-book-returns': {
        'task': 'notifications.tasks.check_and_send_return_reminders',
        'schedule': crontab(hour=9, minute=0),  # Run at 9:00 AM every day
    },
}

# Windows-specific settings
app.conf.update(
    worker_pool_restarts=True,
    worker_concurrency=1,  # Use only one worker process
    task_always_eager=False,
    task_ignore_result=True,
)
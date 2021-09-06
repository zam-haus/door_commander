import os

from celery import Celery, shared_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'door_commander.settings')

app = Celery('door_commander')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

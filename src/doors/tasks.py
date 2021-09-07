
# NEW
from celery import shared_task
from django.core.management import call_command


@shared_task
def publish_door_names():
    call_command("publish_door_names", )
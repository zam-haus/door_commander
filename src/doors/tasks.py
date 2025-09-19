from celery import shared_task
from django.core.management import call_command


@shared_task
def publish_door_names():
    call_command("publish_door_names", )

@shared_task
def update_mqtt_dynsec():
    call_command("update_mqtt_dynsec", )
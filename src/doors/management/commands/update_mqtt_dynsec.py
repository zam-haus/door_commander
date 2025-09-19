from django.core.management.base import BaseCommand

from doors.mqtt_dynsec import update_mqtt_dynamic_security


class Command(BaseCommand):
    help = "Updates the mqtt dynamic security"

    def handle(self, *args, **options):
        update_mqtt_dynamic_security()


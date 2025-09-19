from django.core.management.base import BaseCommand
from doors.door_names_publisher import publish_door_names

class Command(BaseCommand):
    help = "Publishes the names of all the doors on MQTT"

    def handle(self, *args, **options):
        publish_door_names(True)


from django.core.management.base import BaseCommand, CommandError
from web_homepage.door_names_publisher import publish_door_names

class Command(BaseCommand):
    help = "A description of the command"

    def handle(self, *args, **options):
        publish_door_names()


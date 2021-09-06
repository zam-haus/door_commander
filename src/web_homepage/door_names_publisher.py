import json
import logging

from django.conf import settings

from door_commander.mqtt import door_commander_mqtt
from web_homepage.models import Door

log = logging.getLogger(__name__)


def publish_door_names():
    for door in Door.objects.all():
        publish_door_name(door)


def publish_door_name(door):
    log.info("publishing door names for door {}".format(door.id))
    door_commander_mqtt.publish("door/+/display_name", door.mqtt_id, qos=2, retain=True,
                                payload=json.dumps(door.display_name))

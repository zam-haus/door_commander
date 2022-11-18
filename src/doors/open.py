import logging
import time

from icecream import ic

from doors.models import Door
from doors.mqtt import door_commander_mqtt
from doors.check_request import check_can_open_door
from door_commander.request_location_info import IPWARE_KWARGS

from ipware import get_client_ip

log = logging.getLogger(__name__)

def check_permission_and_open(door_id, request):
    """opens the door if the user is allowed to"""

    if check_can_open_door(request, Door.objects.get(pk=door_id)):
        assert door_commander_mqtt
        door = Door.objects.get(pk=door_id)
        mqtt_id = door.mqtt_id

        door_commander_mqtt.open(mqtt_id, timeout=time.time() + 30)

        log.warning(ic.format(
            request.user,
            get_client_ip(request, **IPWARE_KWARGS),
            door,
            door.display_name))

        return True
    else:
        return False

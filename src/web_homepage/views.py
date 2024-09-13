import logging

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from icecream import ic

from doors.check_request import check_can_open_door, check_can_view_door, check_location_hint
from doors.mqtt import door_commander_mqtt
from doors.models import Door
from doors.open import check_permission_and_open

log = logging.getLogger(__name__)


def home(request):
    user_doors = list(door for door in Door.objects.all() if check_can_view_door(request, door))
    # has_allowed_location, allowed_location_reason = check_has_allowed_location(request)
    doors_status = fetch_status()
    can_open_doors = {door: check_can_open_door(request, door) for door in user_doors}
    log.debug(ic.format(can_open_doors, user_doors))
    context = dict(
        can_open_doors=can_open_doors,
        doors=user_doors,
        doors_status=doors_status,
        show_location_hint=check_location_hint(request)
    )
    return render(request, 'web_homepage/index.html', context=context)
    # return redirect("https://betreiberverein.de/impressum/")


def fetch_status():
    return {
        (
            door.display_name,
            door_commander_mqtt.doors_presence.get(door.mqtt_id),
        ) for door in (Door.objects.all())
    }


@require_POST  # for CSRF protection
def open(request, door_id):
    success = check_permission_and_open(door_id, request)

    if not success:
        location_hint = check_location_hint(request)
        log.error("Door open denied, showing hint = %r", location_hint)
        if location_hint:
            messages.error(request, "You are in the wrong location. Consider joining the ZAM Wi-Fi.")
            return redirect(home)
        else:
            raise PermissionDenied("You are not allowed to open the door.")

    log.debug("Door opened")
    return redirect(home)



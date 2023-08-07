import ipaddress
import json
import logging
import time

from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from icecream import ic
from ipware import get_client_ip

from accounts.models import User
from door_commander.opa import get_allowed_result
from doors.mqtt import door_commander_mqtt
from django.conf import settings
from doors.models import PERMISSION_OPEN_DOOR, Door
from clientipaddress.mqtt import wifi_locator_mqtt

log = logging.getLogger(__name__)
log_ip = logging.getLogger(__name__ + ".ip")

IPWARE_KWARGS = getattr(settings, 'IPWARE_KWARGS', None)
PERMITTED_IP_NETWORKS = getattr(settings, 'PERMITTED_IP_NETWORKS', None)


def home(request):
    user_doors = list(door for door in Door.objects.all() if check_can_view_door(request, door))
    user_doors.sort(key=lambda d: d.order)
    #has_allowed_location, allowed_location_reason = check_has_allowed_location(request)
    doors_status = fetch_status()
    can_open_doors = {door: check_can_open_door(request, door) for door in user_doors}
    ic(can_open_doors, user_doors)
    context= dict(
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


def create_door_info(door):
    return dict(door=serialize_model(door))


def check_can_open_door(request, door):
    user_dict = create_request_user_info(request)
    has_permission = get_allowed_result("app/door_commander/physical_access", dict(action="open",user=user_dict,door=create_door_info(door)))
    return has_permission
def check_can_view_door(request, door):
    user_dict = create_request_user_info(request)
    has_permission = get_allowed_result("app/door_commander/physical_access", dict(action="view",user=user_dict,door=create_door_info(door)))
    return has_permission

def check_location_hint(request):
    user_dict = create_request_user_info(request)
    has_permission = get_allowed_result("app/door_commander/physical_access", dict(user=user_dict), key="show_location_hint")
    return has_permission


def create_request_user_info(request):
    permissions = [serialize_model(perm) for perm in request.user.user_permissions.all()]
    if isinstance(request.user, User):
        user = serialize_model(request.user)
        user_connections = [serialize_model(conn) for conn in request.user.connections.all()]
    else:
        user = None
        user_connections = []
    authenticated = request.user.is_authenticated
    location_info = get_location_info(request)
    #ic(user_connections, permissions, user, authenticated, location_info)
    user_dict = dict(authenticated=authenticated, user=user, user_permissions=permissions,
                     user_connections=user_connections,
                     location=location_info, )
    return user_dict


def serialize_model(model):
    return json.loads(serializers.serialize('json', [model, ]))[0]


def get_location_info(request):
    if IPWARE_KWARGS is None or PERMITTED_IP_NETWORKS is None:
        return dict(status="IPWARE_NOT_CONFIGURED")
    else:
        ip = get_client_ip(request, **IPWARE_KWARGS)
        log_ip.debug(ic.format('ip', ip))
        # log_ip.debug(ic.format(request.META))
        # log_ip.debug(ic.format(request.headers))
        if ip:
            networks = wifi_locator_mqtt.ip_networks
            locator_status = {
                locator_mqtt_id: [
                    (ip in locator_ip_network)
                    for locator_ip_network in locator_ip_networks
                ]
                for locator_mqtt_id, locator_ip_networks in networks.items()
            }
            permitted_networks_status = {
                str(network): (ipaddress.ip_address(ip) in network)
                for network in PERMITTED_IP_NETWORKS
            }
            return dict(ip=str(ip), permitted_networks_status=permitted_networks_status, locator_status=locator_status)
        else:
            return dict(status="NO_IP_PRESENT")


def open(request, door_id):
    if not request.POST:
        messages.error(request, "Please try again.")
        return redirect(home)

    if not check_can_open_door(request, Door.objects.get(pk=door_id)):

        if check_location_hint(request):
            messages.error(request, "You are in the wrong location. Consider joining the ZAM Wi-Fi.")
            return redirect(home)

        raise PermissionDenied("You are not allowed to open the door.")


    assert door_commander_mqtt
    door = Door.objects.get(pk=door_id)
    mqtt_id = door.mqtt_id

    door_commander_mqtt.open(mqtt_id, timeout=time.time() + 30)

    log.warn(ic.format(
        request.user,
        get_client_ip(request, **IPWARE_KWARGS),
        door,
        door.display_name))

    return redirect(home)

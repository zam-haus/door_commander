import ipaddress
import random

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import redirect, render
from django.http import HttpResponseNotFound
from django.shortcuts import render

from django.http import HttpResponse
from django.template.context_processors import request
from django.views.decorators.http import require_POST
from pymaybe import maybe
from ipware import get_client_ip

from door_commander.settings import IPWARE_KWARGS, PERMITTED_IP_NETWORKS


def home(request):
    context = get_request_context(request)
    return render(request, 'web_homepage/index.html', context=context)
    # return redirect("https://betreiberverein.de/impressum/")


def get_request_context(request):
    context = dict(
        can_open_door=check_can_open_door(request)
    )
    return context


def check_can_open_door(request):
    is_authenticated = request.user.is_authenticated
    has_permission = request.user.has_perm(PERMISSION_OPEN_DOOR)
    has_allowed_location = check_has_allowed_location(request)
    return is_authenticated and has_permission and has_allowed_location and False


def check_has_allowed_location(request):
    ip, is_public = get_client_ip(request, **IPWARE_KWARGS)
    has_correct_location = False
    if ip:
        # Allow requests from the local network of the server
        if not is_public:
            has_correct_location = True
        if any((ipaddress.ip_address(ip) in network for network in PERMITTED_IP_NETWORKS)):
            has_correct_location = True
        if request.user.has_perm(PERMISSION_LOCATION_OVERRIDE):
            has_correct_location = True
    return has_correct_location


PERMISSION_OPEN_DOOR = 'door_controller.open_door'
PERMISSION_LOCATION_OVERRIDE = 'door_controller.assume_correct_location'


@require_POST  # for CSRF protection
@login_required
@permission_required(PERMISSION_OPEN_DOOR) # this is just a safeguard, there are more requirements.
def open(request):
    if not check_can_open_door(request):
        raise PermissionDenied("You are not allowed to open the door.")
    context = get_request_context(request)
    context.update(dict(message="CLEARLY MAYBE DONE!"))
    return render(request, 'web_homepage/open.html', context=context)
